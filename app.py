"""
app.py - EU Overlap Screen (LAWS90286 Assignment 2): a preliminary EU merger control overlap screen.

Built so far: stages ① Companies, ② Activities and ③ Overlap overview (spec section 5).
Stages ④ market definitions, ⑤ geography and ⑥ export follow.

    streamlit run app.py

Settings (.env in the Codespace, Secrets on Streamlit Cloud; see .env.example):
    DEV_MODE=1, APP_PASSWORD, OPENAI_API_KEY      development: password gate, cost counter, development tools
    MODEL_PROFILE=dev | final                      the models per step (ai_client.py)
    USE_CACHE=1, USE_SAVED_SEARCHES=1              development only: reuse paid calls and the saved Sol searches
With DEV_MODE off (the submitted version) the sidebar asks for the user's own OpenAI key; the course
credentials module replaces that field before the final deployment tests.
"""
import concurrent.futures as cf
import hashlib
import json
import math
import time
from datetime import datetime

import pandas as pd
import streamlit as st

import activity_mapping as am
import ai_client
import comparison as cmp
import examples
import rules

st.set_page_config(page_title="EU Overlap Screen", page_icon="⚖️", layout="wide")

DEV_MODE = ai_client.flag("DEV_MODE")
PROFILE = ai_client.setting("MODEL_PROFILE", "dev")
USE_CACHE = DEV_MODE and ai_client.flag("USE_CACHE", default=True)
USE_SAVED = DEV_MODE and ai_client.flag("USE_SAVED_SEARCHES", default=True)
MAX_PORTCOS = 5

ss = st.session_state
ss.setdefault("log", ai_client.CallLog())     # every AI call of this session
ss.setdefault("versions", {})                 # editor versions per company (a new version = fresh table)
ss.setdefault("n_portcos", 1)
ss.setdefault("stage_logs", {})               # (first, last) position in the call log + seconds, per stage


# =============================================================== credentials
def credentials():
    """Returns the OpenAI key for this session, or stops the script until one is available."""
    with st.sidebar:
        if DEV_MODE:
            expected = ai_client.setting("APP_PASSWORD")
            password = st.text_input("App password", type="password")
            if not expected:
                st.error("APP_PASSWORD is not set in .env or Secrets.")
                st.stop()
            if password != expected:
                st.info("Enter the app password to start.")
                st.stop()
            key = ai_client.setting("OPENAI_API_KEY")
            if not key:
                st.error("OPENAI_API_KEY is not set in .env or Secrets.")
                st.stop()
            return key
        # Placeholder until the course credentials module (github.com/stoneman-mls/openai_credentials) is added
        key = st.text_input("OpenAI API key", type="password",
                            help="Your own key. It is used only for the calls of this session and not stored.")
        if not key:
            st.info("Enter your OpenAI API key in the sidebar to start.")
            st.stop()
        return key


def make_ai(key):
    return ai_client.AI(profile=PROFILE, api_key=key, use_cache=USE_CACHE, log=ss.log)


# =============================================================== small helpers
def is_missing(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or (v is pd.NA)


def clean_text(v):
    """Cell value -> text; an empty cell becomes 'not stated'. Text is kept exactly as it is (no stripping),
    so that an unedited activity produces exactly the abstract of the test runs."""
    if is_missing(v):
        return "not stated"
    s = str(v)
    return s if s.strip() else "not stated"


def clean_list(v, empty=("not stated",)):
    if v is None or (not isinstance(v, (list, tuple)) and not hasattr(v, "tolist") and is_missing(v)):
        return list(empty)
    if hasattr(v, "tolist"):
        v = v.tolist()
    if isinstance(v, str):
        v = [x for x in v.split(";")]
    items = [str(x) for x in v if not is_missing(x) and str(x).strip()]
    return items or list(empty)


def stage_cost(name):
    """Calls, cache hits, cost and time of one stage, from the call log."""
    if name not in ss.stage_logs:
        return ""
    first, last, seconds = ss.stage_logs[name]
    calls = ss.log.calls[first:last]
    text = f"{len(calls)} AI calls"
    if USE_CACHE:
        text += f" ({sum(c['cached'] for c in calls)} from the development cache)"
    text += f" · USD {sum(c['cost'] for c in calls):.4f} (token prices) · {seconds:.0f} s"
    unpriced = sorted({c["model"] for c in calls if not c.get("priced", True)})
    if unpriced:
        text += f" · no price for {', '.join(unpriced)}"
    return text


def reset_after(stage):
    """Results that depend on an earlier stage are discarded when that stage is re-run."""
    order = ["mapping", "confirm"]
    keys = {"mapping": ["mapped", "relationships", "tables", "companies"],
            "confirm": ["confirmed", "confirmed_hash", "results", "names", "profiles_meta", "overrides",
                        "override_store", "profiles_text"]}
    for later in order[order.index(stage):]:
        for k in keys[later]:
            ss.pop(k, None)


# =============================================================== step ① companies
def company_fields(title, k):
    st.markdown(f"**{title}**")
    c1, c2 = st.columns([1, 2])
    c1.text_input("Name", key=f"name_{k}")
    c2.text_input("Identifying description (optional)", key=f"hint_{k}",
                  help="One line that identifies the company and avoids confusion with similar names, e.g. "
                       "'paint manufacturer based in Münster'. Do not name the other companies.")
    with st.expander("Other names and a pasted description (optional)"):
        st.text_input("Other names of the company, comma-separated", key=f"aliases_{k}",
                      help="Short names or former names. Like the name itself, they are removed from every "
                           "anonymised description before a comparison.")
        st.text_area("Description of the company's activities", key=f"pasted_{k}",
                     help="Used as an additional source, marked 'provided by the user'.")


def read_company(k, role):
    return {"name": (ss.get(f"name_{k}") or "").strip(), "role": role,
            "hint": (ss.get(f"hint_{k}") or "").strip(),
            "aliases": [a.strip() for a in (ss.get(f"aliases_{k}") or "").split(",") if a.strip()],
            "pasted": (ss.get(f"pasted_{k}") or "").strip()}


def write_company_fields(k, c):
    ss[f"name_{k}"], ss[f"hint_{k}"] = c["name"], c.get("hint", "")
    ss[f"aliases_{k}"], ss[f"pasted_{k}"] = ", ".join(c.get("aliases", [])), c.get("pasted", "")


def restore_inputs():
    """Widgets that are not shown lose their values in Streamlit; when the user comes back to step ①, the
    companies of the current run are filled in again."""
    if ss.get("companies") and "name_t" not in ss:
        write_company_fields("t", ss.companies[0])
        for i, c in enumerate(ss.companies[1:]):
            write_company_fields(f"p{i}", c)
        ss["n_portcos"] = max(1, len(ss.companies) - 1)


def fill_example():
    """'Try an example': fills in one of the three test cases (examples.py). The run itself is live."""
    tc = (ss.get("example_choice") or "").split(" · ")[0]
    if tc not in examples.TEST_CASES:
        return
    names = [examples.TEST_CASES[tc]] + examples.PORTFOLIO
    for k, name in zip(["t"] + [f"p{i}" for i in range(len(examples.PORTFOLIO))], names):
        write_company_fields(k, {"name": name, **examples.COMPANIES[name], "pasted": ""})
    ss["n_portcos"] = len(examples.PORTFOLIO)


def example_loader():
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    c1.selectbox("Try an example", [f"{tc} · {d}" for tc, d in examples.DESCRIPTIONS.items()], index=None,
                 placeholder="Choose an example (target + four portfolio companies)", key="example_choice")
    c2.button("Fill in", on_click=fill_example, disabled=not ss.get("example_choice"))


def stage_companies(ai):
    st.subheader("① Companies")
    st.write("Enter the company being acquired (the target) and up to five portfolio companies of the buyer. "
             "Each company is analysed as a group, with its subsidiaries and brands; for the target, enter the "
             "entity actually being acquired.")
    restore_inputs()
    example_loader()
    n = st.number_input("Number of portfolio companies", min_value=1, max_value=MAX_PORTCOS, step=1, key="n_portcos")
    with st.form("companies_form"):
        company_fields("Target", "t")
        for i in range(int(n)):
            st.divider()
            company_fields(f"Portfolio company {i + 1}", f"p{i}")
        submitted = st.form_submit_button("Find activities", type="primary")
    if ss.get("mapped"):
        st.button("Continue with the current activities →", on_click=go_to, args=(2,))
    if not submitted:
        return
    companies = [read_company("t", "target")] + [c for c in (read_company(f"p{i}", "portco") for i in range(int(n)))
                                                 if c["name"]]
    problems = []
    if not companies[0]["name"]:
        problems.append("Enter the name of the target.")
    if len(companies) < 2:
        problems.append("Enter at least one portfolio company.")
    lowered = [c["name"].lower() for c in companies if c["name"]]
    if len(lowered) != len(set(lowered)):
        problems.append("Each company may be entered only once.")
    if problems:
        st.error(" ".join(problems))
        return
    reset_after("mapping")
    run_mapping(ai, companies)
    ss.step = 2
    st.rerun()


def run_mapping(ai, companies):
    first, t0 = ss.log.mark(), time.time()
    mapped = {}
    with st.status("Researching each company on public websites (one company per search, in parallel). This "
                   "takes about one to four minutes.", expanded=True) as status:
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(am.map_company, ai, c, companies, USE_SAVED): c["name"] for c in companies}
            for fut in cf.as_completed(futures):
                name = futures[fut]
                m = fut.result()
                mapped[name] = m
                if m["error"]:
                    st.write(f"✖ {name}: {m['error']}")
                else:
                    st.write(f"✔ {name}: {len(m['extraction']['activities'])} activities from "
                             f"{len(m['search']['sources'])} sources")
        status.update(label=f"Activities found in {time.time() - t0:.0f} s", state="complete", expanded=False)
    ss.companies = companies
    ss.mapped = mapped
    ss.relationships = am.find_relationships(mapped, companies)
    ss.tables = {c["name"]: activities_to_df(extracted(mapped[c["name"]]), source_urls(mapped[c["name"]]))
                 for c in companies}
    for c in companies:
        ss.versions[c["name"]] = ss.versions.get(c["name"], 0) + 1
    ss.stage_logs["mapping"] = (first, ss.log.mark(), time.time() - t0)


def extracted(m):
    return (m.get("extraction") or {}).get("activities", [])


def go_to(step):
    ss.step = step


# =============================================================== stage ② activities
EDIT_COLUMNS = ["excluded", "exclusion_reason", "category", "product", "includes", "value_chain_level", "direct_customers", "countries_of_sale",
                "status", "entity", "brands", "description", "intended_use", "main_inputs", "customer_details",
                "end_users", "sales_channels", "business_area", "sector", "category_reason", "source_numbers",
                "evidence"]
CUSTOMER_TEXT = {"●●●": "same direct customers", "●●○": "partly the same direct customers",
                 "●○○": "different direct customers", "?": "direct customers not stated", "": ""}
RELATION_TEXT = {"same product": "same product", "similar product, possibly substitutable": "similar product",
                 "different product": "different product", "not enough information": "not enough information"}


def column_config():
    cc = st.column_config
    return {
        "_check": cc.TextColumn("Source check", disabled=True,
                                help="✔ linked to a source the search returned · ⚠ no verified source"),
        "_link": cc.LinkColumn("Source", display_text="open ↗", disabled=True,
                               help="The first source of this activity; all sources are listed below"),
        "excluded": cc.CheckboxColumn("Not relevant to this deal", default=False,
                                      help="Tick to leave this activity out of the comparison (e.g. a business the "
                                           "fund is selling). Give a short reason; it is recorded in the audit log."),
        "exclusion_reason": cc.TextColumn("Reason", help="Why this activity is not relevant to this deal"),
        "category": cc.SelectboxColumn("Category", options=rules.CATEGORIES, default="main", required=True,
                                       help="main: one of the company's business areas · other: incidental "
                                            "activities and production for own use, combined in one line"),
        "product": cc.TextColumn("Activity", required=True, help="Short generic name, no company or brand names"),
        "includes": cc.ListColumn("Includes", help="Products, formats or customer groups merged into this activity"),
        "value_chain_level": cc.SelectboxColumn("Level of trade", options=list(rules.VALUE_CHAIN_LEVELS),
                                                required=True, default="other",
                                                help="; ".join(f"{k}: {v}" for k, v in rules.VALUE_CHAIN_LEVELS.items())),
        "direct_customers": cc.MultiselectColumn("Direct customers", options=list(rules.DIRECT_CUSTOMER_TYPES),
                                                 default=["not stated"],
                                                 help="Who buys directly from the company, at its own level of trade"),
        "countries_of_sale": cc.ListColumn("Countries of sale", default=["not stated"],
                                           help="Enter countries where the sources give none"),
        "status": cc.SelectboxColumn("Status", options=rules.STATUS, default="on the market"),
        "entity": cc.TextColumn("Group companies / brands"),
        "brands": cc.ListColumn("Brands", help="The only field with brand names; removed before any comparison"),
        "description": cc.TextColumn("Description", help="No company, brand, customer or supplier names"),
        "intended_use": cc.TextColumn("Intended use"),
        "main_inputs": cc.ListColumn("Main inputs"),
        "customer_details": cc.TextColumn("Customer details"),
        "end_users": cc.SelectboxColumn("End users", options=rules.END_USERS, default="not stated"),
        "sales_channels": cc.TextColumn("Sales channels"),
        "business_area": cc.TextColumn("Business area", help="How the company itself groups this activity"),
        "sector": cc.TextColumn("Sector", help="For sorting only, never for filtering"),
        "category_reason": cc.TextColumn("Why this category"),
        "source_numbers": cc.ListColumn("Source numbers", disabled=True),
        "evidence": cc.TextColumn("Evidence", disabled=True, help="Quote or paraphrase from the sources"),
    }


def activities_to_df(acts, urls):
    """The editable table of one company, in the order of the list (_order), so that the confirmed list and the
    labels T-1, P1-1 ... follow it. _origin keeps rows the user added recognisable after a round trip."""
    rows = []
    for i, a in enumerate(acts):
        row = {c: a.get(c) for c in EDIT_COLUMNS}
        row["includes"] = list(a.get("includes") or [])
        row["category"] = rules.category(a)
        row["excluded"] = bool(a.get("excluded", False))
        row["exclusion_reason"] = a.get("exclusion_reason", "")
        row["source_numbers"] = [str(n) for n in a.get("source_numbers", [])]
        row["_link"] = next((urls.get(n) for n in a.get("source_numbers", []) if urls.get(n)), None)
        row["_check"] = ("✔" if a.get("source_numbers") else "⚠ no verified source") + \
            (f" · invalid numbers {a['invalid_source_numbers']} removed" if a.get("invalid_source_numbers") else "")
        row["_order"] = i
        row["_origin"] = a.get("origin", "search")
        rows.append(row)
    return pd.DataFrame(rows, columns=["_check", "_link"] + EDIT_COLUMNS + ["_order", "_origin"])


def df_to_activities(df):
    """Back from the edited table to activity dicts (the format of the extraction). Returns (activities,
    problems). Rows added by the user are marked 'added by user'; deleted rows are gone."""
    acts, problems = [], []
    df = df.copy()
    df["_order"] = pd.to_numeric(df["_order"], errors="coerce").fillna(1e9)
    for _, row in df.sort_values("_order", kind="stable").iterrows():
        added = row["_order"] >= 1e9
        product = clean_text(row.get("product"))
        if added and product == "not stated" and clean_text(row.get("description")) == "not stated":
            continue                                           # an empty row the user added and left blank
        level = row.get("value_chain_level")
        customers = clean_list(row.get("direct_customers"))
        where = f"'{product}'"
        if product == "not stated":
            problems.append(f"An activity has no name (row {len(acts) + 1}).")
        if level not in rules.VALUE_CHAIN_LEVELS:
            problems.append(f"{where}: choose a level of trade.")
        unknown = [c for c in customers if c not in rules.DIRECT_CUSTOMER_TYPES]
        if unknown:
            problems.append(f"{where}: unknown direct customer types {unknown}.")
        sources = [int(n) for n in clean_list(row.get("source_numbers"), empty=()) if str(n).isdigit()]
        excluded = row.get("excluded") is True or (not is_missing(row.get("excluded")) and bool(row.get("excluded")))
        reason_text = row.get("exclusion_reason") if isinstance(row.get("exclusion_reason"), str) else ""
        if excluded and not reason_text.strip():
            problems.append(f"{where}: give a short reason why it is not relevant to this deal.")
        acts.append({
            "excluded": excluded,
            "exclusion_reason": reason_text.strip(),
            "business_area": clean_text(row.get("business_area")),
            "sector": clean_text(row.get("sector")),
            "entity": clean_text(row.get("entity")),
            "brands": clean_list(row.get("brands"), empty=()),
            "category": row.get("category") if row.get("category") in rules.CATEGORIES else "main",
            "merged_from": [],
            "category_reason": clean_text(row.get("category_reason")),
            "product": product,
            "includes": clean_list(row.get("includes"), empty=()),
            "description": clean_text(row.get("description")),
            "intended_use": clean_text(row.get("intended_use")),
            "main_inputs": clean_list(row.get("main_inputs")),
            "value_chain_level": level if level in rules.VALUE_CHAIN_LEVELS else "other",
            "direct_customers": customers,
            "customer_details": clean_text(row.get("customer_details")),
            "end_users": row.get("end_users") if row.get("end_users") in rules.END_USERS else "not stated",
            "sales_channels": clean_text(row.get("sales_channels")),
            "countries_of_sale": clean_list(row.get("countries_of_sale")),
            "status": row.get("status") if row.get("status") in rules.STATUS else "not stated",
            "source_numbers": sources,
            "evidence": clean_text(row.get("evidence")) if not added else "added by user",
            "verified_source": bool(sources),
            "origin": row.get("_origin") if isinstance(row.get("_origin"), str) else
                      ("added by user" if added else "search"),
        })
    return acts, problems


def source_urls(m):
    return {s["n"]: s["url"] for s in ((m.get("search") or {}).get("sources") or []) if s.get("url")}


# Everyday words for the display only; the data and the comparison keep the exact terms of the schema.
CUSTOMER_WORDS = {"consumers": "consumers", "retailers": "shops", "wholesalers / distributors": "wholesalers",
                  "manufacturers / processors": "other manufacturers", "other businesses": "businesses",
                  "public sector": "public bodies", "internal use (captive)": "its own group"}


def words_list(items):
    items = list(dict.fromkeys(items))
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


def everyday(a):
    """What the company does with this activity, in everyday words."""
    if rules.captive_only(a):
        return "only for the group's own use"
    to = words_list([CUSTOMER_WORDS[c] for c in a.get("direct_customers", []) if c in CUSTOMER_WORDS])
    level = a.get("value_chain_level")
    if level == "raw materials":
        return "grows, extracts or trades raw materials" + (f", sold to {to}" if to else "")
    if level == "intermediate products":
        return f"supplies ingredients or components to {to or 'other producers'}"
    if level == "finished products":
        return f"makes products sold to {to}" if to else "makes products"
    if level == "wholesale / distribution":
        return f"resells other companies' products to {to or 'businesses'}"
    if level == "retail":
        return "sells to consumers through its own shops or online"
    if level == "services":
        return f"provides services to {to}" if to else "provides services"
    return ""


def short_item(item):
    """'Hazelnut cultivation (own use) (hazelnut farms)' -> 'Hazelnut cultivation (own use)'."""
    head = item.split(" (")[0]
    return head + (" (own use)" if "(own use)" in item else "")


def activity_bullet(a):
    """One activity in one line: its name, what the company does, three examples."""
    includes = [i for i in a.get("includes") or [] if i]
    if rules.category(a) == "other":
        items = [short_item(i) for i in includes]
        more = f" (+{len(items) - 4} more)" if len(items) > 4 else ""
        return f"- **Other activities:** {'; '.join(items[:4])}{more}"
    line = f"- **{a['product'][:1].upper() + a['product'][1:]}** · {everyday(a)}"
    includes = [i for i in includes if i.strip().lower() != a["product"].strip().lower()]
    if includes:
        line += f" · e.g. {', '.join(includes[:3])}"
    if a.get("status") == "in development":
        line += " · *in development*"
    return line


def activity_list(acts):
    """The activities of one company: business areas, then 'Other activities', then what the user excluded."""
    shown = [a for a in acts if not a.get("excluded")]
    shown = [a for a in shown if rules.category(a) == "main"] + [a for a in shown if rules.category(a) == "other"]
    if shown:
        st.markdown("\n".join(activity_bullet(a) for a in shown))
    excluded = [a for a in acts if a.get("excluded")]
    if excluded:
        st.markdown("*Not relevant to this deal (excluded, not compared):* " + "; ".join(
            f"~~{a['product']}~~ ({a.get('exclusion_reason', '')})" for a in excluded))
    if not acts:
        st.caption("No activities.")


def activity_details(acts, company, m):
    """Everything behind one click: all products, customers, countries, group companies, sources."""
    urls = source_urls(m)
    own_names = next((am.names_of(c) for c in ss.get("companies", []) if c["name"] == company), [company])
    for a in acts:
        includes = ", ".join(a.get("includes") or []) or "not stated"
        countries = ", ".join(c for c in a.get("countries_of_sale", []) if c != "not stated") or "not stated"
        entity = a.get("entity") or ""
        by = f" · by {entity}" if entity and entity != "not stated" and (
            "," in entity or not rules.find_names(entity, own_names)) else ""
        links = " ".join(f"[[{n}]]({urls[n]})" for n in a.get("source_numbers", []) if n in urls)
        if not links:
            links = "*added by you*" if a.get("origin") == "added by user" else "⚠ *no verified source*"
        st.markdown(f"**{a['product']}** ({rules.category(a)}{', excluded' if a.get('excluded') else ''}) · "
                    f"{a['value_chain_level']} · direct customers: {', '.join(a.get('direct_customers', []))} · "
                    f"countries: {countries}{by} {links}  \n:gray[Includes: {includes}]")
    found = m.get("search") or {}
    if found.get("sources"):
        st.markdown(f"**Sources** · search: {found.get('model', '')} · accessed {found.get('date', '')}")
        for s in found["sources"]:
            link = f"[{s['title']}]({s['url']})" if s.get("url") else s["title"]
            st.markdown(f"[{s['n']}] {link} · *{s.get('type') or 'unlabelled'}*")


def show_relationships():
    for company, rs in (ss.get("relationships") or {}).items():
        for r in rs:
            with st.container(border=True):
                st.markdown(f"🔗 **Existing relationship found in public sources:** the sources for **{company}** "
                            f"mention **{r['other']}** ({', '.join(r['names'])}). The tool does not assess it; "
                            "check its nature (supply, distribution, partnership, equity).")
                for p in r["passages"]:
                    st.caption(f"“{p}”")


def profile_of(name):
    """The company profile as confirmed (or edited) by the user, else as extracted."""
    if name in (ss.get("profiles_text") or {}):
        return ss.profiles_text[name]
    return ((ss.mapped.get(name) or {}).get("extraction") or {}).get("company_profile", "")


def stage_activities(ai):
    st.subheader("② Activities")
    st.write("Check what each company does. Everything after this step builds on these activities. Under “Edit” "
             "you can correct, merge, add or delete activities, or mark an activity as not relevant to this deal; "
             "it is then not compared.")
    if DEV_MODE:
        st.caption(stage_cost("mapping"))
    show_relationships()
    edited = {}
    for i, c in enumerate(ss.companies):
        edited[c["name"]] = company_block_edit(ai, c, i)
    current, problems = activities_from_editors(edited)
    ss.current_hash = None if problems else activities_hash(current)
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    if c1.button("Compare activities", type="primary"):
        confirm_activities(ai, current, problems, {n: p for n, (_, p) in edited.items()})
    if ss.get("results") is not None and ss.current_hash == ss.get("confirmed_hash"):
        c2.button("Back to the overview (activities unchanged) →", on_click=go_to, args=(3,))


def company_block_edit(ai, c, index):
    name = c["name"]
    m = ss.mapped[name]
    version = ss.versions.get(name, 0)
    ext = m.get("extraction") or {}
    with st.container(border=True):
        st.markdown(f"#### {'🎯 Target: ' if c['role'] == 'target' else f'Portfolio company {index}: '}{name}")
        if m["error"]:
            st.error(m["error"])
        profile_slot, list_slot = st.container(), st.container()
        details_slot = st.expander("Details: all products, countries, group companies and sources")
        with st.expander("Edit"):
            profile = st.text_area("Company profile", value=profile_of(name), key=f"prof_{name}_{version}",
                                   height=100)
            edited_df = st.data_editor(ss.tables[name], key=f"ed_{name}_{version}", column_config=column_config(),
                                       column_order=["_check", "_link"] + EDIT_COLUMNS, num_rows="dynamic",
                                       hide_index=True)
            st.caption("To merge two activities: widen one (name, includes), then delete the other row.")
            st.markdown("**Map this company again** (replaces its profile and activities; the other companies "
                        "are kept)")
            hint = st.text_input("Identifying description", value=c.get("hint", ""), key=f"rehint_{name}_{version}")
            text = st.text_area("Paste a description of the company's activities", value=c.get("pasted", ""),
                                key=f"repaste_{name}_{version}")
            if st.button(f"Map {name} again", key=f"remap_{name}_{version}"):
                remap_company(ai, name, hint, text)
        acts, _ = df_to_activities(edited_df)
        with profile_slot:
            if profile.strip():
                st.write(profile)
            elif not m["error"]:
                st.caption("No profile found in the sources.")
        with list_slot:
            for w in ext.get("warnings") or []:
                st.warning(w)
            activity_list(acts)
            main_acts = [a for a in acts if rules.category(a) == "main"]
            hints = [f"“{main_acts[i]['product']}” and “{main_acts[j]['product']}”"
                     for i, j in rules.possible_duplicates(main_acts)]
            if hints:
                st.caption("Possibly the same activity listed twice: " + "; ".join(hints) + ". Merge them under "
                           "“Edit” if they are.")
            if len(main_acts) > rules.MAX_MAIN:
                st.caption(f"More than {rules.MAX_MAIN} business areas: check under “Edit” whether some belong "
                           "together.")
        with details_slot:
            activity_details(acts, name, m)
    return edited_df, profile


def remap_company(ai, name, hint, pasted):
    companies = [dict(c, hint=hint.strip(), pasted=pasted.strip()) if c["name"] == name else c
                 for c in ss.companies]
    company = next(c for c in companies if c["name"] == name)
    first, t0 = ss.log.mark(), time.time()
    with st.spinner(f"Mapping {name} ..."):
        ss.mapped[name] = am.map_company(ai, company, companies, USE_SAVED)
    ss.companies = companies
    ss.relationships = am.find_relationships(ss.mapped, companies)
    ss.tables[name] = activities_to_df(extracted(ss.mapped[name]), source_urls(ss.mapped[name]))
    ss.versions[name] = ss.versions.get(name, 0) + 1
    f0, _, s0 = ss.stage_logs.get("mapping", (first, first, 0))
    ss.stage_logs["mapping"] = (f0, ss.log.mark(), s0 + time.time() - t0)
    reset_after("confirm")
    st.rerun()


def activities_from_editors(edited):
    activities, problems = {}, []
    for c in ss.companies:
        df, _ = edited[c["name"]]
        acts, probs = df_to_activities(df)
        activities[c["name"]] = acts
        problems += [f"{c['name']}: {p}" for p in probs]
        if not [a for a in acts if not a.get("excluded")]:
            problems.append(f"{c['name']}: no activities to compare. Paste a description and map the company "
                            "again, add the activities by hand, or keep at least one activity.")
    return activities, problems


def activities_hash(activities):
    return hashlib.sha256(json.dumps(activities, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# =============================================================== stage ③ factual comparison
def confirm_activities(ai, activities, problems, profiles_text):
    if problems:
        st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        return
    reset_after("confirm")
    companies = ss.companies
    target, portcos = companies[0]["name"], [c["name"] for c in companies[1:]]
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in companies}
    names = cmp.collect_names(companies, activities, group)
    compared = {n: [a for a in acts if not a.get("excluded")] for n, acts in activities.items()}
    first, t0 = ss.log.mark(), time.time()
    with st.status("Comparing the activities: one pair of anonymised descriptions per AI call, in parallel",
                   expanded=True) as status:
        profiles, blocked = {}, []
        for c in companies:
            abstracts, problems = cmp.anonymise(compared[c["name"]], names)
            profiles[c["name"]] = {"activities": compared[c["name"]], "abstracts": abstracts}
            blocked += [f"{c['name']} activity {i + 1}: {left}" for i, left in problems]
        st.write(f"✔ Anonymised: {len(rules.name_variants(names))} name variants removed"
                 + (f"; ✖ names left in {len(blocked)} abstracts (their pairs are blocked)" if blocked else
                    "; name check passed for every abstract"))
        try:
            with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
                futures = {ex.submit(cmp.embed_company, ai, n, profiles[n]["activities"], names): n for n in profiles}
                for fut in cf.as_completed(futures):
                    profiles[futures[fut]]["vectors"] = fut.result()
        except Exception as e:  # noqa: BLE001 - never continue without vectors (see comparison.embed_company)
            status.update(label="The comparison stopped", state="error")
            st.error(f"The embeddings failed, so nothing was compared: {type(e).__name__}: {e}. Please try again.")
            return
        st.write("✔ Embeddings: one request per company, anonymised texts only")
        pairs = cmp.build_pairs(target, portcos, profiles)
        bar = st.progress(0.0, text=f"0 of {len(pairs)} pairs compared")
        results = [None] * len(pairs)
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(cmp.assess, ai, p, names): i for i, p in enumerate(pairs)}
            for done, fut in enumerate(cf.as_completed(futures), start=1):
                results[futures[fut]] = fut.result()
                if done % 5 == 0 or done == len(pairs):
                    bar.progress(done / len(pairs), text=f"{done} of {len(pairs)} pairs compared")
        status.update(label=f"{len(pairs)} pairs compared in {time.time() - t0:.0f} s", state="complete",
                      expanded=False)
    ss.confirmed = activities
    ss.profiles_text = profiles_text
    ss.confirmed_hash = activities_hash(activities)
    ss.current_hash = ss.confirmed_hash
    ss.results_version = ss.get("results_version", 0) + 1     # fresh override widgets for new results
    ss.override_store = {}
    ss.names = names
    ss.profiles_meta = {n: {"abstracts": p["abstracts"]} for n, p in profiles.items()}
    ss.results = results
    ss.stage_logs["confirm"] = (first, ss.log.mark(), time.time() - t0)
    for c in companies:            # the tables now show the confirmed state (also after going back to step ②)
        ss.tables[c["name"]] = activities_to_df(activities[c["name"]], source_urls(ss.mapped[c["name"]]))
        ss.versions[c["name"]] = ss.versions.get(c["name"], 0) + 1
    ss.step = 3
    st.rerun()


def reason(r):
    c = r["comparison"]
    return " ".join(x for x in (c.get("product_reason", ""), c.get("vertical_reason", "")) if x)


def flags(r):
    d = r["decision"]
    out = [f for f in r["flags"].split("; ") if f]
    out += [f"✗ {cmp.describe_link(link, ss.companies[0]['name'], r['portco'])} (AI, disregarded: {why})"
            for link, why in d.get("disregarded", [])]
    if r["comparison"].get("blocked") or r["comparison"].get("error"):
        out.append("⚠ " + r["comparison"]["product_reason"])
    return "; ".join(out)


def _store_override(pid, field, key):
    """Widget callback: overrides live in their own store, so they survive when a section is hidden."""
    entry = ss.override_store.setdefault(pid, {"dismiss": False, "add_back": False, "note": ""})
    value = ss.get(key)
    entry[field] = value.strip() if isinstance(value, str) else bool(value)


def kept(status):
    return status in ("candidate", "unclear", "added back by user")


PAIR_ORDER = {"candidate": 0, "added back by user": 1, "unclear": 2, "dismissed by user": 3, "screened out": 4}


def pair_icon(r, status):
    d = r["decision"]
    if status == "dismissed by user":
        return "✖"
    if status == "screened out":
        return "⚪"
    if d["status"] == "unclear":
        return "❔"
    return ("🔴" if d["horizontal"] else "") + ("🟠" if d["vertical_links"] else "") or "↩"


def pair_result_text(r, status, target):
    """The result of one pair in words, with the names re-attached."""
    d = r["decision"]
    if status == "screened out" or (status == "dismissed by user" and d["status"] == "screened out"):
        out = "no overlap found (" + RELATION_TEXT.get(r["comparison"]["product_relation"], "") + ")"
    elif d["status"] == "unclear":
        out = "unclear, please check"
    else:
        parts = []
        if d["horizontal"]:
            parts.append(RELATION_TEXT.get(r["comparison"]["product_relation"], "") + ", "
                         + CUSTOMER_TEXT.get(r["customers"], ""))
        parts += [cmp.describe_link(link, target, r["portco"]) for link in d["vertical_links"]]
        out = " · ".join(p for p in parts if p)
    if status == "dismissed by user":
        out += " · dismissed by you"
    elif status == "added back by user":
        out += " · added back by you"
    if r["flags"] or d.get("disregarded"):
        out += " · ⚑"
    return out


def activity_detail(a, who, urls):
    customers = ", ".join(a.get("direct_customers", []))
    src = " ".join(f"[[{n}]]({urls[n]})" for n in a.get("source_numbers", []) if n in urls) or "no source"
    includes = ", ".join(a.get("includes") or [])
    return (f"**{who}:** {a['product']}" + (f" ({includes})" if includes else "") + f" · {a['value_chain_level']} · "
            f"direct customers: {customers} · countries: {', '.join(a.get('countries_of_sale', []))} · {src}")


def pair_detail(r, status, rv, target):
    """One target activity inside a portco activity's line: result, override, reasons, signals, exact prompt."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    with st.container(border=True):
        st.markdown(f"{pair_icon(r, status)} **{target}: {r['a']['product']}** · {pair_result_text(r, status, target)}")
        c1, c2 = st.columns([1, 2])
        if r["decision"]["status"] == "screened out":
            key = f"add_{rv}_{pid}"
            c1.checkbox("Add back to the list", value=o.get("add_back", False), key=key,
                        on_change=_store_override, args=(pid, "add_back", key))
        else:
            key = f"dis_{rv}_{pid}"
            c1.checkbox("Dismiss", value=o.get("dismiss", False), key=key,
                        on_change=_store_override, args=(pid, "dismiss", key))
        key = f"note_{rv}_{pid}"
        c2.text_input("Note", value=o.get("note", ""), key=key, placeholder="Note (recorded in the audit log)",
                      label_visibility="collapsed", on_change=_store_override, args=(pid, "note", key))
        if st.toggle("Why?", key=f"why_{rv}_{pid}"):
            c = r["comparison"]
            st.markdown(f"**Product (AI):** {c['product_relation']}. {c.get('product_reason', '')}")
            links = r["decision"]["vertical_links"]
            if links or c.get("vertical_reason"):
                found = "; ".join(f"{cmp.describe_link(l, target, r['portco'])} (found by "
                                  f"{r['decision']['found_by'][l]})" for l in links) or "none"
                st.markdown(f"**Vertical:** {found}. {c.get('vertical_reason', '')}")
            st.markdown(f"**Rule applied:** {r['decision']['rule']}")
            st.markdown(activity_detail(r["b"], r["portco"], source_urls(ss.mapped[r["portco"]])) + "  \n"
                        + activity_detail(r["a"], target, source_urls(ss.mapped[target])))
            s = r["sims"]
            signals = "; ".join(f"{link} ({why})" for link, why in r["code_signals"]) or "none"
            st.caption(f"Pair {pid} · vertical signals in code: {signals} · input target→portco "
                       f"{s['input_a_to_b']:.2f}, input portco→target {s['input_b_to_a']:.2f} · similarity "
                       f"{s['product']:.2f} (information only)" + (f" · flags: {flags(r)}" if flags(r) else ""))
            st.caption("Exactly what the AI received (no names; the name check ran before the call):")
            st.code(r["prompt"], language=None)


def activity_line(b, pairs, status, rv, target):
    """ONE line per portfolio-company activity: which target activities it touches (spec: practice table)."""
    rel = [r for r in pairs if kept(status[cmp.pair_id(r)])]
    dismissed = [r for r in pairs if status[cmp.pair_id(r)] == "dismissed by user"]
    icons = "".join(sorted({c for r in rel for c in pair_icon(r, status[cmp.pair_id(r)]) if c in "🔴🟠❔"},
                           key="🔴🟠❔".index)) or "⚪"
    touched = " · ".join(f"{pair_icon(r, status[cmp.pair_id(r)])} {r['a']['product']}" for r in
                         sorted(rel, key=lambda r: PAIR_ORDER[status[cmp.pair_id(r)]]))
    label = f"{icons} **{b['product']}** → " + (touched or "no overlap found")
    if dismissed:
        label += f" · ✖ {len(dismissed)} dismissed"
    with st.expander(label):
        includes = ", ".join(b.get("includes") or [])
        if includes:
            st.caption(f"Includes: {includes}")
        ordered = sorted(pairs, key=lambda r: (PAIR_ORDER[status[cmp.pair_id(r)]], -r["sims"]["product"]))
        for r in ordered:
            if status[cmp.pair_id(r)] != "screened out":
                pair_detail(r, status[cmp.pair_id(r)], rv, target)
        out = [r for r in ordered if status[cmp.pair_id(r)] == "screened out"]
        if out:
            st.caption(f"No overlap found with {len(out)} {target} activit{'y' if len(out) == 1 else 'ies'}:")
            for r in out:
                screened_row(r, rv, target)


def screened_row(r, rv, target):
    """A screened-out pair in one compact row: the target activity, the AI's reason, and 'Add back'."""
    pid = cmp.pair_id(r)
    key = f"add_{rv}_{pid}"
    c1, c2 = st.columns([5, 1])
    c1.markdown(f"⚪ {r['a']['product']}  \n:gray[{r['comparison'].get('product_reason', '')}]")
    c2.checkbox("Add back", value=ss.override_store.get(pid, {}).get("add_back", False), key=key,
                on_change=_store_override, args=(pid, "add_back", key))


def cell(r, status):
    """One cell of the grid: the result of one pair (portfolio company activity x target activity)."""
    d = r["decision"]
    if status == "dismissed by user":
        return "✖"
    if status == "screened out":
        return "–"
    if status == "added back by user":
        return "↩"
    if d["status"] == "unclear":
        return "❔"
    h, v = d["horizontal"], bool(d["vertical_links"])
    return "🔴 H 🟠 V" if h and v else "🔴 H" if h else "🟠 V"


def unique_labels(names, width):
    out = []
    for n in names:
        label = n if len(n) <= width else n[:width - 1] + "…"
        while label in out:
            label += " "
        out.append(label)
    return out


def portco_grid(pairs, status):
    """Rows: the portfolio company's activities; columns: the target's activities."""
    rows = list(dict.fromkeys(r["label_b"] for r in pairs))
    cols = list(dict.fromkeys(r["label_a"] for r in pairs))
    by = {(r["label_b"], r["label_a"]): r for r in pairs}
    name_b = {r["label_b"]: r["b"]["product"] for r in pairs}
    name_a = {r["label_a"]: r["a"]["product"] for r in pairs}
    data = [[cell(by[(rb, ca)], status[cmp.pair_id(by[(rb, ca)])]) if (rb, ca) in by else "" for ca in cols]
            for rb in rows]
    columns = unique_labels([name_a[c] for c in cols], 24)
    df = pd.DataFrame(data, index=unique_labels([name_b[r] for r in rows], 42), columns=columns)
    config = {c: st.column_config.TextColumn(name_a[k], width="small", help=name_a[k]) for c, k in zip(columns, cols)}
    config["_index"] = st.column_config.TextColumn(width="medium")
    st.dataframe(df, width="stretch", column_config=config)


def portco_sentence(p, target, pairs, status):
    """One sentence per portfolio company, assembled in code from the results (no AI call). The grid shows which
    activities; the sentence only says how many and of which kind."""
    acts = list(dict.fromkeys(r["label_b"] for r in pairs))
    live = [r for r in pairs if kept(status[cmp.pair_id(r)])]
    touched = {r["label_b"] for r in live}
    if not touched:
        return f"None of its {len(acts)} activities overlaps with an activity of {target}."
    kinds = [f"{n} {word}" for n, word in (
        (sum(r["decision"]["horizontal"] for r in live), "horizontal"),
        (sum(bool(r["decision"]["vertical_links"]) for r in live), "vertical"),
        (sum(r["decision"]["status"] == "unclear" or status[cmp.pair_id(r)] == "added back by user" for r in live),
         "to check")) if n]
    return (f"{len(touched)} of its {len(acts)} activities overlap with activities of {target} "
            f"({', '.join(kinds)} in the grid).")


def stage_overview(ai):
    st.subheader("③ Overlap overview")
    st.write("For each portfolio company, the grid shows which of its activities (rows) overlap with which "
             "activities of the target (columns). These are potential overlaps for a lawyer to verify; the "
             "Commission's market definitions follow in the next step. Use “Show the reasoning” to see why, to "
             "dismiss a result or to add a note.")
    st.caption("🔴 H horizontal overlap · 🟠 V vertical relationship · ❔ unclear, please check · – no overlap "
               "found · ✖ dismissed · ↩ added back")
    if DEV_MODE:
        st.caption(stage_cost("confirm"))
    results = ss.results
    target = ss.companies[0]["name"]
    portcos = [c["name"] for c in ss.companies[1:]]
    rv = ss.results_version
    ss.setdefault("override_store", {})
    ss.overrides = {pid: dict(o) for pid, o in ss.override_store.items()
                    if o.get("dismiss") or o.get("add_back") or o.get("note")}
    status = {cmp.pair_id(r): cmp.effective_status(r, ss.overrides) for r in results}
    show_relationships()

    with st.expander(f"🎯 Target: {target}"):
        st.write(profile_of(target))
        activity_list(ss.confirmed[target])

    for i, p in enumerate(portcos, start=1):
        pairs = [r for r in results if r["portco"] == p]
        with st.container(border=True):
            st.markdown(f"#### {i}. {p}")
            st.markdown(portco_sentence(p, target, pairs, status))
            if pairs:
                portco_grid(pairs, status)
            excluded = [a for a in ss.confirmed.get(p, []) if a.get("excluded")]
            if excluded:
                st.caption("Not compared (excluded by you): " + "; ".join(
                    f"{a['product']} ({a.get('exclusion_reason', '')})" for a in excluded))
            if pairs and st.toggle("Show the reasoning", key=f"tg_why_{rv}_{i}"):
                grouped = {}
                for r in pairs:
                    grouped.setdefault(r["label_b"], []).append(r)
                for prs in grouped.values():
                    activity_line(prs[0]["b"], prs, status, rv, target)

    if DEV_MODE:
        benchmark_panel(results)
    st.divider()
    st.button("Find Commission market definitions", type="primary", disabled=True,
              help="Step ④ (retrieval with the reflection loop) is the next build step.")
    snap = audit_snapshot(ai)
    st.download_button("Download the audit log so far (.json)", data=lambda: audit_json(snap),
                       mime="application/json", on_click="ignore",
                       file_name=f"overlap_audit_{datetime.now():%Y%m%d-%H%M}.json")
    st.caption(run_summary())


def run_summary():
    """Required output (spec section 10): AI calls, models, cost and time of the run."""
    calls, cost, seconds, models = 0, 0.0, 0.0, set()
    for stage in ("mapping", "confirm"):
        if stage in ss.stage_logs:
            first, last, sec = ss.stage_logs[stage]
            part = ss.log.calls[first:last]
            calls += len(part)
            cost += sum(c["cost"] for c in part)
            seconds += sec
            models |= {c["model"] for c in part}
    return (f"Run summary: {calls} AI calls · models: {', '.join(sorted(models))} · USD {cost:.3f} at token prices "
            f"(web search fees not included) · {seconds:.0f} s")


def benchmark_panel(results):
    """Development only: the expert benchmark (benchmark.py) on the app's own results, for the test cases."""
    try:
        import benchmark
        from examples import TEST_CASES
    except Exception:  # noqa: BLE001 - development tools not present
        return
    target = ss.companies[0]["name"]
    tc = next((k for k, v in TEST_CASES.items() if v == target), None)
    if not tc:
        return
    view = {n: {"extraction": {"activities": acts}, "mentions": (ss.mapped.get(n) or {}).get("mentions", [])}
            for n, acts in ss.confirmed.items()}
    checks = benchmark.run_checks(tc, target, view, results, rules.SIMILARITY_UNCLEAR)
    with st.expander(f"Development: benchmark {tc} (spec section 13)"):
        st.dataframe(pd.DataFrame([{"Check": c["id"], "Portco": c["portco"], "Expected": c["expect"],
                                    "Result": c["mark"], "What": c["what"], "Detail": c["detail"],
                                    "Pairs": ", ".join(c["labels"][:6])} for c in checks]), hide_index=True)


# =============================================================== audit log
def audit_snapshot(ai):
    """References to everything the audit log contains, taken in the script thread. The JSON itself is built
    only when the user clicks the download button (on another thread, which cannot read session state)."""
    return {"created": datetime.now().isoformat(timespec="seconds"), "profile": PROFILE, "dev_mode": DEV_MODE,
            "cache": USE_CACHE, "saved_searches": USE_SAVED, "models": dict(ai.models),
            "companies": ss.get("companies"), "mapped": ss.get("mapped"), "relationships": ss.get("relationships"),
            "confirmed": ss.get("confirmed"), "profiles": ss.get("profiles_text"),
            "names": list(ss.get("names") or []),
            "abstracts": ss.get("profiles_meta"), "results": list(ss.get("results") or []),
            "overrides": dict(ss.get("overrides") or {}), "calls": list(ss.log.calls)}


def audit_json(snap):
    slim = [{k: v for k, v in r.items() if k != "sims"}
            | {"sims": {k: round(v, 3) for k, v in r["sims"].items()},
               "status_after_overrides": cmp.effective_status(r, snap["overrides"])}
            for r in snap["results"]]
    log = {
        "created": snap["created"], "profile": snap["profile"], "dev_mode": snap["dev_mode"],
        "development_cache": snap["cache"], "saved_searches": snap["saved_searches"], "models": snap["models"],
        "prices": {"checked": ai_client.PRICES_CHECKED, "usd_per_1m_tokens": ai_client.PRICES},
        "thresholds": {"similarity_unclear": rules.SIMILARITY_UNCLEAR, "input_match": rules.INPUT_MATCH,
                       "resale_match": rules.RESALE_MATCH},
        "companies": snap["companies"],
        "stage_1_2_activity_mapping": snap["mapped"],
        "existing_relationships": snap["relationships"],
        "stage_2_company_profiles": snap["profiles"],
        "stage_2_confirmed_activities": snap["confirmed"],
        "anonymisation": {"name_variants_removed": sorted(rules.name_variants(snap["names"])),
                          "abstracts": snap["abstracts"]},
        "stage_3_factual_comparison": slim,
        "user_overrides": snap["overrides"],
        "call_log": snap["calls"],
    }
    return json.dumps(log, ensure_ascii=False, indent=1, default=str)


# =============================================================== development sidebar
def deployment_check(ai):
    """One AI call, ChromaDB on this machine, and one hybrid search (spec section 16: deployment test)."""
    rows = []
    try:
        t = time.time()
        resp = ai.respond("check", "Reply with the single word: ready", note="deployment check")
        rows.append(("AI call", "✔", f"{ai.model('check')} answered '{resp.output_text.strip()}' in {time.time() - t:.1f} s"))
    except Exception as e:  # noqa: BLE001
        rows.append(("AI call", "✖", f"{type(e).__name__}: {e}"))
    try:
        import retrieval                      # swaps in pysqlite3 first, if it is installed
        import sqlite3

        import chromadb
        r = retrieval.Retriever(ai.embed_fn())
        rows.append(("ChromaDB", "✔", f"chromadb {chromadb.__version__} · SQLite {sqlite3.sqlite_version} · "
                                      f"{r.col.count()} chunks in '{retrieval.COLLECTION}'"))
        res = r.search("relevant product market for chocolate tablets", k=3)
        rows.append(("Hybrid search", "✔", " · ".join(f"{retrieval.cite(h['paragraph'])} [{h['found_by']}]"
                                                       for h in res["hits"])))
    except Exception as e:  # noqa: BLE001
        rows.append(("ChromaDB / retrieval", "✖", f"{type(e).__name__}: {e}"))
    return rows


def dev_sidebar(ai):
    with st.sidebar:
        st.divider()
        st.caption(f"**DEV_MODE** · profile **{PROFILE}** · cache {'on' if USE_CACHE else 'off'} · "
                   f"saved searches {'on' if USE_SAVED else 'off'}")
        s = ss.log.summary()
        st.metric("Session cost (USD, token prices)", f"{s['cost']:.4f}")
        st.caption(f"{s['calls']} AI calls ({s['cached']} from cache) · {s['web_searches']} web searches "
                   f"(search fees not included) · prices: {ai_client.PRICES_CHECKED}")
        if s["steps"]:
            st.dataframe(pd.DataFrame([{"Step": k, "Calls": v["calls"], "Cached": v["cached"],
                                        "USD": round(v["cost"], 4)} for k, v in s["steps"].items()]),
                         hide_index=True)
        with st.expander("Models per step"):
            st.dataframe(pd.DataFrame([{"Step": k, "Model": v, "Effort": ai.effort(k)} for k, v in ai.models.items()]
                                      + [{"Step": "embed", "Model": ai_client.EMBED_MODEL, "Effort": ""}]),
                         hide_index=True)
        with st.expander("Deployment check"):
            st.caption("One AI call, the ChromaDB index and one hybrid search (about USD 0.0001).")
            if st.button("Run the check"):
                ss.deploy_check = deployment_check(ai)
            for what, mark, detail in ss.get("deploy_check", []):
                st.markdown(f"{mark} **{what}**: {detail}")


# =============================================================== page
INTRO = """When an investor plans to buy a company (the *target*), it must check early whether the target is active in
the same or related markets as the companies it already owns (its *portfolio companies*). This matters under EU merger
control: overlaps can trigger a closer review by the European Commission and require care in sharing information.

This tool prepares a first screen in three steps:
1. **Activities.** It researches each company separately on public websites and lists its business areas. You check
   and correct them.
2. **Comparison.** It compares every activity of the target with every activity of each portfolio company. The AI
   sees descriptions only, never the company names.
3. **Commission precedents.** It looks up how the European Commission defined the relevant markets in past decisions.

**Horizontal overlap:** both companies offer the same or substitutable products (potential competitors).
**Vertical relationship:** one company's products could be an input for the other, or could be resold by it
(potential supplier and customer).

The result is a working document for a lawyer to verify, not a legal conclusion. Each result shows its sources and
reasoning."""

STEPS = {1: "Companies", 2: "Activities", 3: "Overlap overview"}


def progress(step):
    st.markdown("  →  ".join((f"**{'①②③'[k - 1]} {v}**" if k == step else
                              f"✔ {v}" if k < step else f":gray[{'①②③'[k - 1]} {v}]") for k, v in STEPS.items()))


def done_summaries(step):
    """Finished steps collapse into one line each, with a way back."""
    if step > 1 and ss.get("companies"):
        c1, c2 = st.columns([5, 1], vertical_alignment="center")
        c1.markdown(f"✔ **Companies:** target {ss.companies[0]['name']} · portfolio: "
                    f"{', '.join(c['name'] for c in ss.companies[1:])}")
        c2.button("Change", key="back_1", on_click=go_to, args=(1,))
    if step > 2 and ss.get("confirmed"):
        acts = [a for v in ss.confirmed.values() for a in v]
        excl = sum(a.get("excluded", False) for a in acts)
        c1, c2 = st.columns([5, 1], vertical_alignment="center")
        c1.markdown(f"✔ **Activities:** {len(acts) - excl} compared" + (f", {excl} excluded" if excl else ""))
        c2.button("Change", key="back_2", on_click=go_to, args=(2,))


st.title("EU Overlap Screen")
step = ss.get("step", 1)
if step == 1:
    st.markdown(INTRO)
else:
    with st.expander("How this tool works"):
        st.markdown(INTRO)
ai = make_ai(credentials())
if step == 2 and not ss.get("tables"):
    step = ss.step = 1
if step == 3 and ss.get("results") is None:
    step = ss.step = 2 if ss.get("tables") else 1
progress(step)
done_summaries(step)
st.divider()
if step == 1:
    stage_companies(ai)
elif step == 2:
    stage_activities(ai)
else:
    stage_overview(ai)
if DEV_MODE:
    dev_sidebar(ai)