"""
ui/common.py - small helpers used on every screen: the settings (development mode, model profile), the session
state (ss), safe text for Streamlit and HTML, plurals and dates, the cost and time of each step, and moving between
steps.
"""
import html
import math
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from logic import ai_client
from logic import export


DEV_MODE = ai_client.flag("DEV_MODE")
# the app password and the developer's key, but otherwise exactly the submitted version (no development details,
# the final models, no cache): for a run as the teacher sees it without typing in a key
PASSWORD_ONLY = not DEV_MODE and ai_client.flag("PASSWORD_ONLY")
USES_PASSWORD = DEV_MODE or PASSWORD_ONLY
PROFILE = ai_client.setting("MODEL_PROFILE", "dev" if DEV_MODE else "final")   # the submitted version never runs on dev
USE_CACHE = DEV_MODE and ai_client.flag("USE_CACHE", default=True)
MAX_PORTCOS = 5
ss = st.session_state


def is_missing(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or (v is pd.NA)


def cell(v):
    """A cell of the portfolio table as plain text ('' if empty)."""
    try:
        return "" if is_missing(v) else str(v).strip()
    except (TypeError, ValueError):
        return ""


def esc(text):
    """Text from the sources or the AI, made safe inside Streamlit markdown (no links, colour tags or formulas)."""
    out = str(text or "")
    for a, b in (("\\", "\\\\"), ("[", "("), ("]", ")"), ("$", "\\$"), ("*", "\\*"), ("_", "\\_"), ("~", "\\~"),
                 ("<", "&lt;"), (">", "&gt;")):
        out = out.replace(a, b)
    return out


def now_local():
    """The date and time where the user is (the browser's time zone), not the server's: Streamlit Cloud runs on UTC,
    so in Australia a document made before 11 am would otherwise carry the previous day's date."""
    try:
        tz = st.context.timezone
        if tz:
            return datetime.now(ZoneInfo(tz)).replace(tzinfo=None)
    except Exception:  # noqa: BLE001 - no browser time zone (e.g. a test run): the server's time
        pass
    return datetime.now()


def plural(n, word, words=None):
    return f"{n} {word if n == 1 else (words or word + 's')}"


def poss(name):
    """A company's name with the possessive: "Ritter Sport's", but "Planet A Foods'" (a name ending in s)."""
    return export.poss(name)


def words_list(items):
    items = list(dict.fromkeys(items))
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


def log_stage(name, first, seconds):
    """Records one run of a stage (a stage can run several times: partial updates)."""
    ss.stage_logs.setdefault(name, []).append((first, ss.log.mark(), seconds))


def stage_calls(name):
    return [c for first, last, _ in ss.stage_logs.get(name, []) for c in ss.log.calls[first:last]]


def stage_seconds(name):
    return sum(sec for _, _, sec in ss.stage_logs.get(name, []))


EMBED_STEPS = ("embed", "embed_query", "embed_upload")


def call_count(calls):
    """'30 AI calls + 25 embedding requests' (an embedding request turns the search questions into numbers for the
    vector search; it is not an AI answer, so it is counted separately)."""
    emb = sum(1 for c in calls if c["step"] in EMBED_STEPS)
    text = f"{len(calls) - emb} AI calls"
    return text + (f" + {emb} embedding request{'s' if emb != 1 else ''}" if emb else "")


def stage_cost(name):
    """Calls, cache hits, cost and time of one stage (all its runs in this screen), from the call log."""
    if name not in ss.stage_logs:
        return ""
    calls, seconds = stage_calls(name), stage_seconds(name)
    text = call_count(calls)
    if USE_CACHE:
        text += f" ({sum(c['cached'] for c in calls)} from the development cache)"
    text += (f" · USD {sum(c['cost'] for c in calls):.4f} (tokens and web search calls, prices to verify) · "
             f"{seconds:.0f} s")
    unpriced = sorted({c["model"] for c in calls if not c.get("priced", True)})
    if unpriced:
        text += f" · no price for {', '.join(unpriced)}"
    return text


def go_to(step):
    ss.step = step


def capital(text):
    return text[:1].upper() + text[1:]


def _shown(values):
    return [v for v in values or [] if v and v != "not stated"]


def he_lines(text):
    """The lawyer's own wording (from "Edit") with its line breaks: each line escaped like he(), joined by <br> (he()
    alone turns line breaks into spaces)."""
    return "<br>".join(he(x) for x in str(text or "").splitlines() if x.strip())


def he(text):
    """Text from the sources or the AI inside an HTML line that Streamlit also reads as markdown: HTML escaped and the
    markdown characters neutralised."""
    out = h(text)
    for a, b in (("*", "&#42;"), ("_", "&#95;"), ("[", "&#91;"), ("]", "&#93;"), ("~", "&#126;"), ("`", "&#96;")):
        out = out.replace(a, b)
    return out


def quoted(passage):
    """A passage in quotation marks, unless it already starts with one (no ““…)."""
    t = (passage or "").strip()
    return he(t) if t[:1] in "“\"„«" else f"“{he(t)}”"


def long_date(iso):
    """'2010-01-06' -> '6 January 2010', the form of every date in the Word document ('' stays '', anything else
    as it is)."""
    try:
        d = datetime.fromisoformat(str(iso or ""))
    except ValueError:
        return str(iso or "")
    return f"{d.day} {d:%B %Y}"


def run_summary():
    """AI calls, models, cost and time of the run."""
    calls, cost, fees, searches, seconds, models = [], 0.0, 0.0, 0, 0.0, set()
    for stage in ("mapping", "confirm", "precedents"):
        part = stage_calls(stage)
        calls += part
        cost += sum(c["cost"] for c in part)
        fees += sum(c.get("search_fee", 0.0) for c in part)
        searches += sum(c.get("web_searches", 0) for c in part)
        seconds += stage_seconds(stage)
        models |= {c["model"] for c in part}
    # the web search tool's per-call fee is included (ai_client.WEB_SEARCH_FEE, to verify)
    text = (f"Run summary: {call_count(calls)} · models: {', '.join(sorted(models)) or 'none'} · USD {cost:.3f} "
            f"(of which USD {fees:.3f} for {searches} web search calls at USD {ai_client.WEB_SEARCH_FEE:g} each; "
            f"prices to verify) · {seconds:.0f} s")
    waits = sum(c.get("rate_limit_waits", 0) for c in calls)
    if waits:                            # the key's rate limit is waited out, never failed
        text += f" · waited {plural(waits, 'time')} for the API key's rate limit"
    lf = ss.get("loaded_from")
    if lf:                               # steps ①–③ restored from a saved audit log (their calls were paid then)
        before = lf.get("calls_before") or {}
        # counted like the run itself (embedding requests apart from AI calls)
        text += (f" · plus, before loading: {call_count(ss.get('loaded_calls') or [])}, USD "
                 f"{before.get('cost', 0):.3f} (the run of {lf.get('created') or 'unknown date'})")
    return text


def h(text):
    """Text from the decisions, the sources or the AI, made safe inside an HTML block. Line breaks become spaces,
    because a blank line in AI text (a summary, a quotation not found) would end the HTML block and show the rest of the
    step ④ block as raw code."""
    return html.escape(re.sub(r"\s*\n\s*", " ", str(text or "")), quote=True).replace("$", "&#36;")
