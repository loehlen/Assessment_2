"""
test_models.py - Day-1 test: which models work, and how do they behave?

Run in the Codespace terminal:   python test_models.py
Reads OPENAI_API_KEY from .env. Expected cost: well under USD 1.
Results are printed and saved to test_results/ as JSON (evidence for A3).
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(timeout=180)

# ---------------------------------------------------------------- settings
CHAT_MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-5", "gpt-4o", "gpt-4o-mini"]
SEARCH_MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-4o-mini"]
STRUCTURED_MODELS = ["gpt-6-luna", "gpt-6.1-sol", "gpt-4o-mini"]
EMBEDDING_MODEL = "text-embedding-3-large"
INCLUDE_GPT5_PRO = False  # slow and expensive - switch on only if needed

# Reasoning effort for reasoning models (the others get no reasoning parameter)
REASONING_EFFORT = {
    "gpt-6-luna": "low",
    "gpt-6.1-sol": "low",
    "gpt-5": "low",
    "gpt-5-pro": "high",
}

# USD per 1M tokens (input, output). Third-party listings, Oct 2026 - to verify on OpenAI's pricing page.
PRICES = {
    "gpt-6-luna": (0.10, 0.50),
    "gpt-6.1-sol": (2.00, 10.00),
}

SEARCH_COMPANY = "Ritter Sport"

# A fictional company, so the expected answer is known:
# 4 activities - chocolate tablets (consumers), cocoa butter (food manufacturers),
# liquid industrial chocolate (food manufacturers), factory shops (retail, consumers).
TEST_DESCRIPTION = (
    "ChocoNord GmbH (a fictional company) makes milk and dark chocolate tablets that are sold "
    "to consumers through supermarkets in Germany and Austria. It also sells cocoa butter and "
    "liquid industrial chocolate to confectionery and bakery manufacturers across the EEA, "
    "and runs two factory shops in Hamburg."
)


# ---------------------------------------------------------------- schema for the structured-output test
class Activity(BaseModel):
    product: str
    product_category: Literal[
        "cocoa beans",
        "cocoa liquor/butter/powder",
        "chocolate",
        "chocolate compound and alternatives",
        "non-chocolate confectionery",
        "bakery",
        "other food",
        "non-food",
    ]
    value_chain_level: Literal[
        "beans",
        "semi-finished cocoa products",
        "industrial chocolate",
        "consumer confectionery",
        "retail",
        "other",
    ]
    customer_groups: list[Literal["consumers", "food manufacturers", "retailers", "foodservice", "artisans"]]
    countries_of_sale: list[str]


class ActivityList(BaseModel):
    activities: list[Activity]


# ---------------------------------------------------------------- helpers
def call(model, method="create", **kwargs):
    """Call the Responses API with the right reasoning setting. Returns (response, seconds)."""
    if model in REASONING_EFFORT:
        kwargs["reasoning"] = {"effort": REASONING_EFFORT[model]}
    fn = client.responses.parse if method == "parse" else client.responses.create
    start = time.time()
    response = fn(model=model, **kwargs)
    return response, round(time.time() - start, 1)


def usage_info(model, response):
    """Tokens and (where the price is known) cost of one call."""
    u = response.usage
    details = getattr(u, "output_tokens_details", None)
    reasoning = (getattr(details, "reasoning_tokens", 0) or 0) if details else 0
    info = {
        "input_tokens": u.input_tokens,
        "output_tokens": u.output_tokens,
        "reasoning_tokens": reasoning,
    }
    if model in PRICES:
        price_in, price_out = PRICES[model]
        info["cost_usd"] = round((u.input_tokens * price_in + u.output_tokens * price_out) / 1_000_000, 5)
    else:
        info["cost_usd"] = None
    return info


def clean_url(url):
    return url.replace("?utm_source=openai", "").replace("&utm_source=openai", "")


def citations(response):
    """All url_citation links in the answer."""
    urls = []
    for item in response.output:
        if item.type == "message":
            for part in item.content:
                for ann in getattr(part, "annotations", None) or []:
                    if ann.type == "url_citation":
                        urls.append(clean_url(ann.url))
    return urls


def safe(fn, *args):
    """Run one test; record the error instead of stopping the script."""
    try:
        result = fn(*args)
        result["ok"] = True
    except Exception as e:
        result = {"ok": False, "error": f"{type(e).__name__}: {e}"[:400]}
    return result


# ---------------------------------------------------------------- tests
def test_available():
    available = {m.id for m in client.models.list()}
    wanted = CHAT_MODELS + ["gpt-5-pro", EMBEDDING_MODEL]
    return {"models": {m: (m in available) for m in wanted}}


def test_basic(model):
    response, seconds = call(model, input="Reply with the single word: ready")
    return {"answer": response.output_text.strip(), "seconds": seconds, **usage_info(model, response)}


def test_search(model):
    prompt = (
        f"Using web search, list the main business activities of the company {SEARCH_COMPANY}: "
        "products, customer groups and the countries where it sells. "
        "Prefer the company's own website. Cite your sources."
    )
    response, seconds = call(model, input=prompt, tools=[{"type": "web_search"}])
    urls = citations(response)
    searches = sum(1 for item in response.output if item.type == "web_search_call")
    return {
        "seconds": seconds,
        "web_searches": searches,
        "citations": len(urls),
        "unique_sources": sorted(set(urls)),
        "answer_preview": response.output_text[:700],
        **usage_info(model, response),
    }


def test_structured(model):
    instructions = (
        "Extract every business activity of the company described. Use only the information in the text. "
        "List activities at the level of a product market, not individual products. "
        "If countries are not stated specifically, record what the text says (e.g. 'EEA') rather than guessing."
    )
    response, seconds = call(
        model,
        method="parse",
        instructions=instructions,
        input=TEST_DESCRIPTION,
        text_format=ActivityList,
    )
    parsed = response.output_parsed
    return {
        "seconds": seconds,
        "activities": [a.model_dump() for a in parsed.activities],
        **usage_info(model, response),
    }


def test_embedding():
    start = time.time()
    result = client.embeddings.create(model=EMBEDDING_MODEL, input="cocoa butter for confectionery manufacturers")
    return {"seconds": round(time.time() - start, 1), "dimensions": len(result.data[0].embedding)}


# ---------------------------------------------------------------- run
def main():
    results = {"run_at": datetime.now().isoformat(timespec="seconds")}

    print("\n=== 1. Available models ===")
    results["available"] = safe(test_available)
    if results["available"]["ok"]:
        for m, ok in results["available"]["models"].items():
            print(f"  {'OK ' if ok else 'NO '} {m}")
    else:
        print("  Error:", results["available"]["error"])

    print("\n=== 2. Basic call ===")
    chat_models = CHAT_MODELS + (["gpt-5-pro"] if INCLUDE_GPT5_PRO else [])
    results["basic"] = {}
    for m in chat_models:
        r = safe(test_basic, m)
        results["basic"][m] = r
        if r["ok"]:
            print(f"  {m:14} {r['seconds']:>5}s  in {r['input_tokens']:>5}  out {r['output_tokens']:>5} "
                  f"(reasoning {r['reasoning_tokens']})  cost {r['cost_usd']}  -> {r['answer']}")
        else:
            print(f"  {m:14} ERROR  {r['error']}")

    print(f"\n=== 3. Web search ({SEARCH_COMPANY}) ===")
    results["search"] = {}
    for m in SEARCH_MODELS:
        print(f"  running {m} ...")
        r = safe(test_search, m)
        results["search"][m] = r
        if r["ok"]:
            print(f"  {m:14} {r['seconds']:>5}s  searches {r['web_searches']}  citations {r['citations']}  "
                  f"sources {len(r['unique_sources'])}  in {r['input_tokens']}  out {r['output_tokens']}  "
                  f"cost {r['cost_usd']}")
            for url in r["unique_sources"][:6]:
                print(f"      - {url}")
        else:
            print(f"  {m:14} ERROR  {r['error']}")

    print("\n=== 4. Structured output (fictional ChocoNord GmbH, 4 activities expected) ===")
    results["structured"] = {}
    for m in STRUCTURED_MODELS:
        r = safe(test_structured, m)
        results["structured"][m] = r
        if r["ok"]:
            print(f"  {m:14} {r['seconds']:>5}s  {len(r['activities'])} activities  cost {r['cost_usd']}")
            for a in r["activities"]:
                print(f"      - {a['product']} | {a['product_category']} | {a['value_chain_level']} | "
                      f"{', '.join(a['customer_groups'])} | {', '.join(a['countries_of_sale'])}")
        else:
            print(f"  {m:14} ERROR  {r['error']}")

    print("\n=== 5. Embedding ===")
    results["embedding"] = safe(test_embedding)
    r = results["embedding"]
    print(f"  {EMBEDDING_MODEL}: " + (f"{r['dimensions']} dimensions, {r['seconds']}s" if r["ok"] else f"ERROR {r['error']}"))

    out_dir = Path("test_results")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"model_test_{datetime.now():%Y%m%d-%H%M}.json"
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_file}\n")


if __name__ == "__main__":
    main()