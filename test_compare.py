"""
test_compare.py - tests the generic activity overview (stages 1-2) and the factual comparison (stage 3)
on one test case, outside Streamlit. Needs rules.py and schemas.py in the same folder.

Run in the Codespace terminal:
  python test_compare.py                          TC1, Luna everywhere, saved Sol searches of 14 Oct
  python test_compare.py TC2                      another test case
  python test_compare.py TC1 --judge gpt-6.1-sol  the same pairs judged by Sol (search + extraction from cache)
  python test_compare.py TC1 --search gpt-6-luna  new web searches instead of the saved ones
The defaults are in SETTINGS below.

What it does:
  1. Activity overview: one search and one extraction call per company (one company per call, in parallel).
     By default the search is NOT re-run: the Sol searches of 14 Oct (test_results/search_*.json) are reused,
     so the test isolates the extraction and the comparison and costs no search fees.
  2. Anonymisation in code: names and brands removed; every text is checked before it is sent.
  3. Embeddings of the anonymised products and inputs (one request per company).
  4. Factual comparison: every target activity x every portco activity, ONE anonymised pair per AI call.
  5. Decision rule in code (rules.decide): the AI can keep a pair alone, but never screen one out alone.
  6. Benchmark check (benchmark.py): the expert benchmark of spec section 13, checked automatically.

Everything is cached in cache/, so re-running costs nothing; changing a model or a prompt only re-runs
the calls affected. Output: test_results/compare_<TC>_<judge model>_<time>.md and .json
Cost with Luna everywhere: a few cents. A new Sol search costs about USD 0.15-0.35 per company (paid once).
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import re
import statistics
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

import benchmark
import rules
import schemas

load_dotenv()

# =============================================================== SETTINGS (defaults; the command line overrides them)
TEST_CASE = "TC1"                # TC1 Lindt & Sprüngli, TC2 Planet A Foods, TC3 Koa
SEARCH_MODEL = "saved"           # "saved" = reuse SAVED_SEARCH_FILE; or "gpt-6-luna" / "gpt-6.1-sol" for new searches
SAVED_SEARCH_FILE = Path("test_results/search_20261014-0130.json")
SAVED_SEARCH_MODEL = "gpt-6.1-sol"   # the final search model (spec section 8); the file also has Luna searches
EXTRACT_MODEL = "gpt-6-luna"
JUDGE_MODEL = "gpt-6-luna"       # then the same pairs with "gpt-6.1-sol" to compare
EMBED_MODEL = "text-embedding-3-large"
REASONING_EFFORT = "low"
MAX_PARALLEL = 8
TIMEOUT = 300                    # seconds; Sol searches took up to 211 s in the first test

COMPANIES = {
    "Lindt & Sprüngli": {"hint": "Swiss premium chocolate maker based in Kilchberg",
                         "aliases": ["Lindt", "Sprüngli", "Lindt & Sprüngli AG"]},
    "Planet A Foods": {"hint": "Munich-based maker of the cocoa-free chocolate alternative ChoViva",
                       "aliases": ["Planet A", "ChoViva"]},
    "Koa": {"hint": "Swiss-Ghanaian company making products from cocoa fruit pulp",
            "aliases": ["Koa Impact", "Koa Switzerland AG", "Koa Germany GmbH"]},
    "Ritter Sport": {"hint": "German chocolate maker Alfred Ritter GmbH & Co. KG, Waldenbuch",
                     "aliases": ["Ritter", "Alfred Ritter GmbH & Co. KG"]},
    "Barry Callebaut": {"hint": "Swiss cocoa and chocolate manufacturer based in Zurich",
                        "aliases": ["Callebaut", "Barry Callebaut AG"]},
    "Bahlsen": {"hint": "German biscuit and cake maker based in Hanover", "aliases": ["Bahlsen GmbH & Co. KG"]},
    "FRoSTA": {"hint": "German frozen food company based in Bremerhaven", "aliases": ["FRoSTA AG"]},
}
TEST_CASES = {"TC1": "Lindt & Sprüngli", "TC2": "Planet A Foods", "TC3": "Koa"}
PORTFOLIO = ["Ritter Sport", "Barry Callebaut", "Bahlsen", "FRoSTA"]

# USD per 1M tokens (input, output); third-party listings, to verify. Web search fees not included.
PRICES = {"gpt-6-luna": (0.10, 0.50), "gpt-6.1-sol": (2.00, 10.00), "text-embedding-3-large": (0.13, 0.0)}

CACHE = Path("cache")
RESULTS = Path("test_results")
LOG = []
NAMES = []          # every name, alias, group company and brand of the companies in this run


# =============================================================== helpers
_client = None


def client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(timeout=TIMEOUT)
    return _client


def reasoning(model):
    return {"reasoning": {"effort": REASONING_EFFORT}} if model.startswith(("gpt-5", "gpt-6", "o")) else {}


def cache_lookup(kind, key_parts):
    key = hashlib.sha256(json.dumps(key_parts, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:20]
    path = CACHE / kind / f"{key}.json"
    return path, (json.loads(path.read_text(encoding="utf-8")) if path.exists() else None)


def cache_store(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def log_call(step, model, tokens_in, tokens_out, seconds, note="", cached=False):
    p_in, p_out = PRICES.get(model, (0.0, 0.0))
    cost = 0.0 if cached else tokens_in / 1e6 * p_in + tokens_out / 1e6 * p_out
    LOG.append({"step": step, "model": model, "in": tokens_in, "out": tokens_out, "seconds": round(seconds, 1),
                "cost": round(cost, 5), "cached": cached, "note": note})


def usage(resp):
    u = getattr(resp, "usage", None)
    return (getattr(u, "input_tokens", 0) or 0, getattr(u, "output_tokens", 0) or 0) if u else (0, 0)


def with_retry(fn, *args, **kwargs):
    for attempt in (1, 2):
        try:
            return fn(*args, **kwargs)
        except Exception as e:  # noqa: BLE001 - one retry for any API error, then give up
            if attempt == 2:
                raise
            print(f"   retry after error: {e}")
            time.sleep(3)


def names_of(company):
    return [company] + COMPANIES[company]["aliases"]


def guard(text, allowed_company=None):
    """Confidentiality guard: text built by the app may contain at most the one permitted company."""
    others = [n for c in COMPANIES if c != allowed_company for n in names_of(c)]
    found = rules.find_names(text, others)
    if found:
        raise RuntimeError(f"Blocked by the confidentiality guard: {found}")


def clean_url(url):
    url = re.sub(r"([?&])utm_source=openai(&|$)", lambda m: m.group(1) if m.group(2) else "", url)
    return url.rstrip("?&")


def cited_sources(resp):
    seen = {}
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) != "message":
            continue
        for part in getattr(item, "content", []) or []:
            for a in getattr(part, "annotations", None) or []:
                if getattr(a, "type", None) == "url_citation":
                    url = clean_url(a.url)
                    seen.setdefault(url, getattr(a, "title", "") or url)
    return [{"n": i + 1, "url": u, "title": t} for i, (u, t) in enumerate(seen.items())]


# =============================================================== stage 1-2: activity overview
def saved_search(company):
    """The Sol search of 14 Oct for this company, in the same format as search() returns. No API call."""
    entries = json.loads(SAVED_SEARCH_FILE.read_text(encoding="utf-8"))
    for e in entries:
        if e["company"] == company and e["search_model"] == SAVED_SEARCH_MODEL:
            log_call("search", SAVED_SEARCH_MODEL, 0, 0, 0, f"{company} (saved)", cached=True)
            sources = [{"n": s["number"], "url": clean_url(s["url"]), "title": s.get("title") or s["url"],
                        "type": s.get("type", "")} for s in e["sources"]]
            return {"company": company, "model": f"{SAVED_SEARCH_MODEL} (saved {SAVED_SEARCH_FILE.name})",
                    "date": "2026-10-14", "notes": e["notes"], "sources": sources}
    raise RuntimeError(f"No saved {SAVED_SEARCH_MODEL} search for {company} in {SAVED_SEARCH_FILE}")


def search(company):
    if SEARCH_MODEL == "saved":
        return saved_search(company)
    prompt = schemas.search_prompt(company, COMPANIES[company]["hint"])
    guard(prompt, allowed_company=company)
    path, hit = cache_lookup("search", [SEARCH_MODEL, prompt])
    if hit:
        log_call("search", SEARCH_MODEL, 0, 0, 0, company, cached=True)
        return hit
    t = time.time()
    resp = with_retry(client().responses.create, model=SEARCH_MODEL, input=prompt,
                      tools=[{"type": "web_search"}], **reasoning(SEARCH_MODEL))
    log_call("search", SEARCH_MODEL, *usage(resp), time.time() - t, company)
    data = {"company": company, "model": SEARCH_MODEL, "date": datetime.now().strftime("%Y-%m-%d"),
            "notes": resp.output_text, "sources": cited_sources(resp)}
    cache_store(path, data)
    return data


def extract(company, found):
    text = schemas.extraction_input(company, found["notes"], found["sources"])
    guard(schemas.extraction_input(company, "", []), allowed_company=company)  # the part the app writes itself
    key = [EXTRACT_MODEL, schemas.EXTRACTION_INSTRUCTIONS, schemas.ActivityList.model_json_schema(), text]
    path, hit = cache_lookup("extract", key)
    if hit:
        log_call("extract", EXTRACT_MODEL, 0, 0, 0, company, cached=True)
        return hit
    t = time.time()
    resp = with_retry(client().responses.parse, model=EXTRACT_MODEL, instructions=schemas.EXTRACTION_INSTRUCTIONS,
                      input=text, text_format=schemas.ActivityList, **reasoning(EXTRACT_MODEL))
    log_call("extract", EXTRACT_MODEL, *usage(resp), time.time() - t, company)
    if resp.output_parsed is None:  # refusal or invalid structured output: stop with a clear message
        raise RuntimeError(f"Extraction for {company} returned no valid activity list: {resp.output_text[:300]}")
    data = resp.output_parsed.model_dump()
    valid = {s["n"] for s in found["sources"]}
    for act in data["activities"]:  # code check: only source numbers the search actually returned
        act["invalid_source_numbers"] = [n for n in act["source_numbers"] if n not in valid]
        act["source_numbers"] = [n for n in act["source_numbers"] if n in valid]
        act["verified_source"] = bool(act["source_numbers"])
    cache_store(path, data)
    return data


def map_company(company, case_companies):
    found = search(company)
    extracted = extract(company, found)
    # Existing relationships: public sources for this company that mention another company in the run
    mentions = [c for c in case_companies if c != company and rules.find_names(found["notes"], names_of(c))]
    return {"company": company, "search": found, "extraction": extracted, "mentions": mentions}


# =============================================================== stage 3: factual comparison
def embed_company(label, activities):
    """One embedding request per company, anonymised texts only."""
    texts = []
    for a in activities:
        texts.append(rules.redact(rules.product_text(a), NAMES))
        texts += [rules.redact(i, NAMES) for i in a["main_inputs"] if i and i != "not stated"]
    for t in texts:
        if rules.find_names(t, NAMES):
            raise RuntimeError(f"Blocked: name left in embedding text of {label}")
    path, hit = cache_lookup("embed", [EMBED_MODEL, texts])
    if hit:
        log_call("embed", EMBED_MODEL, 0, 0, 0, label, cached=True)
        vectors = hit
    else:
        t = time.time()
        resp = with_retry(client().embeddings.create, model=EMBED_MODEL, input=texts)
        log_call("embed", EMBED_MODEL, getattr(resp.usage, "prompt_tokens", 0), 0, time.time() - t, label)
        vectors = [d.embedding for d in resp.data]
        cache_store(path, vectors)
    out, k = [], 0
    for a in activities:
        n_inputs = len([i for i in a["main_inputs"] if i and i != "not stated"])
        out.append({"product": vectors[k], "inputs": vectors[k + 1:k + 1 + n_inputs]})
        k += 1 + n_inputs
    return out


def compare(prompt):
    """One anonymised pair per call. An error never screens a pair out: it becomes 'not enough information'."""
    leftover = rules.find_names(prompt, NAMES)
    if leftover:
        return {"product_relation": "not enough information", "product_reason": f"Blocked: names found {leftover}",
                "vertical_links": [], "vertical_reason": "", "blocked": True}
    key = [JUDGE_MODEL, schemas.COMPARISON_INSTRUCTIONS, schemas.Comparison.model_json_schema(), prompt]
    path, hit = cache_lookup("compare", key)
    if hit:
        log_call("compare", JUDGE_MODEL, 0, 0, 0, cached=True)
        return hit
    t = time.time()
    try:
        resp = with_retry(client().responses.parse, model=JUDGE_MODEL, instructions=schemas.COMPARISON_INSTRUCTIONS,
                          input=prompt, text_format=schemas.Comparison, **reasoning(JUDGE_MODEL))
    except Exception as e:  # noqa: BLE001
        return {"product_relation": "not enough information", "product_reason": f"Call failed: {e}",
                "vertical_links": [], "vertical_reason": "", "error": True}
    log_call("compare", JUDGE_MODEL, *usage(resp), time.time() - t)
    if resp.output_parsed is None:  # never screen out on an error: treated as "not enough information"
        return {"product_relation": "not enough information", "product_reason": "No valid answer from the model",
                "vertical_links": [], "vertical_reason": "", "error": True}
    data = resp.output_parsed.model_dump()
    cache_store(path, data)
    return data


def build_pairs(target, portcos, profiles):
    pairs = []
    t_acts = profiles[target]["activities"]
    for pi, portco in enumerate(portcos, start=1):
        for ti, ta in enumerate(t_acts):
            for ki, pa in enumerate(profiles[portco]["activities"]):
                tv, pv = profiles[target]["vectors"][ti], profiles[portco]["vectors"][ki]
                sims = {"product": rules.cosine(tv["product"], pv["product"]),
                        "input_a_to_b": rules.best_input_match(tv["product"], pv["inputs"]),
                        "input_b_to_a": rules.best_input_match(pv["product"], tv["inputs"])}
                pairs.append({"portco": portco, "label_a": f"T-{ti + 1}", "label_b": f"P{pi}-{ki + 1}",
                              "a": ta, "b": pa, "abstract_a": profiles[target]["abstracts"][ti],
                              "abstract_b": profiles[portco]["abstracts"][ki], "sims": sims})
    return pairs


def assess(pair):
    prompt = schemas.comparison_input(pair["abstract_a"], pair["abstract_b"])
    comparison = compare(prompt)
    signals = rules.code_vertical_signals(pair["a"], pair["b"], pair["sims"])
    decision = rules.decide(comparison, signals, pair["sims"]["product"], pair["a"], pair["b"])
    customers = rules.customer_overlap(pair["a"]["direct_customers"], pair["b"]["direct_customers"])
    eea = [rules.eea_status(pair["a"]["countries_of_sale"]), rules.eea_status(pair["b"]["countries_of_sale"])]
    flags = (["no EEA overlap"] if "outside the EEA only" in eea else []) + \
        (["captive (not on the merchant market)"] if rules.captive_only(pair["a"]) or rules.captive_only(pair["b"]) else [])
    return {**pair, "prompt": prompt, "comparison": comparison, "code_signals": signals, "decision": decision,
            "customers": customers if decision["horizontal"] else "", "flags": "; ".join(flags)}


# =============================================================== report
def short(text, n=60):
    text = (text or "").replace("|", "/").replace("\n", " ")
    return text if len(text) <= n else text[:n - 1] + "…"


def benchmark_lines(checks):
    marks = {m: sum(c["mark"] == m for c in checks) for m in ("✔", "◐", "✖", "∅", "⚠")}
    L = ["## Benchmark check (spec section 13)", "",
         f"{marks['✔']} ✔ as expected · {marks['◐']} ◐ kept in another form · "
         f"**{marks['✖']} ✖ missed by the comparison** · {marks['∅']} ∅ activity not found · "
         f"{marks['⚠']} ⚠ false positives in a control row", "",
         "Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py "
         "need adjusting: compare with the activity overview below).", "",
         "| Check | Portco | Pair | Expected | Result | Pairs | Detail |", "|---|---|---|---|---|---|---|"]
    for c in checks:
        labels = ", ".join(c["labels"][:4]) + (f" (+{len(c['labels']) - 4})" if len(c["labels"]) > 4 else "")
        L.append(f"| {c['id']} | {c['portco']} | {short(c['what'], 70)} | {c['expect']} | {c['mark']} | "
                 f"{labels} | {short(c['detail'], 160)} |")
    return L + [""]


def write_report(target, portcos, profiles, mapped, results, checks, stamp):
    L = [f"# Factual comparison {TEST_CASE}: {target} ({stamp})", "",
         f"Models: search {SEARCH_MODEL if SEARCH_MODEL != 'saved' else 'saved ' + SAVED_SEARCH_MODEL} · "
         f"extraction {EXTRACT_MODEL} · comparison {JUDGE_MODEL} · {EMBED_MODEL}  ",
         f"Thresholds: unclear ≥ {rules.SIMILARITY_UNCLEAR} · input match ≥ {rules.INPUT_MATCH} · "
         f"resale ≥ {rules.RESALE_MATCH}", ""]
    L += benchmark_lines(checks)
    L += ["## Activity overview (stages ①–②)"]
    for company in [target] + portcos:
        role = "Target" if company == target else f"Portco {portcos.index(company) + 1}"
        m = mapped[company]
        L += ["", f"### {role}: {company} ({len(m['extraction']['activities'])} activities, "
                  f"{len(m['search']['sources'])} sources)"]
        if m["mentions"]:
            L.append(f"🔗 The public sources for {company} mention: {', '.join(m['mentions'])} (check for an existing relationship)")
        L += ["", "| # | Business area | Product | Level | Direct customers | Countries | Status | Src |",
              "|---|---|---|---|---|---|---|---|"]
        prefix = "T" if company == target else f"P{portcos.index(company) + 1}"
        for i, a in enumerate(m["extraction"]["activities"], start=1):
            L.append(f"| {prefix}-{i} | {short(a['business_area'], 25)} | {short(a['product'], 45)} | "
                     f"{a['value_chain_level']} | {', '.join(a['direct_customers'])} | "
                     f"{short(', '.join(a['countries_of_sale']), 30)} | {a['status']} | "
                     f"{a['source_numbers'] or '⚠ none'}"
                     f"{' ⚠ invalid ' + str(a['invalid_source_numbers']) if a.get('invalid_source_numbers') else ''} |")
    counts = {s: sum(r["decision"]["status"] == s for r in results) for s in ("candidate", "unclear", "screened out")}
    L += ["", "## Factual comparison (stage ③)", "",
          f"{len(results)} pairs: {counts['candidate']} candidates · {counts['unclear']} unclear · "
          f"{counts['screened out']} screened out"]
    for portco in portcos:
        rows = [r for r in results if r["portco"] == portco]
        kept = [r for r in rows if r["decision"]["status"] != "screened out"]
        out = [r for r in rows if r["decision"]["status"] == "screened out"]
        L += ["", f"### {portco}", "",
              "| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(kept, key=lambda r: (r["decision"]["status"] != "candidate", -r["sims"]["product"])):
            d = r["decision"]
            vertical = "; ".join([f"{v} ({d['found_by'][v]})" for v in d["vertical_links"]]
                                 + [f"✗ {v} (AI, disregarded: {why})" for v, why in d.get("disregarded", [])])
            L.append(f"| {r['label_a']} {short(r['a']['product'], 30)} | {r['label_b']} {short(r['b']['product'], 30)} | "
                     f"{d['status']} | {r['comparison']['product_relation']} | {r['customers']} | {vertical} | "
                     f"{r['sims']['product']:.2f} | {short(r['comparison']['product_reason'] + ' ' + r['comparison']['vertical_reason'], 160)} | "
                     f"{r['flags']} |")
        if out:
            L += ["", f"<details><summary>{len(out)} pairs screened out</summary>", ""]
            L += [f"- {r['label_a']} {short(r['a']['product'], 35)} ↔ {r['label_b']} {short(r['b']['product'], 35)} "
                  f"(sim. {r['sims']['product']:.2f}): {short(r['comparison']['product_reason'], 100)}" for r in out]
            L += ["", "</details>"]
    screened = sorted((r for r in results if r["decision"]["status"] == "screened out"),
                      key=lambda r: -r["sims"]["product"])[:8]
    L += ["", "## Calibration: closest pairs that were screened out", "",
          "If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.", ""]
    L += [f"- {r['sims']['product']:.2f} · {r['label_a']} {short(r['a']['product'], 40)} ↔ "
          f"{r['label_b']} {short(r['b']['product'], 40)} ({r['portco']})" for r in screened]
    for status in ("candidate", "screened out"):
        sims = [r["sims"]["product"] for r in results if r["decision"]["status"] == status]
        if sims:
            L.append(f"- similarity of {status} pairs: min {min(sims):.2f} · median {statistics.median(sims):.2f} · max {max(sims):.2f}")
    if results:
        L += ["", "## Example: exactly what the comparison call received", "", "```", results[0]["prompt"], "```"]
    blocked = [r for r in results if r["comparison"].get("blocked") or r["comparison"].get("error")]
    L += ["", "## Run summary", "",
          f"- names removed before any comparison: {len(rules.name_variants(NAMES))} name variants "
          f"(list in the .json file)",
          f"- comparison calls blocked or failed: {len(blocked)} (kept as 'unclear', never screened out)"]
    for step in ("search", "extract", "embed", "compare"):
        calls = [c for c in LOG if c["step"] == step]
        if calls:
            L.append(f"- {step}: {len(calls)} calls ({sum(c['cached'] for c in calls)} from cache) · "
                     f"tokens {sum(c['in'] for c in calls):,} in / {sum(c['out'] for c in calls):,} out · "
                     f"USD {sum(c['cost'] for c in calls):.4f}")
    L.append(f"- total: USD {sum(c['cost'] for c in LOG):.4f} (token costs only, without web search fees)")
    return "\n".join(L) + "\n"


# =============================================================== main
def parse_args():
    global TEST_CASE, SEARCH_MODEL, EXTRACT_MODEL, JUDGE_MODEL
    p = argparse.ArgumentParser(description="Test the activity overview and the factual comparison on one test case.")
    p.add_argument("case", nargs="?", default=TEST_CASE, choices=sorted(TEST_CASES))
    p.add_argument("--search", default=SEARCH_MODEL, help='"saved" (default) or a model for new web searches')
    p.add_argument("--extract", default=EXTRACT_MODEL, help="model for the extraction")
    p.add_argument("--judge", default=JUDGE_MODEL, help="model for the factual comparison")
    args = p.parse_args()
    TEST_CASE, SEARCH_MODEL, EXTRACT_MODEL, JUDGE_MODEL = args.case, args.search, args.extract, args.judge


def main():
    parse_args()
    start = time.time()
    target = TEST_CASES[TEST_CASE]
    portcos = PORTFOLIO
    case_companies = [target] + portcos
    print(f"{TEST_CASE}: {target} v {', '.join(portcos)}")

    print("1. Activity overview (one company per call, in parallel) ...")
    with cf.ThreadPoolExecutor(MAX_PARALLEL) as ex:
        futures = {c: ex.submit(map_company, c, case_companies) for c in case_companies}
        mapped = {c: f.result() for c, f in futures.items()}
    for c in case_companies:
        print(f"   {c}: {len(mapped[c]['extraction']['activities'])} activities")

    NAMES.clear()
    for c in case_companies:
        NAMES.extend(names_of(c))
        ext = mapped[c]["extraction"]
        NAMES.extend(ext["group_companies"])
        for a in ext["activities"]:
            NAMES.extend(a["brands"])

    print("2. Anonymisation and embeddings ...")
    profiles = {}
    for c in case_companies:
        acts = mapped[c]["extraction"]["activities"]
        abstracts = []
        for a in acts:
            text, leftover = rules.build_abstract(a, NAMES)
            if leftover:
                raise RuntimeError(f"Name left in an abstract of {c}: {leftover}")
            abstracts.append(text)
        profiles[c] = {"activities": acts, "abstracts": abstracts, "vectors": embed_company(c, acts)}

    pairs = build_pairs(target, portcos, profiles)
    print(f"3. Factual comparison: {len(pairs)} pairs, one anonymised pair per call ...")
    with cf.ThreadPoolExecutor(MAX_PARALLEL) as ex:
        results = list(ex.map(assess, pairs))

    checks = benchmark.run_checks(TEST_CASE, target, mapped, results, rules.SIMILARITY_UNCLEAR)

    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    RESULTS.mkdir(exist_ok=True)
    name = f"compare_{TEST_CASE}_{JUDGE_MODEL}_{stamp}"     # model names contain dots, so no with_suffix()
    md_path, json_path = RESULTS / f"{name}.md", RESULTS / f"{name}.json"
    report = write_report(target, portcos, profiles, mapped, results, checks, stamp)
    md_path.write_text(report, encoding="utf-8")
    slim = [{k: v for k, v in r.items() if k not in ("sims",)} | {"sims": {k: round(v, 3) for k, v in r["sims"].items()}}
            for r in results]
    json_path.write_text(json.dumps(
        {"settings": {"test_case": TEST_CASE, "search": SEARCH_MODEL, "extract": EXTRACT_MODEL, "judge": JUDGE_MODEL,
                      "thresholds": [rules.SIMILARITY_UNCLEAR, rules.INPUT_MATCH, rules.RESALE_MATCH]},
         "mapped": mapped, "names_removed": sorted(rules.name_variants(NAMES)),
         "benchmark": [{k: v for k, v in c.items() if k not in ("target", "portco_act")} for c in checks],
         "results": slim, "log": LOG}, ensure_ascii=False, indent=1), encoding="utf-8")

    counts = {s: sum(r["decision"]["status"] == s for r in results) for s in ("candidate", "unclear", "screened out")}
    print(f"   {counts}")
    print("4. Benchmark check:")
    for c in checks:
        print(f"   {c['mark']} {c['id']} {c['portco']}: {c['what']} -> {c['detail']}")
    print(f"Done in {time.time() - start:.0f} s · USD {sum(c['cost'] for c in LOG):.4f} (token costs) · "
          f"report: {md_path}")


if __name__ == "__main__":
    main()