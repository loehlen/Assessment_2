"""
steps/step2_activities.py - step ② Activities: each company's profile and activities with their sources, for the
lawyer to check, edit, add, delete or mark as not relevant; mapping a company again; and the button that starts the
comparison of step ③.
"""
import concurrent.futures as cf
import copy
import re
import time

import streamlit as st

from logic import activity_mapping as am
from logic import comparison as cmp
from logic import rules

from ui.common import _shown, capital, esc, go_to, he, log_stage, long_date, plural, ss, words_list
from ui.working_screen import start_work, WorkCard
from ui.activity_display import (activity_line, display_order, display_title, other_name, plain_reason, profile_of,
                                 ROW_RULE_SOLID, SOURCE_KIND, source_markers, SOURCE_STATE, STAGE)
from ui.guides import guide_box
from steps.step1_companies import (company_key, DESCRIPTION_HELP, extracted, SEND_ANYWAY, send_key, SOURCE_HELP,
                                   stamp_date, typed_warning)
from steps.step3_assessment import activities_hash, failed_pairs, prepare_comparison


def new_activity():
    return {"aid": cmp.new_aid(), "excluded": False, "exclusion_reason": "", "business_area": "not stated", "sector": "not stated",
            "entity": "not stated", "brands": [], "category": "main", "category_reason": "added by user",
            "product": "", "includes": [], "description": "not stated", "intended_use": "not stated",
            "main_inputs": ["not stated"], "value_chain_level": "finished products", "direct_customers": ["not stated"],
            "customer_details": "not stated", "end_users": "not stated", "sales_channels": "not stated",
            "countries_of_sale": ["not stated"], "status": "on the market", "source_numbers": [],
            "evidence": "added by user", "verified_source": False, "origin": "added by user"}


def _text(v):
    v = (v or "").strip()
    return v or "not stated"


def _items(text, sep):
    return [x.strip() for x in (text or "").replace("\n", sep).split(sep) if x.strip()]


def form_values(a):
    """What the edit form shows for an activity, field by field."""
    levels = list(rules.VALUE_CHAIN_LEVELS)

    def plain(field):
        return "" if a.get(field) == "not stated" else a.get(field, "")
    return {
        # the merged line has the same name here as in the table
        "product": other_name(a) if rules.category(a) == "other" and a.get("product") == "Other activities"
        else a.get("product", ""),
        "includes": "\n".join(a.get("includes") or []),
        "value_chain_level": a["value_chain_level"] if a.get("value_chain_level") in levels else "other",
        "status": a["status"] if a.get("status") in rules.STATUS else rules.STATUS[0],
        "direct_customers": [x for x in a.get("direct_customers") or [] if x in rules.DIRECT_CUSTOMER_TYPES],
        "countries_of_sale": ", ".join(_shown(a.get("countries_of_sale"))),
        "category": rules.category(a),
        "excluded": bool(a.get("excluded")),
        "exclusion_reason": a.get("exclusion_reason", ""),
        "description": (_shown([a.get("description")]) or [""])[0],
        "intended_use": plain("intended_use"),
        "main_inputs": "; ".join(_shown(a.get("main_inputs"))),
        "customer_details": plain("customer_details"),
        "end_users": a["end_users"] if a.get("end_users") in rules.END_USERS else "not stated",
        "sales_channels": plain("sales_channels"),
        "business_area": plain("business_area"),
        "entity": plain("entity"),
        "brands": ", ".join(a.get("brands") or []),
    }


# How a value of the edit form is stored in the activity (fields not listed are stored as they are).
FORM_STORE = {
    "product": str.strip,
    "includes": lambda v: _items(v, "\n"),
    "direct_customers": lambda v: v or ["not stated"],
    "countries_of_sale": lambda v: _items(v, ",") or ["not stated"],
    "exclusion_reason": str.strip,
    "description": _text,
    "intended_use": _text,
    "main_inputs": lambda v: _items(v, ";") or ["not stated"],
    "customer_details": _text,
    "sales_channels": _text,
    "business_area": _text,
    "entity": _text,
    "brands": lambda v: _items(v, ","),
}


def apply_form(a, given):
    """The activity after "Save" in the edit form: only the fields the lawyer changed are written. A field left as it
    was keeps its exact value, so saving an activity unchanged changes nothing (no pair is sent to the AI again and no
    step ④ search goes out of date)."""
    start = form_values(a)
    new = dict(a)
    for field, value in given.items():
        if value != start[field]:
            store = FORM_STORE.get(field)
            new[field] = store(value) if store else value
    return new


@st.dialog("Activity", width="large")
def edit_activity(company, idx):
    """The edit form: every field filled in, text fields that keep their text, the rarely needed fields folded away."""
    acts = ss.acts[company]
    a = copy.deepcopy(acts[idx]) if idx is not None else new_activity()
    start = form_values(a)
    k = f"ea_{ss.acts_version}_{company}_{idx}_"
    st.caption(f"{company} · {'new activity' if idx is None else 'changes are kept for this screen and recorded in the audit log'}")
    name = st.text_input("Activity", value=start["product"], key=k + "name",
                         help="What the business area offers (product or service), in generic words; who buys it goes under "
                              "“Direct customers”, not into the name; no company or brand names")
    includes = st.text_area("Includes (one item per line)", value=start["includes"], key=k + "inc",
                            height=130, help="Every product type, format and customer group this activity covers")
    c1, c2 = st.columns(2)
    levels = list(rules.VALUE_CHAIN_LEVELS)
    level = c1.selectbox("Level of trade", levels, index=levels.index(start["value_chain_level"]),
                         format_func=lambda x: STAGE[x] if STAGE[x].lower() == x else f"{STAGE[x]} ({x})",
                         key=k + "lvl",
                         help="; ".join(f"{x}: {d}" for x, d in rules.VALUE_CHAIN_LEVELS.items()))
    status = c2.selectbox("Status", rules.STATUS, index=rules.STATUS.index(start["status"]), key=k + "status")
    customers = st.multiselect("Direct customers", list(rules.DIRECT_CUSTOMER_TYPES),
                               default=start["direct_customers"],
                               key=k + "cust", help="Who buys directly from the company, at its own level of trade")
    countries = st.text_input("Countries of sale (comma-separated)", value=start["countries_of_sale"],
                              key=k + "ctry", help="Leave empty if not stated")
    category = st.radio("Category", rules.CATEGORIES, index=rules.CATEGORIES.index(start["category"]), horizontal=True,
                        key=k + "cat", help="main: an activity offered to third parties, as a business in its own "
                                            "right or as a side line · other: production for the group's own use "
                                            "(it can only be the customer side)")
    excluded = st.checkbox("Not relevant to this deal (not compared)", value=start["excluded"], key=k + "excl")
    reason = st.text_input("Reason", value=start["exclusion_reason"], key=k + "reason",
                           placeholder="e.g. a business the fund is selling") if excluded else ""
    with st.expander("More Fields"):
        description = st.text_area("Description", value=start["description"],
                                   key=k + "desc", help="No company, brand, customer or supplier names")
        intended = st.text_input("Intended use", value=start["intended_use"], key=k + "use")
        inputs = st.text_input("Main inputs (separated by semicolons)", value=start["main_inputs"], key=k + "inputs")
        details = st.text_input("Customer details", value=start["customer_details"], key=k + "cdet")
        end_users = st.selectbox("End users", rules.END_USERS, index=rules.END_USERS.index(start["end_users"]),
                                 key=k + "end")
        channels = st.text_input("Sales channels", value=start["sales_channels"], key=k + "chan")
        area = st.text_input("Business area (as the company groups it)", value=start["business_area"], key=k + "area")
        entity = st.text_input("Group companies or brands carrying it", value=start["entity"], key=k + "entity")
        brands = st.text_input("Brands (comma-separated; removed before any comparison)",
                               value=start["brands"], key=k + "brands")
    if idx is not None:
        st.markdown("Sources: " + source_markers(a, company), unsafe_allow_html=True)
    typed = " ".join([name, includes, description, intended, inputs, details, channels, area])
    found = am.other_names_in(typed, company, ss.companies)
    if found:      # the lawyer's own text; the name is removed before the comparison, the rest is sent
        st.warning(f"This text names {words_list(found)}, another company in this screen. Company names are removed "
                   "before the comparison, but the rest of the text is sent. Change the text, or save it anyway.")
        anyway = st.checkbox("Save anyway (my responsibility; recorded in the audit log)", key=k + "anyway")
    b1, b2, b3 = st.columns(3)
    if b1.button("Save", type="primary", key=k + "save"):
        problems = []
        if found and not anyway:
            problems.append(f"The text names {words_list(found)}: change it, or tick “Save anyway”.")
        if not name.strip():
            problems.append("Give the activity a name.")
        if excluded and not reason.strip():
            problems.append("Give a short reason why it is not relevant to this deal.")
        if problems:
            st.error(" ".join(problems))
            return
        new = apply_form(a, {
            "product": name, "includes": includes, "value_chain_level": level, "status": status,
            "direct_customers": customers, "countries_of_sale": countries, "category": category,
            "excluded": excluded, "exclusion_reason": reason, "description": description, "intended_use": intended,
            "main_inputs": inputs, "customer_details": details, "end_users": end_users, "sales_channels": channels,
            "business_area": area, "entity": entity, "brands": brands})
        if idx is None:
            if found:
                new["typed_names_confirmed"] = found
            acts.append(new)
        else:
            # extracted activities carry no "origin" (only added ones do), so any change to one of them is marked
            # as edited, for the audit log
            if cmp.content_of(new) != cmp.content_of(acts[idx]) and new.get("origin") != "added by user":
                new["edited_by_user"] = True
            if found:
                new["typed_names_confirmed"] = found
            new["level_checked"] = True         # saved in the edit form: the lawyer has seen the level
            acts[idx] = new
        ss.acts_version += 1
        st.rerun()
    if idx is not None and b2.button("Delete this activity", key=k + "del"):
        del acts[idx]
        ss.acts_version += 1
        st.rerun()
    if b3.button("Cancel", key=k + "cancel"):
        st.rerun()


def _store_profile(name, key):
    ss.profiles_edit[name] = ss.get(key, "")


def stage_activities(ai):
    st.header("② Activities")
    st.write("Check what each company does: everything after this step builds on these activities. Use “Edit” to "
             "correct an activity, mark it as not relevant to this deal or delete it.")
    cmp.ensure_ids(ss.acts)
    guide_box(2)
    for i, c in enumerate(ss.companies):
        # the break between the target and the portfolio companies: a section heading above each group
        if i == 0:
            st.markdown("<div class='sec'>The Target</div><div class='secsub'>The business to be acquired</div>",
                        unsafe_allow_html=True)
        elif i == 1:
            st.markdown("<div class='sec next'>The Portfolio Companies</div><div class='secsub'>The "
                        "companies the buyer already owns, or the buyer itself, each with its subsidiaries and "
                        "brands</div>",
                        unsafe_allow_html=True)
        company_block(ai, c, i)
    name_word_review()
    problems = activity_problems()
    ss.current_hash = None if problems else activities_hash(ss.acts)
    has_results = ss.get("results") is not None
    failed = failed_pairs()
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    if has_results and ss.current_hash == ss.get("confirmed_hash"):
        sync_state_fields()
        if not failed:
            c1.button("Back to the assessment (no changes) →", type="primary", on_click=go_to, args=(3,))
            return
    label = "Compare activities"
    # an earlier comparison (set aside when the companies changed) still has its pair results: only new pairs are sent
    if (has_results or ss.get("pair_cache")) and not problems:
        plan = prepare_comparison(copy.deepcopy(ss.acts))
        what = "new, changed or failed pair" if failed else "new or changed pair"
        label = (f"Update the comparison: {plural(plan['new'], what)} to compare, {plan['kept']} kept"
                 if plan["new"] else "Update the comparison (nothing new to compare)")
    if c1.button(label, type="primary"):
        if problems:
            st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        else:
            start_work("compare", activities=copy.deepcopy(ss.acts),
                       profiles_text={c["name"]: profile_of(c["name"]) for c in ss.companies})
    if has_results:
        unchanged = ss.current_hash == ss.get("confirmed_hash")      # only failed pairs to send again
        c2.button("Back to the assessment →" if unchanged else "Back to the assessment without these changes →",
                  on_click=go_to, args=(3,))


def sources_list(found):
    """All sources of one company with the result of the app's own visit; links that no longer exist were not used
    and are not listed (the progress file keeps them)."""
    st.markdown(f"**Sources** · accessed {esc(long_date(found.get('date', '')))}")
    live = [s for s in found["sources"] if not s.get("dead")]
    for s in live:
        c = s.get("check") or {}
        link = f"[{esc(display_title(s))}]({s['url']})" if s.get("url") else esc(s["title"])
        state = SOURCE_STATE.get(c.get("state"), "")
        if c.get("state") == "readable" and c.get("kind") == "pdf" and c.get("pages"):
            state = f"PDF, {c['pages']} pages"
        elif state and c.get("reason"):
            # the reason replaces the general phrase after the colon: one statement, no brackets inside brackets
            state = state.split(":")[0] + ": " + plain_reason(c["reason"])
        origin = " · :gray[link written by the AI, not a search citation]" if s.get("origin") == "text link" else ""
        st.markdown(f"[{s['n']}] {link} · *{SOURCE_KIND.get(s.get('type'), s.get('type') or 'unlabelled')}*"
                    + origin + (f" · :gray[{esc(state)}]" if state else ""))


def company_block(ai, c, index):
    name = c["name"]
    m = ss.mapped[name]
    ext = m.get("extraction") or {}
    acts = ss.acts[name]
    v = ss.acts_version
    is_target = c["role"] == "target"
    with st.container(border=True):           # the same box for the target and each portfolio company
        st.markdown(f"#### {name if is_target else f'Portfolio Company {index}: {name}'}")
        facts = [c["website"]] if c.get("website") else []
        if am.source_mode(c) != "web search":
            facts.append(f"activities from: {am.source_mode(c)}")
        if facts:
            st.caption(" · ".join(facts))
        if m.get("error"):
            st.error(m["error"])
        profile = profile_of(name)
        if profile.strip():
            psrc = {"source_numbers": ext.get("profile_source_numbers") or [],
                    "quote_checks": ext.get("profile_quote_checks") or []}
            st.markdown("<div class='prof'>" + he(profile) + (" " + source_markers(psrc, name)
                                                              if psrc["source_numbers"] else "") + "</div>",
                        unsafe_allow_html=True)
        elif not m.get("error"):
            st.caption("No profile found in the sources.")
        for w in ext.get("warnings") or []:
            st.warning(w)
        if acts:
            basis = {"my description": "According to your description",
                     "both": "According to your description and the sources"}.get(am.source_mode(c),
                                                                               "According to the sources")
            st.markdown(f"<div class='lead2'>{basis}, {he(name)} carries out the following activities:</div>",
                        unsafe_allow_html=True)
        for k, i in enumerate(display_order(acts)):
            if k:
                st.markdown(ROW_RULE_SOLID, unsafe_allow_html=True)
            row = st.columns([14, 1], vertical_alignment="top")
            row[0].markdown(activity_line(acts[i], name), unsafe_allow_html=True)
            if row[1].button("Edit", key=f"edit_{v}_{name}_{i}"):
                edit_activity(name, i)
        if not acts:
            st.caption("No activities.")
        named = ext.get("named_without_activity") or []
        if named:               # names without a described activity, one quiet line instead of activity lines
            more = f" and {len(named) - 8} more" if len(named) > 8 else ""
            st.caption("Also named in the sources, without a described activity: " + "; ".join(esc(n) for n in named[:8])
                       + more + ". Add an activity if one of them matters for this deal.")
        main_acts = [a for a in acts if rules.category(a) == "main" and not a.get("excluded") and not rules.is_gap(a)]
        for i, j in rules.possible_duplicates(main_acts):
            a1, a2 = main_acts[i], main_acts[j]
            pair = f"“{esc(a1['product'])}” and “{esc(a2['product'])}”"
            c1, c2 = set(_shown(a1.get("direct_customers"))), set(_shown(a2.get("direct_customers")))
            if c1 and c2 and not c1 & c2:
                # same products for different customers may be separate sales channels
                st.caption(f"Same products, different customers: {pair}. Keep both if they are separate sales "
                           "channels; merge them with “Edit” if they are one activity (widen one, delete the other).")
            else:
                st.caption(f"Possibly the same activity listed twice: {pair}. Merge them with “Edit” if they are "
                           "(widen one, delete the other).")
        if len(main_acts) > rules.MAX_MAIN:
            st.caption(f"More than {rules.MAX_MAIN} business areas: check whether some belong together.")
        if st.button("＋ Add an activity", key=f"add_{v}_{name}"):
            edit_activity(name, None)
        with st.expander("Company Profile, Sources and Map Again"):
            key = f"prof_{v}_{name}"
            st.text_area("Company profile", value=profile, key=key, height=100,
                         on_change=_store_profile, args=(name, key))
            found = m.get("search") or {}
            if found.get("sources"):
                sources_list(found)
            st.markdown("**Map This Company Again** (replaces its profile and activities; the other companies "
                        "are kept)")
            r1, r2 = st.columns(2)
            website = r1.text_input("Website (optional)", value=c.get("website", ""), key=f"reweb_{v}_{name}")
            mode = r2.radio("Activities from", am.SOURCE_OPTIONS, index=am.SOURCE_OPTIONS.index(am.source_mode(c)),
                            key=f"resrc_{v}_{name}", horizontal=True, help=SOURCE_HELP)
            text = st.text_area("Description of the company's activities (used for “my description” and “both”)",
                                value=c.get("pasted", ""), key=f"repaste_{v}_{name}", help=DESCRIPTION_HELP)
            found = am.other_names_in(text, name, ss.companies) if mode != "web search" and text.strip() else []
            if found:
                typed_warning(name, found)
                st.checkbox(SEND_ANYWAY, key=send_key(name, found) + f"_{v}")
            if st.button(f"Map {name} again", key=f"remap_{v}_{name}"):
                if mode == "my description" and not text.strip():
                    st.error("Enter a description, or choose web search.")
                elif found and not ss.get(send_key(name, found) + f"_{v}"):
                    st.error(f"The description names {words_list(found)}: change the text, or tick “Send anyway”.")
                else:
                    start_work("remap", name=name, website=website, mode=mode, pasted=text, confirmed=found)


def remap_company(ai, name, website, mode, pasted, confirmed=()):
    companies = [dict(c, website=website.strip(), source=mode, pasted=pasted.strip(),
                      typed_names_confirmed=list(confirmed or [])) if c["name"] == name else c for c in ss.companies]
    company = next(c for c in companies if c["name"] == name)
    first, t0 = ss.log.mark(), time.time()
    card = WorkCard(f"Researching {name} Again", "Researching …",
                    "Only this company is researched again; the others are kept. This usually takes one to two minutes.")
    with cf.ThreadPoolExecutor(1) as ex:
        fut = ex.submit(am.map_company, ai, company, companies)
        for f in card.wait([fut]):
            ss.mapped[name] = stamp_date(f.result())
    card.update(1.0, "Done")
    card.log(f"{name} researched again in {time.time() - t0:.0f} s")
    ss.companies = companies
    if ss.get("results") is None:       # steps ③–⑤ keep the relationships found when the comparison was made
        ss.relationships = am.find_relationships(ss.mapped, companies, ss.get("keep_words") or ())
    ss.acts[name] = copy.deepcopy(extracted(ss.mapped[name]))
    cmp.ensure_ids(ss.acts)
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    ss.profiles_edit.pop(name, None)
    ss.acts_version += 1
    log_stage("mapping", first, time.time() - t0)


def around(text, word, width=70):
    """The passage around the first place where the word appears."""
    m = re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text, re.IGNORECASE)
    if not m:
        return text[:2 * width]
    start, end = max(0, m.start() - width), min(len(text), m.end() + width)
    return ("…" if start else "") + text[start:end] + ("…" if end < len(text) else "")


def _store_keep(word, key):
    keep = set(ss.get("keep_words") or [])
    dropped = set(ss.get("drop_words") or [])
    if ss.get(key):
        keep.add(word.lower())
        dropped.discard(word.lower())
    else:                       # unticked by the lawyer: never proposed again in this screen
        keep.discard(word.lower())
        dropped.add(word.lower())
    ss.keep_words, ss.drop_words = sorted(keep), sorted(dropped)


# The review box below is not shown: its defaults apply (a word the descriptions also use in lower case is kept as an
# ordinary word, a word used only as a name is removed) and are recorded in the saved progress file. True shows the
# box in step ②, where the lawyer can change each choice.
SHOW_NAME_WORDS = False


def name_word_review():
    """Before the comparison: the brands and group company names that also appear as words in the descriptions.
    They are removed by default (confidentiality first); the lawyer can keep an ordinary product
    word, so the comparison still sees it. The choice is recorded in the audit log."""
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in ss.companies}
    found = cmp.names_used_as_words(ss.companies, ss.acts, group)
    if not found:
        return
    # A word that also appears in lower case ("pedelec batteries") is an ordinary product word, so it is kept by
    # default; the lawyer can untick it (with the word removed, the AI would see "[name removed] batteries" and could
    # miss an obvious horizontal overlap). Words that appear only capitalised (names that slipped into a description)
    # stay removed unless the lawyer keeps one. Both the proposal and the lawyer's choice are recorded in the audit log.
    keep = set(ss.get("keep_words") or [])
    dropped = set(ss.get("drop_words") or [])
    proposed = set(ss.get("keep_proposed") or [])
    if ss.pop("freeze_proposals", False):
        # a screen continued from a saved file keeps the lawyer's saved choice; words the lower-case rule would
        # propose count as already proposed (otherwise they would be ticked on top, changing the activities and
        # making the app report a change nobody had made)
        proposed |= {f["word"].lower() for f in found if f.get("lower_case")}
    for f in found:
        w = f["word"].lower()
        if f.get("lower_case") and w not in dropped and w not in proposed:
            proposed.add(w)
            keep.add(w)
    ss.keep_words, ss.keep_proposed = sorted(keep), sorted(proposed)
    if not SHOW_NAME_WORDS:
        return
    ordinary = [f for f in found if f.get("lower_case")]
    names = [f for f in found if not f.get("lower_case")]
    with st.container(border=True):
        st.markdown(f"**Names That Are Also Used as Words in the Descriptions** · {plural(len(found), 'word')}")
        st.caption("Before the comparison, every company name, brand and group company is removed from the descriptions, "
                   "so that the AI never sees who is involved. Some brands are also ordinary product words (e.g. a brand "
                   "called after its product); removing them can take away what the comparison needs. A word that "
                   "the descriptions also use in lower case is ticked for you, because it is probably an ordinary "
                   "product word: untick it if it identifies the company. Names that appear only as names stay "
                   "removed. The entered names and other names are always removed; a part of a name (e.g. “Black” in "
                   "“Black & Decker”) can be kept if it is an ordinary word here.")
        for f in ordinary:
            keep_word_box(f, keep)
        if names:
            # words that appear only capitalised are almost always names that slipped into a description; they
            # stay removed unless the lawyer opens the list and keeps one
            label = (f"{plural(len(names), 'name')} that appear only as names in the descriptions "
                     "(removed; open to keep one)")
            if ordinary:
                with st.expander(label):
                    for f in names:
                        keep_word_box(f, keep)
            else:
                st.caption(label.replace("open to keep one", "tick one only if it is an ordinary word"))
                for f in names:
                    keep_word_box(f, keep)


def keep_word_box(f, keep):
    ex = "; ".join(f"{esc(c)}: “{esc(around(t, f['word']))}”" for c, t in f["examples"])
    key = f"keep_{ss.acts_version}_{f['word']}"
    st.checkbox(f"Keep “{f['word']}” as an ordinary word", value=f["word"].lower() in keep, key=key,
                help=f"{capital(f.get('kind', 'brand or group company'))} of {f['company']}.",
                on_change=_store_keep, args=(f["word"], key))
    what = "part of the name" if f.get("kind") == "part of the name" else "brand or group company"
    st.caption(f"{what} of {esc(f['company'])} · used in: {ex}")


def activity_problems():
    problems = []
    for c in ss.companies:
        acts = ss.acts.get(c["name"], [])
        for a in acts:
            if not (a.get("product") or "").strip():
                problems.append(f"{c['name']}: an activity has no name.")
            if a.get("excluded") and not (a.get("exclusion_reason") or "").strip():
                problems.append(f"{c['name']}: '{a['product']}': give a short reason why it is not relevant.")
        if not [a for a in acts if not a.get("excluded") and not rules.is_gap(a)]:
            problems.append(f"{c['name']}: no activities to compare. Map the company again, add an activity, or keep "
                            "at least one activity.")
    return problems


def sync_state_fields():
    """An activity saved unchanged in the edit form is no change (activities_hash), but what the save records (the
    level of trade checked, so no more hint) is copied to the confirmed activities, which steps ③-⑤ show."""
    for name, acts in (ss.get("confirmed") or {}).items():
        current = {a.get("aid"): a for a in (ss.get("acts") or {}).get(name, [])}
        for a in acts:
            cur = current.get(a.get("aid"))
            if cur is not None:
                for k in rules.STATE_FIELDS:
                    if k in cur:
                        a[k] = cur[k]
