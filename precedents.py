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

import rules
import schemas

MAX_ATTEMPTS = 2          # one rewrite of the queries (Linda, 20 Oct); version 8 planned three attempts
MAX_TYPES = 8             # types of product per search: one small reflection each (Linda, 20 Oct: option B)
MAX_EXTRA = 4             # items the query step left unassigned: searched on their own, at most this many
MAX_REWRITE = 2           # types of product in the rewrite of one type
# 20 Oct: every type of product is searched with two questions, built in code. The test on the corpus (keyword search,
# 11 markets of the test cases): product words alone found a DEFINING paragraph in the top 5 in 9 of 11 cases, the
# Commission's question in 11 of 11, but it also pulls in definitions of other products; the top 3 of each: 11 of 11,
# with the product-specific paragraphs kept. The wording is legal, not sector knowledge.
QUERY_FORMS = ("relevant product market for {p}", "whether {p} constitutes a separate relevant product market")
HITS_PER_FORM = 3         # decision paragraphs kept per question (the Notice states principles and is not searched here)
POOL_PER_QUERY = 10       # hits asked from the retriever per question, before the Notice is left out
MAX_PARAGRAPHS = 14       # paragraphs per reflection of one type (its hits first, then their neighbours); +8 in the
                          # second attempt. 20 Oct (Linda, option B): one focused call per type of product with a few
                          # paragraphs, as in the class code and the chatbot, instead of 30-40 products against up to
                          # 40 paragraphs in one call (the compound paragraph was in that call, but ChoViva was missed)
TYPE_PARALLEL = 4         # types of one search run at the same time (the AI gate allows 8 requests at once in all)
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


def items_text(unit, names, only=None):
    """The item list for some item ids only (one type of product), with the same numbering as unit_input and only the
    activities that have items in it."""
    lines = []
    for k, e in enumerate(unit["activities"], start=1):
        ids = [(f"{k}.{j}", item) for j, item in enumerate(e["items"], start=1) if only is None or f"{k}.{j}" in only]
        if not ids:
            continue
        a = e["activity"]
        customers = rules._join(a.get("direct_customers"))
        details = a.get("customer_details") or "not stated"
        if details != "not stated":
            customers += f" ({details})"
        lines.append(f"Activity {k}: {a.get('product', 'not stated')} · level of trade: "
                     f"{a.get('value_chain_level', 'not stated')} · direct customers: {customers}")
        lines += [f"[{iid}] {item}" for iid, item in ids] + [""]
    return rules.redact("\n".join(lines).strip(), names)


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
def query_text(q):
    """The type of product of a query (older records, before 20 Oct, kept a full query under 'query')."""
    return (q.get("products") or q.get("query") or "").strip()


def retrieve(retriever, queries, use_level):
    """Runs every type of product through the hybrid search (spec section 14), with both questions of QUERY_FORMS,
    and returns (paragraph ids in order, the paragraphs, the trail per question). Only decision paragraphs are kept;
    each hit brings its neighbours (+/-1)."""
    order, paras, trail = [], {}, []
    for q in queries:
        level = q.get("level") if use_level and q.get("level") not in (None, "any") else None
        for form in QUERY_FORMS:
            question = form.format(p=query_text(q))
            res = retriever.search(question, k=POOL_PER_QUERY, level=level)    # the index read is locked inside
            hits = [h for h in res["hits"] if h["paragraph"].get("source_type") == SOURCE_DECISION][:HITS_PER_FORM]
            trail.append({"query": question, "products": query_text(q), "level": q.get("level"),
                          "level_filter": res.get("level_filter"),
                          "level_filter_dropped": res.get("level_filter_dropped"),
                          "hits": [{"id": h["paragraph"]["id"], "found_by": h["found_by"],
                                    "rank_vector": h["rank_vector"], "rank_keyword": h["rank_keyword"],
                                    "score": h["score"], "neighbours": [n["id"] for n in h["neighbours"]]}
                                   for h in hits]})
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
    """The search for one target activity (option B, Linda 20 Oct): one AI call sorts the products into types of
    product; then each type is searched and placed on its own (run_type), in parallel; code merges the results.
    Returns the record that the table, 'Details' and the audit log read."""
    import concurrent.futures as cf
    text, index, leftover = unit_input(unit, names)
    record = empty_record(unit, text, index)
    record["types"] = []
    if leftover:
        record["error"] = record["stop"] = STOP_WORDS["blocked"] + f" ({', '.join(leftover)})"
        return record
    query_prompt = "ITEMS\n" + text
    plan, err = _call(ai, "query", schemas.QueryPlan, schemas.QUERY_INSTRUCTIONS, query_prompt, names)
    record["query_prompt"] = query_prompt
    if plan is None:
        record["error"] = record["stop"] = err
        return record
    types = assign_types(plan, index, unit, names)
    record["unassigned_searched"] = [t["item_ids"][0] for t in types if t.get("extra")]
    record["not_searched"] = [i for i in index if not any(i in t["item_ids"] for t in types)]
    if not types:
        record["error"] = record["stop"] = "the query step returned no type of product"
        return record
    with cf.ThreadPoolExecutor(TYPE_PARALLEL) as ex:
        results = list(ex.map(lambda t: run_type(ai, t, unit, index, names, retriever), types))
    paras_all = {}
    for k, (t, res) in enumerate(zip(types, results), start=1):
        prefix = f"T{k}."
        res["markets"] = {prefix + mid: dict(m, market_id=prefix + mid) for mid, m in res["markets"].items()}
        res["placements"] = {iid: dict(p, market_ids=[prefix + m for m in p["market_ids"]])
                             for iid, p in res["placements"].items()}
        record["markets"].update(res["markets"])
        record["placements"].update(res["placements"])
        record["rejected"] += [f"{t['products']}: {x}" for x in res["rejected"]]
        paras_all.update(res.pop("paras"))
        record["types"].append({**t, **{k2: v for k2, v in res.items() if k2 not in ("markets", "placements")}})
    for iid in record["not_searched"]:
        record["placements"][iid] = {"market_ids": [], "basis": "none",
                                     "reason": "not searched: the query step assigned it to no type of product"}
    stops = [t["stop"].split(":")[0] for t in record["types"]]
    record["stop"] = f"{len(types)} types of product: " + ", ".join(f"{s} ×{stops.count(s)}" for s in dict.fromkeys(stops))
    errors = [t["error"] for t in record["types"] if t.get("error")]
    if errors and not record["markets"] and len(errors) == len(types):
        record["error"] = "; ".join(dict.fromkeys(errors))
    cited = {pid for m in record["markets"].values() for pid in m["product_paragraphs"]}
    record["paragraphs"] = {pid: _para_view(paras_all[pid], paras_all, corpus) for pid in cited if pid in paras_all}
    return record


def assign_types(plan, index, unit, names):
    """The types of product of the query step, checked in code: only item ids that exist, each item in one type only
    (the first that names it); a type without valid items is dropped. Items the query step left out are searched on
    their own (their own words as the type, the level of their activity), at most MAX_EXTRA of them."""
    types, seen = [], set()
    for q in (plan.get("queries") or [])[:MAX_TYPES]:
        ids = [i.strip().strip("[]") for i in q.get("item_ids") or []]
        ids = [i for i in dict.fromkeys(ids) if i in index and i not in seen]
        if not ids or not query_text(q):
            continue
        seen.update(ids)
        types.append({"products": query_text(q), "level": q.get("level") or "any", "item_ids": ids})
    level_of = {e["aid"]: e["activity"].get("value_chain_level") or "any" for e in unit["activities"]}
    for iid in [i for i in index if i not in seen][:MAX_EXTRA]:
        aid, item = index[iid]
        types.append({"products": rules.redact(item, names), "level": level_of.get(aid, "any"), "item_ids": [iid],
                      "extra": True})
    return types


def run_type(ai, t, unit, index, names, retriever):
    """One type of product: retrieval (both questions), one small reflection on its items only, the loop with its three
    STOP conditions (Lab 2), the citation and item checks. Never raises: an error is returned with the type."""
    sub = {i: index[i] for i in t["item_ids"]}
    text = items_text(unit, names, only=set(sub))
    out = {"items_text": text, "attempts": [], "stop": "", "error": "", "kept_attempt": 0, "markets": {},
           "placements": {}, "rejected": [], "paras": {}}
    try:
        queries = [{"products": t["products"], "level": t["level"]}]
        pool, paras, best = [], {}, None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            guard = rules.find_names(" ".join(query_text(q) for q in queries) + "\n" + text, names)
            if guard:                            # AI text and app text: checked like everything else that is sent
                out["stop"] = STOP_WORDS["blocked"] + f" ({', '.join(guard)})"
                break
            order, found, trail = retrieve(retriever, queries, use_level=(attempt == 1))
            new = [pid for pid in order if pid not in paras]
            step = {"attempt": attempt, "queries": queries, "level_filter": attempt == 1, "retrieval": trail,
                    "new_paragraphs": new}
            out["attempts"].append(step)
            if attempt > 1 and not new:
                out["stop"] = STOP_WORDS["same paragraphs"]
                break
            paras.update(found)
            pool = list(dict.fromkeys(pool + _pool_order(order, trail)))[:MAX_PARAGRAPHS + 8 * (attempt - 1)]
            # 20 Oct (Linda): the decisions are public text and pass unchanged, even where they name a company of the
            # screen; the guard checks what the app and the AI write; such names are recorded for the audit log.
            raw = paragraphs_text([paras[p] for p in pool])
            step["screen_names_in_paragraphs"] = rules.find_names(raw, names)
            prompt = "ITEMS\n" + text + "\n\nPARAGRAPHS\n" + raw
            data, err = _call(ai, "reflect", schemas.Reflection, schemas.REFLECTION_INSTRUCTIONS, prompt, names,
                              guard_text="ITEMS\n" + text)
            step["reflection_prompt"] = prompt
            step["paragraphs_sent"] = list(pool)
            if data is None:
                step["error"] = err
                out["stop"] = STOP_WORDS["failed"] + f" ({err})"
                break
            step["reflection"] = data
            result = check(data, sub, set(pool), paras)
            placed = sum(1 for p in result["placements"].values() if ids_of(p))
            step["checked"] = {"placed": placed, "items": len(sub), "rejected": result["rejected"]}
            # keep the better attempt (20 Oct): a second attempt can place FEWER items; on a tie the later one
            if best is None or placed >= sum(1 for p in best["placements"].values() if ids_of(p)):
                best, out["kept_attempt"] = result, attempt
            if placed == len(sub):
                out["stop"] = STOP_WORDS["all placed"]
                break
            if attempt == MAX_ATTEMPTS:
                out["stop"] = STOP_WORDS["attempts"]
                break
            queries = [{"products": query_text(q), "level": q.get("level") or "any"}
                       for q in data.get("rewrite_queries") or [] if query_text(q)][:MAX_REWRITE]
            if not queries:
                out["stop"] = STOP_WORDS["no rewrite"]
                break
        if best is None:
            out["error"] = out["stop"]
        else:
            out["markets"], out["placements"], out["rejected"] = best["markets"], best["placements"], best["rejected"]
        out["paras"] = paras
    except Exception as e:  # noqa: BLE001 - one type failing must not lose the others
        out["error"] = out["stop"] = f"the search failed: {type(e).__name__}: {e}"
    return out


def ids_of(p):
    """The markets a placement names: 'market_ids' since 20 Oct (several per item), 'market_id' in older records."""
    if not p:
        return []
    if "market_ids" in p:
        return [m for m in p["market_ids"] or [] if m and m != "none"]
    return [p["market_id"]] if p.get("market_id") not in (None, "", "none") else []


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
        prod = []
        for raw in m.get("product_paragraphs") or []:
            pid = norm_id(raw)
            if pid in pool and paras.get(pid, {}).get("source_type") == SOURCE_DECISION:
                if pid not in prod:
                    prod.append(pid)
            else:
                rejected.append(f"{mid}: paragraph {raw} was not among the paragraphs retrieved")
        if not prod:
            rejected.append(f"{mid} ({m.get('name', '')}): no valid paragraph left, market not used")
            continue
        markets[mid] = {"market_id": mid, "name": m.get("name") or "not stated", "conclusion": m.get("conclusion"),
                        "product_paragraphs": _sorted_ids(prod), "summary": m.get("summary") or ""}
    placements = {}
    for p in data.get("placements") or []:
        iid = (p.get("item_id") or "").strip().strip("[]")
        if iid not in index:
            rejected.append(f"item id {p.get('item_id')} does not exist")
            continue
        if iid in placements:
            continue
        wanted = p.get("market_ids") if "market_ids" in p else [p.get("market_id")]
        mids = []
        for mid in wanted or []:
            mid = (mid or "").strip()
            if not mid or mid == "none":
                continue
            if mid in markets:
                if mid not in mids:
                    mids.append(mid)
            else:
                rejected.append(f"item {iid}: market {mid} not available")
        basis = p.get("basis") or "none"
        if not mids:
            basis = "none"
        elif basis == "none":
            basis = "analogy"           # placed but not called a precedent: the weaker label, for the lawyer to check
        placements[iid] = {"market_ids": mids, "basis": basis, "reason": p.get("reason") or ""}
    for iid in index:
        placements.setdefault(iid, {"market_ids": [], "basis": "none", "reason": "not placed by the reflection"})
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
    """For one side of a row: [{market_id, market, basis, items}], items grouped by the market(s) they were placed in
    (an item placed in several markets appears in each)."""
    by_item = {(v[0], v[1]): iid for iid, v in (record.get("index") or {}).items()}
    markets = record.get("markets") or {}
    groups = {}
    for item in items:
        iid = by_item.get((aid, item))
        p = (record.get("placements") or {}).get(iid) if iid else None
        mids = [m for m in ids_of(p) if m in markets] or ["none"]
        basis = p["basis"] if p and mids != ["none"] else "none"
        for mid in mids:
            g = groups.setdefault(mid, {"market": markets.get(mid), "basis": set(), "items": []})
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
        # 20 Oct (option B): each type of product is placed in its own call, which names its own markets. Markets of
        # different calls count as one market only if they have the same name; "different markets under the
        # precedent" is claimed only if products of both sides were placed in the SAME call (never across calls)
        key = {mid: _market_key(m["name"]) for mid, m in (record.get("markets") or {}).items()}
        ka = {key.get(g["market_id"], g["market_id"]) for g in a if g["market_id"] != "none"}
        kb = {key.get(g["market_id"], g["market_id"]) for g in b if g["market_id"] != "none"}
        both = ka & kb
        basis_b = {}
        for g in b:
            k = key.get(g["market_id"], g["market_id"])
            basis_b[k] = "precedent" if g["basis"] == "precedent" and basis_b.get(k, "precedent") == "precedent" else g["basis"]
        seen = set()
        view["verdict"] = {
            # a market both sides share counts as "precedent" only if it is a precedent for both; otherwise the line
            # says "by analogy" (TC1: Ritter's bars were placed in "tablets" only by analogy)
            "both": [dict(g, basis="precedent" if g["basis"] == basis_b.get(key.get(g["market_id"])) == "precedent"
                          else "analogy") for g in a if key.get(g["market_id"]) in both
                     and not (key.get(g["market_id"]) in seen or seen.add(key.get(g["market_id"])))],
            "only_a": [g for g in a if g["market_id"] != "none" and key.get(g["market_id"], g["market_id"]) in ka - both],
            "only_b": [g for g in b if g["market_id"] != "none" and key.get(g["market_id"], g["market_id"]) in kb - both],
            # the precedent puts the two companies' items into different markets: shown, never deleted (spec section 8)
            "different": bool(ka and kb and not both and _same_call(record, r, items)),
            "left_open": any((g["market"] or {}).get("conclusion") == "left open" for g in a + b if g["market"]),
        }
    return view


def _market_key(name):
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _same_call(record, r, items):
    """Whether at least one product of each side of the row was placed in the same reflection call. Records from before
    option B had one call for all products."""
    types = record.get("types")
    if not types:
        return True
    by_item = {(v[0], v[1]): iid for iid, v in (record.get("index") or {}).items()}
    call_of = {iid: k for k, t in enumerate(types) for iid in t["item_ids"]}
    ca = {call_of.get(by_item.get((r["a"]["aid"], i))) for i in items["a"]} - {None}
    cb = {call_of.get(by_item.get((r["b"]["aid"], i))) for i in items["b"]} - {None}
    return bool(ca & cb)


def decisions_cited(view, record):
    """The decisions a row cites, with their year (for 'Applicable today?')."""
    paras = record.get("paragraphs") or {}
    out = {}
    for g in (view or {}).get("a", []) + (view or {}).get("b", []):
        m = g.get("market") or {}
        for pid in m.get("product_paragraphs", []):
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