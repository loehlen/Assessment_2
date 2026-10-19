"""
precedents.py - stage 4: the Commission's market definitions for the rows kept after stage 3 (spec sections 8 and 9,
step 4, slimmed down: stage 4 finds and cites, the lawyer decides).

    search_units(target, results, overrides, confirmed_target)   which searches are needed: ONE per target activity,
                                                                 covering the items of all its kept rows, both sides
    unit_input(unit, names)                                      the anonymised item list (ids such as [2.3])
    run_unit(ai, unit, names, retriever)                         query plan -> hybrid retrieval -> reflection, in a
                                                                 loop with three STOP conditions (Lab 2), then the
                                                                 citation check and the item check in code
    row_view(r, record, overrides)                               what one row of the table shows, assembled in code
    reusable(record, unit)                                       whether an earlier search still covers the unit

Decided by Linda on 20 Oct: one search per target activity (so one market keeps one name in all its rows and code can
say where the precedent puts each company's items); at most one rewrite of the queries (two attempts); the loader for a
saved screen first, so that this stage can be tested on the frozen step 3.

What the AI does here: write the queries; read the retrieved paragraphs and place every item in a market the
paragraphs define (or "none"). What code does: the retrieval, the loop and its STOP conditions, the check that every
cited paragraph was actually retrieved, the check that every item id exists, and every sentence shown in the table
(e.g. "different markets under the precedent"). Nothing in this file knows a sector.

Confidentiality: the query and reflection calls contain anonymised items only (names removed in code and checked
again before the call), grouped by activity number, with no company label; a remaining name blocks the call. The
retrieved decision paragraphs are public and are sent unchanged (Linda, 20 Oct), even where a decision names a company
of the screen; such names are recorded in the audit log.
"""
import hashlib
import json
import re
import threading

import rules
import schemas

MAX_ATTEMPTS = 2          # one rewrite of the queries (Linda, 20 Oct); version 8 planned three attempts
HITS_PER_QUERY = 5        # decision paragraphs kept per query (the Notice states principles and is not searched here)
POOL_PER_QUERY = 10       # hits asked from the retriever per query, before the Notice is left out
MAX_PARAGRAPHS = 30       # paragraphs per reflection call (hits first, then their neighbours)
FALLBACK_ITEMS = 8        # items of an "Other activities" line used when a row names no items
SOURCE_DECISION = "Commission decision"

STOP_WORDS = {
    "all placed": "AI STOP: every item was placed in a market or found to have none",
    "no rewrite": "AI STOP: the reflection suggested no further search",
    "same paragraphs": "code STOP: the new search returned no new paragraphs",
    "attempts": f"hard STOP: {MAX_ATTEMPTS} attempts used",
    "blocked": "blocked: a company name was still in the text (no call was made)",
    "failed": "the call failed",
}
BASIS_LABEL = {"precedent": "Precedent", "analogy": "Analogy", "none": "No precedent"}

# The product-market checklist of the Market Definition Notice (2024), shown as questions for the lawyer where the
# corpus has no precedent (spec section 9; the paragraph numbers were checked against the Notice on 14-15 Oct).
# Public sources: "✔" answerable from public sources, "◐" partly, "✖" not at all (only the company or a market
# investigation can answer it). The tool does not answer them (slimmed-down stage 4, Linda 16 Oct).
CHECKLIST = [
    ("P1", "Starting point: take the target's product as the candidate market and add the substitutes until the market "
           "is closed.", "(28)", "✔"),
    ("P2", "Product characteristics, price, intended use and functions (alone often not enough, (49)).",
     "(12)(a), (26), (48)–(49)", "✔ mostly"),
    ("P3", "Why customers would or would not switch: quality, innovation, sustainability, distribution channels "
           "(online / offline), regulatory framework (e.g. labelling).", "(15), (50)", "◐"),
    ("P4", "Barriers to switching: contracts, brand recognition, adapting production processes, regulatory barriers.",
     "(57)", "◐"),
    ("P5", "Sales channels that customers cannot switch between can form separate markets.", "(58)", "◐"),
    ("P6", "Evidence of past substitution (e.g. reactions to an exogenous cost shock), diversion ratios, elasticities.",
     "(51)–(53)", "✖"),
    ("P7", "Hypothetical substitution: surveys, customer and competitor views.", "(54)", "✖"),
    ("P8", "Industry views: who regards whom as a competitor.", "(56)", "◐"),
    ("P9", "Distinct customer groups: a separate market only if the three conditions are met.", "(24), (88)–(89)", "◐"),
    ("P10", "Supply-side substitution: only exceptionally.", "(23)(b), (32)–(37), (60)–(61)", "◐"),
    ("P11", "Products in development (pipeline): part of an existing market, or a new one.", "(90)–(93)", "◐"),
    ("P12", "Potential competition is not part of market definition.", "(23)(c)", "✔ as a label"),
]
APPLICABLE_TODAY = ("Applicable today? The Commission may start from a past decision but is not bound by it and checks "
                    "whether the definition still fits, e.g. after shifts in value chains or digitalisation (Market "
                    "Definition Notice (14)).")


# =============================================================== which searches are needed
def _kept(status):
    return status in ("candidate", "unclear", "added back by user")


def row_items(r, overrides, effective_status, dismissed_parts):
    """The items of one kept row that stage 4 looks up, per side: the items that meet (horizontal, option C) and the
    items of every vertical link the lawyer did not dismiss. A row that names no items (unclear, added back, or a link
    without items) uses each side's product line; an "Other activities" line uses its includes instead."""
    status = effective_status(r, overrides)
    if not _kept(status):
        return None
    off = set(dismissed_parts(r, overrides))
    d = r["decision"]
    a, b = [], []
    if status == "candidate":
        m = r.get("matches") or {}
        if d.get("horizontal") and "horizontal" not in off:
            a += m.get("a") or []
            b += m.get("b") or []
        for v in r.get("vertical_items") or []:
            if v.get("link") in d.get("vertical_links", []) and v["link"] not in off:
                a += v.get("a") or []
                b += v.get("b") or []
    return {"a": list(dict.fromkeys(a or _fallback_items(r["a"]))),
            "b": list(dict.fromkeys(b or _fallback_items(r["b"])))}


def _fallback_items(act):
    items = rules.activity_items(act)
    if rules.category(act) == "other":
        return [i for i in items[1:] if i][:FALLBACK_ITEMS] or items[:1]
    return items[:1]


def search_units(results, overrides, effective_status, dismissed_parts, pair_id, target_order):
    """One unit per target activity that has at least one kept row: the target activity, every portfolio activity in
    its kept rows, and the items each of them contributes. target_order: the target's activity IDs in display order.
    Returns a list of units, in the target's order."""
    units = {}
    for r in results:
        items = row_items(r, overrides, effective_status, dismissed_parts)
        if items is None:
            continue
        ta, pa = r["a"], r["b"]
        u = units.setdefault(ta["aid"], {"target_aid": ta["aid"], "target_product": ta.get("product", ""),
                                         "activities": {}, "rows": []})
        u["rows"].append(pair_id(r))
        for side, act, who in (("a", ta, "target"), ("b", pa, r["portco"])):
            entry = u["activities"].setdefault(act["aid"], {"aid": act["aid"], "role": who, "activity": act, "items": []})
            entry["items"] = list(dict.fromkeys(entry["items"] + items[side]))
    order = {aid: k for k, aid in enumerate(target_order)}
    out = []
    for u in sorted(units.values(), key=lambda x: order.get(x["target_aid"], 99)):
        acts = list(u["activities"].values())
        # the target activity first, then the portfolio activities in the order the rows met them
        acts.sort(key=lambda e: e["role"] != "target")
        u["activities"] = acts
        out.append(u)
    return out


def needed(unit):
    """What a search must cover: every (activity, item), with a hash of the activity's content, so that an edited
    activity is searched again."""
    return sorted({(e["aid"], item, _content_hash(e["activity"])) for e in unit["activities"] for item in e["items"]})


def _content_hash(act):
    content = {k: v for k, v in act.items() if k != "aid"}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]


def reusable(record, unit):
    """An earlier search can be kept if it covered every (activity, item) the unit needs now (e.g. after a row was
    dismissed, it covers more than needed; after a row was added back, it may not)."""
    if not record or record.get("error"):
        return False
    have = {tuple(x) for x in record.get("covered") or []}
    return set(needed(unit)) <= have


# =============================================================== the anonymised input
def unit_input(unit, names):
    """The item list sent to the query and reflection calls: activities numbered 1, 2, ... (no company labels), each
    with its product line, level of trade and direct customers, and its items with ids such as [2.3]. Names removed in
    code. Returns (text, index {item_id: (aid, item)}, leftover names)."""
    lines, index = [], {}
    for k, e in enumerate(unit["activities"], start=1):
        a = e["activity"]
        customers = rules._join(a.get("direct_customers"))
        details = a.get("customer_details") or "not stated"
        if details != "not stated":
            customers += f" ({details})"
        lines.append(f"Activity {k}: {a.get('product', 'not stated')} · level of trade: "
                     f"{a.get('value_chain_level', 'not stated')} · direct customers: {customers} · status: "
                     f"{a.get('status', 'not stated')}")
        for j, item in enumerate(e["items"], start=1):
            iid = f"{k}.{j}"
            index[iid] = (e["aid"], item)
            lines.append(f"[{iid}] {item}")
        lines.append("")
    text = rules.redact("\n".join(lines).strip(), names)
    return text, index, rules.find_names(text, names)


def paragraphs_text(paragraphs):
    """The retrieved paragraphs as the reflection sees them: id, decision, year, section, text and footnotes."""
    out = []
    for p in paragraphs:
        notes = " ".join(f"[fn {f['n']}] {f['text']}" for f in p.get("footnotes") or [])
        head = f"[{p['id']}] {p['case']} {p['title']} ({p['date'][:4]}) · {p.get('section') or 'section not stated'}"
        out.append(head + "\n" + p["text"] + (f"\nFootnotes: {notes}" if notes else ""))
    return "\n\n".join(out)


# =============================================================== the AI calls (development cache as in stage 3)
def _call(ai, step, schema, instructions, prompt, names, guard_text=None):
    """One structured call; invalid output: one retry with the fallback model. Returns (data or None, error).
    guard_text: the part of the prompt the guard checks (default: all of it); the retrieved public paragraphs are
    left out of the check (Linda, 20 Oct)."""
    leftover = rules.find_names(prompt if guard_text is None else guard_text, names)
    if leftover:
        return None, f"blocked: names found {leftover}"
    model = ai.model(step)
    path, hit = ai.cache_get(step, [model, instructions, schema.model_json_schema(), prompt])
    if hit:
        ai.log_cached(step, model)
        return hit, None
    for m in (model, ai.fallback()):
        try:
            resp = ai.respond(step, prompt, instructions=instructions, schema=schema, model=m)
        except Exception as e:  # noqa: BLE001 - reported, never hidden
            return None, f"call failed: {type(e).__name__}: {e}"
        if resp.output_parsed is not None:
            data = resp.output_parsed.model_dump()
            ai.cache_put(path, data)
            return data, None
    return None, "no valid answer from the model"


def cached_embed(ai):
    """Query embeddings through the AI gate (logged as 'embed_query'), with the development cache."""
    def embed(texts):
        texts = list(texts)
        path, hit = ai.cache_get("embed_query", [ai_embed_model(), texts])
        if hit:
            ai.log_cached("embed_query", ai_embed_model())
            return hit
        vectors = ai.embed(texts, note="stage 4 query", step="embed_query")
        ai.cache_put(path, vectors)
        return vectors
    return embed


def ai_embed_model():
    from ai_client import EMBED_MODEL
    return EMBED_MODEL


# =============================================================== retrieval
_search_lock = threading.Lock()


def retrieve(retriever, queries, use_level):
    """Runs every query through the hybrid search (spec section 14) and returns (paragraph ids in order, the
    paragraphs, the trail per query). Only decision paragraphs are kept; each hit brings its neighbours (+/-1)."""
    order, paras, trail = [], {}, []
    for q in queries:
        level = q.get("level") if use_level and q.get("level") not in (None, "any") else None
        with _search_lock:                       # one search at a time on the shared index
            res = retriever.search(q["query"], k=POOL_PER_QUERY, level=level)
        hits = [h for h in res["hits"] if h["paragraph"].get("source_type") == SOURCE_DECISION][:HITS_PER_QUERY]
        trail.append({"query": q["query"], "level": q.get("level"), "level_filter": res.get("level_filter"),
                      "level_filter_dropped": res.get("level_filter_dropped"),
                      "hits": [{"id": h["paragraph"]["id"], "found_by": h["found_by"], "rank_vector": h["rank_vector"],
                                "rank_keyword": h["rank_keyword"], "score": h["score"],
                                "neighbours": [n["id"] for n in h["neighbours"]]} for h in hits]})
        for h in hits:
            for p in [h["paragraph"]] + [n for n in h["neighbours"] if n.get("source_type") == SOURCE_DECISION]:
                if p["id"] not in paras:
                    paras[p["id"]] = p
                    order.append(p["id"])
    return order, paras, trail


def _pool_order(order, trail):
    """Hits first (in query order), then the neighbours, at most MAX_PARAGRAPHS."""
    hits = [h["id"] for t in trail for h in t["hits"]]
    first = list(dict.fromkeys(hits))
    rest = [pid for pid in order if pid not in set(first)]
    return (first + rest)[:MAX_PARAGRAPHS]


# =============================================================== the loop (Lab 2: hard STOP, AI STOP, code STOP)
PARA_ID = re.compile(r"(M\.\s?\d+|Notice)\D{0,10}?(\d+)", re.IGNORECASE)


def norm_id(text):
    """'M.5644-21', 'M.5644 (21)', 'M.5644 para 21' -> 'M.5644-21'."""
    m = PARA_ID.search(text or "")
    if not m:
        return (text or "").strip()
    case = m.group(1).replace(" ", "")
    case = "Notice" if case.lower() == "notice" else "M." + case.split(".")[1]
    return f"{case}-{int(m.group(2))}"


def empty_record(unit, text="", index=None, error=""):
    return {"target_aid": unit["target_aid"], "target_product": unit.get("target_product", ""), "items_text": text,
            "index": {k: list(v) for k, v in (index or {}).items()}, "covered": [list(x) for x in needed(unit)],
            "rows": unit["rows"], "attempts": [], "markets": {}, "placements": {}, "rejected": [], "stop": error,
            "error": error, "paragraphs": {}}


def run_unit(ai, unit, names, retriever, corpus=None):
    """The search for one target activity. Returns the record that the table, 'Details' and the audit log read."""
    text, index, leftover = unit_input(unit, names)
    record = empty_record(unit, text, index)
    if leftover:
        record["error"] = record["stop"] = STOP_WORDS["blocked"] + f" ({', '.join(leftover)})"
        return record
    query_prompt = "ITEMS\n" + text
    plan, err = _call(ai, "query", schemas.QueryPlan, schemas.QUERY_INSTRUCTIONS, query_prompt, names)
    record["query_prompt"] = query_prompt
    if plan is None:
        record["error"] = record["stop"] = err
        return record
    queries = [q for q in plan.get("queries") or [] if (q.get("query") or "").strip()][:4]
    if not queries:
        record["error"] = record["stop"] = "the query call returned no query"
        return record
    pool, paras, best = [], {}, None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        guard = rules.find_names(" ".join(q["query"] for q in queries), names)
        if guard:                                # a query is AI text: checked like everything else that is sent
            record["stop"] = STOP_WORDS["blocked"] + f" ({', '.join(guard)})"
            break
        order, found, trail = retrieve(retriever, queries, use_level=(attempt == 1))
        new = [pid for pid in order if pid not in paras]
        step = {"attempt": attempt, "queries": queries, "level_filter": attempt == 1, "retrieval": trail,
                "new_paragraphs": new}
        record["attempts"].append(step)
        if attempt > 1 and not new:
            record["stop"] = STOP_WORDS["same paragraphs"]
            break
        paras.update(found)
        pool = list(dict.fromkeys(pool + _pool_order(order, trail)))[:MAX_PARAGRAPHS + 10 * (attempt - 1)]
        # 20 Oct (Linda): the decisions are public text and pass unchanged, even where they name a company of the
        # screen (M.6872 is Barry Callebaut / Petra Foods). The guard checks what the app and the AI write (the items
        # and the queries), not the paragraphs; screen names found in the paragraphs are recorded for the audit log.
        raw = paragraphs_text([paras[p] for p in pool])
        step["screen_names_in_paragraphs"] = rules.find_names(raw, names)
        prompt = "ITEMS\n" + text + "\n\nPARAGRAPHS\n" + raw
        data, err = _call(ai, "reflect", schemas.Reflection, schemas.REFLECTION_INSTRUCTIONS, prompt, names,
                          guard_text="ITEMS\n" + text)
        step["reflection_prompt"] = prompt
        step["paragraphs_sent"] = list(pool)
        if data is None:
            step["error"] = err
            record["stop"] = STOP_WORDS["failed"] + f" ({err})"
            break
        step["reflection"] = data
        best = check(data, index, set(pool), paras)
        step["checked"] = {"placed": sum(1 for p in best["placements"].values() if p["market_id"] != "none"),
                           "items": len(index), "rejected": best["rejected"]}
        open_items = [i for i, p in best["placements"].items() if p["market_id"] == "none"]
        if not open_items:
            record["stop"] = STOP_WORDS["all placed"]
            break
        if attempt == MAX_ATTEMPTS:
            record["stop"] = STOP_WORDS["attempts"]
            break
        queries = [q for q in data.get("rewrite_queries") or [] if (q.get("query") or "").strip()][:3]
        if not queries:
            record["stop"] = STOP_WORDS["no rewrite"]
            break
    if best is None:
        record["error"] = record["error"] or record["stop"]
        return record
    record["markets"], record["placements"], record["rejected"] = best["markets"], best["placements"], best["rejected"]
    cited = {pid for m in best["markets"].values() for pid in m["product_paragraphs"] + m["geographic_paragraphs"]}
    record["paragraphs"] = {pid: _para_view(paras[pid], paras, corpus) for pid in cited if pid in paras}
    return record


def check(data, index, pool, paras):
    """The citation check and the item check, in code (spec section 9, step 6): a paragraph may be cited only if the
    retrieval returned it in this search; a market left without any valid paragraph is dropped and its items count as
    'none'; an item id must exist; an item the reflection did not place counts as 'none'. Every correction is listed in
    'rejected' (shown in Details and the audit log)."""
    rejected, markets = [], {}
    for m in data.get("markets") or []:
        mid = (m.get("market_id") or "").strip()
        if not mid or mid.lower() == "none":
            continue
        prod, geo = [], []
        for field, keep in (("product_paragraphs", prod), ("geographic_paragraphs", geo)):
            for raw in m.get(field) or []:
                pid = norm_id(raw)
                if pid in pool and paras.get(pid, {}).get("source_type") == SOURCE_DECISION:
                    if pid not in keep:
                        keep.append(pid)
                else:
                    rejected.append(f"{mid}: paragraph {raw} was not among the paragraphs retrieved")
        if not prod:
            rejected.append(f"{mid} ({m.get('name', '')}): no valid paragraph left, market not used")
            continue
        markets[mid] = {"market_id": mid, "name": m.get("name") or "not stated", "conclusion": m.get("conclusion"),
                        "product_paragraphs": _sorted_ids(prod), "geographic_scope": m.get("geographic_scope") or "",
                        "geographic_paragraphs": _sorted_ids(geo), "summary": m.get("summary") or ""}
    placements = {}
    for p in data.get("placements") or []:
        iid = (p.get("item_id") or "").strip().strip("[]")
        if iid not in index:
            rejected.append(f"item id {p.get('item_id')} does not exist")
            continue
        if iid in placements:
            continue
        mid = (p.get("market_id") or "none").strip()
        basis = p.get("basis") or "none"
        if mid != "none" and mid not in markets:
            rejected.append(f"item {iid}: market {mid} not available")
            mid, basis = "none", "none"
        if mid == "none":
            basis = "none"
        elif basis == "none":
            basis = "analogy"           # placed but not called a precedent: the weaker label, for the lawyer to check
        placements[iid] = {"market_id": mid, "basis": basis, "reason": p.get("reason") or ""}
    for iid in index:
        placements.setdefault(iid, {"market_id": "none", "basis": "none", "reason": "not placed by the reflection"})
    return {"markets": markets, "placements": placements, "rejected": rejected}


def _sorted_ids(ids):
    return sorted(ids, key=lambda pid: (pid.split("-")[0], int(pid.split("-")[1]) if pid.split("-")[-1].isdigit() else 0))


def _para_view(p, paras, corpus):
    """A cited paragraph as shown under 'Paragraphs': its text, footnotes, decision, link and the neighbours."""
    def neighbour(n):
        nid = f"{p['case']}-{n}"
        q = paras.get(nid) or (corpus or {}).get(nid)
        return {"id": nid, "text": q["text"]} if q else None
    return {"id": p["id"], "case": p["case"], "title": p["title"], "date": p["date"], "para": p["para"],
            "section": p.get("section"), "decision": p.get("decision"), "url": p.get("url"), "text": p["text"],
            "footnotes": p.get("footnotes") or [],
            "neighbours": [x for x in (neighbour(p["para"] - 1), neighbour(p["para"] + 1)) if x]}


# =============================================================== what one row shows (code)
def cite_range(ids, paras, short=False):
    """'M.5644 Kraft Foods / Cadbury (2010) (21)–(24), (42)' from paragraph ids, one group per decision; short:
    'M.5644 (2010) (21)–(24), (42)' (the table cell; the title is under "Paragraphs")."""
    by_case = {}
    for pid in ids:
        case, n = pid.split("-")
        by_case.setdefault(case, []).append(int(n))
    out = []
    for case, ns in by_case.items():
        ns = sorted(set(ns))
        runs, start, prev = [], ns[0], ns[0]
        for n in ns[1:] + [None]:
            if n is not None and n == prev + 1:
                prev = n
                continue
            runs.append(f"({start})" if start == prev else f"({start})–({prev})")
            if n is not None:
                start = prev = n
        p = next((paras[x] for x in ids if x.startswith(case + "-") and x in paras), None)
        label = (f"{case} ({p['date'][:4]})" if short else f"{case} {p['title']} ({p['date'][:4]})") if p else case
        out.append(f"{label} {', '.join(runs)}")
    return "; ".join(out)


def side_markets(record, aid, items):
    """For one side of a row: [(market or None, basis, [items])], items grouped by the market they were placed in."""
    by_item = {(v[0], v[1]): iid for iid, v in (record.get("index") or {}).items()}
    groups = {}
    for item in items:
        iid = by_item.get((aid, item))
        p = (record.get("placements") or {}).get(iid) if iid else None
        mid = p["market_id"] if p else "none"
        basis = p["basis"] if p else "none"
        g = groups.setdefault(mid, {"market": (record.get("markets") or {}).get(mid), "basis": set(), "items": []})
        g["basis"].add(basis)
        g["items"].append(item)
    out = []
    for mid, g in groups.items():
        basis = "precedent" if "precedent" in g["basis"] else "analogy" if "analogy" in g["basis"] else "none"
        out.append({"market_id": mid, "market": g["market"], "basis": basis, "items": g["items"]})
    out.sort(key=lambda x: (x["market_id"] == "none", x["market_id"]))
    return out


def row_view(r, record, overrides, effective_status, dismissed_parts):
    """Everything the market column and the 'under the precedent' line of one row show, from the stored search.
    Returns None if the row is not kept or not searched yet. Pure code."""
    items = row_items(r, overrides, effective_status, dismissed_parts)
    if items is None or not record:
        return None
    if record.get("error") and not record.get("markets"):
        return {"error": record["error"], "a": [], "b": [], "verdict": None, "unplaced": items["a"] + items["b"]}
    a = side_markets(record, r["a"]["aid"], items["a"])
    b = side_markets(record, r["b"]["aid"], items["b"])
    view = {"error": "", "a": a, "b": b, "verdict": None,
            "unplaced": [i for g in a + b if g["market_id"] == "none" for i in g["items"]]}
    d = r["decision"]
    off = set(dismissed_parts(r, overrides))
    if d.get("horizontal") and "horizontal" not in off and effective_status(r, overrides) == "candidate":
        ma = {g["market_id"] for g in a if g["market_id"] != "none"}
        mb = {g["market_id"] for g in b if g["market_id"] != "none"}
        both = ma & mb
        view["verdict"] = {
            "both": [g for g in a if g["market_id"] in both],
            "only_a": [g for g in a if g["market_id"] in ma - both],
            "only_b": [g for g in b if g["market_id"] in mb - both],
            # the precedent puts the two companies' items into different markets: shown, never deleted (spec section 8)
            "different": bool(ma and mb and not both),
            "left_open": any((g["market"] or {}).get("conclusion") == "left open" for g in a + b if g["market"]),
        }
    return view


def decisions_cited(view, record):
    """The decisions a row cites, with their year (for 'Applicable today?')."""
    paras = record.get("paragraphs") or {}
    out = {}
    for g in (view or {}).get("a", []) + (view or {}).get("b", []):
        m = g.get("market") or {}
        for pid in m.get("product_paragraphs", []) + m.get("geographic_paragraphs", []):
            p = paras.get(pid)
            if p:
                out[p["case"]] = f"{p['case']} ({p['date'][:4]})"
    return list(out.values())


def summary(records):
    """Counts for the line above the table: searches, markets, placed items, by basis."""
    placed = [p for rec in records for p in (rec.get("placements") or {}).values()]
    return {"searches": len(records), "markets": sum(len(rec.get("markets") or {}) for rec in records),
            "items": len(placed), "precedent": sum(p["basis"] == "precedent" for p in placed),
            "analogy": sum(p["basis"] == "analogy" for p in placed),
            "none": sum(p["basis"] == "none" for p in placed),
            "rejected": sum(len(rec.get("rejected") or []) for rec in records),
            "errors": [rec["error"] for rec in records if rec.get("error")]}