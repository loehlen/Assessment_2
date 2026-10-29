"""
steps/step3_assessment.py - step ③ Preliminary Assessment, the logic behind the table: running the comparison
(logic/comparison.py), the labels of each row (potential horizontal overlap, potential vertical relationship), the
rules checked in code ("less likely", own use, direct customers), the sentences of the preliminary assessment, and the
lawyer's views, notes and edits. The table itself is drawn in steps/step3_4_table.py.
"""
import concurrent.futures as cf
import hashlib
import json
import re
import time

import streamlit as st

from logic import activity_mapping as am
from logic import ai_client
from logic import comparison as cmp
from logic import rules

from ui.common import _shown, capital, esc, go_to, h, he, log_stage, plural, poss, quoted, ss, words_list
from ui.working_screen import WorkCard
from ui.labels import dots_html
from ui.activity_display import CUSTOMER_TEXT, short_name, stage_of


def activities_hash(activities):
    """What the comparison depends on: the activities and the words the lawyer keeps in the descriptions."""
    # the fields that only record the lawyer's handling (e.g. saved unchanged in the edit form) are no change
    content = {c: [{k: v for k, v in a.items() if k not in rules.STATE_FIELDS} for a in acts]
               for c, acts in (activities or {}).items()}
    state = {"activities": content, "keep_words": sorted(ss.get("keep_words") or [])}
    return hashlib.sha256(json.dumps(state, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


POSITION_FIELDS = ("portco", "label_a", "label_b", "a", "b", "abstract_a", "abstract_b", "sims")


def prepare_comparison(activities):
    """Names, abstracts and content keys of the activities to compare, and how many pairs are new: a pair goes to the
    AI only if no result for exactly these two anonymised activities exists in this session. Pure code."""
    companies = ss.companies
    target, portcos = companies[0]["name"], [c["name"] for c in companies[1:]]
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in companies}
    names = cmp.collect_names(companies, activities, group, ss.get("keep_words") or ())
    compared = {c["name"]: [a for a in activities.get(c["name"], []) if not a.get("excluded") and not rules.is_gap(a)]
                for c in companies}
    profiles, blocked, keys = {}, [], {}
    for c in companies:
        abstracts, problems = cmp.anonymise(compared[c["name"]], names)
        profiles[c["name"]] = {"activities": compared[c["name"]], "abstracts": abstracts}
        blocked += [f"{c['name']} activity {i + 1}: {left}" for i, left in problems]
        for a, abstract in zip(compared[c["name"]], abstracts):
            keys[a["aid"]] = cmp.activity_key(a, abstract)
    pair_keys = [(keys[ta["aid"]], keys[pa["aid"]]) for p in portcos for ta in compared[target] for pa in compared[p]
                 if rules.compared_pair(ta, pa)]
    cache = ss.get("pair_cache") or {}
    new = sum(1 for k in pair_keys if k not in cache)
    return {"target": target, "portcos": portcos, "names": names, "profiles": profiles, "keys": keys,
            "blocked": blocked, "pairs": len(pair_keys), "new": new, "kept": len(pair_keys) - new}


def failed_pairs():
    """The rows whose comparison call failed (an API error, not an answer). They are not kept among the pair results,
    so "Update the comparison" in step ② sends them again."""
    return [r for r in ss.get("results") or [] if (r.get("comparison") or {}).get("error")]


def confirm_activities(ai, activities, problems, profiles_text):
    if problems:
        st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        return False
    plan = prepare_comparison(activities)
    target, portcos, names, profiles, keys = (plan[k] for k in ("target", "portcos", "names", "profiles", "keys"))
    ss.setdefault("vec_cache", {})
    ss.setdefault("pair_cache", {})
    first, t0 = ss.log.mark(), time.time()
    card = WorkCard("Comparing the Activities", "Preparing the anonymised descriptions …",
                    "Every activity of the target is compared with every activity of each portfolio company. The AI "
                    "sees descriptions only, never company names. This usually takes one to two minutes.")
    card.log(f"✔ Anonymised: {len(rules.name_variants(names))} name variants removed"
             + (f"; ✖ names left in {len(plan['blocked'])} abstracts (their pairs are blocked)" if plan["blocked"]
                else "; name check passed for every abstract"))
    missing = {n: [a for a in p["activities"] if keys[a["aid"]] not in ss.vec_cache] for n, p in profiles.items()}
    missing = {n: acts for n, acts in missing.items() if acts}
    try:
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(cmp.embed_company, ai, n, acts, names): n for n, acts in missing.items()}
            for fut in card.wait(futures):
                for a, v in zip(missing[futures[fut]], fut.result()):
                    ss.vec_cache[keys[a["aid"]]] = v
    except Exception as e:  # noqa: BLE001 - never continue without vectors (see comparison.embed_company)
        st.error(f"The comparison stopped: the embeddings failed, so nothing was compared ({type(e).__name__}: {e}). "
                 "Your activities are kept; go back and press “Compare activities” again.")
        st.button("← Back to the activities", on_click=go_to, args=(2,))
        return False
    card.log(f"✔ Embeddings: {plural(len(missing), 'request')}, one per company, anonymised texts only"
             if missing else "✔ Embeddings: all kept from before")
    for p in profiles.values():
        p["vectors"] = [ss.vec_cache[keys[a["aid"]]] for a in p["activities"]]
    pairs = cmp.build_pairs(target, portcos, profiles)
    pair_key = {id(p): (keys[p["a"]["aid"]], keys[p["b"]["aid"]]) for p in pairs}
    todo = [p for p in pairs if pair_key[id(p)] not in ss.pair_cache]
    if len(pairs) > len(todo):
        card.log(f"✔ {plural(len(pairs) - len(todo), 'pair')} kept from before (nothing changed in them)")
    card.update(0.0, f"0 of {plural(len(todo), 'pair')} compared" if todo else "Nothing new to compare")
    fresh = {}
    if todo:
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(cmp.assess, ai, p, names): p for p in todo}
            for done, fut in enumerate(card.wait(futures), start=1):
                key, result = pair_key[id(futures[fut])], fut.result()
                fresh[key] = result
                # a failed call (an API error, not an answer) is shown but not kept, so the next update sends it again
                if not result["comparison"].get("error"):
                    ss.pair_cache[key] = result
                card.update(done / len(todo), f"{done} of {plural(len(todo), 'pair')} compared")
    results = [{**(fresh.get(pair_key[id(p)]) or ss.pair_cache[pair_key[id(p)]]), **{k: p[k] for k in POSITION_FIELDS}}
               for p in pairs]
    n_failed = sum(1 for r in fresh.values() if r["comparison"].get("error"))
    card.log(f"{plural(len(todo), 'pair')} compared, {len(pairs) - len(todo)} kept, in {time.time() - t0:.0f} s"
             + (f"; ✖ {plural(n_failed, 'call')} failed" if n_failed else ""))
    ss.compared_names = [c["name"] for c in ss.companies]
    # the research each company's activities come from, so that steps ③–⑤ keep showing the sources the compared
    # activities refer to, also after a company is mapped again
    ss.compared_research = {c["name"]: (ss.mapped.get(c["name"]) or {}).get("search") for c in ss.companies}
    ss.confirmed = activities
    ss.profiles_text = profiles_text
    # names that are also ordinary words (the lawyer's choice in step ②) never make an existing relationship
    ss.relationships = am.find_relationships(ss.mapped, ss.companies, ss.get("keep_words") or ())
    ss.confirmed_hash = activities_hash(activities)
    ss.current_hash = ss.confirmed_hash
    ss.results_version = ss.get("results_version", 0) + 1     # fresh widgets; their values come from override_store
    ss.setdefault("override_store", {})                       # kept: dismissals and notes stay with their pair
    ss.names = names
    ss.profiles_meta = {n: {"abstracts": p["abstracts"]} for n, p in profiles.items()}
    ss.results = results
    log_stage("confirm", first, time.time() - t0)
    ss.step = 3
    return True


FOUND_BY_WORDS = {"AI": "found by the AI", "rule": "found by a rule in the code", "AI and rule": "found by the AI and a "
                                                                                              "rule in the code"}
RULE_WORDS = {
    "A could be an input for B": "{t} sells to producers, and its products are close to inputs that {p} lists",
    "B could be an input for A": "{p} sells to producers, and its products are close to inputs that {t} lists",
    "A could be resold by B": "{t} sells to shops or wholesalers, and {p} resells a close range",
    "B could be resold by A": "{p} sells to shops or wholesalers, and {t} resells a close range",
}
UPSTREAM_LINKS = ("A could be an input for B", "A could be resold by B")


def _entry(pid):
    return ss.override_store.setdefault(pid, {"dismiss": False, "add_back": False, "note": ""})


def _store_override(pid, field, key):
    """Widget callback: overrides live in their own store, so they survive when a section is hidden."""
    value = ss.get(key)
    _entry(pid)[field] = value.strip() if isinstance(value, str) else bool(value)


def _remove_added(pid, field):
    _entry(pid)[field] = False if field == "added_h" else ""


# "Your view" next to every label. Dismiss sets dismissed_parts (so step ④ and the counts follow); the other views are
# the lawyer's assessment, shown in the summary and the Word document; "Ask the company" also puts the row into the Open
# points. Overrides only.
VIEWS = ["To check", "Likely", "Unlikely", "Ask the company", "Dismiss"]


def view_of(pid, part, off=False):
    if off:
        return "Dismiss"
    v = ((ss.override_store.get(pid) or {}).get("views") or {}).get(part)
    return v if v in VIEWS and v != "Dismiss" else "To check"


def _store_view(pid, part, key, tool_parts, kind):
    """Widget callback for "Your view". kind: "tool" (a label of the tool), "lawyer" (a label the lawyer added) or
    "row" (an unclear row, or a row added back without a label)."""
    value = ss.get(key) or "To check"
    e = _entry(pid)
    views = e.setdefault("views", {})
    if kind == "tool":
        chosen = e.setdefault("dismissed_parts", {})
        if e.get("dismiss"):               # the older single box: one entry per label first
            e["dismiss"] = False
            for p in tool_parts:
                chosen[p] = True
        chosen[part] = value == "Dismiss"
    elif kind == "lawyer" and value == "Dismiss":
        _remove_added(pid, part)
        views.pop(part, None)
        return
    elif kind == "row":
        if e.get("add_back") and value == "Dismiss":
            e["add_back"] = False
        else:
            e["dismiss"] = value == "Dismiss"
    if value in ("To check", "Dismiss"):
        views.pop(part, None)
    else:
        views[part] = value


def _store_views(pid, parts, key, tool_parts, kind):
    """"Your view" of a line on the screen: the same view for each label it shows (one, or an input and a resale link
    in the same direction)."""
    for part in parts:
        _store_view(pid, part, key, tool_parts, kind)


def kept(status):
    return status in ("candidate", "unclear", "added back by user")


def has_added(o):
    return bool((o or {}).get("added_h") or (o or {}).get("added_v"))


def row_status(r):
    """The status shown and counted: the code's decision, changed only by the lawyer. A row whose labels the lawyer
    dismissed but to which the lawyer added a label of their own stays in the table."""
    s = cmp.effective_status(r, ss.overrides)
    if s == "dismissed by user" and has_added(ss.overrides.get(cmp.pair_id(r))):
        return r["decision"]["status"]
    return s


def search_overrides():
    """The overrides as step ④ sees them. A row with a lawyer's label is searched as the tool found it (its
    dismissals are left out here), so that adding a label never needs a new search."""
    return {pid: ({k: v for k, v in o.items() if k not in ("dismiss", "dismissed_parts")} if has_added(o) else o)
            for pid, o in (ss.get("overrides") or {}).items()}


def listing(items, limit=3):
    """Items as HTML, on the screen (the Word document uses word_list); more than `limit`: “and 2 more”, hovering
    shows every item. “and 1 more” would save nothing, so one item more is shown as it is."""
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == limit + 1:
        limit += 1
    text = ", ".join(he(i) for i in items[:limit])
    if len(items) > limit:
        tip = h("All: " + "; ".join(items))
        text += f" <span class='hov' title='{tip}'>and {len(items) - limit} more</span>"
    return text


def word_list(items, limit=6):
    """Items as plain text for the Word document (no hover there): more than `limit`, “and 2 more”."""
    items = [str(i) for i in items or [] if i]
    if len(items) <= limit + 1:        # "and 1 more" would save nothing
        return ", ".join(items)
    return ", ".join(items[:limit]) + f" and {len(items) - limit} more"


def side_items(r, side):
    """The items of one side that the comparison named for this row, horizontal and vertical."""
    m = r.get("matches") or {}
    return list(dict.fromkeys(list(m.get(side) or []) + [i for v in r.get("vertical_items") or []
                                                          for i in (v.get(side) or [])]))


def is_own_use(r):
    """A row that involves only production for the group's own use: shown in the collapsed "Own use" section.
    Side lines sold to third parties stay in the main table."""
    for side in ("a", "b"):
        act = r[side]
        if rules.category(act) == "other":
            items = side_items(r, side) or act.get("includes") or []
            return rules.own_use_side(act, items)
    return False


def direction(link, r, target, portco):
    """(upstream company, its activity, downstream company, its activity) of a vertical link."""
    if link in UPSTREAM_LINKS:
        return target, r["a"], portco, r["b"]
    return portco, r["b"], target, r["a"]


def link_sentence(link, vitems, r, target, portco, html_out=True):
    """A vertical link in words, with the names re-attached and the items the link concerns."""
    if html_out:
        a = f"{poss(he(target))} {listing(vitems.get('a', [])) or he(r['a']['product'])}"
        b = f"{poss(he(portco))} {listing(vitems.get('b', [])) or he(r['b']['product'])}"
    else:
        a = f"{poss(target)} {word_list(vitems.get('a')) or r['a']['product']}"
        b = f"{poss(portco)} {word_list(vitems.get('b')) or r['b']['product']}"
    return {
        "A could be an input for B": f"{a} could be an input for {b}",
        "B could be an input for A": f"{b} could be an input for {a}",
        "A could be resold by B": f"{a} could be resold through {b}",
        "B could be resold by A": f"{b} could be resold through {a}",
    }.get(link, link)


def joint_link_sentence(links, r, target, portco):
    """An input and a resale link in the same direction whose supplying side names the same items, as one sentence
    on the screen (None otherwise): "X's … could be an input for Y's …, or be resold through Y's …"."""
    if len(links) != 2 or not any(lk in INPUT_LINKS for lk in links) or all(lk in INPUT_LINKS for lk in links):
        return None
    vi = {v["link"]: v for v in r.get("vertical_items") or []}
    inp = next(lk for lk in links if lk in INPUT_LINKS)
    res = next(lk for lk in links if lk not in INPUT_LINKS)
    sup, cus = ("a", "b") if inp.startswith("A ") else ("b", "a")
    if not res.startswith("A " if sup == "a" else "B "):
        return None
    items_sup = [(vi.get(lk) or {}).get(sup) or [] for lk in (inp, res)]
    if items_sup[0] != items_sup[1]:
        return None
    names = {"a": target, "b": portco}

    def side(x, items):
        return f"{poss(he(names[x]))} {listing(items) or he(r[x]['product'])}"
    c_in, c_res = ((vi.get(lk) or {}).get(cus) or [] for lk in (inp, res))
    if c_in == c_res:
        return f"{side(sup, items_sup[0])} could be an input for, or be resold through, {side(cus, c_in)}"
    return (f"{side(sup, items_sup[0])} could be an input for {side(cus, c_in)}, or be resold through "
            f"{side(cus, c_res)}")


def customer_dots(r, target, portco):
    """The customer score (dots) with its explanation on hover."""
    score = r.get("customers")
    if score not in ("●●●", "●●○", "●○○", "?"):
        return ""
    ca = words_list(_shown(r["a"].get("direct_customers"))) or "not stated"
    cb = words_list(_shown(r["b"].get("direct_customers"))) or "not stated"
    if score == "?":                   # one side's sources do not say who it sells to: nothing to compare
        tip = (f"Direct customers not stated: {target} sells to {ca}; {portco} to {cb}. The sources do not say who "
               "one of the two sells to, so the customers cannot be compared. This does not affect the overlap, which "
               "is about the products.")
        return f"<span class='dots' title='{h(tip)}'>customers not stated</span>"
    tip = (f"{capital(CUSTOMER_TEXT[score])}: {target} sells to {ca}; {portco} to {cb}. This compares only who each "
           "company sells to directly, not the products. Different customers alone do not rule out an overlap: "
           "customers form a separate market only if the seller can tell which group a customer belongs to at the time "
           "of sale, customers cannot resell to each other, and the different treatment is lasting (Market Definition "
           "Notice (88)).")
    return f"<span class='dots' title='{h(tip)}'>{dots_html(score)}</span>"


def own_use_flag(r):
    return any("captive" in f for f in r.get("flags") or [])


def label_parts(r, target, portco):
    """The labels of one row as shown: the tool's labels, each with whether the lawyer dismissed it, and the
    labels the lawyer added. [{part, kind "h"/"v", origin "tool"/"lawyer", up "a"/"b" (vertical), off}]"""
    o = ss.overrides.get(cmp.pair_id(r)) or {}
    off = set(cmp.dismissed_parts(r, ss.overrides))
    out = [{"part": p, "kind": "h" if p == "horizontal" else "v", "origin": "tool", "off": p in off,
            "up": None if p == "horizontal" else ("a" if p in UPSTREAM_LINKS else "b")}
           for p in cmp.assessment_parts(r)]
    if o.get("added_h"):
        out.append({"part": "added_h", "kind": "h", "origin": "lawyer", "off": False, "up": None})
    if o.get("added_v") in ("a>b", "b>a"):
        out.append({"part": "added_v", "kind": "v", "origin": "lawyer", "off": False, "up": o["added_v"][0]})
    return out


def active_labels(r, target, portco):
    """(horizontal shown?, [upstream sides of the vertical relationships shown]) after the lawyer's changes."""
    parts = [p for p in label_parts(r, target, portco) if not p["off"]]
    return any(p["kind"] == "h" for p in parts), list(dict.fromkeys(p["up"] for p in parts if p["kind"] == "v"))


def part_detail(p, r, target, portco, html_out=True):
    """The line(s) under one label, assembled in code from the structured answers (no AI call)."""
    c = r["comparison"]
    if p["origin"] == "lawyer":
        if p["kind"] == "v":
            up, down = (target, portco) if p["up"] == "a" else (portco, target)
            return [f"{he(up) if html_out else up} → {he(down) if html_out else down}"]
        return []
    if p["kind"] == "h":
        kind = "same product" if c["product_relation"] == "same product" else "similar product"
        sa, sb = stage_of(r["a"]).lower(), stage_of(r["b"]).lower()
        level = f"same level ({sa})" if sa == sb else f"different levels ({sa} v {sb})"
        own = " · own use" if own_use_flag(r) else ""
        m = r.get("matches") or {}
        if not html_out:
            cust = CUSTOMER_TEXT.get(r.get("customers") or "", "")
            lines = [f"{kind}, {level}{', ' + cust if cust else ''}"]
            if m.get("a") or m.get("b"):
                lines.append(f"With regard to: {target}: {', '.join(m.get('a') or []) or '–'}; "
                             f"{portco}: {', '.join(m.get('b') or []) or '–'}")
            return lines
        dots = customer_dots(r, target, portco)
        lines = [f"<span class='basis'>{kind} · {level}{' · ' + dots if dots else ''}{own}</span>"]
        a, b = listing(m.get("a", [])), listing(m.get("b", []))
        if (a or b) and not p["off"]:      # one line per company
            lines.append(f"With regard to<span class='wr'><i>{he(target)}:</i> {a or '–'}</span>"
                         f"<span class='wr'><i>{he(portco)}:</i> {b or '–'}</span>")
        return lines
    up, up_act, down, down_act = direction(p["part"], r, target, portco)
    vitems = {v["link"]: v for v in r.get("vertical_items") or []}.get(p["part"], {})
    if not html_out:
        return [f"{up} ({stage_of(up_act).lower()}) → {down} ({stage_of(down_act).lower()})",
                link_sentence(p["part"], vitems, r, target, portco, html_out=False)]
    lines = [f"<span class='basis'>{he(up)} ({stage_of(up_act).lower()}) → {he(down)} "
             f"({stage_of(down_act).lower()}){' · own use' if own_use_flag(r) else ''}</span>"]
    if not p["off"]:
        lines.append(link_sentence(p["part"], vitems, r, target, portco))
    return lines


LABEL_TEXT = {"h": "Potential horizontal overlap", "v": "Potential vertical relationship"}


def label_html(p, less=False):
    cls = "lab-off" if p["off"] else ("lab-h" if p["kind"] == "h" else "lab-v")
    tip = LESS_TIP_H if p["kind"] == "h" else LESS_TIP_V
    tag = " <span class='tag'>added by you</span>" if p["origin"] == "lawyer" else (
        " <span class='tag'>dismissed by you</span>" if p["off"] else
        f" <span class='tag' title='{h(tip)}'>less likely</span>" if less else "")
    return f"<span class='lab {cls}'>{LABEL_TEXT[p['kind']]}</span>{tag}"


def assessment_plain(r, target, portco):
    """The app's wording of a row as plain text: what the lawyer starts from in "Edit"."""
    lines = []
    for p in label_parts(r, target, portco):
        if not p["off"]:
            lines += [LABEL_TEXT[p["kind"]] + (" (added by you)" if p["origin"] == "lawyer" else "")]
            lines += ["  " + x for x in part_detail(p, r, target, portco, html_out=False)]
    return "\n".join(lines)


def relationship_html(rel, target, portco):
    """The existing relationship, folded: one line, the passages behind it on request."""
    quotes = "".join(f"<div class='it one'><span class='sub2'>{poss(he(who))} sources:</span> {quoted(p)}</div>"
                     for who, p in rel)
    return (f"<details class='mkts' style='margin-top:.3rem'><summary><span class='lab lab-q'>Existing "
            f"relationship</span> the public sources of {he(target)} and {he(portco)} mention each other "
            f"({plural(len(rel), 'passage')})</summary>{quotes}<div class='sub2'>Check its nature (supply, "
            "distribution, partnership, equity); the tool does not assess it.</div></details>")


RESELLER_LEVELS = ("retail", "wholesale / distribution")


def set_aside_text(r, link, reason, target, portco, md=True):
    """A link the tool set aside, explained (so that it does not read as if the company had no retail at all). The
    tool compares one activity of each company at a time; a resale link needs the reseller's activity in
    THIS row to be in wholesale or retail. Where that company's shop or wholesale activity is compared in another row,
    the note points there. md=False: plain text (Annex B of the Word document)."""
    e = esc if md else str

    def head(t):
        return f"**{t}:**" if md else f"{t}:"
    side = "a" if reason.startswith("A ") else "b"
    who = target if side == "a" else portco
    act = r[side]
    what = e(cmp.describe_link(link, target, portco))
    if "not active in wholesale or retail" in reason:
        here = stage_of(act).lower()
        others = [a for a in (ss.confirmed or {}).get(who, []) if a.get("value_chain_level") in RESELLER_LEVELS
                  and not a.get("excluded")]
        if others:
            names = " · ".join(f"“{e(short_name(a))}”" for a in others)
            return (f"{head(f'Resale ({what})')} compared in the row {names}. The tool compares one activity of each "
                    f"company at a time, and here {poss(e(who))} activity is {e(here)}.")
        return (f"{head(f'Resale not considered ({what})')} in this row {poss(e(who))} activity is {e(here)}, and the "
                f"screen shows no wholesale or retail activity of {e(who)}.")
    if "own use" in reason:
        return (f"{head(f'Set aside ({what})')} {poss(e(who))} activity here is only for the group's own use, so it "
                "supplies no one and resells nothing to third parties.")
    return f"{head('Link set aside by the tool')} {what}; {e(who)} {e(reason[2:])}."


# The AI compares "ACTIVITY A" (always the target) and "ACTIVITY B" (the portfolio company) and never sees a name;
# its reasons therefore say "A" and "B". On screen and in the Word document the app puts the names back. A capital "A"
# that starts a sentence is only replaced where it is clearly the label ("A's", "A and B", "A sells ..."), not the
# article ("A shared category ...").
_AB_VERBS = ("is|are|was|has|have|makes|make|sells|sell|supplies|supply|produces|produce|offers|offer|provides|"
             "provide|operates|could|can|may|might|would|will|does|uses|use|buys|buy|distributes|resells|resell|"
             "manufactures|lists|includes|include|focuses|targets|also|only|mainly|appears|covers|consists|sources|"
             "processes|serves|requires|needs|lacks|contains|relates|involves|concerns|belongs|falls|trades|delivers|"
             "describes|lies|sits|acts|works|seems|appear|remains")
_AB_NOT_LABEL = {"vitamin", "type", "grade", "class", "plan", "size", "option", "version", "category", "level",
                 "phase", "series", "model", "format"}


def name_ab(text, target, portco):
    # The rules below run one after another. They first put placeholders in, and the names only at the end: otherwise
    # a later rule would read the "A" inside a name already put in ("Planet A Foods") as the label once more.
    names = {"A": "\x01", "B": "\x02"}
    t = str(text or "").replace("\x01", "").replace("\x02", "")

    def label(m, group=1):
        """The name, unless the letter follows a word like "vitamin" or "type" (then it is not the label)."""
        before = t[:m.start()].split()
        if before and before[-1].lower().strip("(") in _AB_NOT_LABEL:
            return m[0]
        return names[m[group]]

    t = re.sub(r"\b(?:[Aa]ctivity|[Cc]ompany|[Ss]ide|[Pp]arty)\s+([AB])['’]s\b", lambda m: f"{poss(names[m[1]])}", t)
    t = re.sub(r"\b[Aa]ctivity\s+([AB])\b(?![-\w])", lambda m: f"{poss(names[m[1]])} activity", t)
    t = re.sub(r"\b(?:[Cc]ompany|[Ss]ide|[Pp]arty)\s+([AB])\b(?![-\w])", lambda m: names[m[1]], t)
    t = re.sub(r"(?<![\w-])([AB])['’]s\b", lambda m: f"{poss(names[m[1]])}", t)
    t = re.sub(r"(?<![\w-])(B)(?![\w-])", label, t)
    # "A" inside a sentence is the label; at the start of a sentence only before "and/or", a comma, a bracket or a verb
    t = re.sub(r"(?<=[a-z,;(]\s)(A)(?![\w-])|(?<=[a-z,;(])(A)(?![\w-])",
               lambda m: label(m, 1 if m[1] else 2), t)
    t = re.sub(r"(?:(?<=^)|(?<=[.!?:]\s))(A)(?=\s+(?:and|or|" + _AB_VERBS + r")\b|[,);:.])", label, t)
    return t.replace("\x01", target).replace("\x02", portco)


# A horizontal label across different levels of trade, where the two companies do not have fully the same direct customers
# (●●○ or ●○○): a horizontal overlap is then less likely (markets differ at different levels of the supply chain,
# Market Definition Notice (14); whether both compete for the same customers is to be checked). A row whose only
# labels are
# such tool labels, untouched by the lawyer, is shown folded under "Less likely" (display only: the label, step ④ and
# the counts stay as they are).
WEAK_CUSTOMERS = ("●●○", "●○○")


def weak_horizontal(r):
    return (r["a"].get("value_chain_level") != r["b"].get("value_chain_level")
            and (r.get("customers") or "") in WEAK_CUSTOMERS)


def is_less_likely(r):
    if r["decision"]["status"] != "candidate" or is_own_use(r) or not weak_horizontal(r):
        return False
    parts = label_parts(r, "", "")
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid) or {}
    if any((o.get(k) or "").strip() for k in ("note", "text_assessment", "text_commission")):
        return False                   # the lawyer has worked on the row: it stays in the table
    # a dismissed label keeps the row where it is; a view other than "To check" moves it into the table
    return (bool(parts) and all(p["kind"] == "h" and p["origin"] == "tool" for p in parts)
            and all(view_of(pid, p["part"]) == "To check" for p in parts if not p["off"]))


# A vertical input link whose customer side is a shop or a wholesaler: such a company resells; an input could only
# serve its own minor use (e.g. food served in its shops), not its main business. Display only, like the horizontal
# rule above: the label, step ④ and the counts stay as they are. Services stay as they are (a service provider can
# use inputs for its main business).
INPUT_LINKS = ("A could be an input for B", "B could be an input for A")
LESS_TIP_H = ("Different levels of trade and not fully the same direct customers: often different markets, so a horizontal "
              "overlap is less likely; to be checked.")
LESS_TIP_V = ("An input for a shop or wholesaler: such a company resells, so the input could only serve its own minor "
              "use (e.g. food served in its shops), not its main business; to be checked.")


def ancillary_input(r, link):
    if link not in INPUT_LINKS:
        return False
    buyer = r["b"] if link == "A could be an input for B" else r["a"]
    return buyer.get("value_chain_level") in ("retail", "wholesale / distribution")


def less_tag(r, p):
    """Whether a label carries the "less likely" tag (whatever the lawyer's view)."""
    if p.get("origin") != "tool":
        return False
    return weak_horizontal(r) if p["kind"] == "h" else ancillary_input(r, p["part"])


def less_likely_part(r, p):
    """A label shown folded in its row (steps ③–④) and counted on one line in the summary: a "less likely" label of
    the tool that the lawyer has not worked on (no view, note or own wording). Display only."""
    if p.get("off") or r["decision"]["status"] != "candidate" or is_own_use(r) or not less_tag(r, p):
        return False
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid) or {}
    if any((o.get(k) or "").strip() for k in ("note", "text_assessment", "text_commission")):
        return False
    return view_of(pid, p["part"]) == "To check"


def label_groups(r, parts):
    """The labels of a row as shown on the screen: the tool's two vertical links in the same direction (an input and a
    resale link) form one label, as in the Word document, when neither is dismissed and both have the same view;
    their "Your view" then sets both. [[part, ...], ...] in the order of the parts."""
    pid = cmp.pair_id(r)
    groups = []
    for p in parts:
        if p["kind"] == "v" and p["origin"] == "tool" and not p["off"]:
            g = next((g for g in groups if g[0]["kind"] == "v" and g[0]["origin"] == "tool" and not g[0]["off"]
                      and g[0]["up"] == p["up"] and view_of(pid, g[0]["part"]) == view_of(pid, p["part"])), None)
            if g is not None:
                g.append(p)
                continue
        groups.append([p])
    return groups


def assign_commission(entries, parts, target):
    """The Commission's parts of a row, each next to the label it belongs to: [[entries] per label]. parts: the labels
    as shown ({kind, up, off}; kind "row" for a line of the whole row). A part for the whole row ("", e.g. a failed
    search) and anything that matches no label go to the first line."""
    out = [[] for _ in parts] or [[]]

    def first(test):
        return next((i for i, p in enumerate(parts) if not p.get("off") and test(p)), 0)
    for e in entries:
        label = e[0]
        if label.startswith("horizontal"):
            i = first(lambda p: p.get("kind") == "h")
        elif label == BOTH_DIRECTIONS:
            i = first(lambda p: p.get("kind") == "v")
        elif label.startswith("vertical, "):
            up = "a" if label.startswith(f"vertical, {target} →") else "b"
            i = first(lambda p: p.get("kind") == "v" and p.get("up") == up)
            if i == 0 and not (parts and parts[0].get("kind") == "v" and parts[0].get("up") == up):
                i = first(lambda p: p.get("kind") == "v")
        else:
            i = 0
        out[i].append(e)
    # links in both directions: each side's markets are given once, beside the first vertical label; the label in the
    # other direction says so (otherwise its Commission cell would stay empty)
    both = next((e for e in entries if e[0] == BOTH_DIRECTIONS), None)
    if both:
        for i, p in enumerate(parts):
            if p.get("kind") == "v" and not p.get("off") and not out[i]:
                out[i].append(("", ["the same markets as the vertical label above: the links run in both "
                                    "directions, so each side's markets are given once there"], both[2]))
    return out


def portco_sentence(target, portco, pairs, status, own_where="in the collapsed section below",
                    less_where="in the collapsed section “Less likely” below"):
    """One sentence per portfolio company, counted by business area (not by pairs), assembled in code. Rows that
    involve only own use are counted separately: they sit in their own section (on screen collapsed, in the Word
    document the table "Own Use"; side lines count with the main activities)."""
    n = len(dict.fromkeys(r["label_b"] for r in pairs))
    live = [r for r in pairs if kept(status[cmp.pair_id(r)])]
    P, T = esc(portco), esc(target)
    if not live:
        return (f"{poss(P)} only activity does not meet any activity of {T}." if n == 1 else
                f"None of {poss(P)} {n} activities meets an activity of {T}.")
    main_live = [r for r in live if not is_own_use(r) and not is_less_likely(r)]
    own_live = [r for r in live if is_own_use(r)]
    less_live = [r for r in live if is_less_likely(r)]
    notes = ([f"{plural(len(less_live), 'less likely horizontal label')} (different levels of trade, not fully the same "
              f"direct customers), {less_where}"] if less_live else []) + \
            ([f"{plural(len(own_live), 'potential link')} involving own use, {own_where}"] if own_live else [])
    if not main_live:
        return f"No overlap with {poss(T)} activities except {' and '.join(notes)}."
    k = len({r["label_b"] for r in main_live})
    text = (f"{poss(P)} only activity meets activities of {T}." if n == 1 else
            f"{k} of {poss(P)} {n} activities {'meets' if k == 1 else 'meet'} activities of {T}.")
    return text + "".join(f" Also {x}." for x in notes)


def current_overrides():
    """The lawyer's dismissals, add-backs, notes, edits and labels for the pairs of the current comparison (from the
    override store, which keeps them across partial updates)."""
    ss.setdefault("override_store", {})
    current = {cmp.pair_id(r) for r in ss.results or []}

    def used(o):
        return (o.get("dismiss") or o.get("add_back") or o.get("note") or any((o.get("dismissed_parts") or {}).values())
                or has_added(o) or o.get("text_assessment") or o.get("text_commission") or o.get("views"))
    ss.overrides = {pid: dict(o) for pid, o in ss.override_store.items() if pid in current and used(o)}
    return ss.overrides


# One Commission box per row, with one part per label of the row: its result and what the decisions give for it (the
# market of both products, or of each side's products). The heading of a part names the label of step ③ it belongs
# to: the relationship itself comes from the app's comparison, the decisions only define markets. The internal label
# ("horizontal", "vertical, X → Y", "vertical, both directions") is what the summary and an edited text use.
BOTH_DIRECTIONS = "vertical, both directions"
