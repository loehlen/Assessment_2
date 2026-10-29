"""
logic/ai_client.py - the one wrapper every AI call goes through.

    ai = AI(profile="dev", api_key=..., use_cache=True, log=CallLog())   one per run
    ai.respond(step, input, ...)     Responses API call: the model for this step comes from the profile,
                                     timeout, one retry, every call logged (tokens, reasoning tokens,
                                     web searches, time, cost, names contained)
    ai.embed(texts, note)            embeddings (text-embedding-3-large), logged the same way
    ai.cache_get / ai.cache_put      response cache in cache/, DEVELOPMENT ONLY (re-running a test case costs
                                     nothing); never active in the submitted version.

The confidentiality guard (rules.find_names) is applied by the step modules before every request, because only
they know which company a call is allowed to contain. This file has no Streamlit code, so it runs in the terminal.

Settings are read from .env (Codespace) or from Secrets (Streamlit Cloud), never from the code:
    DEV_MODE=1              password gate, cost counter, development tools (switch OFF before submission)
    MODEL_PROFILE=dev       dev = GPT-6 Luna everywhere; final = the models chosen per step (PROFILES below)
    USE_CACHE=1             response cache on (only has an effect when DEV_MODE=1)
    MODEL_<STEP>=...        optional override for one step, e.g. MODEL_COMPARE=gpt-6.1-sol (evaluation runs)
"""
import hashlib
import json
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# =============================================================== settings (.env or Streamlit Secrets)
def setting(name, default=""):
    """A setting from the environment (.env) or, on Streamlit Cloud, from Secrets."""
    value = os.getenv(name)
    if value is None:
        try:
            import streamlit as st
            value = st.secrets.get(name)          # raises if there is no secrets file at all
        except Exception:  # noqa: BLE001 - no Streamlit, or no secrets: use the default
            value = None
    return default if value is None else str(value)


def flag(name, default=False):
    return setting(name, "1" if default else "0").strip().lower() in {"1", "true", "yes", "on"}


# =============================================================== models per step
EMBED_MODEL = "text-embedding-3-large"
STEPS = ("search", "extract", "compare", "query", "reflect", "check")

PROFILES = {
    # Development: GPT-6 Luna for every step. The step ④ reflection runs at medium effort, as in the submitted
    # version, because at low effort the same input gave different results from run to run.
    "dev": {step: ("gpt-6-luna", "medium" if step == "reflect" else "low") for step in STEPS},
    # The submitted version
    "final": {
        # Luna with two complementary searches per company: in testing, a single search by the larger model found
        # little more but cost many times as much and took several minutes per test case.
        "search": ("gpt-6-luna", "low"),
        "extract": ("gpt-6-luna", "low"),
        "compare": ("gpt-6-luna", "low"),
        "query": ("gpt-6-luna", "low"),
        # Luna at medium effort, as tested on all test cases (the larger model would cost about 20 times as much)
        "reflect": ("gpt-6-luna", "medium"),
        "check": ("gpt-6-luna", "low"),        # the one-word connection test of the deployment check
    },
}
# Invalid structured output: one retry with the same model, then this (different) model
FALLBACK = {"dev": "gpt-6.1-sol", "final": "gpt-6.1-sol"}

# USD per 1M tokens (input, output), from third-party listings (to verify on OpenAI's pricing page). The pages a
# search reads count as input tokens of the search call.
PRICES_CHECKED = "third-party listings, Oct 2026 (to verify)"
PRICES = {
    "gpt-6-luna": (0.10, 0.50),
    "gpt-6.1-sol": (2.00, 10.00),
    "text-embedding-3-large": (0.13, 0.0),
}

# The web search tool is billed per call on top of the tokens: USD 10 per 1,000 calls (third-party listing, to
# verify). A run with two searches per company makes dozens of such calls, so the fee is several times the token
# cost. WEB_SEARCH_FEE in .env / Secrets overrides it.
WEB_SEARCH_FEE = float(setting("WEB_SEARCH_FEE", "0.01") or 0)    # USD per web search call

TIMEOUT = 300           # seconds; a long web search can take several minutes
# Requests at once per run (enforced in AI.respond / AI.embed, see _slots); each one is a separate, stateless call.
# A rate limit of the key is waited out (_with_retry) instead of failing the call. MAX_PARALLEL in .env / Secrets
# overrides it.
MAX_PARALLEL = max(1, int(setting("MAX_PARALLEL", "16") or 16))
RATE_LIMIT_WAITS = (5, 10, 20, 40)      # seconds between the attempts after HTTP 429 (at most 75 s in all)
CACHE_DIR = Path("cache")


def _rate_limited(e):
    """Whether an API error is a rate limit (HTTP 429), not another error."""
    return getattr(e, "status_code", None) == 429 or type(e).__name__ == "RateLimitError"


def _retry_after(e):
    """The wait the API asks for in its 'retry-after' header, in seconds (at most 60), or None."""
    try:
        return min(60.0, float(getattr(getattr(e, "response", None), "headers", {}).get("retry-after")))
    except (TypeError, ValueError):
        return None


def reasoning(model, effort):
    """Reasoning effort only for the reasoning models."""
    return {"reasoning": {"effort": effort}} if model.startswith(("gpt-5", "gpt-6", "o")) else {}


# A separate function, so that a test can replace it with a fake client.
def client_factory(api_key, timeout):
    from openai import OpenAI
    return OpenAI(api_key=api_key or None, timeout=timeout)


# =============================================================== call log (feeds the run summary and the audit log)
class CallLog:
    """Every AI call of a session: step, model, tokens, time, cost, names contained. Thread-safe."""

    def __init__(self):
        self.calls = []
        self._lock = threading.Lock()

    def add(self, **entry):
        with self._lock:
            entry["n"] = len(self.calls) + 1
            self.calls.append(entry)

    def mark(self):
        """Position in the log, so a stage can report only its own calls."""
        return len(self.calls)

    def summary(self, since=0):
        calls = self.calls[since:]
        steps = {}
        for c in calls:
            s = steps.setdefault(c["step"], {"calls": 0, "cached": 0, "in": 0, "out": 0, "cost": 0.0, "seconds": 0.0})
            s["calls"] += 1
            s["cached"] += c["cached"]
            s["in"] += c["in"]
            s["out"] += c["out"]
            s["cost"] += c["cost"]
            s["seconds"] += c["seconds"]
        return {"calls": len(calls), "cached": sum(c["cached"] for c in calls),
                "cost": round(sum(c["cost"] for c in calls), 4),
                "search_fees": round(sum(c.get("search_fee", 0.0) for c in calls), 4),
                "unpriced": sorted({c["model"] for c in calls if not c.get("priced", True)}),
                "web_searches": sum(c.get("web_searches", 0) for c in calls),
                "models": sorted({c["model"] for c in calls}), "steps": steps}


# =============================================================== the wrapper
class AI:
    def __init__(self, profile="dev", api_key=None, use_cache=False, log=None, timeout=TIMEOUT, cache_dir=CACHE_DIR):
        if profile not in PROFILES:
            raise ValueError(f"Unknown MODEL_PROFILE '{profile}' (use 'dev' or 'final')")
        self.profile = profile
        self.api_key = api_key
        self.use_cache = use_cache
        self.log = log if log is not None else CallLog()
        self.timeout = timeout
        self.cache_dir = Path(cache_dir)
        self._client = None
        self._lock = threading.Lock()
        # At most MAX_PARALLEL requests at once, however the steps nest their thread pools (the two searches per
        # company run inside the pool of companies). Matters for the rate limits of the user's own key.
        self._slots = threading.BoundedSemaphore(MAX_PARALLEL)
        # Resolved once, here, so that worker threads never read settings: an override in .env / Secrets
        # (MODEL_COMPARE=gpt-6.1-sol, EFFORT_REFLECT=high) wins over the profile.
        self.models = {s: setting(f"MODEL_{s.upper()}", "") or PROFILES[profile][s][0] for s in STEPS}
        self.efforts = {s: setting(f"EFFORT_{s.upper()}", "") or PROFILES[profile][s][1] for s in STEPS}
        self._fallback = setting("MODEL_FALLBACK", "") or FALLBACK[profile]

    # ------------------------------------------------------------------ models
    def model(self, step):
        return self.models[step]

    def effort(self, step):
        return self.efforts.get(step, "low")

    def fallback(self):
        return self._fallback

    def client(self):
        with self._lock:
            if self._client is None:
                self._client = client_factory(self.api_key, self.timeout)
            return self._client

    # ------------------------------------------------------------------ calls
    def respond(self, step, input, *, instructions=None, schema=None, web_search=False, model=None,
                note="", names=()):
        """
        One Responses API call. schema (a pydantic model) -> responses.parse with Structured Outputs.
        Stateless: no previous_response_id, no shared conversation, so parallel calls never see each other.
        names: the company names this call contains (for the audit trail; the guard has already checked them).
        """
        model = model or self.model(step)
        kwargs = {"model": model, "input": input, **reasoning(model, self.effort(step))}
        if instructions:
            kwargs["instructions"] = instructions
        if web_search:
            kwargs["tools"] = [{"type": "web_search"}]
        if schema is not None:
            kwargs["text_format"] = schema
        fn = self.client().responses.parse if schema is not None else self.client().responses.create
        with self._slots:
            t = time.time()
            resp, waits = self._with_retry(fn, **kwargs)
            seconds = time.time() - t
        self._log_response(step, model, resp, seconds, note, names, waits)
        return resp

    def embed(self, texts, note="", step="embed"):
        """Embeddings for a list of texts (one request). Returns a list of vectors."""
        with self._slots:
            t = time.time()
            resp, waits = self._with_retry(self.client().embeddings.create, model=EMBED_MODEL, input=texts)
            seconds = time.time() - t
        tokens = getattr(getattr(resp, "usage", None), "prompt_tokens", 0) or 0
        self._add(step, EMBED_MODEL, tokens, 0, seconds, note=note, rate_limit_waits=waits)
        return [d.embedding for d in resp.data]

    def embed_fn(self, step="embed_query"):
        """A plain function texts -> vectors, as retrieval.py expects."""
        return lambda texts: self.embed(texts, note="retrieval query", step=step)

    def _with_retry(self, fn, **kwargs):
        """Returns (response, number of rate-limit waits). Any API error: one retry after 3 s, then the caller decides.
        A rate limit (HTTP 429, e.g. requests or tokens per minute of a new key) is waited out instead, up to
        four times (RATE_LIMIT_WAITS, or the time the API asks for, at most 60 s), so that 16 requests at once never
        turn into failed calls; the waits are recorded in the call log."""
        errors, waits = 0, 0
        while True:
            try:
                return fn(**kwargs), waits
            except Exception as e:  # noqa: BLE001 - retried below, then raised to the caller
                if _rate_limited(e) and waits < len(RATE_LIMIT_WAITS):
                    time.sleep(_retry_after(e) or RATE_LIMIT_WAITS[waits])
                    waits += 1
                    continue
                errors += 1
                if errors == 2:
                    raise
                time.sleep(3)

    # ------------------------------------------------------------------ logging
    def _log_response(self, step, model, resp, seconds, note, names, waits=0):
        u = getattr(resp, "usage", None)
        tokens_in = getattr(u, "input_tokens", 0) or 0
        tokens_out = getattr(u, "output_tokens", 0) or 0
        details = getattr(u, "output_tokens_details", None)
        reasoning_tokens = getattr(details, "reasoning_tokens", 0) or 0
        searches = sum(1 for item in (getattr(resp, "output", None) or [])
                       if getattr(item, "type", "") == "web_search_call")
        self._add(step, model, tokens_in, tokens_out, seconds, note=note, names=list(names),
                  reasoning_tokens=reasoning_tokens, web_searches=searches, rate_limit_waits=waits)

    def _add(self, step, model, tokens_in, tokens_out, seconds, cached=False, **extra):
        price = PRICES.get(model)
        cost = 0.0 if cached or price is None else tokens_in / 1e6 * price[0] + tokens_out / 1e6 * price[1]
        search_fee = 0.0 if cached else extra.get("web_searches", 0) * WEB_SEARCH_FEE
        self.log.add(step=step, model=model, **{"in": tokens_in, "out": tokens_out}, seconds=round(seconds, 1),
                     cost=round(cost + search_fee, 6), search_fee=round(search_fee, 6), cached=cached,
                     priced=price is not None or cached, **extra)

    def log_cached(self, step, model, note="", names=()):
        self._add(step, model, 0, 0, 0, cached=True, note=note, names=list(names))

    # ------------------------------------------------------------------ response cache (development only)
    def cache_get(self, kind, key_parts):
        """Cache key: sha256 of the JSON of the key parts, first 20 characters."""
        if not self.use_cache:
            return None, None
        key = hashlib.sha256(json.dumps(key_parts, sort_keys=True, ensure_ascii=False, default=str)
                             .encode()).hexdigest()[:20]
        path = self.cache_dir / kind / f"{key}.json"
        return path, (json.loads(path.read_text(encoding="utf-8")) if path.exists() else None)

    def cache_put(self, path, data):
        if self.use_cache and path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")