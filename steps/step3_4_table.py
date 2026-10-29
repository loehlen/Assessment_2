"""
steps/step3_4_table.py - the table screen of steps ③ and ④: one box per portfolio company, one block per activity
of the target, one row per activity that meets it. Step ③ shows the preliminary assessment; step ④ adds what the
Commission's decisions say (steps/step4_results.py).
"""
import re

import streamlit as st

from logic import comparison as cmp
from logic import rules

from ui.theme import PREF_CSS
from ui.common import _shown, capital, DEV_MODE, esc, h, he_lines, plural, poss, ss, words_list
from ui.labels import dots_html
from ui.activity_display import (activity_line, CUSTOMER_TEXT, display_order, other_name, profile_of,
                                 relationship_rows, short_name, source_markers, stage_text)
from ui.guides import guide_box
from ui.upload_box import upload_box
from steps.step3_assessment import (_entry, _store_override, _store_views, assessment_plain, current_overrides,
                                    direction, failed_pairs, FOUND_BY_WORDS, is_own_use,
                                    joint_link_sentence, kept, label_groups, label_html, label_parts,
                                    less_likely_part, less_tag, name_ab, own_use_flag, part_detail, portco_sentence,
                                    relationship_html, row_status, RULE_WORDS, set_aside_text, side_items, view_of,
                                    VIEWS)
from steps.step4_search import prec_plan, precedent_button, precedent_warnings, stale_units, uploads_changed
from steps.step4_results import commission_htmls, commission_plain, market_overview, market_overview_html


# One box per portfolio company. In it: a counting sentence, then each target activity (the fixed reference point) with
# the portfolio company's activities that meet it; columns: target activity · portco activity · preliminary assessment
# (one line per label, each with its own "Your view") · notes · Edit and Why?. In step ④ the Commission line and the
# Commission's markets follow under each row, full width. Each target activity's block ends with one line naming the
# activities that do not meet it, with the reasons and "Add back" behind "Why?". Side lines are shown with the main
# activities; only rows that involve production for the group's own use are collapsed below ("Own use"). Lawyer's
# labels: a label the lawyer adds is shown and used in the result, the summary and the step ④ grouping, but never
# changes what step ④ searches (no new search).
WIDTHS = [1.5, 1.5, 4.5, 1.4, 0.95]           # step ③


# In step ④ the Commission is its own column, after the preliminary assessment, so that the row reads in the order
# of the work: facts → the AI's assessment → the Commission → the lawyer's view
WIDTHS4 = [1.3, 1.3, 3.4, 2.65, 1.2, 0.95]
STEP3_INNER = [4.6, 1.9]           # the assessment column of step ③: the labels, your view
STEP4_INNER = [2.04, 2.65, 1.36]   # step ④: the labels, the Commission, your view (the sum of WIDTHS4[2:4])
_THEAD = [0]                                    # a fresh key for every table header of this run


def col_widths():
    return WIDTHS4 if ss.get("step") == 4 and ss.get("precedents") else WIDTHS


BLOCK_RULE = "<hr style='margin:4px 0 8px 0;border:none;border-top:1px solid #C9C2B4'>"
ROW_RULE = "<hr style='margin:4px 0 8px 0;border:none;border-top:1px dashed #DDD7CB'>"


def other_cell(act, r):
    """The merged line in a row: 'Side lines' with the items of this row, or 'Own use'."""
    side = "a" if act is r["a"] else "b"
    items = list(side_items(r, side) or act.get("includes") or [])     # in full: the brackets say what an item is
    if is_own_use(r):
        return "**Own use**", [i.replace(" (own use)", "") for i in items]
    return "**Side lines**", [i for i in items if rules.OWN_USE_MARK not in i]


def table_cell(a, company, r=None):
    """An activity in the table: name, stage, sources. What it includes and does is in 'Why?'."""
    if rules.category(a) == "other" and r is not None:
        name, items = other_cell(a, r)
        shown = "; ".join(esc(i) for i in items[:3])
        more = (f" <span class='hov' title='{h('All: ' + '; '.join(items))}'>and {len(items) - 3} more</span>"
                if len(items) > 3 else "")          # every item on hover, as everywhere else
        return f"{name}  \n:gray[{shown}]{more}  \n{source_markers(a, company)}" if shown else \
            f"{name}  \n{source_markers(a, company)}"
    name = other_name(a) if rules.category(a) == "other" else capital(a["product"])
    side = " · :gray[*side line*]" if a.get("side_line") else ""
    return f"**{esc(name)}**  \n{stage_text(a)}{side} · {source_markers(a, company)}"


def assessment_cell(r, status, rv, target, portco, commission=False):
    """The preliminary assessment column: one line per label, each with its own "Your view" and, in step ④
    (commission=True), the Commission's part for that label beside it. The lawyer's wording, if any, replaces the
    app's lines under the labels."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    parts = label_parts(r, target, portco)
    tool_parts = [p["part"] for p in parts if p["origin"] == "tool"]
    edited = (o.get("text_assessment") or "").strip()

    def line(html_text, part_names, kind, off=False, comm=""):
        if commission:          # step ④: the assessment, the Commission, then the lawyer's view (the lawyer last)
            c1, c3, c2 = st.columns(STEP4_INNER, vertical_alignment="top")
            if comm:
                c3.markdown(comm, unsafe_allow_html=True)
        else:
            c1, c2 = st.columns(STEP3_INNER, vertical_alignment="top")
        c1.markdown(html_text, unsafe_allow_html=True)
        part = part_names[0]
        safe = re.sub(r"\W", "", part)         # no backslash inside an f-string (Python before 3.12)
        key = f"view_{rv}_{pid}_{safe}"
        c2.selectbox("Your view", VIEWS, index=VIEWS.index(view_of(pid, part, off)), key=key,
                     format_func=lambda v: "Your view" if v == "To check" else v,
                     label_visibility="collapsed", on_change=_store_views,
                     args=(pid, part_names, key, tool_parts, kind),
                     help="Your view of this relationship: used in the summary and the Word document. “Ask the "
                          "company” puts it into the open points; “Dismiss” removes it.")

    items = []                          # [text, [parts], kind, off], one line (with its own "Your view") each
    metas = []                          # the label of each line, for the Commission's parts (assign_commission)
    folded = []                         # per line: shown folded ("less likely")
    if status == "added back by user":
        items.append(["<span class='lab lab-q'>Added back by you</span> <span class='sub2'>the tool found no overlap; "
                      "see “Why?”</span>", ["row"], "row", False])
        metas.append({"kind": "row"})
        folded.append(False)
    elif r["decision"]["status"] == "unclear":
        items.append(["<span class='lab lab-q'>Unclear: please check</span> <span class='sub2'>see “Why?”</span>",
                      ["row"], "row", bool(o.get("dismiss"))])
        metas.append({"kind": "row"})
        folded.append(False)
    for g in label_groups(r, parts):
        p = g[0]
        fold = not edited and all(less_likely_part(r, q) for q in g)
        head = label_html(p, less=all(less_tag(r, q) for q in g))
        if edited:
            detail = []
        else:   # the basis line once; under it the sentence of each link (two for an input and a resale link)
            details = [part_detail(q, r, target, portco) for q in g]
            joint = joint_link_sentence([q["part"] for q in g], r, target, portco) if len(g) == 2 else None
            detail = details[0][:1] + ([joint] if joint else [x for d in details for x in d[1:]])
        if fold:            # the label and its basis stay visible; what it concerns opens on request
            text = (f"<div>{head}<br>{detail[0] if detail else ''}"
                    + (f"<details class='mkts lfold'><summary>Details</summary>{'<br>'.join(detail[1:])}</details>"
                       if detail[1:] else "") + "</div>")
        else:
            text = "  \n".join([head] + detail)
        items.append([text, [q["part"] for q in g], p["origin"], p["off"]])
        metas.append(p)
        folded.append(fold)
    comms = commission_htmls(r, target, portco, metas, folded) if commission else [""] * len(items)
    # the lawyer's wording and the existing relationship go under the last label, in the same narrow part of the
    # column (not under "Your view" as well)
    extra = []
    if edited:
        extra.append(he_lines(edited) + " <span class='tag'>edited by you</span>")
    rel = (ss.get("rel_rows") or {}).get(pid)
    if rel:
        extra.append(relationship_html(rel, target, portco))
    if items and extra:
        items[-1][0] += "\n\n" + "".join(f"<div class='aext'>{x}</div>" for x in extra)
    for (text, part_names, kind, off), comm in zip(items, comms):
        line(text, part_names, kind, off=off, comm=comm)
    if not items:
        for x in extra:
            st.markdown(x, unsafe_allow_html=True)
        if commission and comms and comms[0]:
            st.markdown(comms[0], unsafe_allow_html=True)


def why_popover(r, target, portco):
    """'Why?': only the reasoning (the sources are in step ② and in the hover of each source, and what the AI saw is in
    the audit log)."""
    c, d = r["comparison"], r["decision"]
    why = []
    if d["horizontal"] or d["status"] in ("unclear", "screened out"):
        why.append(f"**Product** ({esc(c['product_relation'])}): "
                   f"{esc(name_ab(c.get('product_reason', ''), target, portco))}")
    ai_links = [link for link in d["vertical_links"] if d["found_by"][link] != "rule"]
    for link in d["vertical_links"]:
        up, _, down, _ = direction(link, r, target, portco)
        text = f"**Vertical** ({esc(up)} → {esc(down)}, {FOUND_BY_WORDS[d['found_by'][link]]})"
        if d["found_by"][link] == "rule":
            text += ": " + esc(RULE_WORDS[link].format(t=target, p=portco)) + "."
        why.append(text)
    if ai_links and c.get("vertical_reason"):
        why.append(esc(name_ab(c.get("vertical_reason", ""), target, portco)))
    for link, reason in d.get("disregarded", []):
        why.append(set_aside_text(r, link, reason, target, portco))
    # say what "Why?" contains: the AI's reasoning and the app's own checks, for the lawyer to check
    st.caption("The AI's reasoning on the anonymised descriptions (it saw them as “A” and “B”; the app puts the names "
               "back), and the app's own checks: who each company sells to directly, and whether supply or resale is "
               "possible in this row.")
    st.markdown("\n\n".join(why) or "No reason given.")
    if d["horizontal"] and r.get("customers") == "?":
        ca = words_list(_shown(r["a"].get("direct_customers")))
        cb = words_list(_shown(r["b"].get("direct_customers")))
        st.markdown(f"**Direct customers** not stated: {esc(target)} sells to {esc(ca or 'not stated')}; "
                    f"{esc(portco)} to {esc(cb or 'not stated')}. The customers cannot be compared; this does not "
                    "affect the overlap, which is about the products.")
    if d["horizontal"] and r.get("customers") in ("●●●", "●●○", "●○○"):
        ca = words_list(_shown(r["a"].get("direct_customers")))
        cb = words_list(_shown(r["b"].get("direct_customers")))
        st.markdown(f"**Direct customers** {dots_html(r['customers'])}: {esc(target)} sells to {esc(ca or 'not stated')}; "
                    f"{esc(portco)} to {esc(cb or 'not stated')}, so {CUSTOMER_TEXT[r['customers']]}. This compares "
                    "only who each company sells to directly, not the products. Different customers alone do not rule "
                    "out an overlap: customers form a separate market only if the seller can tell which group a "
                    "customer belongs to at the time of sale, customers cannot resell to each other, and the different "
                    "treatment is lasting (Market Definition Notice (88)).", unsafe_allow_html=True)
    if own_use_flag(r) or is_own_use(r):
        st.markdown("**Own use:** produced for the group's own use, not sold on the market (draft Merger Guidelines "
                    "para 103(i)). It cannot supply the other company, so a link where it would be the supplier is set "
                    "aside (shown under “No overlap found”, with “Add back”).")
    if DEV_MODE:
        s = r["sims"]
        rejected = (r.get("matches") or {}).get("rejected") or []
        st.caption(f"Development · pair {cmp.pair_id(r)} · rule: {d['rule']} · code signals: "
                   f"{'; '.join(f'{x} ({w})' for x, w in r['code_signals']) or 'none'} · similarity "
                   f"{s['product']:.2f} · input {s['input_a_to_b']:.2f}/{s['input_b_to_a']:.2f}"
                   + (f" · items not found: {'; '.join(rejected)}" if rejected else "") + f" · flags: {r['flags'] or 'none'}")


@st.dialog("Edit This Row", width="large")
def edit_row(pid, target, portco):
    """'Edit': the wording of the row (and in step ④ of the Commission line), and labels the lawyer adds. The tool's
    labels are dismissed with the box next to them; nothing here changes what step ④ searches."""
    r = next((x for x in ss.results if cmp.pair_id(x) == pid), None)
    if r is None:
        st.write("This row no longer exists.")
        return
    e = ss.override_store.get(pid, {})
    st.caption(f"{r['a'].get('product', '')} ({target}) · {r['b'].get('product', '')} ({portco}). Your changes are "
               "kept for this screen, used in the summary and the output, and recorded in the progress file next to "
               "the app's wording.")
    app_text = assessment_plain(r, target, portco)
    text = st.text_area("Wording of the preliminary assessment", value=e.get("text_assessment") or app_text,
                        height=150, key=f"ed_text_{pid}")
    com_app = commission_plain(r, target, portco)
    com = None
    if com_app:
        com = st.text_area("Wording of the Commission line (step ④)", value=e.get("text_commission") or com_app,
                           height=110, key=f"ed_com_{pid}")
    st.markdown("**Add a Label** (marked “added by you”; to remove one of the tool's labels, use “Dismiss” next to it)")
    add_h = st.checkbox("Potential horizontal overlap", value=bool(e.get("added_h")), key=f"ed_h_{pid}")
    options = ["none", "a>b", "b>a"]
    words = {"none": "No vertical relationship added", "a>b": f"Potential vertical relationship: {target} → {portco}",
             "b>a": f"Potential vertical relationship: {portco} → {target}"}
    add_v = st.radio("Potential vertical relationship (supplier → customer)", options,
                     index=options.index(e.get("added_v") or "none"), format_func=words.get, key=f"ed_v_{pid}")
    b1, b2, b3 = st.columns(3)
    if b1.button("Save", type="primary", key=f"ed_save_{pid}"):
        entry = _entry(pid)
        changed = text.strip() and text.strip() != app_text.strip()
        entry["text_assessment"] = text.strip() if changed else ""
        entry["text_assessment_app"] = app_text if changed else ""
        if com is not None:
            changed = com.strip() and com.strip() != com_app.strip()
            entry["text_commission"] = com.strip() if changed else ""
            entry["text_commission_app"] = com_app if changed else ""
        entry["added_h"] = bool(add_h)
        entry["added_v"] = "" if add_v == "none" else add_v
        st.rerun()
    if b2.button("Restore the app's wording", key=f"ed_restore_{pid}"):
        entry = _entry(pid)
        for k in ("text_assessment", "text_assessment_app", "text_commission", "text_commission_app"):
            entry[k] = ""
        st.rerun()
    if b3.button("Cancel", key=f"ed_cancel_{pid}"):
        st.rerun()


def pair_row(r, status, rv, target, portco, first):
    """One sub-row: target activity (first sub-row of a block only), portco activity, assessment, in step ④ the
    Commission's view, the user's note, and Edit / Why?. The markets themselves are in the table above the rows."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    s = status[pid]
    w = col_widths()
    step4 = len(w) == 6
    # step ④: the assessment and the Commission share one column, so that each label has its Commission part beside it
    cols = st.columns([w[0], w[1], w[2] + w[3], w[4], w[5]] if step4 else w, vertical_alignment="top")
    if first:
        cols[0].markdown(table_cell(r["a"], target, r), unsafe_allow_html=True)
    cols[1].markdown(table_cell(r["b"], portco, r), unsafe_allow_html=True)
    with cols[2]:
        assessment_cell(r, s, rv, target, portco, commission=step4)
    with cols[3]:
        key = f"note_{rv}_{pid}"
        st.text_area("Note", value=o.get("note", ""), key=key, placeholder="Note (optional)",
                     label_visibility="collapsed", height=68, on_change=_store_override, args=(pid, "note", key))
    with cols[4]:
        if st.button("Edit", key=f"edit_row_{rv}_{pid}", width="stretch"):
            edit_row(pid, target, portco)
        with st.popover("Why?", width="stretch"):
            why_popover(r, target, portco)


def table_header(target, portco):
    """The header of a company's table, in ink with white text (as in the Word document); its columns follow the split
    of the assessment column in the rows (assessment · your view, or in step ④ assessment · Commission · your view)."""
    w = col_widths()
    _THEAD[0] += 1
    if len(w) == 6:
        inner = [x * (w[2] + w[3]) / sum(STEP4_INNER) for x in STEP4_INNER]
        widths = w[:2] + inner + w[4:]
        labels = ["Preliminary Assessment", "Commission Market Definition", "Your View"]
    else:
        inner = [x * w[2] / sum(STEP3_INNER) for x in STEP3_INNER]
        widths = w[:2] + inner + w[3:]
        labels = ["Preliminary Assessment", "Your View"]
    labels = [f"{esc(target)} Activity", f"{esc(portco)} Activity"] + labels + ["Notes", ""]
    with st.container(key=f"thead_{_THEAD[0]}"):
        for col, label in zip(st.columns(widths), labels):
            if label:                      # an empty "****" would render as a horizontal line
                col.markdown(f"**{label}**")


def no_overlap_row(ta, rows, rv, target, portco, n_portco, first):
    """The last line of a target activity's block: the portfolio company's activities that do not meet it.
    'Why?' shows the AI's reasons; 'Add back' moves a pair into the table as a row of its own."""
    w = col_widths()
    cols = st.columns([w[0], sum(w[1:-1]), w[-1]], vertical_alignment="top")
    if first:
        cols[0].markdown(table_cell(ta, target), unsafe_allow_html=True)
    def named(r):
        # an own-use side line says why it never meets (it can only be the customer side)
        own = rules.category(r["b"]) == "other" and (rules.captive_only(r["b"]) or any(
            "own use" in why for _, why in r["decision"].get("disregarded") or []))
        return esc(short_name(r["b"])) + (" :gray[(own use only, so it can only be the customer side)]" if own else "")
    if len(rows) >= n_portco:
        cols[1].markdown(f":gray[No overlap found with {poss(esc(portco))} only activity]" if n_portco == 1 else
                         f":gray[No overlap found with any of {poss(esc(portco))} activities]")
    else:
        cols[1].markdown(":gray[No overlap found with:] " + " · ".join(named(r) for r in rows))
    with cols[2].popover("Why?", width="stretch"):
        st.caption("The AI's reasons, pair by pair. “Add back” moves a pair into the table, where you can add a label "
                   "with “Edit” or dismiss it again.")
        for r in rows:
            pid = cmp.pair_id(r)
            key = f"add_{rv}_{pid}"
            reasons = [name_ab(x, target, portco) for x in (r["comparison"].get("product_reason"),
                                                             r["comparison"].get("vertical_reason")) if x]
            text = f"**{esc(short_name(r['b']))}** {stage_text(r['b'])}  \n" + esc(" ".join(reasons) or "No reason given.")
            for link, why in r["decision"].get("disregarded") or []:
                text += "  \n" + set_aside_text(r, link, why, target, portco)
            st.markdown(text)
            st.checkbox("Add back", value=ss.override_store.get(pid, {}).get("add_back", False), key=key,
                        on_change=_store_override, args=(pid, "add_back", key))


def target_block(ta, kept_rows, screened, status, rv, target, portco, n_portco):
    """One target activity: the portfolio company's activities that meet it (one row each), then one line naming
    those that do not. A solid line between target activities, a dashed line between the rows of one target
    activity."""
    st.markdown(BLOCK_RULE, unsafe_allow_html=True)
    for k, r in enumerate(kept_rows):
        if k:
            st.markdown(ROW_RULE, unsafe_allow_html=True)
        pair_row(r, status, rv, target, portco, first=(k == 0))
    if screened:
        if kept_rows:
            st.markdown(ROW_RULE, unsafe_allow_html=True)
        no_overlap_row(ta, screened, rv, target, portco, n_portco, first=not kept_rows)


def company_lines(target, portco, pairs, status):
    """Under each portfolio company's heading: the counting sentence only (the results are clear from the table
    itself). The existing relationship is shown in the rows (relationship_rows)."""
    st.markdown(portco_sentence(target, portco, pairs, status))


def portco_section(i, p, target, pairs, status, rv):
    """One box per portfolio company. Every compared target activity appears once, in the target's order: with the
    rows that meet it and a line naming what does not. Rows involving only own use are collapsed below.
    A portfolio company where nothing meets: its table is folded into one collapsed box, "open to
    check", with the same lines, reasons and "Add back" inside; once a pair is added back, the box opens up again."""
    with st.container(border=True):
        st.markdown(f"#### {i}. {esc(p)}")
        company_lines(target, p, pairs, status)
        kept_rows = [r for r in pairs if kept(status[cmp.pair_id(r)])]
        ids, rel = relationship_rows(target, p, kept_rows)
        ss.rel_rows = {**(ss.get("rel_rows") or {}), **{pid: rel for pid in ids}}
        if rel and not ids:
            # no kept row to show it in (nothing meets): under the counting sentence, so that it is not lost; a
            # supply or distribution agreement can itself point to a vertical relationship
            st.markdown(relationship_html(rel, target, p), unsafe_allow_html=True)
        excluded = [a for a in ss.confirmed.get(p, []) if a.get("excluded") and not a.get("own_use")]
        if excluded:
            st.caption("Not compared (excluded by you): " + "; ".join(
                f"{esc(a['product'])} ({esc(a.get('exclusion_reason', ''))})" for a in excluded))
        own = [a for a in ss.confirmed.get(p, []) if a.get("excluded") and a.get("own_use")]
        if own:
            items = [i.replace(" " + rules.OWN_USE_MARK, "") for a in own for i in a.get("includes") or [] if i]
            st.caption("Not compared, because it is production for the group's own use, not offered on the market: "
                       + esc("; ".join(items)))
        gaps = [a for a in ss.confirmed.get(p, []) if rules.is_gap(a) and not a.get("excluded")]
        if gaps:
            st.caption("Not compared, because the sources do not say what it offers (a question for the company): "
                       + "; ".join(esc(rules.gap_name(a)) for a in gaps))
        t_acts = [ss.confirmed[target][k] for k in display_order(ss.confirmed[target])
                  if not ss.confirmed[target][k].get("excluded") and not rules.is_gap(ss.confirmed[target][k])]
        n_portco = len([a for a in ss.confirmed.get(p, []) if not a.get("excluded") and not rules.is_gap(a)])
        by_target = {}
        for r in pairs:
            by_target.setdefault(r["a"].get("aid") or r["label_a"], []).append(r)

        def rows_of(ta):
            return by_target.get(ta.get("aid"), [])

        def is_out(r):
            return status[cmp.pair_id(r)] == "screened out"

        nothing_meets = bool(pairs) and all(is_out(r) for r in pairs)
        if nothing_meets:
            with st.expander(f"No overlap found with any activity of {esc(target)} · open to check the reasons or add "
                             "a pair back"):
                section_body(t_acts, rows_of, is_out, pairs, status, rv, target, p, n_portco, nested=True)
        else:
            section_body(t_acts, rows_of, is_out, pairs, status, rv, target, p, n_portco, nested=False)


def section_body(t_acts, rows_of, is_out, pairs, status, rv, target, p, n_portco, nested):
    """The table of one portfolio company's box: every target activity (side lines included), then the rows
    that involve only own use, collapsed. Rows with only a "less likely" label stay in the table, marked as such with
    their details folded, so that the lawyer sees every row once. Inside the collapsed box (nested) Streamlit allows no
    second expander, so "Own use" is a plain sub-heading there."""
    table_header(target, p)
    for ta in t_acts:
        rs = rows_of(ta)
        main_rows = [r for r in rs if not is_out(r) and not is_own_use(r)]
        screened = [r for r in rs if is_out(r)]
        if main_rows or screened:
            target_block(ta, main_rows, screened, status, rv, target, p, n_portco)
    own_rows = [r for r in pairs if not is_out(r) and is_own_use(r)]
    if own_rows:
        title = (f"Own Use: {plural(len(own_rows), 'potential link')} (production for the group itself, which can only "
                 "be the customer side)")
        if nested:
            st.markdown(f"**{title}**")
            own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco)
        else:
            with st.expander(title):
                own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco)


def own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco):
    """The rows of the folded section "Own use", in the target's order."""
    table_header(target, p)
    ids = {cmp.pair_id(r) for r in own_rows}
    for ta in t_acts:
        kept_rows = [r for r in rows_of(ta) if cmp.pair_id(r) in ids]
        if kept_rows:
            target_block(ta, kept_rows, [], status, rv, target, p, n_portco)


STEP3_TEXT = ("Every activity of the target, compared with every activity of each portfolio company. Check each row: "
              "set your view on each label (or dismiss it), add what is missing with “Edit”, or adjust the wording.")
STEP4_TEXT = ("How the European Commission defined the markets of the products in the rows you kept, quoted from its "
              "decisions: first each market once, then in each row what follows for its labels.")


def stage_overview(ai, step=3):
    _THEAD[0] = 0                      # the table headers are numbered afresh on every run of the page
    st.header("④ Commission Market Definitions" if step == 4 else "③ Preliminary Assessment")
    st.write(STEP4_TEXT if step == 4 else STEP3_TEXT)
    st.html(PREF_CSS)                  # the hover boxes (sources, paragraphs, markets); style only, no space
    guide_box(4 if step == 4 else 3)
    ov = market_overview() if step == 4 and ss.get("precedents") else None
    if ov and ov["none"] and not ov["lines"]:
        # nothing at all was found: the database holds no decision for this screen (a partial result is explained in
        # the limits of the guide above)
        st.warning("None of the products in this screen is covered by a decision in the app's database. This does not "
                   "mean that the Commission has never defined these markets: the database holds only a limited set "
                   "of decisions. If you know or find a relevant decision (for example in the Commission's case search "
                   "or a legal database), add it under “Add a Commission Decision or Extract” at the end of this step, "
                   "then press “Update the market definitions”.")
    if ss.get("loaded_from"):
        lf = ss.loaded_from
        st.caption(f"Continued from a saved progress file ({esc((lf.get('created') or 'unknown date').replace('T', ' '))}); "
                   "no AI call was made to restore it.")
    results = ss.results
    target = ss.companies[0]["name"]
    portcos = [c["name"] for c in ss.companies[1:]]
    rv = ss.results_version
    current_overrides()
    ss.rel_rows = {}                   # filled per company in portco_section, read by the rows
    status = {cmp.pair_id(r): row_status(r) for r in results}
    units, todo = prec_plan()
    ss.prec_stale = stale_units(todo)
    if ss.get("precedents"):
        precedent_warnings(units)
    failed = failed_pairs()
    if failed:
        st.warning(f"{plural(len(failed), 'comparison')} could not be made: the AI call returned an error (the rows "
                   "marked “Unclear”; see “Why?”). Go back to step ② and press “Update the comparison” to send "
                   f"{'it' if len(failed) == 1 else 'them'} again.")
    if step == 4 and ss.get("precedents"):
        if ov and (ov["lines"] or ov["none"] or ov["failed"]):
            with st.expander("Markets in the Commission's Decisions"):
                st.caption("Every market a product of the rows below falls in, once, with the products of each company "
                           "and the paragraph it rests on (hover for the paragraph, or the market name for the "
                           "Commission's sentence). The rows below name the markets only.")
                st.markdown(market_overview_html(ov), unsafe_allow_html=True)

    with st.expander(f"Target: {target} · Profile and Activities"):
        st.write(profile_of(target))
        for a in [ss.confirmed[target][i] for i in display_order(ss.confirmed[target])]:
            st.markdown(activity_line(a, target), unsafe_allow_html=True)

    # the decisions used are listed in the sidebar ("Commission decisions"), not above the rows
    for i, p in enumerate(portcos, start=1):
        portco_section(i, p, target, [r for r in results if r["portco"] == p], status, rv)

    # no checklist of the Market Definition Notice on screen: "No precedent" already says the market is to be assessed
    # under the Notice
    st.divider()
    if units:
        upload_box(ai)
        if uploads_changed():
            st.warning("A decision was added or removed after the last search: press “Update the market definitions” "
                       "so that the search uses the decisions as they are now. Until then, the rows show the result of "
                       "the earlier search.")
    precedent_button(units, todo, step)
