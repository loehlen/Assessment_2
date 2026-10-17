"""
app.py - EU Overlap Screen (LAWS90286 Assignment 2): a preliminary EU merger control overlap screen.

Built so far: stages ① Companies, ② Activities and ③ Preliminary assessment (spec 9, sections 6-9).
Going back never deletes anything: a changed company is researched again and only new or changed pairs are compared
again (stable activity IDs and content keys, 16 Oct); dismissals and notes stay with their pair.
Stages ④ market definitions, ⑤ geography and ⑥ export follow; they add columns to the table of stage ③, which
follows the overlap table used in practice: one box per portfolio company; in it, each target activity with the
portfolio company's activities that meet it, the Commission's market definition and the preliminary assessment.

    streamlit run app.py

Settings (.env in the Codespace, Secrets on Streamlit Cloud; see .env.example):
    DEV_MODE=1, APP_PASSWORD, OPENAI_API_KEY      development: password gate, cost counter, development tools
    MODEL_PROFILE=dev | final                      the models per step (ai_client.py); default: dev with
                                                   DEV_MODE on, final with DEV_MODE off (the submitted version)
    USE_CACHE=1, USE_SAVED_SEARCHES=1              development only: reuse paid calls and the saved Sol searches
With DEV_MODE off (the submitted version) the sidebar asks for the user's own OpenAI key; the course
credentials module replaces that field before the final deployment tests.
"""
import concurrent.futures as cf
import copy
import hashlib
import html
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
PROFILE = ai_client.setting("MODEL_PROFILE", "dev" if DEV_MODE else "final")   # the submitted version never runs on dev
USE_CACHE = DEV_MODE and ai_client.flag("USE_CACHE", default=True)
USE_SAVED = DEV_MODE and ai_client.flag("USE_SAVED_SEARCHES", default=True)
MAX_PORTCOS = 5

ss = st.session_state
ss.setdefault("log", ai_client.CallLog())     # every AI call of this session
ss.setdefault("stage_logs", {})               # per stage: [(first, last) position in the call log, seconds], one per run
ss.setdefault("run_first", 0)                 # position in the call log where the current screen started
ss.setdefault("pf_version", 0)                # a new version = a fresh portfolio table in step ①
ss.setdefault("acts_version", 0)              # a new version = fresh widgets for the activity lists in step ②


# =============================================================== credentials
def credentials():
    """Returns the OpenAI key for this session, or stops the script until one is available."""
    with st.sidebar:
        if DEV_MODE:
            expected = ai_client.setting("APP_PASSWORD")
            password = st.text_input("App password", type="password", key="app_password")
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
        key = st.text_input("OpenAI API key", type="password", key="user_api_key",
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


def cell(v):
    """A cell of the portfolio table as plain text ('' if empty)."""
    try:
        return "" if is_missing(v) else str(v).strip()
    except (TypeError, ValueError):
        return ""


def esc(text):
    """Text from the sources or the AI, made safe inside Streamlit markdown (no links, colour tags or formulas)."""
    out = str(text or "")
    for a, b in (("\\", "\\\\"), ("[", "("), ("]", ")"), ("$", "\\$"), ("*", "\\*"), ("_", "\\_"), ("~", "\\~"),
                 ("<", "&lt;"), (">", "&gt;")):
        out = out.replace(a, b)
    return out


def plural(n, word, words=None):
    return f"{n} {word if n == 1 else (words or word + 's')}"


def words_list(items):
    items = list(dict.fromkeys(items))
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


def log_stage(name, first, seconds):
    """Records one run of a stage (a stage can run several times: partial updates since 16 Oct)."""
    ss.stage_logs.setdefault(name, []).append((first, ss.log.mark(), seconds))


def stage_calls(name):
    return [c for first, last, _ in ss.stage_logs.get(name, []) for c in ss.log.calls[first:last]]


def stage_seconds(name):
    return sum(sec for _, _, sec in ss.stage_logs.get(name, []))


def stage_cost(name):
    """Calls, cache hits, cost and time of one stage (all its runs in this screen), from the call log."""
    if name not in ss.stage_logs:
        return ""
    calls, seconds = stage_calls(name), stage_seconds(name)
    text = f"{len(calls)} AI calls"
    if USE_CACHE:
        text += f" ({sum(c['cached'] for c in calls)} from the development cache)"
    text += f" · USD {sum(c['cost'] for c in calls):.4f} (token prices) · {seconds:.0f} s"
    unpriced = sorted({c["model"] for c in calls if not c.get("priced", True)})
    if unpriced:
        text += f" · no price for {', '.join(unpriced)}"
    return text


def go_to(step):
    ss.step = step


# =============================================================== the working screen (17 Oct)
# Long work (research, comparison) used to run in the middle of the page: Streamlit keeps the elements of the previous
# screen, faded, until a run ends, so old blocks lingered for a minute below the progress, sometimes in the wrong
# columns. Now a button only records the work and reloads; the next run clears the page body first and shows nothing
# but the progress, then opens the next step.
def start_work(kind, **args):
    ss.pending = {"kind": kind, **args}
    st.rerun()


def do_work(ai, job):
    """Runs the recorded work on the cleared page. Returns True when the next step can be shown."""
    st.iframe(SCROLL_TOP, height=1)
    kind = job["kind"]
    if kind == "mapping":
        run_mapping(ai, job["companies"])
        ss.step = 2
        return True
    if kind == "remap":
        remap_company(ai, job["name"], job["website"], job["mode"], job["pasted"])
        ss.step = 2
        return True
    if kind == "compare":
        return confirm_activities(ai, job["activities"], [], job["profiles_text"])
    return True


# =============================================================== new screen (reset)
KEEP_ON_RESET = {"log", "app_password", "user_api_key", "deploy_check"}


def reset_all():
    """Discards everything of the current screen; keeps the key or password and, in development, the cost counter.
    The call log continues, but the audit log of the next screen starts here."""
    for k in list(ss.keys()):
        if k not in KEEP_ON_RESET:
            del ss[k]
    ss.run_first = ss.log.mark()


@st.dialog("Start a new screen?")
def confirm_reset(snap):
    st.write("This discards the companies, activities and results of the current screen.")
    if snap is not None:
        st.download_button("Download the audit log first (.json)", data=lambda: audit_json(snap),
                           mime="application/json", on_click="ignore",
                           file_name=f"overlap_audit_{datetime.now():%Y%m%d-%H%M}.json")
    c1, c2 = st.columns(2)
    if c1.button("Discard and start again", type="primary"):
        reset_all()
        st.rerun()
    if c2.button("Cancel"):
        st.rerun()


# =============================================================== value chain and sources (shown in steps ② and ③)
# The stage in the value chain, from the activity's own level of trade (where the company SELLS; what it buys is not
# compared: purchasing overlaps are a listed limitation, spec section 14). Display only: the data keep the schema terms.
STAGE = {"raw materials": "Raw materials", "intermediate products": "Intermediate products",
         "finished products": "Manufacturing", "wholesale / distribution": "Wholesale", "retail": "Retail",
         "services": "Services", "other": "Other"}
SOURCE_KIND = {"company": "company website", "third party": "other public source", "provided by user": "your description"}


def stage_of(a):
    if rules.category(a) == "other":
        return "Own use" if rules.captive_only(a) else "Mixed"
    return STAGE.get(a.get("value_chain_level"), "Other")


def stage_text(a):
    """The stage as plain grey text (16 Oct, Linda: no grey highlight)."""
    return f":gray[{stage_of(a)}]"


def source_index(company):
    m = (ss.get("mapped") or {}).get(company) or {}
    return {s["n"]: s for s in ((m.get("search") or {}).get("sources") or [])}


def source_markers(a, company):
    """Numbered source markers next to an activity: hover shows the page, its kind and the passage the extraction
    relied on; a click opens the page. Company websites are solid, other public sources dotted (decided 16 Oct)."""
    idx = source_index(company)
    evidence = a.get("evidence") or ""
    out = []
    for n in a.get("source_numbers") or []:
        s = idx.get(n)
        if not s:
            continue
        kind = s.get("type") or "unlabelled"
        if kind == "provided by user":
            out.append(f"<span title='{html.escape('Your description (entered in step ①)', quote=True)}' "
                       "style='font-size:0.85em;opacity:0.8'>[your description]</span>")
            continue
        tip = f"{s.get('title', '')}\n{am.site_of(s.get('url'))} · {SOURCE_KIND.get(kind, kind)}"
        if evidence and evidence not in ("not stated", "added by user"):
            tip += f"\n\nPassage used for this activity: “{evidence[:600]}”"
        tip = html.escape(tip, quote=True).replace("\n", "&#10;")
        style = ("text-decoration:none;font-size:0.85em" if kind == "company" else
                 "text-decoration:underline dotted;opacity:0.75;font-size:0.85em")
        out.append(f"<a href='{html.escape(s.get('url', ''), quote=True)}' target='_blank' title='{tip}' "
                   f"style='{style}'>[{n}]</a>")
    if not out:
        out.append("<span style='font-size:0.85em;opacity:0.8'>added by you</span>" if a.get("origin") == "added by user"
                   else "<span title='No source returned by the search supports this activity' "
                        "style='font-size:0.85em'>⚠ no source</span>")
    return " ".join(out)


SOURCES_LEGEND = ("Sources: [n] solid = the company's own website, [n] dotted = other public source. Hover over a "
                  "number to see the page and the passage used; click to open it.")


# =============================================================== step ① companies
SOURCE_HELP = ("web search: public websites only · my description: no web search, only the text you enter · "
               "both: web search plus your text as an additional source")
DESCRIPTION_HELP = ("Describe what the company does: its business areas, products, customers and countries. The text "
                    "is sent to the AI provider only in this company's own call, like search results, and is never "
                    "shown together with another company's name.")


def empty_portfolio():
    return pd.DataFrame([{"name": "", "website": "", "aliases": "", "source": "web search"}])


def portfolio_rows(df):
    """The filled rows of the portfolio table as company dicts (without role and description)."""
    rows = []
    for r in df.to_dict("records"):
        name = cell(r.get("name"))
        if not name:
            continue
        source = cell(r.get("source"))
        rows.append({"name": name, "website": cell(r.get("website")),
                     "aliases": [a.strip() for a in cell(r.get("aliases")).split(",") if a.strip()],
                     "source": source if source in am.SOURCE_OPTIONS else "web search"})
    return rows


def fill_example(key):
    """'Try an example' (button callback): fills in one of the examples (examples.py). The run itself is live."""
    ex = examples.EXAMPLES[key]
    t = examples.COMPANIES[ex["target"]]
    ss.t_name, ss.t_web, ss.t_aliases = ex["target"], t["website"], ", ".join(t["aliases"])
    ss.t_source, ss.t_desc = "web search", ""
    ss.portfolio_df = pd.DataFrame([{"name": n, "website": examples.COMPANIES[n]["website"],
                                     "aliases": ", ".join(examples.COMPANIES[n]["aliases"]), "source": "web search"}
                                    for n in ex["portfolio"]])
    ss.pf_version += 1


def restore_inputs():
    """Widgets that are not shown lose their values in Streamlit; when the user comes back to step ①, the
    companies of the current run are filled in again."""
    if ss.get("companies") and "t_name" not in ss:
        t = ss.companies[0]
        ss.t_name, ss.t_web, ss.t_aliases = t["name"], t.get("website", ""), ", ".join(t.get("aliases", []))
        ss.t_source, ss.t_desc = am.source_mode(t), t.get("pasted", "")
        ss.portfolio_df = pd.DataFrame([{"name": c["name"], "website": c.get("website", ""),
                                         "aliases": ", ".join(c.get("aliases", [])), "source": am.source_mode(c)}
                                        for c in ss.companies[1:]])
        ss.pf_version += 1
        for c in ss.companies[1:]:
            ss[f"desc_{c['name']}"] = c.get("pasted", "")


def example_buttons():
    st.markdown("**Try an example**")
    cols = st.columns(len(examples.EXAMPLES))
    for col, (key, ex) in zip(cols, examples.EXAMPLES.items()):
        col.button(ex["button"], key=f"ex_{key}", help=ex["what"], on_click=fill_example, args=(key,))


def target_card():
    with st.container(border=True):
        st.markdown("**The target** · the company or business being acquired")
        c1, c2 = st.columns(2)
        c1.text_input("Name", key="t_name")
        c2.text_input("Website (optional)", key="t_web", placeholder="e.g. company.com",
                      help="Identifies the company in the web search and marks its own pages as company sources.")
        st.radio("Activities from", am.SOURCE_OPTIONS, key="t_source", horizontal=True, help=SOURCE_HELP)
        if ss.get("t_source", "web search") != "web search":
            st.text_area("Description of the target's activities", key="t_desc", height=140, help=DESCRIPTION_HELP)
        with st.expander("Other names (optional)"):
            st.text_input("Other names of the company, comma-separated", key="t_aliases",
                          help="Short names or former names. Like the name itself, they are removed from every "
                               "anonymised description before a comparison.")


def portfolio_card():
    with st.container(border=True):
        st.markdown(f"**The buyer's portfolio companies** · up to {MAX_PORTCOS}")
        st.caption("One row per company. Add a row with + under the table; several rows can also be pasted from a "
                   "spreadsheet.")
        cc = st.column_config
        edited = st.data_editor(
            ss.get("portfolio_df", empty_portfolio()), key=f"pf_{ss.pf_version}", num_rows="dynamic",
            hide_index=True, width="stretch",
            column_config={
                "name": cc.TextColumn("Name"),
                "website": cc.TextColumn("Website (optional)", help="e.g. company.com"),
                "aliases": cc.TextColumn("Other names (optional)",
                                         help="Comma-separated; removed from every anonymised description, like the name"),
                "source": cc.SelectboxColumn("Activities from", options=list(am.SOURCE_OPTIONS), default="web search",
                                             required=True, help=SOURCE_HELP)})
        for r in portfolio_rows(edited):
            if r["source"] != "web search":
                st.text_area(f"Description of {r['name']}'s activities", key=f"desc_{r['name']}", height=120,
                             help=DESCRIPTION_HELP)
    return edited


def read_companies(edited):
    """The target and the portfolio companies as entered, and the problems that stop the run."""
    t_source = ss.get("t_source", "web search")
    target = {"name": (ss.get("t_name") or "").strip(), "role": "target", "website": (ss.get("t_web") or "").strip(),
              "aliases": [a.strip() for a in (ss.get("t_aliases") or "").split(",") if a.strip()],
              "source": t_source, "pasted": (ss.get("t_desc") or "").strip() if t_source != "web search" else ""}
    portcos = [dict(r, role="portco", pasted=(ss.get(f"desc_{r['name']}") or "").strip()
                    if r["source"] != "web search" else "") for r in portfolio_rows(edited)]
    companies = [target] + portcos
    problems = []
    if not target["name"]:
        problems.append("Enter the name of the target.")
    if not portcos:
        problems.append("Enter at least one portfolio company.")
    if len(portcos) > MAX_PORTCOS:
        problems.append(f"Enter at most {MAX_PORTCOS} portfolio companies.")
    lowered = [c["name"].lower() for c in companies if c["name"]]
    if len(lowered) != len(set(lowered)):
        problems.append("Each company may be entered only once.")
    for c in companies:
        if c["name"] and c["source"] == "my description" and not c["pasted"]:
            problems.append(f"Enter a description for {c['name']}, or choose web search.")
    return companies, problems


def stage_companies(ai):
    st.subheader("① Companies")
    st.write("Enter the company being acquired (the target) and the buyer's portfolio companies. Each company is "
             "analysed as a group, with its subsidiaries and brands; for the target, enter the entity actually being "
             "acquired.")
    restore_inputs()
    example_buttons()
    target_card()
    edited = portfolio_card()
    st.caption("Each company is researched separately; the AI never sees two company names together. With web search "
               "this takes about one to four minutes.")
    c1, c2 = st.columns([1, 3], vertical_alignment="center")
    submitted = c1.button("Find activities →", type="primary")
    if ss.get("mapped"):
        c2.button("Continue with the current activities →", on_click=go_to, args=(2,))
    if not submitted:
        return
    companies, problems = read_companies(edited)
    if problems:
        st.error(" ".join(problems))
        return
    ss.portfolio_df = edited.reset_index(drop=True)
    ss.pf_version += 1
    start_work("mapping", companies=companies)


def company_key(c):
    """What the research of a company depends on: if none of it changed, the company is not searched again."""
    return json.dumps({k: c.get(k) for k in ("name", "website", "aliases", "source", "pasted")}, sort_keys=True,
                      ensure_ascii=False)


def run_mapping(ai, companies):
    """Maps the companies that are new or whose input changed (16 Oct); the others keep their research and the
    user's edits of their activities. A new screen starts with "↺ New screen" (reset_all), not here."""
    first, t0 = ss.log.mark(), time.time()
    old, old_keys = ss.get("mapped") or {}, ss.get("map_keys") or {}
    kept = {c["name"] for c in companies if c["name"] in old and not old[c["name"]].get("error")
            and old_keys.get(c["name"]) == company_key(c)}
    todo = [c for c in companies if c["name"] not in kept]
    mapped = {n: old[n] for n in kept}
    searching = any(am.source_mode(c) != "my description" for c in todo)
    label = ("Researching each company on public websites (one company per search, in parallel). This takes about "
             "one to four minutes." if searching else "Reading your descriptions (one company per call, in parallel).")
    if not todo:
        label = "Nothing new to research: the companies are unchanged."
    with st.status(label, expanded=True) as status:
        for n in sorted(kept):
            st.write(f"✔ {n}: kept from before (no change)")
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(am.map_company, ai, c, companies, USE_SAVED): c for c in todo}
            for fut in cf.as_completed(futures):
                c = futures[fut]
                m = fut.result()
                mapped[c["name"]] = m
                if m["error"]:
                    st.write(f"✖ {c['name']}: {m['error']}")
                else:
                    origin = ("your description" if am.source_mode(c) == "my description"
                              else f"{len(m['search']['sources'])} sources")
                    st.write(f"✔ {c['name']}: {len(m['extraction']['activities'])} activities from {origin}")
        status.update(label=f"Activities found in {time.time() - t0:.0f} s", state="complete", expanded=False)
    old_acts = ss.get("acts") or {}
    ss.companies = companies
    ss.mapped = {c["name"]: mapped[c["name"]] for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    ss.relationships = am.find_relationships(ss.mapped, companies)
    ss.acts = {c["name"]: old_acts[c["name"]] if c["name"] in kept and c["name"] in old_acts
               else copy.deepcopy(extracted(ss.mapped[c["name"]])) for c in companies}
    cmp.ensure_ids(ss.acts)
    ss.profiles_edit = {n: t for n, t in (ss.get("profiles_edit") or {}).items() if n in kept}
    ss.acts_version += 1
    log_stage("mapping", first, time.time() - t0)


def extracted(m):
    return (m.get("extraction") or {}).get("activities", [])


# =============================================================== stage ② activities
# Activities are kept as the extraction's dicts (ss.acts) and changed only through the edit form, so a change to one
# field keeps every other field (decided 16 Oct: the table editor replaced a cell's whole text when typing).
CUSTOMER_WORDS = {"consumers": "consumers", "retailers": "shops", "wholesalers / distributors": "wholesalers",
                  "manufacturers / processors": "other manufacturers", "other businesses": "businesses",
                  "public sector": "public bodies", "internal use (captive)": "its own group"}
CUSTOMER_TEXT = {"●●●": "same direct customers", "●●○": "partly the same direct customers",
                 "●○○": "different direct customers", "?": "direct customers not stated", "": ""}


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


def capital(text):
    return text[:1].upper() + text[1:]


def activity_line(a, company):
    """One activity in step ②: name, stage, what the company does, three examples, sources."""
    markers = source_markers(a, company)
    if a.get("excluded"):
        return (f"~~**{esc(capital(a['product']))}**~~ {stage_text(a)} · *not relevant to this deal:* "
                f"{esc(a.get('exclusion_reason', ''))} {markers}")
    if rules.is_gap(a):
        return (f"**{esc(rules.gap_name(a))}** · ❔ *named in the sources, but what it offers is not stated* · question "
                f"for the company; use “Edit” to add the product if you know it (until then it is not compared) {markers}")
    includes = [i for i in a.get("includes") or [] if i]
    if rules.category(a) == "other":
        items = [esc(short_item(i)) for i in includes]
        more = f" (+{len(items) - 4} more)" if len(items) > 4 else ""
        return f"**Other activities** {stage_text(a)} · {'; '.join(items[:4])}{more} {markers}"
    line = f"**{esc(capital(a['product']))}** {stage_text(a)} · {esc(everyday(a))}"
    includes = [esc(i) for i in includes if i.strip().lower() != a["product"].strip().lower()]
    if includes:
        line += f" · e.g. {', '.join(includes[:3])}"
    if a.get("status") == "in development":
        line += " · *in development*"
    return f"{line} {markers}"


def display_order(acts):
    """Business areas first, then 'Other activities', then what the user excluded (indices into the list)."""
    main = [i for i, a in enumerate(acts) if not a.get("excluded") and rules.category(a) == "main"]
    other = [i for i, a in enumerate(acts) if not a.get("excluded") and rules.category(a) == "other"]
    return main + other + [i for i, a in enumerate(acts) if a.get("excluded")]


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
    for store in ("profiles_text", "profiles_edit"):
        if name in (ss.get(store) or {}):
            return ss[store][name]
    return (((ss.get("mapped") or {}).get(name) or {}).get("extraction") or {}).get("company_profile", "")


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


def _shown(values):
    return [v for v in values or [] if v and v != "not stated"]


@st.dialog("Activity", width="large")
def edit_activity(company, idx):
    """The edit form: every field filled in, text fields that keep their text, the rarely needed fields folded away."""
    acts = ss.acts[company]
    a = copy.deepcopy(acts[idx]) if idx is not None else new_activity()
    k = f"ea_{ss.acts_version}_{company}_{idx}_"
    st.caption(f"{company} · {'new activity' if idx is None else 'changes are kept for this screen and recorded in the audit log'}")
    name = st.text_input("Activity", value=a.get("product", ""), key=k + "name",
                         help="What the business area offers (product or service), in generic words; who buys it goes under "
                              "“Direct customers”, not into the name; no company or brand names")
    includes = st.text_area("Includes (one item per line)", value="\n".join(a.get("includes") or []), key=k + "inc",
                            height=130, help="Every product type, format and customer group this activity covers")
    c1, c2 = st.columns(2)
    levels = list(rules.VALUE_CHAIN_LEVELS)
    level = c1.selectbox("Level of trade", levels, index=levels.index(a.get("value_chain_level", "other"))
                         if a.get("value_chain_level") in levels else levels.index("other"),
                         format_func=lambda x: f"{STAGE[x]} ({x})", key=k + "lvl",
                         help="; ".join(f"{x}: {d}" for x, d in rules.VALUE_CHAIN_LEVELS.items()))
    status = c2.selectbox("Status", rules.STATUS, index=rules.STATUS.index(a["status"]) if a.get("status") in rules.STATUS
                          else 0, key=k + "status")
    customers = st.multiselect("Direct customers", list(rules.DIRECT_CUSTOMER_TYPES),
                               default=[x for x in a.get("direct_customers", []) if x in rules.DIRECT_CUSTOMER_TYPES],
                               key=k + "cust", help="Who buys directly from the company, at its own level of trade")
    countries = st.text_input("Countries of sale (comma-separated)", value=", ".join(_shown(a.get("countries_of_sale"))),
                              key=k + "ctry", help="Leave empty if not stated")
    category = st.radio("Category", rules.CATEGORIES, index=rules.CATEGORIES.index(rules.category(a)), horizontal=True,
                        key=k + "cat", help="main: a business area offered as a business in its own right · other: "
                                            "own use or a side line supporting the main business (combined in one line)")
    excluded = st.checkbox("Not relevant to this deal (not compared)", value=bool(a.get("excluded")), key=k + "excl")
    reason = st.text_input("Reason", value=a.get("exclusion_reason", ""), key=k + "reason",
                           placeholder="e.g. a business the fund is selling") if excluded else ""
    with st.expander("More fields"):
        description = st.text_area("Description", value=_shown([a.get("description")])[0] if _shown([a.get("description")]) else "",
                                   key=k + "desc", help="No company, brand, customer or supplier names")
        intended = st.text_input("Intended use", value="" if a.get("intended_use") == "not stated" else a.get("intended_use", ""),
                                 key=k + "use")
        inputs = st.text_input("Main inputs (separated by semicolons)", value="; ".join(_shown(a.get("main_inputs"))),
                               key=k + "inputs")
        details = st.text_input("Customer details", value="" if a.get("customer_details") == "not stated"
                                else a.get("customer_details", ""), key=k + "cdet")
        end_users = st.selectbox("End users", rules.END_USERS, index=rules.END_USERS.index(a["end_users"])
                                 if a.get("end_users") in rules.END_USERS else rules.END_USERS.index("not stated"),
                                 key=k + "end")
        channels = st.text_input("Sales channels", value="" if a.get("sales_channels") == "not stated"
                                 else a.get("sales_channels", ""), key=k + "chan")
        area = st.text_input("Business area (as the company groups it)", value="" if a.get("business_area") == "not stated"
                             else a.get("business_area", ""), key=k + "area")
        entity = st.text_input("Group companies or brands carrying it", value="" if a.get("entity") == "not stated"
                               else a.get("entity", ""), key=k + "entity")
        brands = st.text_input("Brands (comma-separated; removed before any comparison)",
                               value=", ".join(a.get("brands") or []), key=k + "brands")
    if idx is not None:
        st.markdown("Sources: " + source_markers(a, company), unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    if b1.button("Save", type="primary", key=k + "save"):
        problems = []
        if not name.strip():
            problems.append("Give the activity a name.")
        if excluded and not reason.strip():
            problems.append("Give a short reason why it is not relevant to this deal.")
        if problems:
            st.error(" ".join(problems))
            return
        new = dict(a, product=name.strip(), includes=_items(includes, "\n"), value_chain_level=level, status=status,
                   direct_customers=customers or ["not stated"], countries_of_sale=_items(countries, ",") or ["not stated"],
                   category=category, excluded=excluded, exclusion_reason=reason.strip(), description=_text(description),
                   intended_use=_text(intended), main_inputs=_items(inputs, ";") or ["not stated"],
                   customer_details=_text(details), end_users=end_users, sales_channels=_text(channels),
                   business_area=_text(area), entity=_text(entity), brands=_items(brands, ","))
        if idx is None:
            acts.append(new)
        else:
            if new != acts[idx] and new.get("origin") == "search":
                new["edited_by_user"] = True
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
    st.subheader("② Activities")
    st.write("Check what each company does. Everything after this step builds on these activities. Use “Edit” next to "
             "an activity to correct it, mark it as not relevant to this deal or delete it; “Add an activity” adds one.")
    st.caption(SOURCES_LEGEND)
    if DEV_MODE:
        st.caption(stage_cost("mapping"))
    cmp.ensure_ids(ss.acts)
    show_relationships()
    for i, c in enumerate(ss.companies):
        company_block(ai, c, i)
    name_word_review()
    problems = activity_problems()
    ss.current_hash = None if problems else activities_hash(ss.acts)
    has_results = ss.get("results") is not None
    c1, c2 = st.columns([3, 2], vertical_alignment="center")
    if has_results and ss.current_hash == ss.get("confirmed_hash"):
        c1.button("Back to the assessment (no changes) →", type="primary", on_click=go_to, args=(3,))
        return
    label = "Compare activities"
    if has_results and not problems:
        plan = prepare_comparison(copy.deepcopy(ss.acts))
        label = (f"Update the comparison: {plural(plan['new'], 'new or changed pair')} to compare, {plan['kept']} kept"
                 if plan["new"] else "Update the comparison (nothing new to compare)")
    if c1.button(label, type="primary"):
        if problems:
            st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        else:
            start_work("compare", activities=copy.deepcopy(ss.acts),
                       profiles_text={c["name"]: profile_of(c["name"]) for c in ss.companies})
    if has_results:
        c2.button("Back to the assessment without these changes →", on_click=go_to, args=(3,))


def company_block(ai, c, index):
    name = c["name"]
    m = ss.mapped[name]
    ext = m.get("extraction") or {}
    acts = ss.acts[name]
    v = ss.acts_version
    with st.container(border=True):
        st.markdown(f"#### {'🎯 Target: ' if c['role'] == 'target' else f'Portfolio company {index}: '}{name}")
        facts = [c["website"]] if c.get("website") else []
        if am.source_mode(c) != "web search":
            facts.append(f"activities from: {am.source_mode(c)}")
        if facts:
            st.caption(" · ".join(facts))
        if m["error"]:
            st.error(m["error"])
        profile = profile_of(name)
        if profile.strip():
            psrc = {"source_numbers": ext.get("profile_source_numbers") or [], "evidence": ""}
            st.markdown(esc(profile) + (" " + source_markers(psrc, name) if psrc["source_numbers"] else ""),
                        unsafe_allow_html=True)
        elif not m["error"]:
            st.caption("No profile found in the sources.")
        for w in ext.get("warnings") or []:
            st.warning(w)
        for i in display_order(acts):
            row = st.columns([14, 1], vertical_alignment="center")
            row[0].markdown(activity_line(acts[i], name), unsafe_allow_html=True)
            if row[1].button("Edit", key=f"edit_{v}_{name}_{i}"):
                edit_activity(name, i)
        if not acts:
            st.caption("No activities.")
        main_acts = [a for a in acts if rules.category(a) == "main" and not a.get("excluded")]
        hints = [f"“{main_acts[i]['product']}” and “{main_acts[j]['product']}”"
                 for i, j in rules.possible_duplicates(main_acts)]
        if hints:
            st.caption("Possibly the same activity listed twice: " + "; ".join(hints) + ". Merge them with “Edit” if "
                       "they are (widen one, delete the other).")
        if len(main_acts) > rules.MAX_MAIN:
            st.caption(f"More than {rules.MAX_MAIN} business areas: check whether some belong together.")
        if st.button("＋ Add an activity", key=f"add_{v}_{name}"):
            edit_activity(name, None)
        with st.expander("Company profile, all sources, map again"):
            key = f"prof_{v}_{name}"
            st.text_area("Company profile", value=profile, key=key, height=100,
                         on_change=_store_profile, args=(name, key))
            found = m.get("search") or {}
            if found.get("sources"):
                st.markdown(f"**Sources** · {found.get('model', '')} · accessed {found.get('date', '')}")
                for s in found["sources"]:
                    link = f"[{esc(s['title'])}]({s['url']})" if s.get("url") else esc(s["title"])
                    st.markdown(f"[{s['n']}] {link} · *{SOURCE_KIND.get(s.get('type'), s.get('type') or 'unlabelled')}*")
            st.markdown("**Map this company again** (replaces its profile and activities; the other companies "
                        "are kept)")
            r1, r2 = st.columns(2)
            website = r1.text_input("Website (optional)", value=c.get("website", ""), key=f"reweb_{v}_{name}")
            mode = r2.radio("Activities from", am.SOURCE_OPTIONS, index=am.SOURCE_OPTIONS.index(am.source_mode(c)),
                            key=f"resrc_{v}_{name}", horizontal=True, help=SOURCE_HELP)
            text = st.text_area("Description of the company's activities (used for “my description” and “both”)",
                                value=c.get("pasted", ""), key=f"repaste_{v}_{name}", help=DESCRIPTION_HELP)
            if st.button(f"Map {name} again", key=f"remap_{v}_{name}"):
                if mode == "my description" and not text.strip():
                    st.error("Enter a description, or choose web search.")
                else:
                    start_work("remap", name=name, website=website, mode=mode, pasted=text)


def remap_company(ai, name, website, mode, pasted):
    companies = [dict(c, website=website.strip(), source=mode, pasted=pasted.strip()) if c["name"] == name else c
                 for c in ss.companies]
    company = next(c for c in companies if c["name"] == name)
    first, t0 = ss.log.mark(), time.time()
    with st.status(f"Researching {name} again (one company, its own calls) ...", expanded=True) as status:
        ss.mapped[name] = am.map_company(ai, company, companies, USE_SAVED)
        status.update(label=f"{name} researched again in {time.time() - t0:.0f} s", state="complete")
    ss.companies = companies
    ss.relationships = am.find_relationships(ss.mapped, companies)
    ss.acts[name] = copy.deepcopy(extracted(ss.mapped[name]))
    cmp.ensure_ids(ss.acts)
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    ss.profiles_edit.pop(name, None)
    ss.acts_version += 1
    log_stage("mapping", first, time.time() - t0)


def _store_keep(word, key):
    keep = set(ss.get("keep_words") or [])
    (keep.add if ss.get(key) else keep.discard)(word.lower())
    ss.keep_words = sorted(keep)


def name_word_review():
    """Option b (17 Oct, Linda): before the comparison, the brands and group company names that also appear as words in
    the descriptions. They are removed by default (confidentiality first); the lawyer can keep an ordinary product
    word, so the comparison still sees it. The choice is recorded in the audit log."""
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in ss.companies}
    found = cmp.names_used_as_words(ss.companies, ss.acts, group)
    if not found:
        return
    keep = set(ss.get("keep_words") or [])
    with st.container(border=True):
        st.markdown(f"**Names that are also used as words in the descriptions** · {plural(len(found), 'word')}")
        st.caption("Before the comparison, every company name, brand and group company is removed from the descriptions, "
                   "so that the AI never sees who is involved. Some brands are also ordinary product words (e.g. a brand "
                   "called after its product); removing them can take away what the comparison needs. Tick a word "
                   "only if it describes the product rather than identifying the company. The entered company names "
                   "are always removed.")
        for f in found:
            ex = "; ".join(f"{esc(c)}: “{esc(t[:120])}”" for c, t in f["examples"])
            key = f"keep_{ss.acts_version}_{f['word']}"
            st.checkbox(f"Keep “{f['word']}” as an ordinary word", value=f["word"].lower() in keep, key=key,
                        help=f"A brand or group company of {f['company']}.", on_change=_store_keep,
                        args=(f["word"], key))
            st.caption(f"{esc(f['company'])}'s brand or group company · used in: {ex}")


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


def activities_hash(activities):
    """What the comparison depends on: the activities and (17 Oct) the words the lawyer keeps in the descriptions."""
    state = {"activities": activities, "keep_words": sorted(ss.get("keep_words") or [])}
    return hashlib.sha256(json.dumps(state, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


# =============================================================== stage ③ factual comparison
POSITION_FIELDS = ("portco", "label_a", "label_b", "a", "b", "abstract_a", "abstract_b", "sims")


def prepare_comparison(activities):
    """Names, abstracts and content keys of the activities to compare, and how many pairs are new: a pair goes to the
    AI only if no result for exactly these two anonymised activities exists in this session (16 Oct). Pure code."""
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


def confirm_activities(ai, activities, problems, profiles_text):
    if problems:
        st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        return False
    plan = prepare_comparison(activities)
    target, portcos, names, profiles, keys = (plan[k] for k in ("target", "portcos", "names", "profiles", "keys"))
    ss.setdefault("vec_cache", {})
    ss.setdefault("pair_cache", {})
    first, t0 = ss.log.mark(), time.time()
    with st.status("Comparing the activities: one pair of anonymised descriptions per AI call, in parallel",
                   expanded=True) as status:
        st.write(f"✔ Anonymised: {len(rules.name_variants(names))} name variants removed"
                 + (f"; ✖ names left in {len(plan['blocked'])} abstracts (their pairs are blocked)" if plan["blocked"]
                    else "; name check passed for every abstract"))
        missing = {n: [a for a in p["activities"] if keys[a["aid"]] not in ss.vec_cache] for n, p in profiles.items()}
        missing = {n: acts for n, acts in missing.items() if acts}
        try:
            with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
                futures = {ex.submit(cmp.embed_company, ai, n, acts, names): n for n, acts in missing.items()}
                for fut in cf.as_completed(futures):
                    for a, v in zip(missing[futures[fut]], fut.result()):
                        ss.vec_cache[keys[a["aid"]]] = v
        except Exception as e:  # noqa: BLE001 - never continue without vectors (see comparison.embed_company)
            status.update(label="The comparison stopped", state="error")
            st.error(f"The embeddings failed, so nothing was compared: {type(e).__name__}: {e}. Your activities are "
                     "kept; go back and press “Compare activities” again.")
            st.button("← Back to the activities", on_click=go_to, args=(2,))
            return False
        st.write(f"✔ Embeddings: {plural(len(missing), 'request')}, one per company, anonymised texts only"
                 if missing else "✔ Embeddings: all kept from before")
        for p in profiles.values():
            p["vectors"] = [ss.vec_cache[keys[a["aid"]]] for a in p["activities"]]
        pairs = cmp.build_pairs(target, portcos, profiles)
        pair_key = {id(p): (keys[p["a"]["aid"]], keys[p["b"]["aid"]]) for p in pairs}
        todo = [p for p in pairs if pair_key[id(p)] not in ss.pair_cache]
        if len(pairs) > len(todo):
            st.write(f"✔ {plural(len(pairs) - len(todo), 'pair')} kept from before (nothing changed in them)")
        if todo:
            bar = st.progress(0.0, text=f"0 of {len(todo)} pairs compared")
            with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
                futures = {ex.submit(cmp.assess, ai, p, names): p for p in todo}
                for done, fut in enumerate(cf.as_completed(futures), start=1):
                    ss.pair_cache[pair_key[id(futures[fut])]] = fut.result()
                    if done % 5 == 0 or done == len(todo):
                        bar.progress(done / len(todo), text=f"{done} of {len(todo)} pairs compared")
        results = [{**ss.pair_cache[pair_key[id(p)]], **{k: p[k] for k in POSITION_FIELDS}} for p in pairs]
        status.update(label=f"{plural(len(todo), 'pair')} compared, {len(pairs) - len(todo)} kept, in "
                            f"{time.time() - t0:.0f} s", state="complete", expanded=False)
    ss.confirmed = activities
    ss.profiles_text = profiles_text
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


# =============================================================== stage ③ the preliminary assessment table
# One box per portfolio company (decided 16 Oct). In it: each target activity (the fixed reference point) with the
# portfolio company's activities that meet it; columns: target activity · portco activity · Commission market
# definition (grey until stage ④) · preliminary assessment · notes · check. Pairs involving "Other activities" come
# last and collapsed. Each target activity's block ends with one line naming the activities that do not meet it,
# with the reasons and "Add back" behind "Why?" (16 Oct, replacing the separate list of pairs without overlap).
WIDTHS = [1.6, 1.6, 1.25, 3.2, 1.5, 1.15]
BLOCK_RULE = "<hr style='margin:6px 0 10px 0;border:none;border-top:2px solid rgba(128,128,128,0.45)'>"
ROW_RULE = "<hr style='margin:4px 0 8px 0;border:none;border-top:1px dashed rgba(128,128,128,0.35)'>"
FOUND_BY_WORDS = {"AI": "found by the AI", "rule": "found by a code rule", "AI and rule": "found by the AI and a code rule"}
RULE_WORDS = {
    "A could be an input for B": "{t} sells to producers, and its products are close to inputs that {p} lists",
    "B could be an input for A": "{p} sells to producers, and its products are close to inputs that {t} lists",
    "A could be resold by B": "{t} sells to shops or wholesalers, and {p} resells a close range",
    "B could be resold by A": "{p} sells to shops or wholesalers, and {t} resells a close range",
}
LEGEND = ("🔴 potential horizontal overlap · 🟠 potential vertical relationship (the arrow points downstream) · "
          "●●● same direct customers, ●●○ partly the same, ●○○ different (never a reason on its own to dismiss) · "
          + SOURCES_LEGEND)


def _store_override(pid, field, key):
    """Widget callback: overrides live in their own store, so they survive when a section is hidden."""
    entry = ss.override_store.setdefault(pid, {"dismiss": False, "add_back": False, "note": ""})
    value = ss.get(key)
    entry[field] = value.strip() if isinstance(value, str) else bool(value)


def _store_part(pid, part, key):
    """Widget callback for one label of a pair with several labels (17 Oct): dismissed on its own."""
    entry = ss.override_store.setdefault(pid, {"dismiss": False, "add_back": False, "note": ""})
    entry.setdefault("dismissed_parts", {})[part] = bool(ss.get(key))


def kept(status):
    return status in ("candidate", "unclear", "added back by user")


def listing(items, limit=4):
    items = [esc(i) for i in items]
    if not items:
        return ""
    return ", ".join(items[:limit]) + (f" and {len(items) - limit} more" if len(items) > limit else "")


def table_cell(a, company):
    """An activity in the table: name, stage, sources. What it includes and does is in 'Details'."""
    name = "Other activities" if rules.category(a) == "other" else capital(a["product"])
    return f"**{esc(name)}**  \n{stage_text(a)} · {source_markers(a, company)}"


def direction(link, r, target, portco):
    """(upstream company, its activity, downstream company, its activity) of a vertical link."""
    if link in ("A could be an input for B", "A could be resold by B"):
        return target, r["a"], portco, r["b"]
    return portco, r["b"], target, r["a"]


def link_sentence(link, vitems, r, target, portco):
    """A vertical link in words, with the names re-attached and the items the link concerns (option C)."""
    a = f"{esc(target)}'s {listing(vitems.get('a', [])) or esc(r['a']['product'])}"
    b = f"{esc(portco)}'s {listing(vitems.get('b', [])) or esc(r['b']['product'])}"
    return {
        "A could be an input for B": f"{a} could be an input for {b}",
        "B could be an input for A": f"{b} could be an input for {a}",
        "A could be resold by B": f"{a} could be resold through {b}",
        "B could be resold by A": f"{b} could be resold through {a}",
    }.get(link, esc(link))


def assessment(r, status, target, portco):
    """The preliminary assessment of one pair, assembled in code from the structured answers (no AI call). The
    reasons are in 'Details'. A label the user dismissed on its own is struck through (17 Oct)."""
    d, c = r["decision"], r["comparison"]
    m = r.get("matches") or {}
    off = set(cmp.dismissed_parts(r, ss.get("overrides") or {}))
    lines = ["✖ **Dismissed by you**"] if status == "dismissed by user" else []
    if status == "added back by user":
        return "↩ **Added back by you.** The tool found no overlap; see “Details”."
    if d["status"] == "unclear":
        return "  \n".join(lines + ["❔ **Unclear, please check** (see “Details”)"])
    own = " · own use" if "captive" in r["flags"] else ""

    def mark(part, text):
        return f"✖ ~~{text}~~ *(dismissed by you)*" if part in off and status != "dismissed by user" else text

    if d["horizontal"]:
        kind = "same product" if c["product_relation"] == "same product" else "similar product"
        sa, sb = stage_of(r["a"]).lower(), stage_of(r["b"]).lower()
        level = f"same level ({sa})" if sa == sb else f"different levels ({sa} v {sb})"
        dots = f" · {r['customers']}" if r.get("customers") in ("●●●", "●●○", "●○○") else ""
        lines.append(mark("horizontal", f"🔴 **Potential horizontal overlap** ({kind}) · {level}{dots}{own}"))
        a, b = listing(m.get("a", [])), listing(m.get("b", []))
        if (a or b) and "horizontal" not in off:
            lines.append(f"with regard to: *{esc(target)}:* {a or '–'} · *{esc(portco)}:* {b or '–'}")
    vitems = {v["link"]: v for v in r.get("vertical_items") or []}
    for link in d["vertical_links"]:
        up, up_act, down, down_act = direction(link, r, target, portco)
        lines.append(mark(link, f"🟠 **Potential vertical relationship** · {esc(up)} ({stage_of(up_act).lower()}) → "
                                f"{esc(down)} ({stage_of(down_act).lower()}){own}"))
        if link not in off:
            lines.append(link_sentence(link, vitems.get(link, {}), r, target, portco))
    return "  \n".join(lines)


def part_label(part, r, target, portco):
    """Short label for the narrow column (the colour marks of the assessment), the full wording as help text."""
    parts = cmp.assessment_parts(r)
    if part == "horizontal":
        return "🔴 Dismiss", "Dismiss the potential horizontal overlap only"
    up, _, down, _ = direction(part, r, target, portco)
    verticals = [x for x in parts if x != "horizontal"]
    number = f" {verticals.index(part) + 1}" if len(verticals) > 1 else ""
    return f"🟠 Dismiss{number}", f"Dismiss the potential vertical relationship {up} → {down} only"


def pair_details(r, target, portco):
    """'Details': why (the AI's reasons or the code rule), the customer score, the sources of both activities, and
    at the end the exact text the AI received."""
    c, d = r["comparison"], r["decision"]
    st.markdown("**Why**")
    why = []
    if d["horizontal"] or d["status"] == "unclear" or d["status"] == "screened out":
        why.append(f"*Product ({c['product_relation']}):* {esc(c.get('product_reason', ''))}")
    ai_links = [link for link in d["vertical_links"] if d["found_by"][link] != "rule"]
    for link in d["vertical_links"]:
        up, _, down, _ = direction(link, r, target, portco)
        text = f"*Vertical ({esc(up)} → {esc(down)}, {FOUND_BY_WORDS[d['found_by'][link]]})*"
        if d["found_by"][link] == "rule":
            text += ": " + esc(RULE_WORDS[link].format(t=target, p=portco)) + "."
        why.append(text)
    if ai_links:
        why.append(esc(c.get("vertical_reason", "")))
    for link, reason in d.get("disregarded", []):
        who = target if reason.startswith("A ") else portco
        why.append(f"*AI link disregarded:* {esc(cmp.describe_link(link, target, portco))}; {esc(who)} {esc(reason[2:])}.")
    st.markdown("  \n".join(why))
    if d["horizontal"] and r.get("customers") in CUSTOMER_TEXT and r.get("customers"):
        ca = words_list(_shown(r["a"].get("direct_customers")))
        cb = words_list(_shown(r["b"].get("direct_customers")))
        st.markdown(f"**Direct customers** {r['customers']}  \n{esc(target)} sells to {esc(ca or 'not stated')}; "
                    f"{esc(portco)} to {esc(cb or 'not stated')} → {CUSTOMER_TEXT[r['customers']]}. Different customer "
                    "groups alone never make separate markets (Market Definition Notice (88)–(89)).")
    if "captive" in r["flags"]:
        st.markdown("**Own use:** produced for the group's own use, not sold on the market (draft Merger Guidelines "
                    "para 103(i)). It cannot supply the other company, so a link where it would be the supplier is set "
                    "aside (shown under “No overlap found”, with “Add back”).")
    st.markdown("**Sources**")
    for who, act in ((target, r["a"]), (portco, r["b"])):
        includes = ", ".join(esc(i) for i in act.get("includes") or [])
        evidence = act.get("evidence") or ""
        text = (f"*{esc(who)}:* **{esc(act['product'])}** {stage_text(act)} {source_markers(act, who)}  \n"
                f":gray[{esc(everyday(act))}" + (f" · includes: {includes}" if includes else "") + "]")
        if evidence and evidence not in ("not stated", "added by user"):
            text += f"  \n> {esc(evidence[:500])}"
        st.markdown(text, unsafe_allow_html=True)
    if DEV_MODE:
        s = r["sims"]
        rejected = (r.get("matches") or {}).get("rejected") or []
        st.caption(f"Development · pair {cmp.pair_id(r)} · rule: {d['rule']} · code signals: "
                   f"{'; '.join(f'{x} ({why})' for x, why in r['code_signals']) or 'none'} · similarity "
                   f"{s['product']:.2f} · input {s['input_a_to_b']:.2f}/{s['input_b_to_a']:.2f}"
                   + (f" · items not found: {'; '.join(rejected)}" if rejected else "") + f" · flags: {r['flags'] or 'none'}")
    st.markdown("**What the AI saw** (no names; the name check ran before the call)")
    st.code(r["prompt"], language=None, wrap_lines=True)


def pair_row(r, status, rv, target, portco, first):
    """One sub-row: target activity (first sub-row of a block only), portco activity, market definition (step ④),
    assessment, the user's note, and the check (dismiss or added back, details)."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    s = status[pid]
    cols = st.columns(WIDTHS, vertical_alignment="top")
    if first:
        cols[0].markdown(table_cell(r["a"], target), unsafe_allow_html=True)
    cols[1].markdown(table_cell(r["b"], portco), unsafe_allow_html=True)
    cols[2].markdown(":gray[added in step ④]")
    cols[3].markdown(assessment(r, s, target, portco))
    with cols[4]:
        key = f"note_{rv}_{pid}"
        st.text_area("Note", value=o.get("note", ""), key=key, placeholder="Note (optional)",
                     label_visibility="collapsed", height=68, on_change=_store_override, args=(pid, "note", key))
    with cols[5]:
        if r["decision"]["status"] == "screened out":
            key = f"add_{rv}_{pid}"
            st.checkbox("Added back", value=o.get("add_back", False), key=key,
                        on_change=_store_override, args=(pid, "add_back", key))
        elif len(cmp.assessment_parts(r)) > 1 and not o.get("dismiss"):
            # 17 Oct (Linda): a pair with a horizontal and a vertical label (or two vertical links) gets one box per
            # label, so that one can be dismissed and the other kept
            chosen = o.get("dismissed_parts") or {}
            for k, part in enumerate(cmp.assessment_parts(r)):
                key = f"dis_{rv}_{pid}_{k}"
                label, tip = part_label(part, r, target, portco)
                st.checkbox(label, value=bool(chosen.get(part)), key=key, help=tip,
                            on_change=_store_part, args=(pid, part, key))
        else:
            key = f"dis_{rv}_{pid}"
            st.checkbox("Dismiss", value=o.get("dismiss", False), key=key,
                        on_change=_store_override, args=(pid, "dismiss", key))
        with st.popover("Details"):
            pair_details(r, target, portco)


def table_header(target, portco):
    header = st.columns(WIDTHS)
    for col, label in zip(header, [f"{esc(target)} activity", f"{esc(portco)} activity", "Commission market definition",
                                   "Preliminary assessment", "Notes", ""]):
        if label:                      # an empty "****" would render as a horizontal line
            col.markdown(f"**{label}**")


def short_name(a):
    return "Other activities" if rules.category(a) == "other" else capital(a["product"])


def no_overlap_row(ta, rows, rv, target, portco, n_portco, first):
    """The last line of a target activity's block (16 Oct): the portfolio company's activities that do not meet it.
    'Why?' shows the AI's reasons; 'Add back' moves a pair into the table as a row of its own."""
    cols = st.columns([WIDTHS[0], sum(WIDTHS[1:5]), WIDTHS[5]], vertical_alignment="top")
    if first:
        cols[0].markdown(table_cell(ta, target), unsafe_allow_html=True)
    if len(rows) >= n_portco:
        cols[1].markdown(f":gray[No overlap found with any of {esc(portco)}'s activities]")
    else:
        cols[1].markdown(":gray[No overlap found with:] " + " · ".join(esc(short_name(r["b"])) for r in rows))
    with cols[2].popover("Why?"):
        st.caption("The AI's reasons, pair by pair. “Add back” moves a pair into the table, where it can be dismissed "
                   "again.")
        for r in rows:
            pid = cmp.pair_id(r)
            key = f"add_{rv}_{pid}"
            reasons = [x for x in (r["comparison"].get("product_reason"), r["comparison"].get("vertical_reason")) if x]
            text = f"**{esc(short_name(r['b']))}** {stage_text(r['b'])}  \n" + esc(" ".join(reasons) or "No reason given.")
            for link, why in r["decision"].get("disregarded") or []:
                who = target if why.startswith("A ") else portco
                text += (f"  \n*Link set aside by the tool:* {esc(cmp.describe_link(link, target, portco))}; "
                         f"{esc(who)} {esc(why[2:])}.")
            st.markdown(text)
            st.checkbox("Add back", value=ss.override_store.get(pid, {}).get("add_back", False), key=key,
                        on_change=_store_override, args=(pid, "add_back", key))


def target_block(ta, kept_rows, screened, status, rv, target, portco, n_portco):
    """One target activity: the portfolio company's activities that meet it (one row each), then one line naming
    those that do not (16 Oct: replaces the separate list of pairs without overlap)."""
    st.markdown(BLOCK_RULE, unsafe_allow_html=True)
    for k, r in enumerate(kept_rows):
        if k:
            st.markdown(ROW_RULE, unsafe_allow_html=True)
        pair_row(r, status, rv, target, portco, first=(k == 0))
    if screened:
        if kept_rows:
            st.markdown(ROW_RULE, unsafe_allow_html=True)
        no_overlap_row(ta, screened, rv, target, portco, n_portco, first=not kept_rows)


def portco_sentence(target, portco, pairs, status):
    """One sentence per portfolio company, counted by business area (not by pairs), assembled in code. Links that
    involve only "Other activities" are counted separately (17 Oct): they sit in the collapsed section, and a count
    without saying so read as if the table contradicted the sentence."""
    acts = list(dict.fromkeys(r["label_b"] for r in pairs))
    live = [r for r in pairs if kept(status[cmp.pair_id(r)])]
    n_acts = plural(len(acts), "activity", "activities")
    if not live:
        return f"None of {esc(portco)}'s {n_acts} meets an activity of {esc(target)}."
    main_live = [r for r in live if not is_other(r)]
    other_live = [r for r in live if is_other(r)]
    other_note = (f"{plural(len(other_live), 'potential link')} involving “Other activities” (own use and side lines), "
                  "in the collapsed section below")
    if not main_live:
        return f"No overlap with {esc(target)}'s main activities; {other_note}."
    found = [r for r in main_live if r["decision"]["status"] == "candidate"]
    off = {cmp.pair_id(r): set(cmp.dismissed_parts(r, ss.get("overrides") or {})) for r in found}
    h = {r["label_b"] for r in found if r["decision"]["horizontal"] and "horizontal" not in off[cmp.pair_id(r)]}
    v = {r["label_b"] for r in found if set(r["decision"]["vertical_links"]) - off[cmp.pair_id(r)]}
    check = {r["label_b"] for r in main_live
             if r["decision"]["status"] == "unclear" or status[cmp.pair_id(r)] == "added back by user"}
    touched = {r["label_b"] for r in main_live}
    parts = [x for x in (f"horizontal in {len(h)}" if h else "", f"vertical in {len(v)}" if v else "",
                         f"to check in {len(check)}" if check else "") if x]
    text = (f"{len(touched)} of {esc(portco)}'s {n_acts} meet main activities of {esc(target)}: "
            f"{', '.join(parts) or 'see the table'}.")
    return text + (f" Also {other_note}." if other_live else "")


def is_other(r):
    return rules.category(r["a"]) == "other" or rules.category(r["b"]) == "other"


def portco_section(i, p, target, pairs, status, rv):
    """One box per portfolio company. Every compared target activity appears once, in the target's order: with the
    rows that meet it and a line naming what does not. Pairs involving "Other activities" are collapsed below.
    A portfolio company where nothing meets (17 Oct, Linda): its table is folded into one collapsed box, "open to
    check", with the same lines, reasons and "Add back" inside; once a pair is added back, the box opens up again."""
    with st.container(border=True):
        st.markdown(f"#### {i}. {esc(p)}")
        st.markdown(portco_sentence(target, p, pairs, status))
        excluded = [a for a in ss.confirmed.get(p, []) if a.get("excluded")]
        if excluded:
            st.caption("Not compared (excluded by you): " + "; ".join(
                f"{esc(a['product'])} ({esc(a.get('exclusion_reason', ''))})" for a in excluded))
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
    """The table of one portfolio company's box. Inside the collapsed box (nested) Streamlit allows no second
    expander, so "Other activities" is a plain sub-heading there."""
    main_t = [ta for ta in t_acts if rules.category(ta) == "main"]
    if main_t:
        table_header(target, p)
        for ta in main_t:
            rs = rows_of(ta)
            target_block(ta, [r for r in rs if not is_out(r) and not is_other(r)], [r for r in rs if is_out(r)],
                         status, rv, target, p, n_portco)
    other_rows = [r for r in pairs if not is_out(r) and is_other(r)]
    other_t = [ta for ta in t_acts if rules.category(ta) == "other"]
    if not (other_rows or other_t):
        return
    title = f"Other activities (own use and side lines): {plural(len(other_rows), 'potential link')}"
    if nested:
        st.markdown(f"**{title}**")
        other_table(t_acts, rows_of, is_out, status, rv, target, p, n_portco)
    else:
        with st.expander(title + " · show"):
            other_table(t_acts, rows_of, is_out, status, rv, target, p, n_portco)


def other_table(t_acts, rows_of, is_out, status, rv, target, p, n_portco):
    table_header(target, p)
    for ta in t_acts:
        rs = rows_of(ta)
        kept_rows = [r for r in rs if not is_out(r) and is_other(r)]
        screened = [r for r in rs if is_out(r)] if rules.category(ta) == "other" else []
        if kept_rows or screened:
            target_block(ta, kept_rows, screened, status, rv, target, p, n_portco)


def stage_overview(ai):
    h1, h2 = st.columns([4, 1], vertical_alignment="center")
    h1.subheader("③ Preliminary assessment")
    h2.button("← Back to the activities", on_click=go_to, args=(2,), width="stretch")
    st.write("For each portfolio company, the table shows which of its activities meet each activity of the target, and "
             "how. “Potential” means: not yet checked against the Commission's market definitions, which are added in "
             "step ④. Where you disagree, tick “Dismiss”; a row with a horizontal and a vertical label has one box for each "
             "(🔴 / 🟠), so you can dismiss one and keep the other; "
             "a note is optional. Both go into the audit log. The line "
             "“No overlap found with” under a target activity names the activities that do not meet it; “Why?” shows "
             "the reasons and lets you add a pair back.")
    if ss.get("acts") and ss.get("confirmed_hash") and activities_hash(ss.acts) != ss.confirmed_hash:
        st.info("You changed the activities after this comparison. Go back to the activities and press “Update the "
                "comparison”: only the new or changed pairs are compared again, and your dismissals and notes stay.")
    st.caption(LEGEND)
    if DEV_MODE:
        st.caption(stage_cost("confirm"))
    results = ss.results
    target = ss.companies[0]["name"]
    portcos = [c["name"] for c in ss.companies[1:]]
    rv = ss.results_version
    ss.setdefault("override_store", {})
    current = {cmp.pair_id(r) for r in results}
    ss.overrides = {pid: dict(o) for pid, o in ss.override_store.items()
                    if pid in current and (o.get("dismiss") or o.get("add_back") or o.get("note")
                                           or any((o.get("dismissed_parts") or {}).values()))}
    status = {cmp.pair_id(r): cmp.effective_status(r, ss.overrides) for r in results}
    show_relationships()

    with st.expander(f"🎯 Target: {target}"):
        st.write(profile_of(target))
        for a in [ss.confirmed[target][i] for i in display_order(ss.confirmed[target])]:
            st.markdown("- " + activity_line(a, target), unsafe_allow_html=True)

    for i, p in enumerate(portcos, start=1):
        portco_section(i, p, target, [r for r in results if r["portco"] == p], status, rv)

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
        part = stage_calls(stage)
        calls += len(part)
        cost += sum(c["cost"] for c in part)
        seconds += stage_seconds(stage)
        models |= {c["model"] for c in part}
    return (f"Run summary: {calls} AI calls · models: {', '.join(sorted(models))} · USD {cost:.3f} at token prices "
            f"(web search fees not included) · {seconds:.0f} s")


def benchmark_panel(results):
    """Development only: the expert benchmark (benchmark.py) on the app's own results, for the examples (same target
    and same portfolio only)."""
    try:
        import benchmark
    except Exception:  # noqa: BLE001 - development tools not present
        return
    target = ss.companies[0]["name"]
    portcos = {c["name"] for c in ss.companies[1:]}
    case = next((k for k, ex in examples.EXAMPLES.items() if ex["target"] == target and set(ex["portfolio"]) == portcos),
                None)
    if not case:
        return
    view = {n: {"extraction": {"activities": acts}, "mentions": (ss.mapped.get(n) or {}).get("mentions", [])}
            for n, acts in ss.confirmed.items()}
    checks = benchmark.run_checks(case, target, view, results, rules.SIMILARITY_UNCLEAR)
    with st.expander(f"Development: benchmark {case} (spec section 13)"):
        st.dataframe(pd.DataFrame([{"Check": c["id"], "Portco": c["portco"], "Expected": c["expect"],
                                    "Result": c["mark"], "What": c["what"], "Detail": c["detail"],
                                    "Pairs": ", ".join(c["labels"][:6])} for c in checks]), hide_index=True)


# =============================================================== audit log
def audit_calls():
    """Every call of the current screen (since the screen started): the research of each company, including companies
    mapped again, and every comparison run. Since 16 Oct a comparison only sends new or changed pairs, so no call
    is repeated, and the results shown can come from any of these runs."""
    return ss.log.calls[ss.get("run_first", 0):]


def audit_snapshot(ai):
    """References to everything the audit log contains, taken in the script thread. The JSON itself is built
    only when the user clicks the download button (on another thread, which cannot read session state)."""
    return {"created": datetime.now().isoformat(timespec="seconds"), "profile": PROFILE, "dev_mode": DEV_MODE,
            "cache": USE_CACHE, "saved_searches": USE_SAVED, "models": dict(ai.models),
            "companies": ss.get("companies"), "mapped": ss.get("mapped"), "relationships": ss.get("relationships"),
            "confirmed": ss.get("confirmed"), "profiles": ss.get("profiles_text"),
            "names": list(ss.get("names") or []), "keep_words": list(ss.get("keep_words") or []),
            "abstracts": ss.get("profiles_meta"), "results": list(ss.get("results") or []),
            "overrides": dict(ss.get("overrides") or {}), "calls": audit_calls()}


def audit_json(snap):
    slim = [{k: v for k, v in r.items() if k != "sims"}
            | {"sims": {k: round(v, 3) for k, v in r["sims"].items()},
               "status_after_overrides": cmp.effective_status(r, snap["overrides"])}
            for r in snap["results"]]
    log = {
        "created": snap["created"], "profile": snap["profile"], "dev_mode": snap["dev_mode"],
        "development_cache": snap["cache"], "saved_searches": snap["saved_searches"], "models": snap["models"],
        "prices": {"checked": ai_client.PRICES_CHECKED, "usd_per_1m_tokens": ai_client.PRICES},
        "thresholds": {"input_match": rules.INPUT_MATCH, "resale_match": rules.RESALE_MATCH},
        "companies": snap["companies"],
        "stage_1_2_activity_mapping": snap["mapped"],
        "existing_relationships": snap["relationships"],
        "stage_2_company_profiles": snap["profiles"],
        "stage_2_confirmed_activities": snap["confirmed"],
        "anonymisation": {"name_variants_removed": sorted(rules.name_variants(snap["names"])),
                          "kept_as_ordinary_words_by_user": snap["keep_words"],
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
1. **Activities.** It researches each company separately on public websites, or reads a description you provide, and
   lists its business areas with their stage in the value chain (raw materials, intermediate products, manufacturing,
   wholesale, retail, services). You check and correct them.
2. **Preliminary assessment.** It compares every activity of the target with every activity of each portfolio company.
   The AI sees descriptions only, never the company names.
3. **Commission precedents.** It looks up how the European Commission defined the relevant markets in past decisions.

**Horizontal overlap:** both companies offer the same or substitutable products (potential competitors).
**Vertical relationship:** one company's products could be an input for the other, or could be resold by it
(potential supplier and customer). Until step 3, every result is *potential*: not yet checked against the Commission's
market definitions.

The result is a working document for a lawyer to verify, not a legal conclusion. The facts about each company carry
their sources (hover over the numbers); the assessment is the AI's reasoning on anonymised descriptions, shown under
“Details”."""

STEPS = {1: "Companies", 2: "Activities", 3: "Preliminary assessment"}
SCROLL_TOP = """<script>
const d = window.parent.document;
for (const s of ['[data-testid="stMain"]', 'section.stMain', 'section.main', '[data-testid="stAppViewContainer"]']) {
  const e = d.querySelector(s); if (e) { e.scrollTo({top: 0}); }
}
window.parent.scrollTo(0, 0);
</script>"""


def scroll_to_top_on_new_step(step):
    """Streamlit keeps the scroll position when the screen changes, so a new step would open in the middle of the
    page (16 Oct). A small script jumps to the top once per change of step."""
    slot = st.empty()          # always one element here, so that everything below keeps its position (17 Oct)
    if ss.get("_shown_step") != step:
        ss._shown_step = step
        with slot:
            st.iframe(SCROLL_TOP, height=1)      # our own constant script, never user input


def progress_nav(step):
    """The steps as buttons (16 Oct): every step already reached can be opened again; nothing is deleted by going
    back. Returns the last column, for the "New screen" button."""
    reachable = {1: True, 2: bool(ss.get("acts")), 3: ss.get("results") is not None}
    cols = st.columns([1.2, 1.2, 1.7, 1.1], vertical_alignment="center")
    for k, name in STEPS.items():
        cols[k - 1].button(f"{'①②③'[k - 1]} {name}", key=f"nav_{k}", type="primary" if k == step else "secondary",
                           disabled=not reachable[k], on_click=go_to, args=(k,), width="stretch")
    return cols[3]


def done_summaries(step):
    """Finished steps in one line each, as context; the step buttons above lead back to them."""
    lines = []
    if step > 1 and ss.get("companies"):
        lines.append(f"✔ **Companies:** target {esc(ss.companies[0]['name'])} · portfolio: "
                     f"{esc(', '.join(c['name'] for c in ss.companies[1:]))}")
    if step > 2 and ss.get("confirmed"):
        acts = [a for v in ss.confirmed.values() for a in v]
        excl = sum(a.get("excluded", False) for a in acts)
        gaps = sum(rules.is_gap(a) and not a.get("excluded", False) for a in acts)
        lines.append(f"✔ **Activities:** {len(acts) - excl - gaps} compared" + (f", {excl} excluded" if excl else "")
                     + (f", {gaps} not stated (questions for the company)" if gaps else ""))
    slot = st.empty()          # always one element (see scroll_to_top_on_new_step)
    if lines:
        slot.markdown("  \n".join(lines))


st.title("EU Overlap Screen")
step = ss.get("step", 1)
if step == 1:
    st.markdown(INTRO)
else:
    with st.expander("How this tool works"):
        st.markdown(INTRO)
ai = make_ai(credentials())
if step == 2 and not ss.get("acts"):
    step = ss.step = 1
if step == 3 and ss.get("results") is None:
    step = ss.step = 2 if ss.get("acts") else 1
scroll_to_top_on_new_step(step)
top = progress_nav(step)
if top.button("↺ New screen", help="Discard this screen and start again", width="stretch"):
    confirm_reset(audit_snapshot(ai) if ss.get("mapped") else None)
done_summaries(step)
st.divider()
if DEV_MODE:
    dev_sidebar(ai)
# Two slots (17 Oct): the working screen and the page. During long work the page slot is set to empty, which removes
# the previous screen at once (writing a new container into the same slot would keep its old children, faded, until
# the work ends), and the progress is shown in the slot above it.
work = st.empty()
body = st.empty()
job = ss.pop("pending", None)
if job:
    body.empty()
    with work.container():
        if do_work(ai, job):
            st.rerun()
else:
    with body.container():
        if step == 1:
            stage_companies(ai)
        elif step == 2:
            stage_activities(ai)
        else:
            stage_overview(ai)