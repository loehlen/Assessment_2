"""
steps/step5_summary.py - step ⑤ Summary and the Word document: the result of the screen (what the lawyer kept in
steps ③ and ④, strongest first), the content of the Word document (written by logic/export.py), and the "Save
progress" copy that the app can open again.
"""
import re
from collections import Counter

import streamlit as st

from logic import comparison as cmp
from logic import export
from logic import precedents as prec
from logic import rules

from ui.common import capital, esc, he, long_date, now_local, plural, poss, run_summary, ss
from ui.labels import outcome_chip, OUTCOME_CLASS
from ui.decisions import added_case, corpus_paragraphs, decision_years
from ui.activity_display import (CUSTOMER_TEXT, display_order, display_title, profile_of, relationship_rows,
                                 research_of, short_name, stage_of)
from steps.step3_assessment import (assign_commission, BOTH_DIRECTIONS, current_overrides, INPUT_LINKS,
                                    is_less_likely, is_own_use, kept, label_parts, less_likely_part, less_tag,
                                    name_ab, part_detail, portco_sentence, row_status, set_aside_text, view_of,
                                    weak_horizontal, word_list)
from steps.step4_search import prec_plan, row_failed, row_view, search_gap, stale_units
from steps.step4_results import (_rank, _side_text, commission_parts, commission_sentences, ctx_entries, exact_match,
                                 label_of_heading, level_word, market_list, market_overview, market_overview_cited,
                                 market_overview_plain, SETTLED, uncovered_items)
from ui.saved_screens import audit_json


# The output is a fully usable work product for the lawyer: the main part holds only the lawyer's final choices (no "by
# you" tags, no struck labels, nothing dismissed); everything that points to the tool goes into an Annex that can be
# ignored or deleted. Step ⑤ shows the summary of the same model, so that the screen and the document always say the
# same. Built in code from the rows; no AI call.
def parse_commission(text):
    """The Commission's view as the lawyer edited it ("Edit"), back into [(label, bullets, outcome)]: the heading
    lines written by commission_plain ("Confirmed · Horizontal Label:") keep the result
    and the relationship, so an edited row still shows its result in the summary and the Word document."""
    groups = []
    for line in (x.strip() for x in text.split("\n")):
        if not line:
            continue
        # "One side defined · Vertical Label, A → B:"; as written before: "Confirmed · Commission (horizontal):" or
        # "Confirmed · Both Products in the Commission's Decisions (for the label horizontal):"
        m = re.fullmatch(r"(?:(.+?)\s*·\s*)?(?:Commission|[^·:()]*Commission's Decisions)(?:\s*\((?:for the label )?"
                         r"(.+)\))?\s*:", line)
        if m:
            outcome = m.group(1) if m.group(1) in OUTCOME_CLASS else ""
            groups.append([m.group(2) or "", [], outcome])
            continue
        m = re.fullmatch(r"(?:(.+?)\s*·\s*)?(Horizontal Label|Vertical Labels?, .+|This Row)\s*:", line)
        if m:
            outcome = m.group(1) if m.group(1) in OUTCOME_CLASS else ""
            groups.append([label_of_heading(m.group(2)), [], outcome])
            continue
        if not groups:
            groups.append(["", [], ""])
        groups[-1][1].append(line.lstrip("-•").strip())
    return [(label, bullets, outcome) for label, bullets, outcome in groups if bullets or outcome]


VIEW_WORD = {"Likely": "likely", "Unlikely": "unlikely", "Ask the company": "open point"}


def label_view(pid, p):
    """The lawyer's view of one label, as a word for the output ('' for "to check")."""
    return VIEW_WORD.get(view_of(pid, p["part"], p["off"]), "")


def row_record(r, target, portco, step4):
    """One row of a company's table, as the output shows it, or None if nothing of it is left (all dismissed)."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    status = row_status(r)
    parts = [p for p in label_parts(r, target, portco) if not p["off"]]
    c = r["comparison"]
    labels = []
    edited = (o.get("text_assessment") or "").strip()
    for p in parts:
        lab = {"kind": p["kind"], "view": label_view(pid, p), "basis": "", "regard": [], "lines": [], "up": p["up"],
               "part": p["part"],                   # the link (input or resale), for the summary's wording
               "less": less_likely_part(r, p),      # the summary counts it on one line
               "tag_less": less_tag(r, p)}          # a vertical label's basis says "less likely" (as a horizontal's)
        if not edited:
            if p["kind"] == "h" and p["origin"] == "tool":
                kind = "same product" if c.get("product_relation") == "same product" else "similar product"
                sa, sb = stage_of(r["a"]).lower(), stage_of(r["b"]).lower()
                level = f"same level ({sa})" if sa == sb else f"different levels ({sa} v {sb})"
                cust = CUSTOMER_TEXT.get(r.get("customers") or "", "")
                less = "less likely" if weak_horizontal(r) else ""
                lab["basis"] = " · ".join(x for x in (kind, level, cust, less) if x)
                m = r.get("matches") or {}
                if m.get("a") or m.get("b"):
                    lab["regard"] = [(target, word_list(m.get("a")) or "–"), (portco, word_list(m.get("b")) or "–")]
            else:
                detail = part_detail(p, r, target, portco, html_out=False)
                lab["basis"] = detail[0] if detail else ""
                lab["lines"] = detail[1:]
        labels.append(lab)
    if not labels:
        if status == "added back by user" or (r["decision"]["status"] == "unclear" and not o.get("dismiss")):
            v = VIEW_WORD.get(view_of(pid, "row", bool(o.get("dismiss"))), "")
            # the label itself says "To be checked"; no second line repeating it
            labels.append({"kind": "q", "view": v, "basis": "", "regard": [], "lines": []})
        else:
            return None
    commission, pending = [], False
    if step4:
        ed = (o.get("text_commission") or "").strip()
        if ed:
            commission = parse_commission(ed)
        else:
            commission = commission_sentences(r, target, portco, html_out=False)
            if not commission:
                commission = commission_gap(r)
                pending = bool(commission)
            elif row_failed(r):            # part of the row's search failed: counted with the rows to look up again
                pending = True
    # in the document, two vertical labels in the same direction (input and resale) are one label with both lines
    all_labels = [dict(x) for x in labels]         # each label as it is, for the summary and the open points
    views = [lab["view"] for lab in labels if lab["view"]]
    merged, metas = [], []
    for p, lab in zip(parts, labels):
        same = next((k for k, m in enumerate(metas) if lab["kind"] == "v" and m["kind"] == "v" and m["up"] == p["up"]),
                    None)
        if same is None:
            merged.append(lab)
            metas.append({"kind": p["kind"], "up": p["up"]})
            continue
        prev = merged[same]
        prev["lines"] += [x for x in lab["lines"] if x not in prev["lines"]]
        prev["view"] = prev["view"] or lab["view"]
        prev["tag_less"] = prev.get("tag_less") and lab.get("tag_less")     # a resale link is never less likely
    for lab in merged:
        if lab["kind"] == "v" and lab.get("tag_less") and lab["basis"]:
            lab["basis"] += " · less likely"
    labels = merged + labels[len(parts):]          # the "To be checked" line of a row without labels stays
    metas = metas or [{"kind": "row"}]
    return {"pid": pid, "a": r["a"], "b": r["b"], "b_rec": activity_record(r["b"], portco), "labels": labels,
            "all_labels": all_labels,
            "edited": edited.split("\n") if edited else [],
            # the Commission's parts, each beside the label it belongs to (one list per label)
            "commission": commission, "commission_by_label": assign_commission(commission, metas, target),
            "views": views, "note": (o.get("note") or "").strip(), "pending": pending}


def commission_gap(r):
    """The Commission cell of a kept row whose search is missing, out of date or failed, so that the summary and the
    Word document say so instead of showing nothing (or, in the run right after a change, "no precedent")."""
    rec, view = row_view(r)
    if view is None:
        why = search_gap(r, rec)
    elif view.get("error"):
        why = f"The search failed ({view['error']})"
    else:
        return []
    return [("", [f"{why}: run “Update the market definitions” in step ④ before relying on this row."], "")]


def activity_record(a, company):
    return {"name": short_name(a), "stage": stage_of(a), "sources": list(a.get("source_numbers") or []),
            "items": [i for i in a.get("includes") or [] if i], "aid": a.get("aid"), "company": company}


# The summary (step ⑤ and page 1 of the Word document). In each column, the portfolio company's activities are listed
# under the target activity they meet, strongest first, each with a short line saying which products meet and what the
# Commission's decisions say about them (the full sentences are in step ④ and section 2 of the Word document). The
# order rests on the lawyer's view, then on the Commission's result; it says nothing the rows do not say.
VIEW_RANK = {"likely": 0, "": 1, "open point": 1, "unlikely": 2}
RESULT_RANK = {"Confirmed": 0, "Possible": 1, "Not excluded": 2, "No precedent": 3, "Not supported": 4,
               "Markets defined": 0, "One side defined": 1, "": 5}


# a vertical entry in words, read after the target activity above it: (upstream side, input?, resale?)
V_PHRASE = {("a", True, False): "Could supply", ("a", False, True): "Could be resold through",
            ("a", True, True): "Could supply, or be resold through,",
            ("b", True, False): "Could be supplied by", ("b", False, True): "Could resell the products of",
            ("b", True, True): "Could be supplied by, or resell the products of,"}
V_VERB = {(True, False): "could be an input for", (False, True): "could be resold through",
          (True, True): "could be an input for, or be resold through,"}


def summary_item(kind, up, names_, res, lab, r, rec, aidx, target, portco):
    """One label of a kept row, for the summary: (target activity, portfolio company's activity, their stages), its
    result and view, and what its short lines are made of."""
    a, b, la, lb = names_
    edited = bool(rec.get("edited"))
    return {"kind": kind, "up": up, "a": a, "b": b, "la": la, "lb": lb, "pair": (a, b), "res": res,
            "view": lab["view"], "less": bool(lab.get("less")), "aidx": aidx,
            "links": {lab["part"]} if kind == "v" and lab.get("part") else set(),
            "vitems": [] if edited else list(r.get("vertical_items") or []),
            "reasons": summary_reasons_h(r, rec, target, portco) if kind == "h" else []}


def summary_reasons_h(r, rec, target, portco):
    """The short lines under a horizontal entry: which products meet and what the decisions say about them. The same
    groups as horizontal_sentences (step ④), in fewer words; the products are named with their company."""
    o = ss.override_store.get(cmp.pair_id(r), {})
    if (o.get("text_commission") or "").strip():          # the lawyer's own wording of step ④
        return [capital(b) for label, bullets, _ in rec.get("commission") or []
                if not label or label.startswith("horizontal") for b in bullets]
    if rec.get("pending"):                                 # said once above the summary (pending_warning)
        return []
    parts = commission_parts(r, target, portco)
    if not parts or parts[1] is None or parts[1].get("error"):
        return []
    _, view, entries, _, _, verdict = parts

    def items(es, s):
        return word_list(list(dict.fromkeys(i for e in es if e.get(s) for i in e[s].get("items") or [])), 3)

    def lead(es=None):
        if es is None:                 # the products of the label (step ③)
            m = r.get("matches") or {}
            a, b = word_list(m.get("a"), 3), word_list(m.get("b"), 3)
        else:
            a, b = items(es, "a"), items(es, "b")
        text = " and ".join(x for x in (f"{poss(target)} {a}" if a else "", f"{poss(portco)} {b}" if b else "") if x)
        return f"{text}: " if text else ""

    def names(es, joiner=", "):
        return market_list(es, {}, False, joiner=joiner)
    if verdict and verdict.get("levels_differ"):
        return [f"{lead(entries)}different levels of trade, separate markets ({target}: "
                f"{_side_text(entries, view, 'a', {}, False)}; {portco}: {_side_text(entries, view, 'b', {}, False)})"]
    if verdict and verdict.get("different"):
        out = [f"{lead(entries)}separate markets ({target}: {_side_text(entries, view, 'a', {}, False)}; "
               f"{portco}: {_side_text(entries, view, 'b', {}, False)})"]
        u = uncovered_items(r, entries)
        return out + [f"{poss(w)} {word_list(u[s], 3)}: no precedent, to be checked"
                      for s, w in (("a", target), ("b", portco)) if u[s]]
    shared = [e for e in entries if e["a"] and e["b"]]
    cat = [e for e in shared if e.get("category")]
    shared = [e for e in shared if not e.get("category")]

    def conc(e):
        return e["market"].get("conclusion")
    both = [e for e in shared if _rank(e) == "specific" and conc(e) in SETTLED and exact_match(e)]
    near = [e for e in shared if _rank(e) == "specific" and conc(e) in SETTLED and not exact_match(e)]
    left = [e for e in shared if _rank(e) == "specific" and conc(e) == "left open"]
    unknown = [e for e in shared if _rank(e) == "specific" and conc(e) not in SETTLED + ("left open",)]
    possibly = [e for e in shared if _rank(e) == "possibly"]
    general = [e for e in shared if _rank(e) == "general"]
    out = []
    if both:
        partly = any(conc(e) == prec.PARTLY for e in both)
        out.append(f"{lead(both)}both fall in {names(both)}" + ("; a further question was left open" if partly else ""))
    if near:
        out.append(f"{lead(near)}both may fall in {names(near)}")
    if left:
        out.append(f"{lead(left)}both fall in {names(left)}, whose definition was left open")
    if possibly:
        out.append(f"{lead(possibly)}both may fall in {names(possibly, ' or ')}, depending on the product format")
    for e in cat:
        out.append(f"{lead([e])}both fall within {names([e])}, which the Commission divided into separate markets")
    if unknown:
        out.append(f"{lead(unknown)}both fall in {names(unknown)}: no market definition in the paragraphs found")
    if general:
        out.append(f"{lead(general)}both fall in {names(general)} only through a general term, to be checked")
    if out:
        return out
    # no market of both: a side without a market at its own level of trade says so (e.g. a shop: the retail of the
    # products it sells)
    bare = [s for s in ("a", "b") if not any(e.get(s) for e in entries) and ctx_entries(view, s)]
    if bare:
        who = " and ".join(f"{poss(target if s == 'a' else portco)} side ({level_word(r[s])})" for s in bare)
        return [f"{lead()}no decision in the database places both in one market; {who}: no precedent at that level "
                "of trade"]
    return [f"{lead()}no decision in the database places both in one market"]


def _interleave(lists):
    """Items of several lists in turn (the first of each, then the second of each, …), without repeats: a joined
    entry names the products of every pair it stands for."""
    out = []
    for k in range(max((len(x) for x in lists), default=0)):
        for x in lists:
            if k < len(x) and x[k] not in out:
                out.append(x[k])
    return out


def summary_reasons_v(xs, target, portco):
    """The short line under a vertical entry: the link in words, with the products it names (the sentence of step
    ③). xs: the labels the entry stands for (one per target activity of a joined group)."""
    up = xs[0]["up"]
    sup_s, cus_s = ("a", "b") if up == "a" else ("b", "a")
    links = set().union(*(x["links"] for x in xs))
    per = [[v for v in x["vitems"] if v.get("link") in links] for x in xs]
    if not any(per):                   # a label the lawyer added or reworded: no line
        return []
    sup = _interleave([list(dict.fromkeys(i for v in vs for i in v.get(sup_s) or [])) for vs in per])
    cus = _interleave([list(dict.fromkeys(i for v in vs for i in v.get(cus_s) or [])) for vs in per])
    sup_name, cus_name = (target, portco) if up == "a" else (portco, target)
    inp, res = any(lk in INPUT_LINKS for lk in links), any(lk not in INPUT_LINKS for lk in links)
    sup_act = xs[0]["a"] if up == "a" else xs[0]["b"]
    cus_act = xs[0]["b"] if up == "a" else xs[0]["a"]
    return [f"{poss(sup_name)} {word_list(sup, 3) or sup_act.lower()} {V_VERB[(inp or not res, res)]} "
            f"{poss(cus_name)} {word_list(cus, 3) or cus_act.lower()}"]


def summary_groups(items, target, portco):
    """One column of the summary for one portfolio company: [{"targets": [target activities], "entries": [{"text",
    "res", "view", "reasons"}]}]. Each target activity is a group with the portfolio company's activities it meets,
    strongest first. Target activities whose entries are the same in every respect the summary shows or rests on (kind,
    direction, link, both stages, the portfolio activity, the Commission's result, the lawyer's view) are one group, so
    that a pair is never shown with a result it does not have. Groups are in the target's order; a group with a
    stronger entry comes first."""
    def phrase(x):
        if x["kind"] == "h":
            return ""
        inp = any(lk in INPUT_LINKS for lk in x["links"]) or not x["links"]
        res = any(lk not in INPUT_LINKS for lk in x["links"])
        return V_PHRASE[(x["up"], inp, res)]

    def sig(x):
        return x["kind"], x["up"], phrase(x), x["la"], x["lb"], x["b"], x["res"], x["view"]

    def rank(x):
        return VIEW_RANK.get(x["view"], 1), RESULT_RANK.get(x["res"], 5)
    by_target = {}
    for x in items:
        by_target.setdefault((x["aidx"], x["a"]), []).append(x)
    joined = {}                        # the set of entries -> the target activities that have exactly it
    for (aidx, a), xs in sorted(by_target.items()):
        joined.setdefault(tuple(sorted(Counter(sig(x) for x in xs).items())), []).append((aidx, a, xs))
    groups = []
    for members in joined.values():
        entries = []
        for s in dict.fromkeys(sig(x) for x in members[0][2]):
            xs = [x for _, _, m in members for x in m if sig(x) == s]
            x0 = xs[0]
            reasons = (list(dict.fromkeys(r_ for x in xs for r_ in x["reasons"])) if x0["kind"] == "h"
                       else summary_reasons_v(xs, target, portco))
            entries.append({"text": f"{phrase(x0)} {x0['b']}".strip(), "res": x0["res"], "view": x0["view"],
                            "reasons": reasons, "rank": rank(x0)})
        entries.sort(key=lambda e: e["rank"])            # stable: ties keep the order of the rows
        groups.append({"targets": [a for _, a, _ in members], "entries": entries,
                       "rank": (entries[0]["rank"] if entries else (9, 9), members[0][0])})
    groups.sort(key=lambda g: g["rank"])
    for g in groups:
        g.pop("rank")
        for e in g["entries"]:
            e.pop("rank")
    return groups


def count_line(items, kind):
    """'4 potential horizontal overlaps (2 Possible, 1 No precedent, 1 Not supported)'."""
    if not items:
        return "no potential horizontal overlap" if kind == "h" else "no potential vertical relationship"
    n = Counter(x["res"] for x in items)
    by = ", ".join(f"{n[r_]} {r_}" for r_ in sorted(n, key=lambda r_: RESULT_RANK.get(r_, 5)) if r_)
    word = "potential horizontal overlap" if kind == "h" else "potential vertical relationship"
    return plural(len(items), word) + (f" ({by})" if by else "")


def overview_lines(target, summary, rels):
    """The result in two or three sentences, above the summary table: which portfolio companies have what."""
    names = [s["portco"] for s in summary]
    n = len(names)
    with_h = [s["portco"] for s in summary if s["count_h"] or s["less_h"]]
    with_v = [s["portco"] for s in summary if s["count_v"] or s["less_v"]]
    none = [p for p in names if p not in with_h and p not in with_v]

    def who(ps, first):
        if n == 1:
            return ps[0]
        return (f"{len(ps)} of {n} portfolio companies" if first else str(len(ps))) + f" ({', '.join(ps)})"
    out = []
    if with_h:
        out.append(f"Potential horizontal overlaps with {who(with_h, True)}.")
    if with_v:
        out.append(f"Potential vertical relationships with {who(with_v, not with_h)}.")
    if none:
        out.append(f"None found with {', '.join(none)}." if with_h or with_v else
                   ("None found." if n == 1 else f"None found with any of the {n} portfolio companies."))
    return {"text": " ".join(out),
            "relationships": [f"{target} and {rel['portco']}: the public sources of each name the other (Annex C)."
                              for rel in rels]}


def report_model():
    """Everything the summary and the Word document show. Pure code on the session."""
    current_overrides()
    target = ss.companies[0]["name"]
    portcos = [c["name"] for c in ss.companies[1:]]
    step4 = bool(ss.get("precedents"))
    if step4:
        # which searches are out of date NOW: the sidebar builds this model before the page does, so the value of
        # the last run would be one change behind (a row added back would read "no precedent")
        ss.prec_stale = stale_units(prec_plan()[1])
    saved_step = ss.get("step")
    ss.step = 4 if step4 else 3        # the Commission's view is assembled as in step ④
    try:
        sections, summary, annex_b, open_points, rels, cited = [], [], [], [], [], {}
        used_sources = {c["name"]: set() for c in ss.companies}
        for p in portcos:
            pairs = [r for r in ss.results if r["portco"] == p]
            status = {cmp.pair_id(r): row_status(r) for r in pairs}
            blocks, own, less, hor, ver = [], [], [], [], []
            t_acts = [ss.confirmed[target][k] for k in display_order(ss.confirmed[target])]
            kept_rows = [r for r in pairs if kept(status[cmp.pair_id(r)])]
            rel_ids, rel = relationship_rows(target, p, kept_rows)
            if rel:
                rels.append({"portco": p, "passages": rel})
            for aidx, ta in enumerate(t_acts):
                rows_main, rows_own, rows_less = [], [], []
                for r in [x for x in pairs if (x["a"].get("aid") or x["label_a"]) == ta.get("aid")]:
                    s_ = status[cmp.pair_id(r)]
                    rec = row_record(r, target, p, step4) if kept(s_) else None
                    if rec is None:
                        o = ss.override_store.get(cmp.pair_id(r), {})
                        reasons = [name_ab(x, target, p) for x in (r["comparison"].get("product_reason"),
                                                                   r["comparison"].get("vertical_reason")) if x]
                        if s_ == "dismissed by user":
                            reason = o.get("note") or "Dismissed in the review."
                        else:       # the AI's reasons and, as in "Why?", the links the app's own checks set aside
                            reason = " ".join(reasons + [set_aside_text(r, link, why, target, p, md=False)
                                                         for link, why in r["decision"].get("disregarded") or []])
                            reason = reason or "No reason given."

                        annex_b.append({"portco": p, "pair": f"{short_name(r['a'])} × {short_name(r['b'])}",
                                        "reason": reason})
                        continue
                    rec["relationship"] = cmp.pair_id(r) in rel_ids and bool(rel)
                    used_sources[target].update(rec["a"].get("source_numbers") or [])
                    used_sources[p].update(rec["b"].get("source_numbers") or [])
                    (rows_own if is_own_use(r) else rows_less if is_less_likely(r) else rows_main).append(rec)
                    for label, bullets, outcome in rec["commission"]:
                        for b in bullets:
                            for m in re.finditer(r"\[(M\.\d+|Notice) \((\d+)\)", b):
                                cited.setdefault(m.group(1), set()).add(int(m.group(2)))
                    if not is_own_use(r):
                        names_ = (short_name(r["a"]), short_name(r["b"]), stage_of(r["a"]), stage_of(r["b"]))
                        outs = {}       # per relationship and direction; a label "" covers all
                        for lab_, _, o_ in rec["commission"]:
                            if lab_.startswith("horizontal"):
                                keys = ["h"]
                            elif lab_ == BOTH_DIRECTIONS:
                                keys = ["va", "vb"]
                            elif lab_.startswith("vertical"):
                                keys = ["va" if lab_.startswith(f"vertical, {target} →") else "vb"]
                            else:
                                keys = ["h", "va", "vb"]
                            for k_ in keys:
                                outs.setdefault(k_, o_)
                        for lab in rec["all_labels"]:
                            if lab["kind"] == "h":
                                hor.append(summary_item("h", None, names_, outs.get("h", ""), lab, r, rec, aidx,
                                                        target, p))
                            elif lab["kind"] == "v":           # up "a": the target supplies
                                entry = summary_item("v", lab["up"], names_,
                                                     outs.get("va" if lab["up"] == "a" else "vb", ""), lab,
                                                     r, rec, aidx, target, p)
                                same = [x for x in ver if x["pair"] == entry["pair"] and x["up"] == entry["up"]
                                        and x["res"] == entry["res"]]
                                if not same:        # two links in one direction (input and resale): one entry
                                    ver.append(entry)
                                else:               # the lawyer's view of either; less likely only if both are
                                    same[0]["view"] = same[0]["view"] or entry["view"]
                                    same[0]["less"] = same[0]["less"] and entry["less"]
                                    same[0]["links"] |= entry["links"]
                    for lab in rec["all_labels"]:
                        if lab["view"] == "open point":
                            open_points.append({"portco": p, "pair": f"{short_name(r['a'])} × {short_name(r['b'])}",
                                                "text": rec["note"] or "To be clarified with the company."})
                            break
                if rows_main:
                    blocks.append({"target": activity_record(ta, target), "rows": rows_main})
                if rows_less:
                    less.append({"target": activity_record(ta, target), "rows": rows_less})
                if rows_own:
                    own.append({"target": activity_record(ta, target), "rows": rows_own})
            sentence = portco_sentence(target, p, pairs, status, own_where="in the table “Own Use” below",
                                       less_where="in the table “Less Likely” below")
            sections.append({"portco": p, "sentence": re.sub(r"\\(.)", r"\1", sentence),
                             "blocks": blocks, "own": own, "less": less,
                             # a relationship with no kept row to show it in: one line under the sentence
                             "relationship": bool(rel) and not rel_ids})
            main_h, main_v = [x for x in hor if not x["less"]], [x for x in ver if not x["less"]]
            summary.append({"portco": p, "horizontal": summary_groups(main_h, target, p),
                            "vertical": summary_groups(main_v, target, p),
                            "less_h": sum(1 for x in hor if x["less"]), "less_v": sum(1 for x in ver if x["less"]),
                            "count_h": len(main_h), "count_v": len(main_v),
                            # the company's line in the first column: what it has, in a sentence
                            "result": capital(f"{count_line(main_h, 'h')} and {count_line(main_v, 'v')}.")
                            if main_h or main_v else "",
                            "compared": len(dict.fromkeys(r["label_b"] for r in pairs)), "pairs": len(pairs),
                            "relationship": bool(rel), "n": portcos.index(p) + 1})
        sources = []
        for c in ss.companies:
            found = research_of(c["name"])         # the research the compared activities' source numbers refer to
            idx = {x["n"]: x for x in found.get("sources") or [] if not x.get("dead")}
            nums = sorted(n for n in used_sources[c["name"]] if n in idx)
            if nums:
                sources.append({"company": c["name"], "date": long_date(found.get("date", "")),
                                "items": [(n, display_title(idx[n]), idx[n].get("url", "")) for n in nums]})
        not_compared = []
        for c in ss.companies:
            for a in ss.confirmed.get(c["name"], []):
                if a.get("excluded"):
                    if a.get("own_use"):
                        items = [i.replace(" " + rules.OWN_USE_MARK, "") for i in a.get("includes") or [] if i]
                        not_compared.append(f"{c['name']}: own use ({'; '.join(items)}): production for the group's "
                                            "own use, not offered on the market")
                        continue
                    not_compared.append(f"{c['name']}: {short_name(a)} (excluded as not relevant to this deal: "
                                        f"{a.get('exclusion_reason', '')})")
                elif rules.is_gap(a):
                    not_compared.append(f"{c['name']}: {rules.gap_name(a)} (named in the sources, but what it "
                                        "offers is not stated)")
            # the names moved out of the activity list in step ① (shown in step ② as "Also named in the sources")
            ext = ((ss.mapped.get(c["name"]) or {}).get("extraction") or {})
            for n in ext.get("named_without_activity") or []:
                label = re.sub(r"\s*\(([^()]*); products not stated\)$", r" (\1)", n)
                not_compared.append(f"{c['name']}: {label}: named in the sources, but what it offers is not stated")
        markets = []
        if step4:                       # the market table of step ④; its paragraphs are the ones cited
            ov = market_overview()
            if ov:
                markets = market_overview_plain(ov)
                for case, nums in market_overview_cited(ov).items():
                    cited.setdefault(case, set()).update(nums)
        cases = sorted(c for c in cited if c != "Notice")
        decisions = []
        for case in cases + (["Notice"] if "Notice" in cited else []):
            p0 = next((x for pid, x in corpus_paragraphs().items() if pid.startswith(case + "-")), {})
            decisions.append({"case": case, "title": p0.get("title", ""), "date": long_date(p0.get("date")),
                              "paras": sorted(cited[case], key=lambda x: (str(type(x)), x)),
                              "added": added_case(case)})
        years = decision_years(cases)
        today = now_local()
        pending = sum(1 for sec in sections for b in sec["blocks"] + sec["less"] + sec["own"] for x in b["rows"]
                      if x["pending"])
        return {"target": target, "portcos": portcos, "date": f"{today.day} {today:%B %Y}", "pending": pending,
                "overview": overview_lines(target, summary, rels),
                "step4": step4, "years": years, "summary": summary, "sections": sections, "markets": markets,
                "open_points": open_points, "sources": sources, "decisions": decisions,
                "annex": {"run_summary": run_summary().replace("Run summary: ", ""), "pairs": annex_b,
                          "relationships": rels, "not_compared": not_compared}}
    finally:
        ss.step = saved_step


# The same summary as page 1 of the Word document (one bullet per relationship, the Commission's result and the lawyer's
# view), the open points, and the download. Built in code from the rows, live; no AI call.
def summary_html(model):
    """The summary table of step ⑤ (the same model as page 1 of the Word document)."""
    def cell(groups, less=""):
        if not groups and not less:
            return "<span class='sub2'>None found</span>"
        out = ""
        for k, g in enumerate(groups):
            lis = "".join(f"<li>{he(e['text'])} {outcome_chip(e['res']) if e['res'] else ''}"
                          + (f"<i class='sub2'>{he(e['view'])}</i>" if e["view"] else "")
                          + "".join(f"<div class='swrt'>{he(x)}</div>" for x in e["reasons"]) + "</li>"
                          for e in g["entries"])
            out += (f"<div class='sgrp{' next' if k else ''}'>{he('; '.join(g['targets']))}</div>"
                    f"<ul class='sumul'>{lis}</ul>")
        return out + (f"<div class='sub2 sless'>{he(less)}</div>" if less else "")

    def company(s):
        rel = ("<div class='srel'><span class='lab lab-q'>Existing relationship</span></div>"
               if s["relationship"] else "")
        result = f"{s['result']} " if s["result"] else ""
        compared = plural(s["compared"], "activity", "activities")
        return f"<td><b>{he(s['portco'])}</b><div class='scnt'>{he(result)}{compared} compared.</div>{rel}</td>"
    rows = ""
    for s in model["summary"]:
        less_h = export.less_line("h", s["less_h"], "step ③")
        less_v = export.less_line("v", s["less_v"], "step ③")
        if not (s["horizontal"] or s["vertical"] or less_h or less_v):
            rows += (f"<tr>{company(s)}<td colspan='2'><span class='sub2'>None found: "
                     f"{plural(s['pairs'], 'pair')} compared, each with the reason in Annex B of the Word "
                     "document.</span></td></tr>")
            continue
        rows += f"<tr>{company(s)}<td>{cell(s['horizontal'], less_h)}</td><td>{cell(s['vertical'], less_v)}</td></tr>"
    return ("<table class='sumt'><thead><tr><th style='width:20%'>Portfolio Company</th><th style='width:39%'>"
            "<span class='lab lab-h'>Potential horizontal overlaps</span></th><th style='width:41%'><span class='lab "
            "lab-v'>Potential vertical relationships</span></th></tr></thead>"
            f"<tbody>{rows}</tbody></table>")


def overview_html(model):
    """The result above the summary table, in a sand box."""
    ov = model.get("overview") or {}
    rels = "".join(f"<div><span class='lab lab-q'>Existing relationship</span> {he(x)}</div>"
                   for x in ov.get("relationships") or [])
    return (f"<div class='sres'><div class='sres-t'>Result</div><div>{he(ov.get('text', ''))}</div>{rels}</div>"
            if ov.get("text") or rels else "")


def pending_warning(model, sidebar=False):
    """Rows whose Commission market definitions are missing, out of date or failed: the summary and the Word document
    say so in those rows; this says it once above them (and, shorter, above the Word button in the sidebar)."""
    n = model.get("pending")
    if not n:
        return
    if sidebar:
        st.caption(f"⚠ {plural(n, 'row')} without up-to-date market definitions: see step ④.")
    else:
        st.warning(f"{plural(n, 'row has', 'rows have')} no up-to-date Commission market definitions (changed since the "
                   "search, not looked up yet, or the search failed). Run “Update the market definitions” in step ④ "
                   "first; otherwise the summary and the Word document say so in those rows.")


def nothing_to_look_up():
    """Step ③ is done and no row is kept: step ④ has nothing to search, so the summary and the Word document are
    made without it (the cleanest result, no overlap at all, can be exported too)."""
    if ss.get("results") is None or ss.get("precedents"):
        return False
    current_overrides()
    return not prec_plan()[0]


def summary_ready():
    return ss.get("results") is not None and (bool(ss.get("precedents")) or nothing_to_look_up())


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def activities_model():
    """What a progress copy saved in step ②, before the comparison, shows: each company with its profile and its
    activities as they stand now (pure code on the session)."""
    today = now_local()
    companies = []
    for c in ss.companies:
        acts = (ss.get("acts") or {}).get(c["name"]) or []
        companies.append({"name": c["name"], "role": c.get("role", "portco"), "profile": profile_of(c["name"]) or "",
                          "activities": [{"name": short_name(a), "stage": stage_of(a),
                                          "includes": [str(x) for x in a.get("includes") or []],
                                          "customers": ", ".join(a.get("direct_customers") or []),
                                          "excluded": (a.get("exclusion_reason") or "") if a.get("excluded") else None}
                                         for a in (acts[k] for k in display_order(acts))]})
    return {"kind": "activities", "target": ss.companies[0]["name"], "portcos": [c["name"] for c in ss.companies[1:]],
            "date": f"{today.day} {today:%B %Y}", "companies": companies}


def progress_model():
    """The Word document of "Save progress", built in the script thread (the download runs on another thread, which
    cannot read the session), and the line saying how far the screen has got."""
    if ss.get("results") is None:
        return activities_model(), ""
    model = report_model()
    if not model["step4"] and not nothing_to_look_up():
        return model, "Saved in step ③: the Commission's market definitions have not been looked up yet."
    return model, ""


def progress_bytes(snap, model, note):
    """The progress copy: the Word document with the screen's data (the audit log) inside."""
    data = audit_json(snap).encode("utf-8")
    if model.get("kind") == "activities":
        return export.activities_docx(model, progress=data, note=note)
    return export.docx_bytes(model, progress=data, note=note)


def progress_name():
    name = rules._without_accents(rules._german_spelling(ss.companies[0]["name"]))
    return f"Overlap_progress_{re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')}_{now_local():%Y-%m-%d_%H%M}.docx"


def word_name():
    """'Overlap_overview_Mueller_Soehne_2026-10-23.docx' for "Müller & Söhne": letters with accents spelled out first
    (German spelling for umlauts), so that no letter of the name is lost."""
    name = rules._without_accents(rules._german_spelling(ss.companies[0]["name"]))
    return f"Overlap_overview_{re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')}_{now_local():%Y-%m-%d}.docx"


def stage_summary(ai):
    st.header("⑤ Summary")
    model = report_model()
    if model["step4"]:
        st.markdown("**The result of the screen:** what you kept in steps ③ and ④, strongest first. Steps ① to ④ "
                    "are generous on purpose, so that nothing is missed; every finding can be checked, changed or "
                    "dismissed there. The Word document holds the same summary, the full tables and the sources.")
    else:
        st.markdown("**The result of the screen:** no row is kept in step ③, so there were no market definitions to "
                    "look up. The Word document lists every pair compared, with the reason.")
    pending_warning(model)
    st.markdown(overview_html(model), unsafe_allow_html=True)
    st.caption(f"How to read: under each activity of {esc(model['target'])} (in bold), the portfolio company's "
               "activities it meets, each with the Commission's result and, once set, your view. Below it, in grey, "
               "which products meet and what the Commission's decisions say about them.")
    st.markdown(summary_html(model), unsafe_allow_html=True)
    st.caption("Activities joined by “;” each have the relationship shown, with the same result and view. Less "
               "likely labels are counted on one line; set a view on one in step ③ to list it here.")
    if model["open_points"]:
        st.markdown("##### Open Points")
        st.markdown("\n".join(f"- {esc(o['text'])} :gray[({esc(o['pair'])}, {esc(o['portco'])})]"
                               for o in model["open_points"]))
    st.download_button("Download the Word document", data=lambda: export.docx_bytes(model), type="primary",
                       file_name=word_name(), on_click="ignore", mime=DOCX_MIME)
    st.caption("The document to share, without the app's data. To continue this screen later, use “Save progress” in "
               "the sidebar: a Word document that the app can open again.")
