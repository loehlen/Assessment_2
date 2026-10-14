"""
test_search_all.py - Search all 7 test companies with Luna and Sol, extract activity tables, compare.

Run in the Codespace terminal:   python test_search_all.py
Expected cost: roughly USD 0.75 (mostly the Sol searches), plus OpenAI's per-search tool fee.
Output:
  test_results/search_<timestamp>.json         everything, including the full answers
  test_results/search_report_<timestamp>.md    readable comparison (open in VS Code -> Open Preview)
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(timeout=240)

# ---------------------------------------------------------------- settings
SEARCH_MODELS = ["gpt-6-luna", "gpt-6.1-sol"]
EXTRACTION_MODEL = "gpt-6.1-sol"  # same extractor for both, so differences come from the search
REASONING_EFFORT = {"gpt-6-luna": "low", "gpt-6.1-sol": "low"}

# USD per 1M tokens (input, output). Third-party listings, Oct 2026 - to verify.
# Not included: OpenAI's per-call fee for the web search tool (to verify).
PRICES = {"gpt-6-luna": (0.10, 0.50), "gpt-6.1-sol": (2.00, 10.00)}

MAX_PARALLEL = 6

# hint = what a user would type into the optional description field in stage 1
COMPANIES = [
    {"name": "Lindt & Sprüngli", "role": "Target (TC1)", "hint": "", "own_domains": ["lindt"]},
    {"name": "Planet A Foods", "role": "Target (TC2)", "hint": "Munich-based maker of the cocoa-free chocolate alternative ChoViva",
     "own_domains": ["planet-a-foods", "planetafoods", "choviva"]},
    {"name": "Koa", "role": "Target (TC3)", "hint": "Swiss-Ghanaian company making products from cocoa fruit pulp",
     "own_domains": ["koa"]},
    {"name": "Ritter Sport", "role": "Portco", "hint": "", "own_domains": ["ritter-sport", "rittersport"]},
    {"name": "Barry Callebaut", "role": "Portco", "hint": "",
     "own_domains": ["barry-callebaut", "barrycallebaut", "callebaut", "cabosse"]},
    {"name": "Bahlsen", "role": "Portco", "hint": "", "own_domains": ["bahlsen"]},
    {"name": "FRoSTA", "role": "Portco", "hint": "", "own_domains": ["frosta"]},
]

SEARCH_PROMPT = """Research the company {name}{hint}.

List ALL of its business activities, including activities outside chocolate and cocoa.
For each activity describe:
- the product or service,
- who buys it directly from the company (e.g. retailers, wholesalers, foodservice operators,
  food manufacturers, artisans, or consumers directly through own shops or online),
- who ultimately consumes it,
- how it is sold (e.g. through supermarkets, own shops, online, directly to manufacturers),
- the countries where it is sold, especially within the EEA.

Use the company's own website and annual report first; use other sources only where they add information.
Say explicitly when the countries of sale are not stated. Cite your sources."""

EXTRACTION_INSTRUCTIONS = """You turn research notes about ONE company into an activity table.
Rules:
- Use only the information in the notes. Do not add knowledge of your own.
- List activities at the level of a product market (at most about 10), not individual products or flavours.
- Include activities outside cocoa and chocolate.
- If the company sells the same product both to retailers and directly to consumers (own shops, online),
  list these as separate activities, because they are different levels of trade.
- direct_customers = who buys the product FROM THE COMPANY, at the company's own level of trade.
  A manufacturer selling through supermarkets -> 'retailers'. Own shops or own online shop -> 'consumers'.
  Supply to other food producers -> 'food manufacturers'.
- end_users = who ultimately consumes the product (supporting information only).
- sales_channels = how the product reaches the customer (e.g. supermarkets, discounters, own shops, online,
  direct supply to manufacturers).
- countries_of_sale: name the countries stated in the notes; keep wording such as 'more than 100 countries';
  write 'not stated' if the notes give nothing.
- source_numbers: use ONLY numbers from the numbered source list below the notes.
- If information is missing, write 'not stated' rather than guessing."""


# ---------------------------------------------------------------- extraction schema
# The direct_customers options are PROVISIONAL - to be aligned with how the decisions frame the customer side.
class Activity(BaseModel):
    product: str = Field(description="The product or service, at the level of a product market")
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
    direct_customers: list[Literal[
        "retailers",
        "wholesalers / distributors",
        "foodservice / out-of-home",
        "food manufacturers",
        "artisans",
        "consumers",
        "other businesses",
    ]] = Field(description="Who buys the product from the company, at its own level of trade")
    end_users: list[Literal["consumers", "businesses"]] = Field(description="Who ultimately consumes the product")
    sales_channels: list[str]
    countries_of_sale: list[str]
    source_numbers: list[int]
    evidence: str = Field(description="Short quote or close paraphrase from the notes supporting this activity")


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
    u = response.usage
    details = getattr(u, "output_tokens_details", None)
    reasoning = (getattr(details, "reasoning_tokens", 0) or 0) if details else 0
    cost = None
    if model in PRICES:
        price_in, price_out = PRICES[model]
        cost = round((u.input_tokens * price_in + u.output_tokens * price_out) / 1_000_000, 5)
    return {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
            "reasoning_tokens": reasoning, "cost_usd": cost}


def clean_url(url):
    return url.replace("?utm_source=openai", "").replace("&utm_source=openai", "")


def cited_urls(response):
    """Unique cited URLs, in order of first appearance."""
    urls = []
    for item in response.output:
        if item.type == "message":
            for part in item.content:
                for ann in getattr(part, "annotations", None) or []:
                    if ann.type == "url_citation":
                        urls.append(clean_url(ann.url))
    return list(dict.fromkeys(urls))


def source_type(url, own_domains):
    """Heuristic: 'company' if the domain contains one of the company's own domain keywords."""
    host = urlparse(url).netloc.lower()
    return "company" if any(d in host for d in own_domains) else "third party"


# ---------------------------------------------------------------- one company with one search model
def research(company, search_model):
    hint = f" ({company['hint']})" if company["hint"] else ""

    # 1. Search call - knows only this company
    search, search_secs = call(
        search_model,
        input=SEARCH_PROMPT.format(name=company["name"], hint=hint),
        tools=[{"type": "web_search"}],
    )
    urls = cited_urls(search)
    notes = clean_url(search.output_text)
    web_searches = sum(1 for item in search.output if item.type == "web_search_call")
    sources = [{"number": i + 1, "url": u, "type": source_type(u, company["own_domains"])} for i, u in enumerate(urls)]

    # 2. Extraction call - no search, numbered sources only
    source_list = "\n".join(f"[{s['number']}] {s['url']}" for s in sources) or "(no sources)"
    extraction, extract_secs = call(
        EXTRACTION_MODEL,
        method="parse",
        instructions=EXTRACTION_INSTRUCTIONS,
        input=f"RESEARCH NOTES:\n{notes}\n\nNUMBERED SOURCES:\n{source_list}",
        text_format=ActivityList,
    )

    # 3. Code check: only source numbers that exist are accepted
    activities = []
    for a in extraction.output_parsed.activities:
        a = a.model_dump()
        valid = [n for n in a["source_numbers"] if 1 <= n <= len(sources)]
        a["invalid_source_numbers"] = [n for n in a["source_numbers"] if n not in valid]
        a["sources"] = [sources[n - 1]["url"] for n in valid]
        a["verified_source"] = bool(valid)
        activities.append(a)

    s_usage = usage_info(search_model, search)
    e_usage = usage_info(EXTRACTION_MODEL, extraction)
    costs = [c for c in (s_usage["cost_usd"], e_usage["cost_usd"]) if c is not None]

    return {
        "company": company["name"],
        "role": company["role"],
        "search_model": search_model,
        "extraction_model": EXTRACTION_MODEL,
        "search_seconds": search_secs,
        "extraction_seconds": extract_secs,
        "web_searches": web_searches,
        "sources": sources,
        "notes": notes,
        "activities": activities,
        "search_usage": s_usage,
        "extraction_usage": e_usage,
        "cost_usd": round(sum(costs), 5),
    }


# ---------------------------------------------------------------- report
def md(text):
    return str(text).replace("|", "/").replace("\n", " ")


def write_report(results, path):
    lines = [f"# Search test - {datetime.now():%d %b %Y %H:%M}", "",
             f"Extraction model for all runs: {EXTRACTION_MODEL}. Costs exclude the per-search tool fee.", "",
             "## Summary", "",
             "| Company | Role | Search model | Search time | Searches | Sources (company / third party) | Activities | Without verified source | Cost USD |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['company']} | {r['role']} | {r['search_model']} | ERROR | | | | | |")
            continue
        own = sum(1 for s in r["sources"] if s["type"] == "company")
        third = len(r["sources"]) - own
        unsourced = sum(1 for a in r["activities"] if not a["verified_source"])
        lines.append(f"| {r['company']} | {r['role']} | {r['search_model']} | {r['search_seconds']} s | "
                     f"{r['web_searches']} | {own} / {third} | {len(r['activities'])} | {unsourced} | {r['cost_usd']} |")

    for company in COMPANIES:
        lines += ["", f"## {company['name']} ({company['role']})"]
        for r in [x for x in results if x["company"] == company["name"]]:
            lines += ["", f"### {r['search_model']}"]
            if "error" in r:
                lines.append(f"ERROR: {r['error']}")
                continue
            lines += ["",
                      "| Product | Category | Level | Direct customers | End users | Channels | Countries | Sources |",
                      "|---|---|---|---|---|---|---|---|"]
            for a in r["activities"]:
                src = ", ".join(str(n) for n in a["source_numbers"]) or "none"
                if a["invalid_source_numbers"]:
                    src += f" (invalid: {a['invalid_source_numbers']})"
                lines.append(f"| {md(a['product'])} | {a['product_category']} | {a['value_chain_level']} | "
                             f"{', '.join(a['direct_customers'])} | {', '.join(a['end_users'])} | "
                             f"{md(', '.join(a['sales_channels']))} | {md(', '.join(a['countries_of_sale']))} | {src} |")
            lines += ["", "Sources:"]
            for s in r["sources"]:
                lines.append(f"{s['number']}. [{s['type']}] {s['url']}")
            lines += ["", "<details><summary>Full search answer</summary>", "", r["notes"], "", "</details>"]

    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------- run
def main():
    jobs = [(c, m) for c in COMPANIES for m in SEARCH_MODELS]
    print(f"Running {len(jobs)} searches ({len(COMPANIES)} companies x {len(SEARCH_MODELS)} models), "
          f"{MAX_PARALLEL} in parallel ...\n")

    results = []
    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {pool.submit(research, c, m): (c, m) for c, m in jobs}
        for future in as_completed(futures):
            c, m = futures[future]
            try:
                r = future.result()
                own = sum(1 for s in r["sources"] if s["type"] == "company")
                print(f"  done  {c['name']:18} {m:12} search {r['search_seconds']:>5}s  "
                      f"sources {len(r['sources']):>2} ({own} company)  activities {len(r['activities']):>2}  "
                      f"cost {r['cost_usd']}")
            except Exception as e:
                r = {"company": c["name"], "role": c["role"], "search_model": m,
                     "error": f"{type(e).__name__}: {e}"[:400]}
                print(f"  ERROR {c['name']:18} {m:12} {r['error']}")
            results.append(r)

    # keep a stable order: company list order, then model order
    order = {(c["name"], m): i for i, (c, m) in enumerate(jobs)}
    results.sort(key=lambda r: order[(r["company"], r["search_model"])])

    total_cost = round(sum(r.get("cost_usd", 0) or 0 for r in results), 4)
    print(f"\nTotal time {time.time() - start:.0f}s, total token cost USD {total_cost} (excluding search tool fees)")

    out_dir = Path("test_results")
    out_dir.mkdir(exist_ok=True)
    stamp = f"{datetime.now():%Y%m%d-%H%M}"
    json_path = out_dir / f"search_{stamp}.json"
    report_path = out_dir / f"search_report_{stamp}.md"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(results, report_path)
    print(f"Saved: {json_path}\nReport: {report_path}\n")


if __name__ == "__main__":
    main()