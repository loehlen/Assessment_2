"""
steps/step1_companies.py - step ① Companies: the target and the portfolio companies (name, website, other names,
source of the activities), the example buttons, the confidentiality warnings, and the research of each company
(logic/activity_mapping.py), which leads to step ②.
"""
import concurrent.futures as cf
import copy
import hashlib
import json
import time

import streamlit as st

from logic import activity_mapping as am
from logic import ai_client
from logic import comparison as cmp
from logic import examples

from ui.common import go_to, log_stage, MAX_PORTCOS, now_local, plural, poss, ss, words_list
from ui.working_screen import start_work, WorkCard


SOURCE_HELP = ("web search: public websites only · my description: no web search, only the text you enter · "
               "both: web search plus your text as an additional source")
DESCRIPTION_HELP = ("Describe what the company does: its business areas, products, customers and countries. The text "
                    "is sent to the AI provider only in this company's own call, like search results, and is never "
                    "shown together with another company's name.")


# The portfolio companies are form rows (one per company, under an ink header like the table of step ③). Each row
# has its own id, so removing a row keeps what is typed in the others; its fields are ordinary widgets keyed by the id.
PF_KEY = {"name": "pfn", "website": "pfw", "aliases": "pfa", "source": "pfs", "desc": "pfd"}
PF_WIDTHS = [2.2, 2, 2.4, 1.6, 0.4]
ALIAS_HELP = ("Short names or former names, comma-separated: for example the name without its legal form, or the name the "
              "company had before. Like the name itself, "
              "they are removed from every anonymised description before a comparison. The confidentiality check only "
              "recognises names it knows; parts of a name joined by “&” or “and” are recognised automatically.")


def pf_key(field, i):
    return f"{PF_KEY[field]}_{i}"


def _drop_row(i):
    for field in PF_KEY:
        ss.pop(pf_key(field, i), None)


def load_portfolio(rows):
    """Fills the portfolio rows of step ① (an example, or the companies of the current run); no rows = one empty row.
    New ids each time, so no widget of the previous rows is reused."""
    for i in ss.get("pf_ids") or []:
        _drop_row(i)
    rows = rows or [{}]
    start = ss.get("pf_next", 0)
    ss.pf_ids, ss.pf_next = list(range(start, start + len(rows))), start + len(rows)
    for i, r in zip(ss.pf_ids, rows):
        for field in ("name", "website", "aliases", "desc"):
            ss[pf_key(field, i)] = r.get(field) or ""
        ss[pf_key("source", i)] = r.get("source") if r.get("source") in am.SOURCE_OPTIONS else "web search"


def add_portco():
    i = ss.get("pf_next", 0)
    ss.pf_ids, ss.pf_next = list(ss.get("pf_ids") or []) + [i], i + 1
    ss[pf_key("source", i)] = "web search"


def remove_portco(i):
    _drop_row(i)
    ss.pf_ids = [j for j in ss.pf_ids if j != i]
    if not ss.pf_ids:
        add_portco()


def portfolio_entries():
    """The filled portfolio rows as company dicts (without role), in the order shown."""
    rows = []
    for i in ss.get("pf_ids") or []:
        name = (ss.get(pf_key("name", i)) or "").strip()
        if not name:
            continue
        source = ss.get(pf_key("source", i))
        source = source if source in am.SOURCE_OPTIONS else "web search"
        rows.append({"name": name, "website": (ss.get(pf_key("website", i)) or "").strip(),
                     "aliases": [a.strip() for a in (ss.get(pf_key("aliases", i)) or "").split(",") if a.strip()],
                     "source": source,
                     "pasted": (ss.get(pf_key("desc", i)) or "").strip() if source != "web search" else ""})
    return rows


def fill_example(key):
    """'Try an example' (button callback): fills in one of the examples (logic/examples.py). The run itself is live."""
    ex = examples.EXAMPLES[key]
    ss.example = key
    t = examples.COMPANIES[ex["target"]]
    ss.t_name, ss.t_web, ss.t_aliases = ex["target"], t["website"], ", ".join(t["aliases"])
    ss.t_source, ss.t_desc = "web search", ""
    typed = ex.get("sources", {})            # a company the test case describes ("my description" or "both")
    load_portfolio([{"name": n, "website": examples.COMPANIES[n]["website"],
                     "aliases": ", ".join(examples.COMPANIES[n]["aliases"]),
                     "source": typed.get(n, ("web search", ""))[0], "desc": typed.get(n, ("web search", ""))[1]}
                    for n in ex["portfolio"]])


def restore_inputs():
    """Widgets that are not shown lose their values in Streamlit; when the user comes back to step ①, the
    companies of the current run are filled in again."""
    if ss.get("companies") and "t_name" not in ss:
        t = ss.companies[0]
        ss.t_name, ss.t_web, ss.t_aliases = t["name"], t.get("website", ""), ", ".join(t.get("aliases", []))
        ss.t_source, ss.t_desc = am.source_mode(t), t.get("pasted", "")
        load_portfolio([{"name": c["name"], "website": c.get("website", ""), "aliases": ", ".join(c.get("aliases", [])),
                         "source": am.source_mode(c), "desc": c.get("pasted", "")} for c in ss.companies[1:]])


def example_buttons():
    st.markdown("**Try an Example**")
    st.caption("The examples use real companies in a hypothetical portfolio: no real transaction is implied. "
               "The research and the comparison run live.")
    with st.container(horizontal=True):          # side by side, not spread over the page width
        for key, ex in examples.EXAMPLES.items():
            st.button(ex["button"], key=f"ex_{key}", on_click=fill_example, args=(key,))
    # what the loaded example shows, as a line rather than a hover tip (a tip stays on screen after the click)
    ex = examples.EXAMPLES.get(ss.get("example"))
    if ex and ss.get("t_name") == ex["target"]:
        st.caption(f"**{ex['button']}:** {ex['what']}.")


def target_card():
    with st.container(border=True):
        st.markdown("**The Target**")
        st.caption("The company or business being acquired.")
        c1, c2 = st.columns(2)
        c1.text_input("Name", key="t_name")
        c2.text_input("Website (optional)", key="t_web", placeholder="e.g. company.com",
                      help="Identifies the company in the web search and marks its own pages as company sources.")
        st.radio("Activities from", am.SOURCE_OPTIONS, key="t_source", horizontal=True, help=SOURCE_HELP)
        if ss.get("t_source", "web search") != "web search":
            st.text_area("Description of the target's activities", key="t_desc", height=140, help=DESCRIPTION_HELP)
        with st.expander("Other Names (Optional)"):
            st.text_input("Other names of the company, comma-separated", key="t_aliases",
                          placeholder="e.g. a short name, a former name", help=ALIAS_HELP)


def portfolio_card():
    if "pf_ids" not in ss:
        load_portfolio([])
    with st.container(border=True, key="pfbox"):
        st.markdown("**The Buyer's Portfolio Companies**")
        st.caption(f"One row per company, up to {MAX_PORTCOS}. One row is enough: if the buyer is a single company "
                   "or group, enter the buyer itself.")
        with st.container(key="thead_pf"):              # the ink header of the tables in steps ③ and ④
            h = st.columns(PF_WIDTHS, vertical_alignment="center")
            h[0].markdown("**Name**")
            h[1].markdown("**Website** (optional)", help="Identifies the company in the web search and marks its own "
                                                          "pages as company sources.")
            h[2].markdown("**Other Names** (optional)", help=ALIAS_HELP)
            h[3].markdown("**Activities From**", help=SOURCE_HELP)
        for n, i in enumerate(ss.pf_ids, start=1):
            with st.container(key=f"pfrow_{i}"):
                c = st.columns(PF_WIDTHS, vertical_alignment="center")
                c[0].text_input(f"Name of portfolio company {n}", key=pf_key("name", i), label_visibility="collapsed",
                                placeholder="Company name")
                c[1].text_input(f"Website of portfolio company {n}", key=pf_key("website", i),
                                label_visibility="collapsed", placeholder="e.g. company.com")
                c[2].text_input(f"Other names of portfolio company {n}", key=pf_key("aliases", i),
                                label_visibility="collapsed", placeholder="Short or former names, brands")
                c[3].selectbox(f"Activities of portfolio company {n} from", am.SOURCE_OPTIONS, key=pf_key("source", i),
                               label_visibility="collapsed")
                c[4].button("×", key=f"pfx_{i}", help="Remove this company", type="tertiary",
                            on_click=remove_portco, args=(i,))
                if ss.get(pf_key("source", i), "web search") != "web search":
                    name = (ss.get(pf_key("name", i)) or "").strip() or f"portfolio company {n}"
                    st.text_area(f"Description of {poss(name)} activities", key=pf_key("desc", i), height=110,
                                 help=DESCRIPTION_HELP)
        with st.container(horizontal=True, vertical_alignment="center"):
            st.button("＋ Add a portfolio company", key="pf_add", on_click=add_portco,
                      disabled=len(ss.pf_ids) >= MAX_PORTCOS)
            st.caption(f"{len(ss.pf_ids)} of {MAX_PORTCOS}")


# Text the lawyer types: a description that names another company of the screen is not blocked but
# shown with a warning; the lawyer decides ("Send anyway"), and the decision is recorded with the company in the audit
# log. What may be typed into an AI tool is the lawyer's professional responsibility; the warning catches slips.
def typed_names(c, companies):
    return am.other_names_in(c.get("pasted") or "", c["name"], companies) if (c.get("pasted") or "").strip() else []


def send_key(name, found):
    return "send_" + hashlib.sha1((name + "|" + "|".join(sorted(found))).encode()).hexdigest()[:12]


SEND_ANYWAY = "Send anyway (my responsibility; recorded in the audit log)"


def typed_warning(name, found, what="The description of"):
    st.warning(f"{what} {name} names {words_list(found)}, another company in this screen. The description is sent "
               f"in {poss(name)} own research call, so the AI would see both names together. Change the text, or send it "
               "anyway if the sentence reveals nothing confidential.")


def typed_text_warnings(companies):
    """Shows the warnings; returns the companies whose description the lawyer sends anyway."""
    sent = []
    for c in companies:
        found = typed_names(c, companies)
        if found:
            typed_warning(c["name"], found)
            if st.checkbox(SEND_ANYWAY, key=send_key(c["name"], found)):
                sent.append(c["name"])
    return sent


def read_companies():
    """The target and the portfolio companies as entered, and the problems that stop the run."""
    t_source = ss.get("t_source", "web search")
    target = {"name": (ss.get("t_name") or "").strip(), "role": "target", "website": (ss.get("t_web") or "").strip(),
              "aliases": [a.strip() for a in (ss.get("t_aliases") or "").split(",") if a.strip()],
              "source": t_source, "pasted": (ss.get("t_desc") or "").strip() if t_source != "web search" else ""}
    portcos = [dict(r, role="portco") for r in portfolio_entries()]
    companies = [target] + portcos
    problems = []
    if not target["name"]:
        problems.append("Enter the name of the target.")
    if not portcos:
        problems.append("Enter at least one portfolio company (or the buyer itself).")
    if len(portcos) > MAX_PORTCOS:
        problems.append(f"Enter at most {MAX_PORTCOS} portfolio companies.")
    lowered = [c["name"].lower() for c in companies if c["name"]]
    if len(lowered) != len(set(lowered)):
        problems.append("Each company may be entered only once.")
    for c in companies:
        if c["name"] and c["source"] == "my description" and not c["pasted"]:
            problems.append(f"Enter a description for {c['name']}, or choose web search.")
        found = typed_names(c, companies) if c["name"] else []
        if found and ss.get(send_key(c["name"], found)):
            c["typed_names_confirmed"] = found
        elif found:
            problems.append(f"The description of {c['name']} names {words_list(found)}: change the text, or tick "
                            "“Send anyway”.")
    return companies, problems


def stage_companies(ai):
    st.header("① Companies")
    st.markdown("Enter the company to be bought (the *target*) and the businesses the buyer already has (the "
                "*portfolio companies*): for an investor such as a private equity fund, one row for each company it "
                "owns; for a company buying another, one row with the buyer itself. Each is looked at together with its "
                "subsidiaries and brands, because EU merger control looks at the buyer's whole group. For the target, "
                "enter only the business being sold, for example a division rather than the seller's whole group.")
    restore_inputs()
    example_buttons()
    target_card()
    portfolio_card()
    sent = typed_text_warnings(read_companies()[0])
    together = ("the AI never sees two company names together" if not sent else
                f"the AI sees two company names together only in the description{'s' if len(sent) > 1 else ''} of "
                f"{words_list(sent)} that you send anyway")
    st.caption(f"Each company is researched separately; {together}. With web search this takes about one to four "
               "minutes.")
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    submitted = c1.button("Find activities →", type="primary")
    if ss.get("mapped"):
        c2.button("Continue with the current activities →", on_click=go_to, args=(2,))
    if not submitted:
        return
    companies, problems = read_companies()
    if problems:
        st.error(" ".join(problems))
        return
    start_work("mapping", companies=companies)


def company_key(c):
    """What the research of a company depends on: if none of it changed, the company is not searched again."""
    return json.dumps({k: c.get(k) for k in ("name", "website", "aliases", "source", "pasted")}, sort_keys=True,
                      ensure_ascii=False)


def run_mapping(ai, companies):
    """Maps the companies that are new or whose input changed; the others keep their research and the
    user's edits of their activities. A new screen starts with "↺ New screen" (reset_all), not here."""
    first, t0 = ss.log.mark(), time.time()
    old, old_keys = ss.get("mapped") or {}, ss.get("map_keys") or {}
    kept = {c["name"] for c in companies if c["name"] in old and not old[c["name"]].get("error")
            and old_keys.get(c["name"]) == company_key(c)}
    todo = [c for c in companies if c["name"] not in kept]
    mapped = {n: old[n] for n in kept}
    searching = any(am.source_mode(c) != "my description" for c in todo)
    title = "Researching the Companies" if searching else "Reading Your Descriptions"
    note = ("Each company is researched on its own, on public websites. This usually takes one to four minutes."
            if searching else "Each company is read on its own.")
    n = len(todo)
    card = WorkCard(title, f"0 of {plural(n, 'company', 'companies')} done" if n else "Nothing new to research",
                    note if n else "The companies are unchanged.")
    for name in sorted(kept):
        card.log(f"✔ {name}: kept from before (no change)")
    with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
        futures = {ex.submit(am.map_company, ai, c, companies): c for c in todo}
        for done, fut in enumerate(card.wait(futures), start=1):
            c = futures[fut]
            m = fut.result()
            stamp_date(m)
            mapped[c["name"]] = m
            card.update(done / n, f"{done} of {plural(n, 'company', 'companies')} done")
            if m.get("error"):
                card.log(f"✖ {c['name']}: {m['error']}")
            else:
                origin = ("your description" if am.source_mode(c) == "my description"
                          else f"{len(m['search']['sources'])} sources")
                card.log(f"✔ {c['name']}: {len(m['extraction']['activities'])} activities from {origin}")
    old_acts = ss.get("acts") or {}
    ss.companies = companies
    ss.mapped = {c["name"]: mapped[c["name"]] for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    if ss.get("results") is not None and [c["name"] for c in companies] != ss.get("compared_names"):
        set_aside_comparison()
    if ss.get("results") is None:       # steps ③–⑤ keep the relationships found when the comparison was made
        ss.relationships = am.find_relationships(ss.mapped, companies, ss.get("keep_words") or ())
    ss.acts = {c["name"]: old_acts[c["name"]] if c["name"] in kept and c["name"] in old_acts
               else copy.deepcopy(extracted(ss.mapped[c["name"]])) for c in companies}
    cmp.ensure_ids(ss.acts)
    ss.profiles_edit = {n: t for n, t in (ss.get("profiles_edit") or {}).items() if n in kept}
    ss.acts_version += 1
    log_stage("mapping", first, time.time() - t0)


def set_aside_comparison():
    """The companies of the screen changed (another target, or a company added, removed or renamed): the assessment of
    steps ③–⑤ no longer fits them and is set aside until the activities are compared again. Nothing already paid for
    is lost: the pair results, the vectors, the step ④ searches and the lawyer's views, dismissals and notes stay in
    their stores and are used again for every pair whose activities did not change."""
    ss.results = None
    ss.confirmed = None
    ss.confirmed_hash = None
    ss.compared_names = None
    ss.compared_research = {}


def stamp_date(m):
    """The date the sources were accessed, in the user's time zone (the research ran just now)."""
    if (m or {}).get("search"):
        m["search"]["date"] = now_local().date().isoformat()
    return m


def extracted(m):
    return (m.get("extraction") or {}).get("activities", [])
