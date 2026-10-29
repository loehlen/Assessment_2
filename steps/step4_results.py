"""
steps/step4_results.py - step ④, the results: for each row, in which markets the Commission's decisions place the
products of both sides, with the result ("Confirmed", "Possible", "Not supported", "No precedent", ...) and the
Commission's sentences on hover; and the table of all markets found in the screen, each listed once.
"""
import re

from logic import comparison as cmp
from logic import precedents as prec

from ui.common import capital, h, he, he_lines, poss, ss
from ui.labels import outcome_chip
from ui.decisions import decision_label, decision_of, para_ref, para_refs
from ui.activity_display import short_name
from steps.step3_assessment import (active_labels, assign_commission, BOTH_DIRECTIONS, current_overrides, kept,
                                    listing, RESELLER_LEVELS, row_status, search_overrides, UPSTREAM_LINKS, word_list)
from steps.step4_search import prec_plan, row_view, search_gap


STATUS_RANK = {"specific": 0, "possibly": 1, "general": 2}


def _merge_group(old, g):
    if old is None:
        return dict(g, items=list(g["items"]), notes=dict(g.get("notes") or {}))
    old["items"] += [i for i in g["items"] if i not in old["items"]]
    old["notes"].update(g.get("notes") or {})
    old["status"] = min(old.get("status", "specific"), g.get("status", "specific"), key=STATUS_RANK.get)
    old["basis"] = "precedent" if "precedent" in (old["basis"], g["basis"]) else "analogy"
    return old


def row_markets(view):
    """The markets of one row, each once (the same market found by several searches is merged by its name), with
    each side's products: [{market, paragraphs, a, b}]."""
    out = {}
    for side in ("a", "b"):
        for g in view[side]:
            if g["market_id"] == "none" or not g["market"]:
                continue
            e = out.setdefault(prec._market_key(g["market"]["name"]), {"markets": [], "a": None, "b": None})
            if g["market"] not in e["markets"]:
                e["markets"].append(g["market"])
            e[side] = _merge_group(e[side], g)
    rows = []
    for e in out.values():
        best = _best(e["markets"])
        paras = {pid for m in e["markets"] for pid in m.get("product_paragraphs") or []}
        rows.append({"market": best, "paragraphs": paras, "a": e["a"], "b": e["b"]})
    return rows


CONCLUSION_TEXT = {"defined": "defined", "left open": "definition left open",
                   prec.PARTLY: "defined, a further question left open",
                   prec.NOT_STATED: "no market definition in the paragraphs found: check the decision"}
SETTLED = ("defined", prec.PARTLY)          # a boundary the Commission decided


def may_be_category(m):
    """A market without a conclusion in its paragraphs, which may be a category the Commission divided into other
    markets (see commission_parts). Not a market whose AI label failed the word-for-word check: that one was found as a
    market of its own, only its conclusion is unverified."""
    return m.get("conclusion") == prec.NOT_STATED and not m.get("label_not_verified")


def screen_records():
    """The stored searches of the rows kept NOW, each with the ids of the products those rows still use, so that a
    market is no longer listed as "used in this screen" after its rows were dismissed, or after its target activity
    was deleted or excluded in step ②."""
    current_overrides()
    units, _ = prec_plan()
    store = ss.get("precedents") or {}
    out = []
    for u in units:
        rec = store.get(u["target_aid"])
        if not rec:
            continue
        wanted = {(e["aid"], item) for e in u["activities"] for item in e["items"]}
        out.append((rec, {iid for iid, v in (rec.get("index") or {}).items() if (v[0], v[1]) in wanted}))
    return out


def used_markets():
    """Every market that at least one product of a kept row was placed in, merged across the searches by decision and
    name: {(case, key): {"markets": [...], "name": ...}}."""
    out = {}
    for rec, iids in screen_records():
        placements = rec.get("placements") or {}
        used = {mid for iid in iids for mid in prec.ids_of(placements.get(iid))}
        for mid, m in (rec.get("markets") or {}).items():
            prec.upgrade_market(m)
            if mid not in used:
                continue
            e = out.setdefault((decision_of(m), prec._market_key(m["name"])), {"markets": [], "name": m["name"]})
            e["markets"].append(m)
    return out


def _best(markets):
    for m in markets:
        prec.upgrade_market(m)
    return max(markets, key=lambda m: (m.get("conclusion") in prec.STATED,
                                       bool(m.get("decided_quote_found")) + bool(m.get("open_quote_found")),
                                       bool(m.get("scope_quote_found"))))


def mname(name):
    """A market's name as shown: "Market for e-bikes" and "e-bikes" are the same market, shown as "E-bikes"."""
    name = re.sub(r"^\s*(?:the\s+)?(?:relevant\s+)?(?:product\s+)?markets?\s+for\s+(?:the\s+)?", "", name or "",
                  flags=re.IGNORECASE)
    return capital(name.strip())


def is_reseller(act):
    """A shop or a wholesaler: its own market is the retail or wholesale of the products it sells. The Commission's
    markets found for its products are markets for making and supplying them, so they describe what it sells, not its
    own market."""
    return (act or {}).get("value_chain_level") in RESELLER_LEVELS


def level_word(act):
    return "wholesale" if (act or {}).get("value_chain_level") == "wholesale / distribution" else "retail"


def market_hover(m, paras, category=None):
    """A market name; hover shows its definition in short (the decisions are listed in the sidebar)."""
    case = decision_of(m)
    status = ("a category the Commission divided into separate markets (" + ", ".join(category) + ")"
              if category else CONCLUSION_TEXT.get(m.get("conclusion"), "defined"))
    box = f"<b>{h(mname(m['name']))}</b> · {h(status)}"
    box += f"<br><span style='opacity:.7'>{h(decision_label(case))}</span>" if case else ""
    prec.upgrade_market(m)
    for label, part in (("Decided", "decided"), ("Left open", "open"), ("Covers", "scope"),
                        ("Left open in another decision", "other_open")):
        q, pid = m.get(f"{part}_quote"), m.get(f"{part}_paragraph")
        if q and m.get(f"{part}_quote_found"):
            box += f"<br><i>{label}:</i> “{h(q)}” ({h(pid.replace('-', ' (') + ')')})"
    if not (m.get("decided_quote_found") or m.get("open_quote_found")) and m.get("summary"):
        # no passage of the Commission verified word for word: the AI's summary, marked as such
        box += f"<br><i>AI summary (not a quotation):</i> {h(m['summary'])}"
    box += "<br><span style='opacity:.7'>The decision is listed in the sidebar, under “Commission decisions”.</span>"
    return f"<span class='pref mk'>{h(mname(m['name']))}<span class='pbox' lang='en'>{box}</span></span>"


def _items_html(g, market_name=""):
    """One side's products in one market: a product that could be in several markets says where else
    it could be, e.g. “folding bikes (or City bicycles)”; a range or the activity's own name is marked “(general term)”."""
    if not g:
        return "–"
    notes = g.get("notes") or {}
    shown = g["items"]
    if g.get("status") != "general":
        shown = [i for i in g["items"] if "spans several markets" not in notes.get(i, "")] or g["items"]
    out = []
    here = prec._market_key(mname(market_name))
    for i in shown:
        note = notes.get(i, "")
        if "unclear which" in note:
            others = list(dict.fromkeys(mname(x.strip()) for x in note.replace(", unclear which", "").split(" or ")
                                        if x.strip() and prec._market_key(mname(x)) != here))
            out.append(f"{he(i)} <span class='or'>(or {he(' or '.join(others))})</span>" if others else he(i))
        elif note:
            out.append(f"{he(i)} <span class='or' title='{h(note)}'>(general term)</span>")
        else:
            out.append(he(i))
    return ", ".join(out) + (NOT_EXACT if g["basis"] != "precedent" else "")


NOT_EXACT_TIP = ("The Commission defined this market for the same product at another level of trade, or for a similar "
                 "product, not for this product as sold here. Whether its reasoning carries over is for the lawyer to "
                 "judge.")
NOT_EXACT = f" <span class='or' title='{h(NOT_EXACT_TIP)}'>(not an exact match)</span>"


def market_list(found, paras, html_out=True, sides=("a", "b"), joiner=", "):
    """Markets as a list, each marked "not an exact match" where the products of the given side(s) were placed in it
    although the decision defined it for the same product at another level of trade or for a similar product (basis
    "analogy" in the AI's answer); if every market of the list is, the mark is given once at the end."""
    def analog(e):
        return any(e.get(s) and e[s].get("basis") != "precedent" for s in sides)
    # one market, one name: two decisions naming the same market slightly differently ("Cocoa cake/powder" and
    # "Cocoa cake/powder (standard and non-standard products)") are listed once, as in the market table
    seen, unique = set(), []
    for e in found:
        k = overview_key(e["market"]["name"])
        if k not in seen:
            seen.add(k)
            unique.append(e)
    found = unique
    if html_out:
        names = [market_hover(e["market"], paras, e.get("category")) for e in found]
        mark = NOT_EXACT
    else:
        names = [mname(e["market"]["name"]) for e in found]
        mark = " (not an exact match)"
    flags = [analog(e) for e in found]
    if len(found) > 1 and all(flags):
        return joiner.join(names) + (NOT_EXACT.replace("(not an exact match)", "(none an exact match)") if html_out
                                     else " (none an exact match)")
    return joiner.join(n + (mark if f else "") for n, f in zip(names, flags))


def _side_text(entries, view, side, paras, html_out=True):
    """Where one side's products fall: the markets, else “no precedent for …” or “search failed”."""
    found = [e for e in entries if e[side]]
    if found:
        # a market reached only through a general term (e.g. the activity's name) is not a market of its products
        spec = [e for e in found if (e[side] or {}).get("status") != "general"]
        gen = [e for e in found if (e[side] or {}).get("status") == "general"]
        text = market_list(spec, paras, html_out, sides=(side,)) if spec else "no precedent"
        if gen:
            text += (", and only through a general term: " if spec else ", except through a general term: ") \
                + market_list(gen, paras, html_out, sides=(side,))
        return text
    groups = view.get(side) or []
    if any(g["market_id"] == "failed" for g in groups):
        return "search failed"
    return "no precedent"


def _rank(e):
    return max((e["a"] or {}).get("status", "specific"), (e["b"] or {}).get("status", "specific"), key=STATUS_RANK.get)


def exact_match(e):
    """Both sides' products placed in the market on the decision's own terms (basis "precedent")."""
    return all((e[s] or {}).get("basis") == "precedent" for s in ("a", "b") if e.get(s))


def horizontal_outcome(entries, verdict, rs=None):
    """What the Commission's view means for a horizontal row: Confirmed · Possible · Not excluded · Not supported ·
    No precedent. The strongest result of the row counts.
    A category the Commission divided into separate markets is not a market: both products in it is
    "Possible" (which segment is to be checked). A shop or wholesaler on either side: "No precedent" (its own market
    is the retail or wholesale of the products, which the decisions found do not define), unless a decision defines a
    market at its level (reseller_flags)."""
    if rs and (rs.get("a") or rs.get("b")):
        return "No precedent"
    if verdict and verdict.get("different"):
        return "Not supported"
    shared = [e for e in entries if e["a"] and e["b"] and not e.get("category")]
    in_category = [e for e in entries if e["a"] and e["b"] and e.get("category")]
    # "Confirmed" only where the decision defined the market for both products as sold (an exact match on both
    # sides); a market defined for the same product at another level of trade, or for a similar product, is at most
    # "Possible": whether the Commission's reasoning carries over is for the lawyer
    if any(_rank(e) == "specific" and exact_match(e) and e["market"].get("conclusion") in SETTLED for e in shared):
        return "Confirmed"
    if any(_rank(e) != "specific" or not exact_match(e) for e in shared) or in_category:
        return "Possible"
    if shared:
        return "Not excluded"
    return "No precedent"


def vertical_outcome(entries, up, rs=None):
    """The same for a vertical relationship; a shop's or wholesaler's side counts as no precedent unless a decision
    defines a market at its level (see reseller_flags)."""
    down = "b" if up == "a" else "a"
    sides = sum(1 for s in (up, down) if any(e[s] for e in entries) and not (rs and rs.get(s)))
    return {2: "Markets defined", 1: "One side defined", 0: "No precedent"}[sides]


PREFIX_SEP = ":\u2009 "         # plain text: ends the products a bullet concerns (the Word document sets them in italics)


def _prefix(es, html_out=True, limit=3):
    """The products a bullet concerns (each bullet says which products meet)."""
    items = list(dict.fromkeys(i for e in es for side in ("a", "b") for i in ((e[side] or {}).get("items") or [])))
    text = ", ".join(items[:limit]) + (" …" if len(items) > limit else "")
    if not text:
        return ""
    return f"<i>{he(capital(text))}:</i> " if html_out else f"{capital(text)}{PREFIX_SEP}"


def horizontal_sentences(entries, view, verdict, target, portco, paras, html_out=True, rs=None, acts=None):
    """The Commission's view of a horizontal row as bullets, in the terms of the Commission's decisions: one bullet
    per group of products, a category divided into separate markets named as
    such, and the level rule for shops and wholesalers. Market names only (hover: the Commission's sentence); the
    paragraphs are cited once, in the market table above the rows. The products a bullet concerns are named only
    when a row has several bullets."""
    T, P = (he(target), he(portco)) if html_out else (target, portco)

    def names(es, joiner=", "):
        return market_list(es, paras, html_out, joiner=joiner)
    if rs and (rs.get("a") or rs.get("b")):
        acts = acts or {}
        if rs.get("a") and rs.get("b"):
            la, lb = level_word(acts.get("a")), level_word(acts.get("b"))
            if la == lb:
                text = (f"no decision in the database covers the {la} of these products: to be assessed under the "
                        "Market Definition Notice")
            else:           # retail v wholesale are different levels of trade
                text = (f"different levels of trade ({T}: {la}; {P}: {lb}), often different markets; whether both "
                        f"compete for the same customers is to be checked; no decision in the database covers the {la} "
                        f"or {lb} of these products: to be assessed under the Market Definition Notice")
            sold = [e for e in entries if e["a"] or e["b"]]
            if sold:
                text += f"; the products sold fall in {names(sold)}"
            return [text]
        side = "a" if rs.get("a") else "b"
        who = T if side == "a" else P
        lw = level_word(acts.get(side))
        if html_out:        # the screen: one line, the full explanation on hover (the Word document has it in full)
            name = target if side == "a" else portco
            tip = (f"{poss(name)} side is {lw}: the decisions define the markets of the products, not the {lw} market. "
                   "Markets can differ at different levels of the supply chain (Market Definition Notice (14)); "
                   "whether both compete for the same customers is to be checked (Market Definition Notice (25)).")
            return [f"<span class='hov' title='{h(tip)}'>{poss(who)} side is {lw}: the decisions define product markets, not a {lw} market</span> "
                    f"{para_ref('Notice-14', {}, seen=False)} {para_ref('Notice-25', {}, seen=False)}"]
        n14, n25 = "(Market Definition Notice (14))", "(Market Definition Notice (25))"
        return [f"{poss(who)} side is {lw}: the decisions define the markets of the products, not the {lw} market. "
                f"Markets can differ at different levels of the supply chain {n14}; whether both compete for the same "
                f"customers is to be checked {n25}"]
    if verdict and verdict.get("different"):
        return [f"the products fall in separate markets ({T}: {_side_text(entries, view, 'a', paras, html_out)}; "
                f"{P}: {_side_text(entries, view, 'b', paras, html_out)}): no horizontal overlap at product-market "
                "level; check for a vertical relationship"]
    shared = [e for e in entries if e["a"] and e["b"]]
    conc = lambda e: e["market"].get("conclusion")   # noqa: E731
    cat = [e for e in shared if e.get("category")]
    shared = [e for e in shared if not e.get("category")]
    both = [e for e in shared if _rank(e) == "specific" and conc(e) in SETTLED and exact_match(e)]
    near = [e for e in shared if _rank(e) == "specific" and conc(e) in SETTLED and not exact_match(e)]
    partly = [e for e in both if conc(e) == prec.PARTLY]
    left = [e for e in shared if _rank(e) == "specific" and conc(e) == "left open"]
    unknown = [e for e in shared if _rank(e) == "specific" and conc(e) not in SETTLED + ("left open",)]
    possibly = [e for e in shared if _rank(e) == "possibly"]
    general = [e for e in shared if _rank(e) == "general"]
    out = []                          # (the products concerned, the sentence)
    if both:
        word = "market" if len(both) == 1 else "markets"
        out.append((both, f"both products fall in the {word} for {names(both)}: horizontal overlap at product-market "
                          "level" + ("; a further question about this market was left open" if partly else "")))
    if near:
        word = "market" if len(near) == 1 else "markets"
        out.append((near, f"both products fall in the {word} for {names(near)}: horizontal overlap at product-market "
                          "level possible, to be checked"))
    if left:
        out.append((left, f"{names(left)}; the exact definition was left open: a horizontal overlap cannot be "
                          "excluded"))
    if possibly:
        out.append((possibly, f"{names(possibly, ' or ')}, depending on the product format: horizontal overlap at "
                              "product-market level possible, to be checked"))
    for e in cat:
        out.append(([e], f"within {names([e])}, which the Commission divided into separate markets "
                         f"({', '.join(e['category'])}): which of them is to be checked"))
    if unknown:
        out.append((unknown, f"{names(unknown)}: no market definition in the paragraphs found: check the decision"))
    if general:
        out.append((general, f"both companies' products fall in {names(general)} only through a general term: which "
                             "products are in it is to be checked"))
    if len(out) > 1:
        out = [_prefix(es, html_out) + text for es, text in out]
    else:
        out = [text for _, text in out]
    if not out:
        if any(e["a"] or e["b"] for e in entries):
            out.append(f"no decision in the database places both companies' products in one market ({T}: "
                       f"{_side_text(entries, view, 'a', paras, html_out)}; {P}: "
                       f"{_side_text(entries, view, 'b', paras, html_out)}): to be assessed under the Market "
                       "Definition Notice")
        else:
            out.append("no decision in the database covers these products: to be assessed under the Market Definition "
                       "Notice")
    return out


def vertical_sentence(entries, view, up, target, portco, paras, html_out=True, rs=None, acts=None):
    """The market of each side's products as two bullets: the possible supplier first, then the possible customer
    (the roles come from step ③; the decisions define the markets, not the link). A shop's or wholesaler's side is the
    retail or wholesale of the products it sells (no precedent); the markets of those products are named as what it
    sells."""
    down = "b" if up == "a" else "a"
    who = {"a": he(target) if html_out else target, "b": he(portco) if html_out else portco}
    acts = acts or {}
    if not any(e["a"] or e["b"] for e in entries):
        return ["no decision in the database covers either side: to be assessed under the Market Definition Notice"]

    def ms(found, s):
        segs = {mname(e["market"]["name"]) for e in found if not e.get("category")}
        found = [e for e in found if not (e.get("category") and set(e["category"]) & segs)] or found
        return market_list(found, paras, html_out, sides=(s,))

    def side(s, level, role):
        found = [e for e in entries if e[s]]
        head = f"{who[s]} (possible {role})" if role else who[s]
        if rs and rs.get(s):
            text = f"{head}: no precedent for the {level_word(acts.get(s))} of these products"
            return text + (f"; the products {who[s]} sells fall in {ms(found, s)}" if found else "")
        if found:
            return f"{head}: {ms(found, s)}"
        return f"{head}: {_side_text(entries, view, s, paras, html_out)}"
    if up == "both":                   # links in both directions: each side's market once, without a role
        return [side("a", "", ""), side("b", "", "")]
    return [side(up, "upstream", "supplier"), side(down, "downstream", "customer")]


def commission_parts(r, target, portco):
    """Everything the Commission line of a row needs: (record, view, entries, horizontal shown, upstream sides, verdict)
    or None. A horizontal overlap the lawyer added uses the same stored search (no new search).
    An entry without a conclusion that cites the paragraph in which the same decision defines other markets of
    this search is a category the Commission divided into those markets (e["category"]: their names), not a market."""
    if not ss.get("precedents"):
        return None
    rec, view = row_view(r)
    if view is None or view.get("error"):
        return rec, view, [], False, [], None
    entries = sorted(row_markets(view), key=lambda e: (not (e["a"] and e["b"]), STATUS_RANK.get(_rank(e), 0),
                                                       e["market"].get("conclusion") not in SETTLED,
                                                       e["market"]["name"].lower()))
    settled = {}
    for m in ((rec or {}).get("markets") or {}).values():
        if m.get("conclusion") in SETTLED and m.get("decided_paragraph"):
            settled.setdefault(m["decided_paragraph"], set()).add(mname(m["name"]))
    for e in entries:
        m = e["market"]
        e["category"] = None
        if may_be_category(m):
            own = prec._market_key(mname(m["name"]))
            segs = sorted({n for pid in (m.get("product_paragraphs") or []) for n in settled.get(pid, set())
                           if prec._market_key(n) != own})
            e["category"] = segs or None
    h_on, ups = active_labels(r, target, portco)
    verdict = view.get("verdict")
    if h_on and verdict is None and rec:
        items = prec.row_items(r, search_overrides(), cmp.effective_status, cmp.dismissed_parts)
        if items:
            verdict = prec.horizontal_verdict(rec, r, items, view["a"], view["b"])
    return rec, view, entries, h_on, ups, verdict


# Above the rows: every market that a product of a kept row was placed in, once, with the products of each company in
# it, and the paragraph it rests on cited once. The rows below only name the markets. The same market found by several
# searches is one line, and so are names that differ only by "market for" or a qualifier in brackets (two decisions
# naming the same market slightly differently); a different name stays its own line (whether it is the same market is
# for the lawyer).
MARKET_GROUPS = (("both", "Products of Both Sides"), ("target", "Only the Target's Products"),
                 ("portco", "Only Portfolio Companies' Products"))
ITEMS_SHOWN = 6


def overview_key(name):
    return prec._market_key(re.sub(r"\s*\([^)]*\)", "", mname(name)))


def market_overview():
    """{"lines": [{"name", "market" (the best record), "decisions": [(case, record, status)], "sides": {company:
    {activity: group}}, "group"}], "none": {company: {activity: [items]}}, "failed": {...}, "paras": {...}} or None.
    Code only, from the stored searches of the rows kept now."""
    if not ss.get("precedents") or not ss.get("results"):
        return None
    current_overrides()
    target = ss.companies[0]["name"]
    lines, none, failed, paras, settled = {}, {}, {}, {}, {}
    for r in ss.results:
        if not kept(row_status(r)):
            continue
        rec, view = row_view(r)
        if not rec or view is None or view.get("error"):
            continue
        paras.update(rec.get("paragraphs") or {})
        for m in (rec.get("markets") or {}).values():
            if m.get("conclusion") in SETTLED and m.get("decided_paragraph"):
                settled.setdefault(m["decided_paragraph"], set()).add(mname(m["name"]))
        for side, company, act in (("a", target, r["a"]), ("b", r["portco"], r["b"])):
            aname = short_name(act)
            for g in view[side]:
                if g["market_id"] in ("none", "failed") or not g.get("market"):
                    store = failed if g["market_id"] == "failed" else none
                    lst = store.setdefault(company, {}).setdefault(aname, [])
                    lst += [i for i in g["items"] if i not in lst]
                    continue
                e = lines.setdefault(overview_key(g["market"]["name"]), {"markets": [], "sides": {}})
                if g["market"] not in e["markets"]:
                    e["markets"].append(g["market"])
                acts = e["sides"].setdefault(company, {})
                acts[aname] = _merge_group(acts.get(aname), g)
    placed = {(c, a, i) for e in lines.values() for c, acts in e["sides"].items() for a, g in acts.items()
              for i in g["items"]}
    for store in (none, failed):          # placed in a market by another search: not "no precedent"
        for c in list(store):
            for a in list(store[c]):
                store[c][a] = [i for i in store[c][a] if (c, a, i) not in placed]
                if not store[c][a]:
                    del store[c][a]
            if not store[c]:
                del store[c]
    out = []
    for e in lines.values():
        best = _best(e["markets"])
        by_case = {}
        for m in e["markets"]:
            by_case.setdefault(decision_of(m), []).append(m)
        # per decision, each different statement once (e.g. one decision that leaves the definition of a category open
        # in one paragraph and divides the category into separate markets in another)
        decisions = []
        for case in sorted(by_case, key=lambda c: (c == "", c)):
            found = {}
            for m in by_case[case]:
                status, pids = CONCLUSION_TEXT.get(m.get("conclusion"), "defined"), market_pids(m)
                if may_be_category(m):
                    own = overview_key(m["name"])
                    seg_pids = {pid for pid in m.get("product_paragraphs") or [] if pid in settled
                                and any(overview_key(n) != own for n in settled[pid])}
                    segs = sorted({n for pid in seg_pids for n in settled[pid] if overview_key(n) != own})
                    if segs:
                        status, pids = (f"category divided into separate markets ({', '.join(segs)})",
                                        prec._sorted_ids(seg_pids))
                found.setdefault(status, []).append((m, pids))
            if len(found) > 1:             # "no definition in the paragraphs found" adds nothing next to a statement
                found.pop(CONCLUSION_TEXT[prec.NOT_STATED], None)
            for status, ms in found.items():
                m = _best([x for x, _ in ms])
                pids = next(p_ for x, p_ in ms if x is m)
                decisions.append((case, m, status, pids))
        has_t = target in e["sides"]
        has_p = any(c != target for c in e["sides"])
        out.append({"name": mname(best["name"]), "market": best, "decisions": decisions, "sides": e["sides"],
                    "group": "both" if has_t and has_p else ("target" if has_t else "portco")})
    order = [k for k, _ in MARKET_GROUPS]
    out.sort(key=lambda x: (order.index(x["group"]), x["name"].lower()))
    return {"lines": out, "none": none, "failed": failed, "paras": paras, "target": target}


def market_pids(m, limit=2):
    """The paragraphs a market's conclusion rests on: the paragraphs of its decided and open passages, else its first
    product paragraphs."""
    pids = [x for x in (m.get("decided_paragraph"), m.get("open_paragraph")) if x]
    if not pids:
        pids = prec._sorted_ids({x for x in m.get("product_paragraphs") or [] if not x.startswith("Notice")})[:limit]
    return list(dict.fromkeys(pids))[:limit]


def _plain_refs(pids):
    return " ".join("[" + pid.rpartition("-")[0] + " (" + pid.rpartition("-")[2] + ")]" for pid in pids)


def _items_short(g, name):
    """A company's products in one market: the first few, the rest on hover."""
    shown = dict(g, items=g["items"][:ITEMS_SHOWN])
    text = _items_html(shown, name)
    rest = g["items"][ITEMS_SHOWN:]
    if rest:
        text += f" <span class='hov' title='{h(', '.join(rest))}'>and {len(rest)} more</span>"
    if g.get("status") == "possibly":
        text += " <span class='or'>possibly</span>"
    return text


def market_overview_html(ov):
    target = ov["target"]
    paras = ov["paras"]

    def companies(sides, name, own):
        out = []
        for c, acts in sides.items():
            if (c == target) != own:
                continue
            for a, g in acts.items():
                who = "" if own else f"<span class='mco'>{he(c)}</span> · "
                out.append(f"<div class='mrow'>{who}<span class='mact'>{he(a)}:</span> {_items_short(g, name)}</div>")
        return "".join(out) or "<span class='sub2'>–</span>"

    def plain_items(store, own):
        out = []
        for c, acts in store.items():
            if (c == target) != own:
                continue
            for a, items in acts.items():
                who = "" if own else f"<span class='mco'>{he(c)}</span> · "
                more = (f" <span class='hov' title='{h(', '.join(items[ITEMS_SHOWN:]))}'>and "
                        f"{len(items) - ITEMS_SHOWN} more</span>" if len(items) > ITEMS_SHOWN else "")
                out.append(f"<div class='mrow'>{who}<span class='mact'>{he(a)}:</span> "
                           f"{he(', '.join(items[:ITEMS_SHOWN]))}{more}</div>")
        return "".join(out) or "<span class='sub2'>–</span>"

    body = ""
    for key, title in MARKET_GROUPS:
        lines = [x for x in ov["lines"] if x["group"] == key]
        if not lines:
            continue
        body += f"<tr class='mgrp'><td colspan='4'>{h(title)}</td></tr>"
        for x in lines:
            decs = "".join(f"<div class='mrow'>{h(capital(status))} {para_refs(pids, paras)}"
                           + (f" <span class='sub2'>(as “{h(mname(m['name']))}”)</span>"
                              if mname(m["name"]) != x["name"] else "") + "</div>"
                           for case, m, status, pids in x["decisions"])
            body += (f"<tr><td><b>{market_hover(x['market'], paras)}</b></td><td>{decs}</td>"
                     f"<td>{companies(x['sides'], x['name'], True)}</td>"
                     f"<td>{companies(x['sides'], x['name'], False)}</td></tr>")
    for store, title, text in ((ov["none"], "No Precedent", "to be assessed under the Market Definition Notice"),
                               (ov["failed"], "Search Failed", "press “Update the market definitions” below")):
        if store:
            body += (f"<tr class='mgrp'><td colspan='4'>{h(title)}</td></tr><tr><td>"
                     + (outcome_chip("No precedent") if title == "No Precedent" else "<b>Search failed</b>")
                     + f"</td><td><span class='sub2'>{h(text)}</span></td><td>{plain_items(store, True)}</td>"
                     f"<td>{plain_items(store, False)}</td></tr>")
    return (f"<table class='sumt mkt'><colgroup><col style='width:17%'><col style='width:21%'><col style='width:31%'>"
            f"<col style='width:31%'></colgroup><thead><tr><th>Market</th><th>Commission's Decision</th>"
            f"<th>{he(target)}</th><th>Portfolio Companies</th></tr></thead><tbody>{body}</tbody></table>")


def market_overview_plain(ov):
    """The same table as text, for the Word document: [{"group", "market", "decisions", "target", "portcos"}]."""
    target = ov["target"]

    def items(g):
        text = ", ".join(g["items"])
        return text + (" (possibly)" if g.get("status") == "possibly" else "")

    def rows(sides, own, store=False):
        out = []
        for c, acts in sides.items():
            if (c == target) != own:
                continue
            for a, g in acts.items():
                out.append(("" if own else f"{c} · ") + f"{a}: " + (", ".join(g) if store else items(g)))
        return out
    out = []
    for x in ov["lines"]:
        out.append({"group": dict(MARKET_GROUPS)[x["group"]], "market": x["name"],
                    "decisions": [f"{capital(status)} {_plain_refs(pids)}".strip()
                                  + (f" (as “{mname(m['name'])}”)" if mname(m["name"]) != x["name"] else "")
                                  for case, m, status, pids in x["decisions"]],
                    "target": rows(x["sides"], True), "portcos": rows(x["sides"], False)})
    if ov["none"]:
        out.append({"group": "No Precedent", "market": "No precedent",
                    "decisions": ["to be assessed under the Market Definition Notice"],
                    "target": rows(ov["none"], True, True), "portcos": rows(ov["none"], False, True)})
    if ov["failed"]:                      # as in the table of step ④: never part of "No precedent"
        out.append({"group": "Search Failed", "market": "Search failed",
                    "decisions": ["to be looked up again (“Update the market definitions” in step ④)"],
                    "target": rows(ov["failed"], True, True), "portcos": rows(ov["failed"], False, True)})
    return out


def market_overview_cited(ov):
    """{case: {paragraph numbers}} of the paragraphs the market table cites (for the list of decisions cited)."""
    cited = {}
    for x in ov["lines"]:
        for case, m, status, pids in x["decisions"]:
            for pid in pids:
                c, _, n = pid.rpartition("-")
                if n.isdigit():
                    cited.setdefault(c, set()).add(int(n))
    return cited


# A shop's or wholesaler's own market is the retail or wholesale of the products it sells. The decisions usually define
# markets for making and supplying the products, so such a side counts as "No precedent", unless a decision defines a
# market at its own level of trade (e.g. "retail distribution of decorative coatings" in a decision the lawyer added).
# Both conditions, so that a manufacturers' market is never taken for a retail one (e.g. a chocolate shop placed in
# "Tablets"; "travel retail" in M.5644 (39) means sales TO travel retailers): (1) the AI placed the side's products there as a precedent, i.e. a market defined at this level of trade;
# (2) the market's name in the Commission's words is a retail or wholesale market, checked in code. Legal vocabulary
# only, no sector knowledge.
LEVEL_MARKET = {"retail": re.compile(r"\bretail(?:ing)?\b", re.IGNORECASE),
                "wholesale": re.compile(r"\bwholesal(?:e|ing)\b", re.IGNORECASE)}
CHANNEL_ONLY = re.compile(r"\b(?:to|for|through|via)\s+(?:the\s+)?(?:travel\s+)?(?:retail|wholesal)\w*|\btravel\s+retail",
                          re.IGNORECASE)


def level_market(market, level):
    """Whether a market's name (as the AI found it, or as shown) names a market at this level of trade, not a sales
    channel of the manufacturers ("supply to retailers", "travel retail")."""
    names = [n for n in ((market or {}).get("name_as_found"), (market or {}).get("name")) if n]
    return any(LEVEL_MARKET[level].search(n) and not CHANNEL_ONLY.search(n) for n in names)


def reseller_flags(r, entries=None):
    """{"a": bool, "b": bool}: the side is a shop or wholesaler without a market defined at its own level among the
    row's markets (entries of row_markets)."""
    out = {}
    for s in ("a", "b"):
        flag = is_reseller(r[s])
        if flag and entries:
            lw = level_word(r[s])
            if any(e.get(s) and e[s].get("basis") == "precedent" and level_market(e.get("market"), lw)
                   for e in entries):
                flag = False
        out[s] = flag
    return out


def commission_heading(label):
    if label == BOTH_DIRECTIONS:
        return "Vertical Labels, Both Directions"
    if label.startswith("vertical, "):
        return "Vertical Label, " + label[len("vertical, "):]
    if label.startswith("horizontal"):
        return "Horizontal Label"
    return "This Row"


def label_of_heading(head):
    """The internal label of a part heading (for an edited text read back)."""
    head = head.strip()
    if head == "Vertical Labels, Both Directions":
        return BOTH_DIRECTIONS
    if head.startswith("Vertical Label, "):
        return "vertical, " + head[len("Vertical Label, "):]
    return "horizontal" if head == "Horizontal Label" else ""


def link_items(r, up):
    """The products the vertical links of one direction name ("a": the target's, "b": the portfolio company's);
    up "both" for links in both directions. Empty on a side where the comparison named none (e.g. a label the lawyer
    added)."""
    out = {"a": set(), "b": set()}
    for v in r.get("vertical_items") or []:
        if up == "both" or ("a" if v.get("link") in UPSTREAM_LINKS else "b") == up:
            for s in ("a", "b"):
                out[s].update(i for i in v.get(s) or [] if i)
    return out


def link_entries(entries, r, up):
    """The markets of a vertical relationship: on each side only the markets of the products the link names. A row's
    markets also hold the products of its horizontal label, which are not part of the supply (e.g. the target's
    ingredients, where the link concerns its finished foods). Where the link names no products of a side, that side
    keeps all its markets."""
    items = link_items(r, up)
    out = []
    for e in entries:
        e2 = dict(e)
        for s in ("a", "b"):
            if items[s] and e2.get(s) and not set(e2[s].get("items") or []) & items[s]:
                e2[s] = None
        if e2.get("a") or e2.get("b"):
            out.append(e2)
    return out


def uncovered_items(r, entries):
    """The products of a horizontal label (step ③'s "with regard to") that no market of the row covers."""
    m = r.get("matches") or {}
    out = {}
    for s in ("a", "b"):
        covered = {i for e in entries if e.get(s) for i in (e[s].get("items") or [])}
        out[s] = [i for i in m.get(s) or [] if i and i not in covered]
    return out


def uncovered_sentences(r, entries, target, portco, html_out=True):
    """'Separate markets' covers only the products placed in a market: the products of the label without any precedent
    are named, so that the result is not read as covering them (e.g. a replacer of a product that is in a market)."""
    u = uncovered_items(r, entries)
    out = []
    for s, who in (("a", target), ("b", portco)):
        if u[s]:
            items = listing(u[s]) if html_out else word_list(u[s])
            out.append(f"{poss(he(who) if html_out else who)} {items}: no precedent, so the separate markets do not "
                       "cover " + ("it" if len(u[s]) == 1 else "them") + "; to be assessed under the Market Definition "
                       "Notice")
    return out


def commission_sentences(r, target, portco, html_out=True):
    """[(label, bullets, outcome)], one per relationship shown in the row."""
    parts = commission_parts(r, target, portco)
    if not parts or parts[1] is None or parts[1].get("error"):
        return []
    rec, view, entries, h_on, ups, verdict = parts
    paras = (rec or {}).get("paragraphs") or {}
    rs, acts = reseller_flags(r, entries), {"a": r["a"], "b": r["b"]}
    out = []
    if h_on:
        outcome = horizontal_outcome(entries, verdict, rs)
        bullets = horizontal_sentences(entries, view, verdict, target, portco, paras, html_out, rs, acts)
        if outcome == "Not supported":
            bullets += uncovered_sentences(r, entries, target, portco, html_out)
        out.append(("horizontal", bullets, outcome))
    if len(ups) > 1:                   # supply in both directions: each side's market once
        le = link_entries(entries, r, "both")
        out.append((BOTH_DIRECTIONS, vertical_sentence(le, view, "both", target, portco, paras, html_out, rs,
                                                       acts), vertical_outcome(le, ups[0], rs)))
    for up in ups if len(ups) == 1 else []:
        u, d = (target, portco) if up == "a" else (portco, target)
        le = link_entries(entries, r, up)
        out.append((f"vertical, {u} → {d}", vertical_sentence(le, view, up, target, portco, paras, html_out, rs,
                                                               acts), vertical_outcome(le, up, rs)))
    if len(out) > 1 and all(o == "No precedent" for _, _, o in out) and not any(rs.values()):
        out = [("", ["no decision in the database covers these products: "
                     "to be assessed under the Market Definition Notice"], "No precedent")]
    if not out:          # unclear, or added back without a label: where each side's products fall
        out.append(("", [f"{he(target) if html_out else target}: {_side_text(entries, view, 'a', paras, html_out)}",
                         f"{he(portco) if html_out else portco}: {_side_text(entries, view, 'b', paras, html_out)}"],
                    ""))
    failed = list(dict.fromkeys(view.get("failed") or []))
    if failed:
        # a failed search is never a result: while products of the row are missing, "No precedent" and "One side
        # defined" are not claimed, and the failure comes first
        items = ", ".join(he(x) for x in failed) if html_out else ", ".join(failed)
        out = [(label, ["no result while the search for some of these products has failed"]
                if outcome == "No precedent" else bullets,
                "" if outcome in ("No precedent", "One side defined") else outcome) for label, bullets, outcome in out]
        out.insert(0, ("", [f"the search failed for {items}: run “Update the market definitions” in step ④ before "
                            "relying on this row"], ""))
    return out


def commission_plain(r, target, portco):
    """The Commission's view as plain text, for “Edit” (one line per bullet)."""
    sentences = commission_sentences(r, target, portco, html_out=False)
    if not sentences:
        return ""

    def head(label, outcome):
        return " · ".join(x for x in (outcome, commission_heading(label)) if x)
    return "\n".join(f"{head(label, outcome)}:\n"
                     + "\n".join(f"- {capital(b).replace(PREFIX_SEP, ': ')}" for b in bullets)
                     for label, bullets, outcome in sentences)


def commission_htmls(r, target, portco, parts, folded=None):
    """Step ④: the Commission's part for each line of a row (parts as in assign_commission), as HTML; the chip says
    the result, the line beside it says which label it belongs to. A folded line ("less likely") shows its chip; the
    markets open with a click on it. Code only, no AI call."""
    folded = folded or [False] * len(parts)
    out = [""] * max(len(parts), 1)
    if not ss.get("precedents") or ss.get("step") != 4:
        return out
    rec, view = row_view(r)
    if view is None:
        if kept(row_status(r)):
            out[0] = f"<div class='ccell'><span class='sub2'>{he(search_gap(r, rec))}: press “Update the market " \
                     "definitions” below.</span></div>"
        return out
    if view["error"]:
        out[0] = (f"<div class='ccell'><b>Commission:</b> the search failed ({he(view['error'])}): press “Update the "
                  "market definitions” below.</div>")
        return out
    o = ss.override_store.get(cmp.pair_id(r), {})
    edited = (o.get("text_commission") or "").strip()
    if edited:
        failed = ""
        if view.get("failed"):
            failed = (f"<b>The search failed</b> for {he(', '.join(dict.fromkeys(view['failed'])))}: press “Update "
                      "the market definitions” below. ")
        out[0] = f"<div class='ccell'>{failed}{he_lines(edited)} <span class='ed'>edited by you</span></div>"
        return out
    groups = assign_commission(commission_sentences(r, target, portco), parts, target)
    # a line for the whole row (e.g. "no decision covers these products" for all labels, or a failed search) sits on
    # the first label; if that label is folded ("less likely"), it is repeated, open, on the first label shown in full
    if groups and folded and folded[0]:
        whole = [e for e in groups[0] if not e[0]]
        j = next((i for i, p in enumerate(parts) if i and not folded[i] and not p.get("off")), None)
        if whole and j is not None and j < len(groups):
            groups[j] = whole + groups[j]
    for i, p in enumerate(parts):      # a second vertical label in the same direction (input and resale): same markets
        if (p.get("kind") == "v" and not p.get("off") and not groups[i] and any(
                q.get("kind") == "v" and not q.get("off") and q.get("up") == p.get("up") and groups[j]
                for j, q in enumerate(parts[:i]))):
            out[i] = "<div class='ccell'><span class='sub2'>Same markets as the vertical label above.</span></div>"
    for i, g in enumerate(groups[:len(out)]):
        if g and i < len(folded) and folded[i]:
            out[i] = "<div class='ccell'>" + "".join(
                f"<details class='mkts lfold'><summary>{outcome_chip(outcome) or 'Details'}</summary><ul>"
                + "".join(f"<li>{b[:1].upper() + b[1:] if not b.startswith('<') else b}</li>" for b in bullets)
                + "</ul></details>" for label, bullets, outcome in g) + "</div>"
        elif g:
            out[i] = "<div class='ccell'>" + "".join(
                f"<div class='cpart'>{outcome_chip(outcome)}"
                + (f"<span class='cph'>{he(commission_heading(label))}</span>" if label == BOTH_DIRECTIONS else "")
                + "<ul>" + "".join(f"<li>{b[:1].upper() + b[1:] if not b.startswith('<') else b}</li>" for b in bullets)
                + "</ul></div>" for label, bullets, outcome in g) + "</div>"
    return out
