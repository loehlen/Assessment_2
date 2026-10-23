"""
comparison.py - step ③: anonymisation and the factual comparison.

    collect_names(companies, activities, group_companies)   every name that must never reach a comparison
    anonymise(activities, names)                            the abstracts, with the name check
    embed_company(ai, label, activities, names)             one embedding request per company
    build_pairs(target, portcos, profiles)                  every target activity x every portco activity (except
                                                            "Other activities" x "Other activities")
    assess(ai, pair, names)                                 ONE anonymised pair per AI call + code signals + rule

The prompts are in schemas.py, the decision rules (reseller check, resale threshold) in rules.py.
"""
import hashlib
import json
import re
import uuid

import rules
import schemas
from ai_client import EMBED_MODEL


# =============================================================== stable activity IDs and content keys
# Each activity carries a fixed ID ("aid") from the moment it is extracted or added, so that the user's dismissals
# and notes stay with the right pair when activities are added, deleted or re-ordered. The content key decides
# whether a pair must go to the AI again: it changes when anything in the activity or its anonymised abstract
# changes (e.g. a new brand name to remove), and only then.
def new_aid():
    return uuid.uuid4().hex[:10]


def ensure_ids(activities_by_company):
    """Gives every activity without an ID one (e.g. an activity added by the user)."""
    for acts in activities_by_company.values():
        for a in acts:
            if not a.get("aid"):
                a["aid"] = new_aid()


def content_of(activity):
    """What the activity is, without its ID and without the fields that only record the lawyer's handling of it
    (rules.STATE_FIELDS: saving it unchanged in the edit form must not count as a change)."""
    return {k: v for k, v in activity.items() if k != "aid" and k not in rules.STATE_FIELDS}


def activity_key(activity, abstract):
    content = content_of(activity)
    raw = json.dumps(content, sort_keys=True, ensure_ascii=False, default=str) + "\n" + abstract
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


# =============================================================== names and abstracts
def collect_names(companies, activities, group_companies, keep=()):
    """All entered names and aliases, the group companies found by the extraction, and every brand in the
    (confirmed) activity lists. activities / group_companies: {company name: [...]}.
    keep: brands or group company names the lawyer marked as ordinary product words, which stay in the descriptions
    (e.g. a brand that is also the word for the product). The entered names and aliases can never be kept. A part of
    an entered name can be kept when it is an ordinary word in the descriptions ("Black" of "Black & Decker"); a part
    that is itself an entered name or alias cannot."""
    keep = {k.strip().lower() for k in keep or () if k}
    names = []
    for c in companies:
        entered = [c["name"]] + [a for a in c.get("aliases", []) if a]
        fixed = {v.lower() for v in rules.name_variants(entered)}
        names += entered + [p for p in rules.name_parts(entered)      # "Smith" for "Smith & Sons"
                            if p.lower() in fixed or p.strip().lower() not in keep]
        names += [g for g in group_companies.get(c["name"], []) if g and g.strip().lower() not in keep]
        for a in activities.get(c["name"], []):
            names += [b for b in a.get("brands") or [] if b and b.strip().lower() not in keep]
    return names


GENERIC_FIELDS = ("product", "includes", "description", "intended_use", "main_inputs")


def names_used_as_words(companies, activities, group_companies):
    """Brands and group company names that also appear in the generic fields of the activities, where the extraction
    writes no names. Such a word is either an ordinary product word that happens to be a brand or a name that slipped
    in; removing it can take away what the comparison needs, so the lawyer decides.
    Also the parts of entered names ("Black" of "Black & Decker"), which are removed everywhere by default and may be
    ordinary product words; a part that is itself an entered name or alias is never listed.
    Returns [{"word", "company" (whose name, brand or group company it is), "kind" ("part of the name" or "brand or
    group company"), "examples": [(company, text)]}]. Pure code."""
    typed = [n for c in companies for n in [c["name"]] + list(c.get("aliases") or []) if n]
    fixed = {v.lower() for v in rules.name_variants(typed)}
    entered = {v.lower() for v in rules.name_variants(typed + rules.name_parts(typed))}
    owners, kinds = {}, {}
    for c in companies:
        for p in rules.name_parts([c["name"]] + list(c.get("aliases") or [])):
            if p.lower() not in fixed:
                owners.setdefault(p.lower(), (p, c["name"]))
                kinds.setdefault(p.lower(), "part of the name")
    for c in companies:
        for n in list(group_companies.get(c["name"]) or []) + [b for a in activities.get(c["name"], [])
                                                               for b in a.get("brands") or []]:
            n = (n or "").strip()
            # a group company whose short form is an entered name ("X S.r.l." -> "X") is the company itself: always removed
            if not n or n.lower() == "not stated" or {v.lower() for v in rules.name_variants([n])} & entered:
                continue
            owners.setdefault(n.lower(), (n, c["name"]))
            kinds.setdefault(n.lower(), "brand or group company")
    found = []
    for word, owner in owners.values():
        examples, lower = [], False
        for c in companies:
            for a in activities.get(c["name"], []):
                for f in GENERIC_FIELDS:
                    values = a.get(f)
                    for text in (values if isinstance(values, list) else [values]):
                        if text and rules.find_names(str(text), [word]):
                            examples.append((c["name"], str(text)))
                            lower = lower or used_in_lower_case(str(text), word)
        if examples:
            found.append({"word": word, "company": owner, "kind": kinds[word.lower()], "lower_case": lower,
                          "examples": list(dict.fromkeys(examples))[:3]})
    return sorted(found, key=lambda x: (not x["lower_case"], x["word"].lower()))


def used_in_lower_case(text, word):
    """Whether the word appears at least once starting with a lower-case letter ("cacaofruit ingredients"). Brand
    names written into a description are almost always capitalised, while an ordinary product word usually appears in
    lower case somewhere. Scripts without upper and lower case never count as lower case, so such a word stays in the
    folded list (removed by default, the safe side)."""
    for m in re.finditer(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text, re.IGNORECASE):
        first = m.group(0)[:1]
        if first.islower():
            return True
    return False


def anonymise(activities, names):
    """Abstracts of one company's activities. Returns (abstracts, problems); problems lists the activities in
    which a name is still found after the removal. Their pairs are blocked (shown as 'unclear')."""
    abstracts, problems = [], []
    for i, a in enumerate(activities):
        text, leftover = rules.build_abstract(a, names)
        abstracts.append(text)
        if leftover:
            problems.append((i, leftover))
    return abstracts, problems


# =============================================================== embeddings (one request per company)
def embedding_texts(activities, names):
    texts = []
    for a in activities:
        texts.append(rules.redact(rules.product_text(a), names))
        texts += [rules.redact(i, names) for i in a.get("main_inputs") or [] if i and i != "not stated"]
    return texts


def embed_company(ai, label, activities, names):
    """Anonymised product texts and inputs of ONE company in one request. Returns one entry per activity:
    {"product": vector, "inputs": [vectors]}. An error is raised, never hidden: a missing vector would
    make two products look unrelated, and an error must never screen a pair out."""
    texts = embedding_texts(activities, names)
    for t in texts:
        if rules.find_names(t, names):
            raise RuntimeError(f"Blocked: a name is left in an embedding text of {label}")
    if not texts:
        return []
    path, hit = ai.cache_get("embed", [EMBED_MODEL, texts])
    if hit:
        ai.log_cached("embed", EMBED_MODEL, label)
        vectors = hit
    else:
        vectors = ai.embed(texts, note=label)
        ai.cache_put(path, vectors)
    out, k = [], 0
    for a in activities:
        n_inputs = len([i for i in a.get("main_inputs") or [] if i and i != "not stated"])
        out.append({"product": vectors[k], "inputs": vectors[k + 1:k + 1 + n_inputs]})
        k += 1 + n_inputs
    return out


# =============================================================== pairs
def build_pairs(target, portcos, profiles):
    """profiles: {name: {"activities", "abstracts", "vectors"}}.
    Labels: T-2 = target activity 2, P1-3 = portco 1, activity 3. The key never leaves the app."""
    pairs = []
    t = profiles[target]
    for pi, portco in enumerate(portcos, start=1):
        p = profiles[portco]
        for ti, ta in enumerate(t["activities"]):
            for ki, pa in enumerate(p["activities"]):
                if not rules.compared_pair(ta, pa):        # never "Other activities" with "Other activities"
                    continue
                tv, pv = t["vectors"][ti], p["vectors"][ki]
                sims = {"product": rules.cosine(tv["product"], pv["product"]),
                        "input_a_to_b": rules.best_input_match(tv["product"], pv["inputs"]),
                        "input_b_to_a": rules.best_input_match(pv["product"], tv["inputs"])}
                pairs.append({"portco": portco, "label_a": f"T-{ti + 1}", "label_b": f"P{pi}-{ki + 1}",
                              "a": ta, "b": pa, "abstract_a": t["abstracts"][ti], "abstract_b": p["abstracts"][ki],
                              "sims": sims})
    return pairs


# =============================================================== one anonymised pair per AI call
NO_ITEMS = {"matching_items_a": [], "matching_items_b": [], "vertical_items": []}


def compare(ai, prompt, names):
    """An error or a blocked call never screens a pair out: it becomes 'not enough information' -> unclear."""
    leftover = rules.find_names(prompt, names)
    if leftover:
        return {"product_relation": "not enough information", "product_reason": f"Blocked: names found {leftover}",
                "vertical_links": [], "vertical_reason": "", "blocked": True, **NO_ITEMS}
    model = ai.model("compare")
    path, hit = ai.cache_get("compare", [model, schemas.COMPARISON_INSTRUCTIONS,
                                         schemas.Comparison.model_json_schema(), prompt])
    if hit:
        ai.log_cached("compare", model)
        return hit
    try:
        resp = ai.respond("compare", prompt, instructions=schemas.COMPARISON_INSTRUCTIONS,
                          schema=schemas.Comparison, model=model)
    except Exception as e:  # noqa: BLE001
        return {"product_relation": "not enough information", "product_reason": f"Call failed: {e}",
                "vertical_links": [], "vertical_reason": "", "error": True, **NO_ITEMS}
    if resp.output_parsed is None:
        return {"product_relation": "not enough information", "product_reason": "No valid answer from the model",
                "vertical_links": [], "vertical_reason": "", "error": True, **NO_ITEMS}
    data = resp.output_parsed.model_dump()
    ai.cache_put(path, data)
    return data


def assess(ai, pair, names):
    prompt = schemas.comparison_input(pair["abstract_a"], pair["abstract_b"])
    comparison = compare(ai, prompt, names)
    signals = rules.code_vertical_signals(pair["a"], pair["b"], pair["sims"])
    decision = rules.decide(comparison, signals, pair["sims"]["product"], pair["a"], pair["b"])
    customers = rules.customer_overlap(pair["a"]["direct_customers"], pair["b"]["direct_customers"])
    eea = [rules.eea_status(pair["a"]["countries_of_sale"]), rules.eea_status(pair["b"]["countries_of_sale"])]
    flags = (["no EEA overlap"] if "outside the EEA only" in eea else []) + \
        (["captive (not on the merchant market)"] if rules.captive_only(pair["a"]) or rules.captive_only(pair["b"])
         else [])
    matches, vertical_items = check_matches(comparison, decision, pair, names)
    return {**pair, "prompt": prompt, "comparison": comparison, "code_signals": signals, "decision": decision,
            "customers": customers if decision["horizontal"] else "", "flags": "; ".join(flags),
            "matches": matches, "vertical_items": vertical_items}


def check_matches(comparison, decision, pair, names):
    """The items the AI says meet, checked in code against each activity's own items. Only for
    what the decision kept: matching items for a horizontal candidate, items for each vertical link that counts
    (a link disregarded by the reseller check keeps no items). Rejected items go to the audit trail only."""
    items_a, items_b = rules.activity_items(pair["a"]), rules.activity_items(pair["b"])
    rejected = []
    matches = {"a": [], "b": [], "rejected": rejected}
    if decision["horizontal"]:
        matches["a"], bad_a = rules.check_items(comparison.get("matching_items_a"), items_a, names)
        matches["b"], bad_b = rules.check_items(comparison.get("matching_items_b"), items_b, names)
        rejected += bad_a + bad_b
    vertical_items = []
    for v in comparison.get("vertical_items") or []:
        if v.get("link") not in decision["vertical_links"] or any(x["link"] == v["link"] for x in vertical_items):
            continue
        a, bad_a = rules.check_items(v.get("items_a"), items_a, names)
        b, bad_b = rules.check_items(v.get("items_b"), items_b, names)
        rejected += bad_a + bad_b
        vertical_items.append({"link": v["link"], "a": a, "b": b})
    return matches, vertical_items


# =============================================================== presentation helpers (names re-attached in code)
def pair_id(r):
    """The pair's fixed ID: the two activity IDs, so overrides survive re-ordering and partial updates. Results
    without IDs (e.g. from an older saved audit log) fall back to the position labels."""
    return f"{r['a'].get('aid') or r['label_a']}×{r['b'].get('aid') or r['label_b']}"


def describe_link(link, target, portco):
    """Which party supplies the other, with the names re-attached (A is always the target, B the portco)."""
    return {
        "A could be an input for B": f"{target} → {portco} (input)",
        "B could be an input for A": f"{portco} → {target} (input)",
        "A could be resold by B": f"{portco} could resell {target}'s product",
        "B could be resold by A": f"{target} could resell {portco}'s product",
    }.get(link, link)


def assessment_parts(r):
    """The labels of a kept pair that the lawyer can dismiss one by one: "horizontal" and each vertical link. A pair
    with both a horizontal and a vertical label, or two vertical links, has several parts."""
    d = r["decision"]
    if d["status"] != "candidate":
        return []
    return (["horizontal"] if d["horizontal"] else []) + list(d["vertical_links"])


def dismissed_parts(r, overrides):
    """The parts of a pair the user dismissed. 'dismiss' (the single box of a pair with one label) dismisses all
    parts."""
    o = overrides.get(pair_id(r), {})
    parts = assessment_parts(r)
    if o.get("dismiss"):
        return parts
    chosen = o.get("dismissed_parts") or {}
    return [p for p in parts if chosen.get(p)]


def effective_status(r, overrides):
    """The code's decision, changed only by the user (never by the AI): 'dismissed' or 'added back'. A pair with
    several labels counts as dismissed only when every label is; with some labels dismissed it stays in the table,
    with those labels struck through."""
    o = overrides.get(pair_id(r), {})
    status = r["decision"]["status"]
    if status == "screened out" and o.get("add_back"):
        return "added back by user"
    if status != "screened out" and o.get("dismiss"):
        return "dismissed by user"
    parts = assessment_parts(r)
    if parts and set(dismissed_parts(r, overrides)) == set(parts):
        return "dismissed by user"
    return status