"""
save_searches.py - development only: one GPT-6.1 Sol web search per company, saved in the format of the searches of
14 Oct, so that the app's development mode (USE_SAVED_SEARCHES=1) reuses them instead of a live Luna search.

    python save_searches.py Brillux Hornbach Sto Henkel

Names and websites come from examples.py. Cost: about USD 0.15-0.35 per company at token prices, plus the web search
fees (spec section 18). The result is written to test_results/search_<date-time>.json; activity_mapping.saved_search
reads every test_results/search_*.json, newest first. Like the other development tools, it stays out of the final app.
"""
import concurrent.futures as cf
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path

import activity_mapping as am
import ai_client
import examples
import schemas

MODEL = am.SAVED_SEARCH_MODEL          # gpt-6.1-sol, the search model of the final profile


def search_one(ai, name):
    c = examples.COMPANIES[name]
    company = {"name": name, "role": "", "website": c["website"], "aliases": c["aliases"], "source": "web search"}
    prompt = schemas.search_prompt(name, "", c["website"])
    am.guard(prompt, name, [company])               # one company per call, as in the app
    t = time.time()
    resp = ai.respond("search", prompt, web_search=True, model=MODEL, note=f"{name} (save_searches.py)", names=[name])
    sources = am.cited_sources(resp)
    am.label_sources(sources, company, [])
    searches = sum(1 for item in (getattr(resp, "output", None) or []) if getattr(item, "type", "") == "web_search_call")
    return {"company": name, "role": "", "website": c["website"], "search_model": MODEL, "date": date.today().isoformat(),
            "search_seconds": round(time.time() - t, 1), "web_searches": searches, "notes": resp.output_text,
            "sources": [{"number": s["n"], "url": s["url"], "title": s["title"], "type": s.get("type", "")}
                        for s in sources]}


def main(names):
    unknown = [n for n in names if n not in examples.COMPANIES]
    if not names or unknown:
        sys.exit(f"Usage: python save_searches.py <names from examples.py>  (unknown: {unknown})")
    key = ai_client.setting("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set in .env")
    ai = ai_client.AI(profile="final", api_key=key, use_cache=False)
    entries = []
    with cf.ThreadPoolExecutor(min(4, len(names))) as ex:
        for entry in ex.map(lambda n: search_one(ai, n), names):
            entries.append(entry)
            print(f"✔ {entry['company']}: {len(entry['sources'])} sources, {entry['web_searches']} searches, "
                  f"{entry['search_seconds']:.0f} s")
    path = Path("test_results") / f"search_{datetime.now():%Y%m%d-%H%M}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    s = ai.log.summary()
    print(f"Saved {path} · {s['calls']} calls · USD {s['cost']:.2f} at token prices (search fees not included)")


if __name__ == "__main__":
    main(sys.argv[1:])