"""
app.py - EU Overlap Screen (LAWS90286 Assignment 2): a preliminary EU merger control overlap screen.

The steps: ① Companies, ② Activities, ③ Preliminary assessment, ④ Commission market definitions, ⑤ Summary, and the
Word document (export.py). Geography is not part of the screen.
Going back never deletes anything: a changed company is researched again and only new or changed pairs are compared
again (stable activity IDs and content keys); dismissals and notes stay with their pair.
The table of step ③ follows the overlap table used in practice: one box per portfolio company; in it, each target
activity with the portfolio company's activities that meet it and the preliminary assessment; step ④ adds, under each
row, the Commission's market definition and what follows from it.

    streamlit run app.py

Settings (.env locally, Secrets on Streamlit Cloud):
    DEV_MODE=1, APP_PASSWORD, OPENAI_API_KEY      development: password gate, cost counter, development tools
    MODEL_PROFILE=dev | final                      the models per step (ai_client.py); default: dev with
                                                   DEV_MODE on, final with DEV_MODE off (the submitted version)
    USE_CACHE=1                                    development only: reuse calls already paid for
With DEV_MODE off (the submitted version) the first screen asks for the user's own OpenAI key, which is kept for
the session only.
"""
import concurrent.futures as cf
import copy
import hashlib
import html
import json
import math
import re
import time
from datetime import datetime

import pandas as pd
import streamlit as st

import activity_mapping as am
import ai_client
import comparison as cmp
import examples
import export
import precedents as prec
import rules

st.set_page_config(page_title="EU Overlap Screen", page_icon="⚖️", layout="wide")

# =============================================================== visual design
# The theme (colours, fonts) is in .streamlit/config.toml. Here: the few things the theme cannot reach, in one place:
# the flat labels, the Commission line, the step tabs, the row rules and the hover boxes. Colours carry meaning only:
# red = potential horizontal overlap, yellow = potential vertical relationship; in step ④ the result of the
# Commission's view: blue = confirmed, grey = possible / not excluded, green = not supported, outline = no
# precedent. Neutral bands (no result: an unclear row, a rewritten line, a decision entry) are sand.
APP_CSS = """<style>
.lab{display:inline-block;font-size:.8rem;font-weight:600;padding:.08rem .45rem;border-radius:4px;line-height:1.45;
 margin:.05rem .25rem .05rem 0}
.lab-h{background:#FDECEA;color:#8A1C12}
.lab-v{background:#FFF3D1;color:#6E4B00}
.lab-q{background:#ECEAE5;color:#4A463F}
.lab-off{background:#ECEAE5;color:#7A756C;text-decoration:line-through}
.tag{font-size:.78rem;color:#55514A;font-style:italic;white-space:nowrap}
.sub2{color:#55514A}
.hov{cursor:help;border-bottom:1px dotted #8A857C}
.dots{cursor:help;letter-spacing:.05em;border-bottom:1px dotted #8A857C}
.src{text-decoration:none;font-size:.85em;color:#3A5A80}
.cline{background:#F2EFE8;color:#3D3A35;border-left:3px solid #C9C2B4;padding:.4rem .8rem;margin:.35rem 0 .2rem 0;
 line-height:1.55;border-radius:0}
.cline .ed{color:#55514A;font-style:italic;font-size:.8rem}
.cline.o-conf{background:#DCE6F2;border-left-color:#2E5A88;color:#1F3F66}
.cline.o-open{background:#ECEAE5;border-left-color:#8A857C;color:#3D3A35}
.cline.o-nosup{background:#E3EDE4;border-left-color:#5E8A66;color:#2F5D3A}
.cline.o-nopre{background:#FBFAF7;border:1px dashed #C9C2B4;border-left:3px solid #C9C2B4;color:#55514A}
.oc{display:inline-block;font-size:.75rem;font-weight:600;padding:.02rem .5rem;border-radius:10px;margin:0 .3rem;
 white-space:nowrap}
.oc.o-conf{background:#DCE6F2;color:#1F3F66}.oc.o-open{background:#ECEAE5;color:#4A463F}
.oc.o-nosup{background:#E3EDE4;color:#2F5D3A}.oc.o-nopre{background:#fff;color:#55514A;border:1px solid #C9C2B4}
details.mkts{margin:.1rem 0 .4rem 0}
details.mkts>summary{cursor:pointer;color:#5B7089;font-size:.85rem;list-style:none}
details.mkts>summary::-webkit-details-marker{display:none}
details.mkts>summary:before{content:"▸ "}
details.mkts[open]>summary:before{content:"▾ "}
.grp{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.95rem;margin:.5rem 0 .15rem 0}
.it{padding:.12rem 0 .12rem .6rem;border-left:2px solid #5B7089;margin:.1rem 0}
.it.one{border-left-color:#E2DDD2}
.or{color:#55514A;font-style:italic}
.rbox{background:#fff;border:1px solid #E2DDD2;border-radius:6px;padding:.6rem .9rem;margin:.3rem 0 .6rem 0;line-height:1.6}
.rbox .rt{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1rem;margin-bottom:.15rem}
.st-key-stepnav{border-bottom:1px solid #E2DDD2;margin-bottom:.4rem}
.st-key-stepnav button{background:transparent !important;border:none !important;border-bottom:2px solid transparent !important;
 border-radius:0 !important;box-shadow:none !important;color:#1F1D1A !important;padding-left:0;padding-right:0}
.st-key-stepnav button p{font-size:.95rem}
.st-key-stepnav button[data-testid="stBaseButton-primary"]{border-bottom-color:#22313F !important;color:#22313F !important}
.st-key-stepnav button[data-testid="stBaseButton-primary"] p{font-weight:600}
.st-key-stepnav button:disabled{color:#A39E94 !important}
.st-key-stepnav button:hover:not(:disabled){color:#22313F !important}
.workcard h4{margin-bottom:.2rem}
.lg{margin:.15rem 0;cursor:help;line-height:1.5;font-size:.88rem}
.tl-lead{font-size:1.05rem;margin:.1rem 0 1rem 0;max-width:52rem}
.tl{margin:.2rem 0 .2rem 0}
.tl-step{display:flex;gap:.8rem;position:relative;padding-bottom:1rem}
.tl-step:last-child{padding-bottom:0}
.tl-line{position:absolute;left:.82rem;top:1.9rem;bottom:.1rem;width:2px;background:#E2DDD2}
.tl-num{position:relative;display:inline-flex;align-items:center;justify-content:center;flex:none;width:1.7rem;
 height:1.7rem;border-radius:50%;background:#22313F;color:#fff;font-size:.85rem;font-weight:600}
.tl-title{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.08rem;line-height:1.3;margin-top:.1rem}
.tl-note{border-top:1px solid #E2DDD2;margin:.9rem 0 1.6rem 0;padding-top:.6rem;font-size:.88rem;max-width:52rem}
.chip{display:inline-block;font-size:.76rem;padding:.02rem .5rem;border-radius:10px;background:#ECEAE5;color:#4A463F;
 margin:0 .2rem;white-space:nowrap}
.k{display:inline-block;min-width:6.8rem;color:#55514A;font-size:.85rem}
.prof{background:#F2EFE8;border-radius:6px;padding:.55rem .8rem;margin:.2rem 0 .7rem 0;line-height:1.6}
.sec{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.45rem;color:#22313F;margin:.6rem 0 0 0}
.secsub{color:#55514A;font-size:.9rem;margin:0 0 .5rem 0}
.cut{height:0;border-top:2px solid #22313F;margin:1.8rem 0 1rem 0}
.st-key-tbox{border-left:4px solid #22313F !important}
.st-key-tband{background:#F2EFE8;border-radius:6px;padding:.7rem .9rem .3rem .9rem}
.st-key-tband .prof{background:#FBFAF7}
.basis{color:#6E6A63}
.sumt{border-collapse:collapse;width:100%;margin:.4rem 0 .3rem 0}
.sumt th{background:#22313F;color:#fff;text-align:left;padding:.45rem .7rem;font-weight:600}
.sumt th .lab{margin:0}
.sumt td{border-bottom:1px solid #C9C2B4;padding:.5rem .7rem;vertical-align:top}
.sumul{margin:0;padding-left:1.1rem}.sumul li{margin:.15rem 0}
[class*="st-key-thead"]{background:#22313F;border-radius:4px;padding:.5rem .7rem .05rem .7rem;margin-top:.3rem}
[class*="st-key-thead"] p{color:#FFFFFF !important;font-weight:600}
.wr{display:block;padding-left:.9rem}
.br{color:#6E6A63}
</style>"""
st.html(APP_CSS)            # style only: takes no space on the page

DEV_MODE = ai_client.flag("DEV_MODE")
PROFILE = ai_client.setting("MODEL_PROFILE", "dev" if DEV_MODE else "final")   # the submitted version never runs on dev
USE_CACHE = DEV_MODE and ai_client.flag("USE_CACHE", default=True)
MAX_PORTCOS = 5

ss = st.session_state
ss.setdefault("log", ai_client.CallLog())     # every AI call of this session
ss.setdefault("stage_logs", {})               # per stage: [(first, last) position in the call log, seconds], one per run
ss.setdefault("run_first", 0)                 # position in the call log where the current screen started
ss.setdefault("pf_version", 0)                # a new version = a fresh portfolio table in step ①
ss.setdefault("acts_version", 0)              # a new version = fresh widgets for the activity lists in step ②


# =============================================================== credentials
def credentials():
    """The OpenAI key for this session. The password (in the submitted version the user's own key) is the first
    screen on its own; once entered, it disappears, also from the sidebar. The key is kept for the session only (never
    stored)."""
    if ss.get("auth_key"):
        return ss.auth_key
    if DEV_MODE:
        expected, server_key = ai_client.setting("APP_PASSWORD"), ai_client.setting("OPENAI_API_KEY")
        if not expected:
            st.error("APP_PASSWORD is not set in .env or Secrets.")
            st.stop()
        if not server_key:
            st.error("OPENAI_API_KEY is not set in .env or Secrets.")
            st.stop()
    left, _ = st.columns([2, 3])
    with left:
        st.markdown("<div class='tl-lead'>A preliminary overlap screen for EU merger control.</div>",
                    unsafe_allow_html=True)
        if DEV_MODE:
            value = st.text_input("App password", type="password", key="gate_input")
        else:
            value = st.text_input("OpenAI API key", type="password", key="gate_input",
                                  help="Your own key. It is used only for the calls of this session and not stored.")
        st.button("Continue", type="primary")       # Enter in the field does the same
    if value:
        if DEV_MODE and value != expected:
            left.error("This password is not correct.")
            st.stop()
        ss.auth_key = server_key if DEV_MODE else value.strip()
        st.rerun()
    st.stop()


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
    """Records one run of a stage (a stage can run several times: partial updates)."""
    ss.stage_logs.setdefault(name, []).append((first, ss.log.mark(), seconds))


def stage_calls(name):
    return [c for first, last, _ in ss.stage_logs.get(name, []) for c in ss.log.calls[first:last]]


def stage_seconds(name):
    return sum(sec for _, _, sec in ss.stage_logs.get(name, []))


EMBED_STEPS = ("embed", "embed_query")


def call_count(calls):
    """'30 AI calls + 25 embedding requests' (an embedding request turns the search questions into numbers for the
    vector search; it is not an AI answer, so it is counted separately)."""
    emb = sum(1 for c in calls if c["step"] in EMBED_STEPS)
    text = f"{len(calls) - emb} AI calls"
    return text + (f" + {emb} embedding request{'s' if emb != 1 else ''}" if emb else "")


def stage_cost(name):
    """Calls, cache hits, cost and time of one stage (all its runs in this screen), from the call log."""
    if name not in ss.stage_logs:
        return ""
    calls, seconds = stage_calls(name), stage_seconds(name)
    text = call_count(calls)
    if USE_CACHE:
        text += f" ({sum(c['cached'] for c in calls)} from the development cache)"
    text += (f" · USD {sum(c['cost'] for c in calls):.4f} (tokens and web search calls, prices to verify) · "
             f"{seconds:.0f} s")
    unpriced = sorted({c["model"] for c in calls if not c.get("priced", True)})
    if unpriced:
        text += f" · no price for {', '.join(unpriced)}"
    return text


def go_to(step):
    ss.step = step


# =============================================================== the working screen
# Long work (research, comparison) does not run in the middle of the page: Streamlit keeps the elements of the previous
# screen, faded, until a run ends, so old blocks would linger below the progress. A button only records the work and
# reloads; the next run clears the page body first and shows nothing but the progress, then opens the next step.
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
        remap_company(ai, job["name"], job["website"], job["mode"], job["pasted"], job.get("confirmed"))
        ss.step = 2
        return True
    if kind == "compare":
        return confirm_activities(ai, job["activities"], [], job["profiles_text"])
    if kind == "precedents":
        return run_precedents(ai)
    return True


class WorkCard:
    """The loading screen, the same everywhere: a heading, one progress bar and one plain sentence. The detailed lines
    are kept for development only, collapsed. Every card shows the seconds since it started, refreshed every second
    while the work runs (wait())."""

    def __init__(self, title, text, note=""):
        self.t0, self.text, self.fraction = time.time(), text, 0.0
        self.box = st.container(border=True)
        with self.box:
            st.markdown(f"#### {title}")
            self.bar = st.progress(0.0, text=self._label())
            if note:
                st.caption(note)
            self.dev = st.expander("Developer details") if DEV_MODE else None

    def _label(self):
        return f"{self.text} · {time.time() - self.t0:.0f} s"

    def update(self, fraction, text):
        self.fraction, self.text = max(0.0, min(fraction, 1.0)), text
        self.bar.progress(self.fraction, text=self._label())

    def tick(self):
        self.bar.progress(self.fraction, text=self._label())

    def wait(self, futures):
        """Yields the futures as they finish, refreshing the seconds every second in between."""
        pending = set(futures)
        while pending:
            done, pending = cf.wait(pending, timeout=1, return_when=cf.FIRST_COMPLETED)
            self.tick()
            yield from done

    def log(self, line):
        if self.dev is not None:
            self.dev.write(line)


# =============================================================== new screen (reset)
KEEP_ON_RESET = {"log", "auth_key", "deploy_check", "started"}


def reset_all():
    """Discards everything of the current screen; keeps the key or password and, in development, the cost counter.
    The call log continues, but the audit log of the next screen starts here."""
    for k in list(ss.keys()):
        if k not in KEEP_ON_RESET:
            del ss[k]
    ss.run_first = ss.log.mark()


@st.dialog("Start over?")
def confirm_reset(snap):
    st.write("This discards the companies, activities and results of the current screen.")
    if snap is not None:
        st.download_button("Save progress first (.json)", data=lambda: audit_json(snap),
                           mime="application/json", on_click="ignore",
                           file_name=f"overlap_audit_{datetime.now():%Y%m%d-%H%M}.json")
    c1, c2 = st.columns(2)
    if c1.button("Discard and start over", type="primary"):
        reset_all()
        st.rerun()
    if c2.button("Cancel"):
        st.rerun()


# =============================================================== value chain and sources (shown in steps ② and ③)
# The stage in the value chain, from the activity's own level of trade (where the company SELLS; what it buys is not
# compared: purchasing overlaps are a known limitation). Display only: the data keep the schema terms.
STAGE = {"raw materials": "Raw materials", "intermediate products": "Intermediate products",
         "finished products": "Manufacturing", "wholesale / distribution": "Wholesale", "retail": "Retail",
         "services": "Services", "other": "Other"}
SOURCE_KIND = {"company": "company website", "third party": "other public source", "provided by user": "your description"}


ROW_RULE_SOLID = "<hr style='margin:2px 0 6px 0;border:none;border-top:1px solid #E2DDD2'>"
OTHER_NAME = "Side lines and own use"      # the merged "Other activities" line, as shown


def stage_of(a):
    if rules.category(a) == "other":
        return "Own use" if rules.captive_only(a) else "Mixed"
    return STAGE.get(a.get("value_chain_level"), "Other")


def stage_text(a):
    """The stage as plain grey text (no highlight)."""
    return f":gray[{stage_of(a)}]"


def source_index(company):
    m = (ss.get("mapped") or {}).get(company) or {}
    return {s["n"]: s for s in ((m.get("search") or {}).get("sources") or [])}


def display_title(s):
    """The title of a source as shown; a bare file name or web address (common for PDFs) becomes 'PDF on site'."""
    title = (s.get("title") or "").strip()
    site = am.site_of(s.get("url"))
    pdf = (s.get("check") or {}).get("kind") == "pdf" or (s.get("url") or "").lower().split("?")[0].endswith(".pdf")
    junk = (not title or title.startswith("http") or title == s.get("url") or title.lower().endswith(".pdf")
            or title.lower() in (site, "www." + site)
            or (" " not in title and (re.search(r"[_%]|\d{5}", title) or len(title) > 40)))
    if junk and site:
        return f"{'PDF' if pdf else 'Page'} on {site}"
    return title or site


# The marks are levels of trust, so that the lawyer sees at a glance which sources can be relied
# on and where a check is worth it. ✔ checked · ≈ probably right, worth a quick look · ○ not checked · ⚠ check before
# relying on it. The search reads pages through the AI provider's own access; the app's check is a second, separate
# visit, which some sites refuse: "not checked" says nothing about the source itself.
TRUST_HEAD = {"found": "✔ Checked: the quotation is on the page",
              "close": "≈ Probably right: worth a quick look",
              "not found": "⚠ Check before relying on it",
              "not checked": "○ Not checked",
              "no quote": "○ Not checked"}
NOT_CHECKED_WHY = {
    "blocked": "The search read this page, but the site refused the app's own check ({reason}).",
    "no text": "The search read this page, but it shows the app almost no text (probably built by JavaScript).",
    "error": "The search read this page, but the app could not open it for its own check ({reason}).",
    "off": "The source check is switched off.",
}


def check_result(c):
    """The result as shown. Older saved files have no "close": a quotation not found word for word that is the
    search's translation, or whose words are mostly on the page, is shown as ≈ too (the figure check needs the page
    text, which a saved file does not keep)."""
    r = (c or {}).get("result", "")
    if r == "not found" and (c.get("translated") or (c.get("words_on_page") or 0) >= am.source_check.WORDING_SHARE):
        return "close"
    return r


def source_tip(s, c, kind_text):
    tip = f"{display_title(s)}\n{am.site_of(s.get('url'))} · {kind_text}"
    if s.get("origin") == "text link":
        tip += "\nLink written by the AI in its notes (not a search citation)"
    if not c:
        return tip + "\n\nNot checked (source check off, or mapped before 18 Oct). Open the page to check."
    r, quote = check_result(c), (c.get("quote") or "")[:600]
    reason = (c.get("reason") or "").rstrip(".")
    page = f" (PDF page {c['page']})" if c.get("page") else ""
    if r == "found":
        body = f"{TRUST_HEAD['found']}{page}, in context:\n"
        body += (context_text(c["context"], "»", "«") if c.get("context") else f"“{quote}”")
        return tip + "\n\n" + body + "\n\nClick to open the page there."
    if r == "close":
        if c.get("basis") == "activity terms":
            return (tip + f"\n\n{TRUST_HEAD['close']}\nThe search cited this page without quoting it; the page names "
                    + ", ".join(f"“{t}”" for t in c.get("terms_found") or []) + ". Open the page to check.")
        why = reason[:1].upper() + reason[1:] if c.get("result") == "close" else (
            "The wording is not on the page word for word" + (
                ": the page is probably in another language and the quotation the search's translation"
                if c.get("translated") else ", but most of its words are: probably reworded by the search"))
        return tip + f"\n\n{TRUST_HEAD['close']}\n{why}.\nQuotation given by the search:\n“{quote}”"
    if r == "not found":
        # older saved files were checked for the wording only (no "substance_on_page"): claim no more
        what = ("Neither the wording nor its figures or names were found on the page" if "substance_on_page" in c
                else "The wording was not found on the page")
        return (tip + f"\n\n{TRUST_HEAD['not found']}\n{what}{page}"
                + (f" ({reason})" if reason and not reason.startswith(("neither", "the page was read")) else "")
                + f".\nQuotation given by the search:\n“{quote}”\n\nOpen the page and check.")
    if r == "no quote":
        return (tip + f"\n\n{TRUST_HEAD['no quote']}\nThe search cited this page without quoting it, so there was "
                "nothing to compare. Open the page to check what it says.")
    why = NOT_CHECKED_WHY.get((s.get("check") or {}).get("state"), "The app could not check this page ({reason}).")
    return (tip + f"\n\n{TRUST_HEAD['not checked']}\n" + why.format(reason=reason or "no reason given")
            + " This says nothing about the source itself; the page usually opens normally in your browser."
            + (f"\nQuotation given by the search:\n“{quote}”" if quote else ""))


def source_markers(a, company, checks=None):
    """Numbered source markers next to an activity (or the profile). Each marker shows the result of the code check of
    its quotation (as a level of trust, see TRUST_HEAD); hover shows the quotation of THAT source and why it got its
    mark. Dead links were removed as sources and are not shown here. A source whose quotation was found on another
    source gets no mark (its own check says nothing). Company websites and other public sources share one style; the
    hover names the kind."""
    idx = source_index(company)
    by_n = {c["n"]: c for c in (a.get("quote_checks") if checks is None else checks) or []}
    out = []
    for n in a.get("source_numbers") or []:
        s = idx.get(n)
        if not s or s.get("dead"):
            continue
        c = by_n.get(n)
        moved = bool(c and c.get("result") == "no quote" and (c.get("moved_to") or "found on source" in
                                                             (c.get("reason") or "")))
        mark = "" if moved else (am.source_check.STATUS_MARK.get(check_result(c), "") if c else "")
        kind = s.get("type") or "unlabelled"
        if kind == "provided by user":
            tip = "Your description (entered in step ①)"
            if c and c.get("quote"):
                tip += ("\n\n✔ Passage found in your description:" if c["result"] == "found" else
                        "\n\n⚠ Passage NOT found in your description:") + f"\n“{c['quote'][:600]}”"
            tip = html.escape(tip, quote=True).replace("\n", "&#10;")
            out.append(f"<span title='{tip}' style='font-size:0.85em;opacity:0.8'>[your description]{mark}</span>")
            continue
        if moved:
            tip = f"{display_title(s)}\n{am.site_of(s.get('url'))} · {SOURCE_KIND.get(kind, kind)}"
        else:
            tip = source_tip(s, c, SOURCE_KIND.get(kind, kind))
        tip = html.escape(tip, quote=True).replace("\n", "&#10;")
        style = "text-decoration:none;font-size:0.85em"       # one style; the hover says the kind
        href = (c or {}).get("link") or s.get("url", "")
        if not str(href).lower().startswith(("http://", "https://")):
            href = ""                    # only web links (a loaded audit log could carry anything)
        out.append(f"<a href='{html.escape(href, quote=True)}' target='_blank' title='{tip}' "
                   f"style='{style}'>[{n}]{mark}</a>")
    if a.get("no_available_source") and not out:
        out.append("<span title='Every source the search gave for this activity no longer exists (page not found). "
                   "The activity is kept, but nothing available supports it.' style='font-size:0.85em'>"
                   "⚠ no available source: verify, or ask the company</span>")
    elif not out:
        out.append("<span style='font-size:0.85em;opacity:0.8'>added by you</span>" if a.get("origin") == "added by user"
                   else "<span title='No source returned by the search supports this activity' "
                        "style='font-size:0.85em'>⚠ no source</span>")
    return " ".join(out)


def context_text(ctx, left, right):
    """A found passage in its surroundings as plain text, the passage between the two marks."""
    return f"{ctx['before']}{left}{ctx['passage']}{right}{ctx['after']}".strip()


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
    st.caption("The examples use real companies in a hypothetical portfolio: no real transaction is implied. "
               "The research and the comparison run live.")
    with st.container(horizontal=True):          # side by side, not spread over the page width
        for key, ex in examples.EXAMPLES.items():
            st.button(ex["button"], key=f"ex_{key}", help=ex["what"], on_click=fill_example, args=(key,))


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
        with st.expander("Other names (optional): short names used in everyday language"):
            st.text_input("Other names of the company, comma-separated", key="t_aliases",
                          placeholder="e.g. a short name, a former name",
                          help="Short names or former names, e.g. “Lindt” for Lindt & Sprüngli. Like the name itself, they "
                               "are removed from every anonymised description before a comparison. The confidentiality "
                               "check only recognises names it knows; parts of a name joined by “&” or “and” are "
                               "recognised automatically.")


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
                                         help="Short names used in everyday language, comma-separated (e.g. “Lindt” for "
                                              "Lindt & Sprüngli); removed from every anonymised description, like the "
                                              "name. Parts joined by “&” or “and” are recognised automatically."),
                "source": cc.SelectboxColumn("Activities from", options=list(am.SOURCE_OPTIONS), default="web search",
                                             required=True, help=SOURCE_HELP)})
        for r in portfolio_rows(edited):
            if r["source"] != "web search":
                st.text_area(f"Description of {r['name']}'s activities", key=f"desc_{r['name']}", height=120,
                             help=DESCRIPTION_HELP)
    return edited


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
               f"in {name}'s own research call, so the AI would see both names together. Change the text, or send it "
               "anyway if the sentence reveals nothing confidential.")


def typed_text_warnings(companies):
    for c in companies:
        found = typed_names(c, companies)
        if found:
            typed_warning(c["name"], found)
            st.checkbox(SEND_ANYWAY, key=send_key(c["name"], found))


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
        found = typed_names(c, companies) if c["name"] else []
        if found and ss.get(send_key(c["name"], found)):
            c["typed_names_confirmed"] = found
        elif found:
            problems.append(f"The description of {c['name']} names {words_list(found)}: change the text, or tick "
                            "“Send anyway”.")
    return companies, problems


def stage_companies(ai):
    st.subheader("① Companies")
    st.markdown("Enter the company to be bought (the *target*) and the companies the buyer already owns (the "
                "*portfolio companies*). Each portfolio company is looked at together with its subsidiaries and brands. "
                "For the target, enter only the business being sold, for example a division rather than the seller's "
                "whole group.")
    restore_inputs()
    example_buttons()
    target_card()
    edited = portfolio_card()
    typed_text_warnings(read_companies(edited)[0])
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
    """Maps the companies that are new or whose input changed; the others keep their research and the
    user's edits of their activities. A new screen starts with "↺ New screen" (reset_all), not here."""
    first, t0 = ss.log.mark(), time.time()
    old, old_keys = ss.get("mapped") or {}, ss.get("map_keys") or {}
    kept = {c["name"] for c in companies if c["name"] in old and not old[c["name"]].get("error")
            and old_keys.get(c["name"]) == company_key(c)}
    todo = [c for c in companies if c["name"] not in kept]
    mapped = {n: old[n] for n in kept}
    searching = any(am.source_mode(c) != "my description" for c in todo)
    title = "Researching the companies" if searching else "Reading your descriptions"
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
            mapped[c["name"]] = m
            card.update(done / n, f"{done} of {plural(n, 'company', 'companies')} done")
            if m["error"]:
                card.log(f"✖ {c['name']}: {m['error']}")
            else:
                origin = ("your description" if am.source_mode(c) == "my description"
                          else f"{len(m['search']['sources'])} sources")
                card.log(f"✔ {c['name']}: {len(m['extraction']['activities'])} activities from {origin}")
    old_acts = ss.get("acts") or {}
    ss.companies = companies
    ss.mapped = {c["name"]: mapped[c["name"]] for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    ss.relationships = am.find_relationships(ss.mapped, companies, ss.get("keep_words") or ())
    ss.acts = {c["name"]: old_acts[c["name"]] if c["name"] in kept and c["name"] in old_acts
               else copy.deepcopy(extracted(ss.mapped[c["name"]])) for c in companies}
    cmp.ensure_ids(ss.acts)
    ss.profiles_edit = {n: t for n, t in (ss.get("profiles_edit") or {}).items() if n in kept}
    ss.acts_version += 1
    log_stage("mapping", first, time.time() - t0)


def extracted(m):
    return (m.get("extraction") or {}).get("activities", [])


# =============================================================== step ② activities
# Activities are kept as the extraction's dicts (ss.acts) and changed only through the edit form, so a change to one
# field keeps every other field (a table editor would replace a cell's whole text when typing).
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


def item_html(item):
    """An item in full: 'menu branding program (approved use of brand …)' with the brackets in grey."""
    head, sep, rest = item.partition(" (")
    return he(head) + (f" <span class='br'>({he(rest)}</span>" if sep else "")


def capital(text):
    return text[:1].upper() + text[1:]


def activity_line(a, company):
    """One activity in step ② (two lines with labels; the text stays complete): the name, the stage and the sources
    on the first line; below, what the company does, examples and brands, each with a small grey label."""
    markers = source_markers(a, company)
    stage = f"<span class='chip'>{h(stage_of(a))}</span>"

    def field(label, value):
        return f"<span class='k'>{label}</span>{value}"
    if a.get("excluded"):
        return (f"<s><b>{he(capital(a['product']))}</b></s> {stage} {markers}  \n"
                + field("Not relevant", f"<i>{he(a.get('exclusion_reason', ''))}</i> (excluded by you)"))
    brands = [b for b in a.get("brands") or [] if b and b != "not stated"]
    if rules.is_gap(a):        # the bold part names the activity, as on every other line
        level = a.get("value_chain_level")
        known = level in rules.VALUE_CHAIN_LEVELS and level != "other"
        lines = [f"<b>{'Products not stated' if known else 'Activity not stated'}</b> "
                 + (stage + " " if known else "") + markers]
        if known and everyday(a):
            lines.append(field("What it does", he(everyday(a))))
        entity = (a.get("entity") or "").strip()
        if brands:
            lines.append(field("Brands", he(", ".join(brands[:4])) + more_items(brands, 4)))
        elif entity and entity.lower() != "not stated":
            lines.append(field("Company", he(entity)))
        lines.append(field("Open", "named in the sources, but what it offers is not stated: a question for the company; "
                                   "use “Edit” to add the product if you know it (until then it is not compared)"))
        return "  \n".join(lines)
    includes = [i for i in a.get("includes") or [] if i]
    if rules.category(a) == "other":
        # every item in full, the text in brackets in the secondary colour (it often says what the item is)
        return (f"<b>{OTHER_NAME}</b> {stage} {markers}  \n"
                + field("Includes", "; ".join(item_html(i) for i in includes[:6]) + more_items(includes, 6)))
    first = f"<b>{he(capital(a['product']))}</b> {stage}"
    if a.get("status") == "in development":
        first += " <span class='tag'>in development</span>"
    hint = rules.level_hint(a, own_names(company))
    if hint:
        first += f" <span class='hov' title='{h(hint)}'>⚠ level of trade?</span>"
    lines = [first + " " + markers]
    what = everyday(a)          # empty for the level "other"
    if what:
        lines.append(field("What it does", he(what)))
    raw = [i for i in includes if i.strip().lower() != a["product"].strip().lower()]
    if raw:
        lines.append(field("Examples", ", ".join(he(i) for i in raw[:4]) + more_items(raw, 4)))
    if brands:                 # step ② is where names may be shown, so the brands are visible here
        lines.append(field("Brands", he(", ".join(brands[:4])) + more_items(brands, 4)))
    return "  \n".join(lines)


def own_names(company):
    """The company's own names, for the level hint: entered name, other names and their parts, group companies
    and the brands of its lines that are not at wholesale level."""
    c = next((x for x in ss.get("companies") or [] if x["name"] == company), {"name": company})
    group = (((ss.get("mapped") or {}).get(company) or {}).get("extraction") or {}).get("group_companies") or []
    brands = [b for a in (ss.get("acts") or {}).get(company, []) if a.get("value_chain_level") != "wholesale / distribution"
              for b in a.get("brands") or [] if b and b != "not stated"]
    return am.names_of(c) + [g for g in group if g] + brands


def more_items(items, shown):
    """'(+6 more)' after the examples of an activity; hovering shows every item."""
    if len(items) <= shown:
        return ""
    tip = html.escape("All items: " + "; ".join(items), quote=True)
    return (f" <span title='{tip}' style='text-decoration:underline dotted'>"
            f"(+{len(items) - shown} more)</span>")


def display_order(acts):
    """Business areas first, then 'Other activities', then what the user excluded (indices into the list)."""
    main = [i for i, a in enumerate(acts) if not a.get("excluded") and rules.category(a) == "main"]
    other = [i for i, a in enumerate(acts) if not a.get("excluded") and rules.category(a) == "other"]
    return main + other + [i for i, a in enumerate(acts) if a.get("excluded")]


def _row_words(act):
    words = [act.get("product") or ""] + list(act.get("includes") or []) + list(act.get("brands") or [])
    return [w for w in words if w and w != "not stated" and len(w) > 3]


def relationship_rows(target, portco, rows):
    """The rows an existing relationship is shown in (in the preliminary assessment of the row, as a supporting
    argument): the rows whose portfolio activity (its name, products or brands) appears in the passages,
    else those whose target activity does, else every kept row of the company. Code only."""
    rel = relationship_between(target, portco)
    if not rel or not rows:
        return set(), rel
    text = " ".join(p for _, p in rel).lower()
    # the companies' own names (often also a brand) are in every passage, so they say nothing about the row
    own = {n.lower() for c in ss.companies if c["name"] in (target, portco) for n in am.names_of(c)}

    def named(words):
        return any(re.search(r"(?<!\w)" + re.escape(w.lower()) + r"(?!\w)", text) for w in words
                   if w.lower() not in own)
    # the portfolio company's activity first (it differs from row to row), then the target's, else every kept row
    hit = ({cmp.pair_id(r) for r in rows if named(_row_words(r["b"]))}
           or {cmp.pair_id(r) for r in rows if named(_row_words(r["a"]))})
    return (hit or {cmp.pair_id(r) for r in rows}), rel


def relationship_between(target, portco):
    """The passages in which the public sources of the target or of this portfolio company mention the other, both
    directions merged (shown only in the result box of the company concerned, as a supporting argument).
    Relationships between two portfolio companies are not shown."""
    rels = ss.get("relationships") or {}
    out = []
    for who, other in ((target, portco), (portco, target)):
        for r in rels.get(who) or []:
            if r.get("other") == other:
                out += [(who, p) for p in r.get("passages") or []]
    return out


def profile_of(name):
    """The company profile as edited by the user, else as extracted. The profile confirmed with the comparison
    (profiles_text) is only the fallback (a company without a mapping), so that an edit in step ② or a new mapping is
    always shown."""
    if name in (ss.get("profiles_edit") or {}):
        return ss.profiles_edit[name]
    ext = (((ss.get("mapped") or {}).get(name) or {}).get("extraction") or {})
    if "company_profile" in ext:
        return ext["company_profile"]
    return (ss.get("profiles_text") or {}).get(name, "")


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
    shown_name = OTHER_NAME if rules.category(a) == "other" and a.get("product") == "Other activities" else \
        a.get("product", "")      # the merged line has the same name here as in the table
    name = st.text_input("Activity", value=shown_name, key=k + "name",
                         help="What the business area offers (product or service), in generic words; who buys it goes under "
                              "“Direct customers”, not into the name; no company or brand names")
    includes = st.text_area("Includes (one item per line)", value="\n".join(a.get("includes") or []), key=k + "inc",
                            height=130, help="Every product type, format and customer group this activity covers")
    c1, c2 = st.columns(2)
    levels = list(rules.VALUE_CHAIN_LEVELS)
    level = c1.selectbox("Level of trade", levels, index=levels.index(a.get("value_chain_level", "other"))
                         if a.get("value_chain_level") in levels else levels.index("other"),
                         format_func=lambda x: STAGE[x] if STAGE[x].lower() == x else f"{STAGE[x]} ({x})",
                         key=k + "lvl",
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
        product = a.get("product") if name.strip() == OTHER_NAME and rules.category(a) == "other" else name.strip()
        new = dict(a, product=product, includes=_items(includes, "\n"), value_chain_level=level, status=status,
                   direct_customers=customers or ["not stated"], countries_of_sale=_items(countries, ",") or ["not stated"],
                   category=category, excluded=excluded, exclusion_reason=reason.strip(), description=_text(description),
                   intended_use=_text(intended), main_inputs=_items(inputs, ";") or ["not stated"],
                   customer_details=_text(details), end_users=end_users, sales_channels=_text(channels),
                   business_area=_text(area), entity=_text(entity), brands=_items(brands, ","))
        if found:
            new["typed_names_confirmed"] = found
        if idx is None:
            acts.append(new)
        else:
            # extracted activities carry no "origin" (only added ones do), so any change to one of them is marked
            # as edited, for the audit log
            if new != acts[idx] and new.get("origin") != "added by user":
                new["edited_by_user"] = True
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
    st.subheader("② Activities")
    st.write("Check what each company does: everything after this step builds on these activities. Use “Edit” to "
             "correct an activity, mark it as not relevant to this deal or delete it.")
    cmp.ensure_ids(ss.acts)
    guide_box(2)
    for i, c in enumerate(ss.companies):
        # a visual cut between the target and the portfolio companies
        if i == 0:
            st.markdown("<div class='sec'>The target</div><div class='secsub'>The business to be acquired</div>",
                        unsafe_allow_html=True)
        elif i == 1:
            st.markdown("<div class='cut'></div><div class='sec'>The portfolio companies</div><div class='secsub'>The "
                        "companies the buyer already owns, each with its subsidiaries and brands</div>",
                        unsafe_allow_html=True)
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


SOURCE_STATE = {
    "readable": "read",
    "blocked": "○ could not be checked automatically",
    "no text": "○ could not be checked automatically",
    "error": "○ could not be checked automatically",
    "off": "○ not checked",
}


def sources_list(found):
    """All sources of one company with the result of the check; links that no longer exist are listed apart, as
    'no longer available (cited by the search, not used)', and not as links."""
    check = found.get("source_check") or {}
    st.markdown(f"**Sources** · {found.get('model', '')} · accessed {found.get('date', '')}"
                + (f" · checked by the app on the same day ({check.get('seconds')} s)" if check.get("checked") else ""))
    live = [s for s in found["sources"] if not s.get("dead")]
    dead = [s for s in found["sources"] if s.get("dead")]
    for s in live:
        c = s.get("check") or {}
        link = f"[{esc(display_title(s))}]({s['url']})" if s.get("url") else esc(s["title"])
        state = SOURCE_STATE.get(c.get("state"), "")
        if c.get("state") == "readable" and c.get("kind") == "pdf" and c.get("pages"):
            state = f"read (PDF, {c['pages']} pages)"
        detail = f" ({c['reason']})" if c.get("reason") and c.get("state") != "readable" else ""
        if c.get("state") == "readable" and c.get("reason"):
            detail = f" ({c['reason']})"
        origin = " · :gray[link written by the AI, not a search citation]" if s.get("origin") == "text link" else ""
        st.markdown(f"[{s['n']}] {link} · *{SOURCE_KIND.get(s.get('type'), s.get('type') or 'unlabelled')}*"
                    + origin + (f" · :gray[{esc(state)}{esc(detail)}]" if state else ""))
    if dead:
        st.markdown("**✖ No longer available** (cited by the search, not used: the page or domain no longer exists, "
                    "so what it said can no longer be checked)")
        for s in dead:
            st.markdown(f":gray[source {s['n']}: {esc(display_title(s))} · {esc((s.get('check') or {}).get('reason', ''))}]"
                        f"  \n:gray[`{s.get('url', '')}`]")


def company_block(ai, c, index):
    name = c["name"]
    m = ss.mapped[name]
    ext = m.get("extraction") or {}
    acts = ss.acts[name]
    v = ss.acts_version
    is_target = c["role"] == "target"
    with st.container(border=True, key="tbox" if is_target else None):
        # the target's name and profile on a sand band; its activities stay ivory
        with st.container(key="tband" if is_target else None):
            st.markdown(f"#### {name if is_target else f'Portfolio company {index}: {name}'}")
            facts = [c["website"]] if c.get("website") else []
            if am.source_mode(c) != "web search":
                facts.append(f"activities from: {am.source_mode(c)}")
            if facts:
                st.caption(" · ".join(facts))
            if m["error"]:
                st.error(m["error"])
            profile = profile_of(name)
            if profile.strip():
                psrc = {"source_numbers": ext.get("profile_source_numbers") or [],
                        "quote_checks": ext.get("profile_quote_checks") or []}
                st.markdown("<div class='prof'>" + he(profile) + (" " + source_markers(psrc, name)
                                                                  if psrc["source_numbers"] else "") + "</div>",
                            unsafe_allow_html=True)
            elif not m["error"]:
                st.caption("No profile found in the sources.")
        for w in ext.get("warnings") or []:
            st.warning(w)
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
        with st.expander("Company profile, all sources, map again"):
            key = f"prof_{v}_{name}"
            st.text_area("Company profile", value=profile, key=key, height=100,
                         on_change=_store_profile, args=(name, key))
            found = m.get("search") or {}
            if found.get("sources"):
                sources_list(found)
            st.markdown("**Map this company again** (replaces its profile and activities; the other companies "
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
    card = WorkCard(f"Researching {name} again", "Researching …",
                    "Only this company is researched again; the others are kept. This usually takes one to two minutes.")
    with cf.ThreadPoolExecutor(1) as ex:
        fut = ex.submit(am.map_company, ai, company, companies)
        for f in card.wait([fut]):
            ss.mapped[name] = f.result()
    card.update(1.0, "Done")
    card.log(f"{name} researched again in {time.time() - t0:.0f} s")
    ss.companies = companies
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


def name_word_review():
    """Before the comparison: the brands and group company names that also appear as words in the descriptions.
    They are removed by default (confidentiality first); the lawyer can keep an ordinary product
    word, so the comparison still sees it. The choice is recorded in the audit log."""
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in ss.companies}
    found = cmp.names_used_as_words(ss.companies, ss.acts, group)
    if not found:
        return
    # A word that also appears in lower case ("cacaofruit ingredients") is an ordinary product word, so it is kept by
    # default; the lawyer can untick it (with the word removed, the AI would see "[name removed] ingredients" and could
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
    ordinary = [f for f in found if f.get("lower_case")]
    names = [f for f in found if not f.get("lower_case")]
    with st.container(border=True):
        st.markdown(f"**Names that are also used as words in the descriptions** · {plural(len(found), 'word')}")
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


def activities_hash(activities):
    """What the comparison depends on: the activities and the words the lawyer keeps in the descriptions."""
    state = {"activities": activities, "keep_words": sorted(ss.get("keep_words") or [])}
    return hashlib.sha256(json.dumps(state, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


# =============================================================== step ③ factual comparison
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


def confirm_activities(ai, activities, problems, profiles_text):
    if problems:
        st.error("Please fix these points first:\n\n" + "\n".join(f"- {p}" for p in problems))
        return False
    plan = prepare_comparison(activities)
    target, portcos, names, profiles, keys = (plan[k] for k in ("target", "portcos", "names", "profiles", "keys"))
    ss.setdefault("vec_cache", {})
    ss.setdefault("pair_cache", {})
    first, t0 = ss.log.mark(), time.time()
    card = WorkCard("Comparing the activities", "Preparing the anonymised descriptions …",
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
    if todo:
        with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
            futures = {ex.submit(cmp.assess, ai, p, names): p for p in todo}
            for done, fut in enumerate(card.wait(futures), start=1):
                ss.pair_cache[pair_key[id(futures[fut])]] = fut.result()
                card.update(done / len(todo), f"{done} of {plural(len(todo), 'pair')} compared")
    results = [{**ss.pair_cache[pair_key[id(p)]], **{k: p[k] for k in POSITION_FIELDS}} for p in pairs]
    card.log(f"{plural(len(todo), 'pair')} compared, {len(pairs) - len(todo)} kept, in {time.time() - t0:.0f} s")
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


# =============================================================== step ③ the preliminary assessment table
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
WIDTHS4 = [1.1, 1.1, 3.75, 3.1, 1.05, 0.8]
_THEAD = [0]                                    # a fresh key for every table header of this run


def col_widths():
    return WIDTHS4 if ss.get("step") == 4 and ss.get("precedents") else WIDTHS
BLOCK_RULE = "<hr style='margin:4px 0 8px 0;border:none;border-top:1px solid #C9C2B4'>"
ROW_RULE = "<hr style='margin:4px 0 8px 0;border:none;border-top:1px dashed #DDD7CB'>"
FOUND_BY_WORDS = {"AI": "found by the AI", "rule": "found by a rule in the code", "AI and rule": "found by the AI and a "
                                                                                              "rule in the code"}
RULE_WORDS = {
    "A could be an input for B": "{t} sells to producers, and its products are close to inputs that {p} lists",
    "B could be an input for A": "{p} sells to producers, and its products are close to inputs that {t} lists",
    "A could be resold by B": "{t} sells to shops or wholesalers, and {p} resells a close range",
    "B could be resold by A": "{p} sells to shops or wholesalers, and {t} resells a close range",
}
UPSTREAM_LINKS = ("A could be an input for B", "A could be resold by B")


def he(text):
    """Text from the sources or the AI inside an HTML line that Streamlit also reads as markdown: HTML escaped and the
    markdown characters neutralised."""
    out = h(text)
    for a, b in (("*", "&#42;"), ("_", "&#95;"), ("[", "&#91;"), ("]", "&#93;"), ("~", "&#126;"), ("`", "&#96;")):
        out = out.replace(a, b)
    return out


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


def listing(items, limit=4):
    """Items as HTML; more than `limit`: “and 2 more”, hovering shows every item."""
    items = [i for i in items if i]
    if not items:
        return ""
    text = ", ".join(he(i) for i in items[:limit])
    if len(items) > limit:
        tip = h("All: " + "; ".join(items))
        text += f" <span class='hov' title='{tip}'>and {len(items) - limit} more</span>"
    return text


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


def other_cell(act, r):
    """The merged line in a row: 'Side lines' with the items of this row, or 'Own use'."""
    side = "a" if act is r["a"] else "b"
    items = [short_item(i) for i in (side_items(r, side) or act.get("includes") or [])]
    if is_own_use(r):
        return "**Own use**", [i.replace(" (own use)", "") for i in items]
    return "**Side lines**", [i for i in items if rules.OWN_USE_MARK not in i]


def table_cell(a, company, r=None):
    """An activity in the table: name, stage, sources. What it includes and does is in 'Why?'."""
    if rules.category(a) == "other" and r is not None:
        name, items = other_cell(a, r)
        shown = ", ".join(esc(i) for i in items[:3]) + (f" and {len(items) - 3} more" if len(items) > 3 else "")
        return f"{name}  \n:gray[{shown}]  \n{source_markers(a, company)}" if shown else \
            f"{name}  \n{source_markers(a, company)}"
    name = OTHER_NAME if rules.category(a) == "other" else capital(a["product"])
    return f"**{esc(name)}**  \n{stage_text(a)} · {source_markers(a, company)}"


def direction(link, r, target, portco):
    """(upstream company, its activity, downstream company, its activity) of a vertical link."""
    if link in UPSTREAM_LINKS:
        return target, r["a"], portco, r["b"]
    return portco, r["b"], target, r["a"]


def link_sentence(link, vitems, r, target, portco, html_out=True):
    """A vertical link in words, with the names re-attached and the items the link concerns."""
    if html_out:
        a = f"{he(target)}'s {listing(vitems.get('a', [])) or he(r['a']['product'])}"
        b = f"{he(portco)}'s {listing(vitems.get('b', [])) or he(r['b']['product'])}"
    else:
        a = f"{target}'s {', '.join(vitems.get('a', [])) or r['a']['product']}"
        b = f"{portco}'s {', '.join(vitems.get('b', [])) or r['b']['product']}"
    return {
        "A could be an input for B": f"{a} could be an input for {b}",
        "B could be an input for A": f"{b} could be an input for {a}",
        "A could be resold by B": f"{a} could be resold through {b}",
        "B could be resold by A": f"{b} could be resold through {a}",
    }.get(link, link)


def customer_dots(r, target, portco):
    """The customer score (dots) with its explanation on hover."""
    score = r.get("customers")
    if score not in ("●●●", "●●○", "●○○"):
        return ""
    ca = words_list(_shown(r["a"].get("direct_customers"))) or "not stated"
    cb = words_list(_shown(r["b"].get("direct_customers"))) or "not stated"
    tip = (f"{capital(CUSTOMER_TEXT[score])}: {target} sells to {ca}; {portco} to {cb}. This compares only who each "
           "company sells to directly, not the products. Different customers alone do not rule out an overlap: "
           "customers form a separate market only if the seller can tell which group a customer belongs to at the time "
           "of sale, customers cannot resell to each other, and the different treatment is lasting (Market Definition "
           "Notice (88)).")
    return f"<span class='dots' title='{h(tip)}'>{score}</span>"


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
            lines = [f"{kind}, {level}{', ' + CUSTOMER_TEXT.get(r.get('customers') or '', '') if r.get('customers') in ('●●●', '●●○', '●○○') else ''}"]
            if m.get("a") or m.get("b"):
                lines.append(f"with regard to: {target}: {', '.join(m.get('a') or []) or '–'}; "
                             f"{portco}: {', '.join(m.get('b') or []) or '–'}")
            return lines
        dots = customer_dots(r, target, portco)
        lines = [f"<span class='basis'>{kind} · {level}{' · ' + dots if dots else ''}{own}</span>"]
        if sa != sb and not p["off"]:      # display only
            lines.append("<span class='basis'>different levels: usually a vertical relationship; horizontal only if "
                         "both sell to the same customers</span>")
        a, b = listing(m.get("a", [])), listing(m.get("b", []))
        if (a or b) and not p["off"]:      # one line per company
            lines.append(f"with regard to<span class='wr'><i>{he(target)}:</i> {a or '–'}</span>"
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


def label_html(p):
    cls = "lab-off" if p["off"] else ("lab-h" if p["kind"] == "h" else "lab-v")
    tag = " <span class='tag'>added by you</span>" if p["origin"] == "lawyer" else (
        " <span class='tag'>dismissed by you</span>" if p["off"] else "")
    return f"<span class='lab {cls}'>{LABEL_TEXT[p['kind']]}</span>{tag}"


def assessment_plain(r, target, portco):
    """The app's wording of a row as plain text: what the lawyer starts from in "Edit"."""
    lines = []
    for p in label_parts(r, target, portco):
        if not p["off"]:
            lines += [LABEL_TEXT[p["kind"]] + (" (added by you)" if p["origin"] == "lawyer" else "")]
            lines += ["  " + x for x in part_detail(p, r, target, portco, html_out=False)]
    return "\n".join(lines)


def assessment_cell(r, status, rv, target, portco):
    """The preliminary assessment column: one line per label, each with its own "Your view". The lawyer's wording, if
    any, replaces the app's lines under the labels."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    parts = label_parts(r, target, portco)
    tool_parts = [p["part"] for p in parts if p["origin"] == "tool"]
    edited = (o.get("text_assessment") or "").strip()

    def line(html_text, part, kind, off=False):
        c1, c2 = st.columns([4.4, 2.1] if len(col_widths()) == 6 else [4.6, 1.9], vertical_alignment="top")
        c1.markdown(html_text, unsafe_allow_html=True)
        safe = re.sub(r"\W", "", part)         # no backslash inside an f-string (Python before 3.12)
        key = f"view_{rv}_{pid}_{safe}"
        c2.selectbox("Your view", VIEWS, index=VIEWS.index(view_of(pid, part, off)), key=key,
                     label_visibility="collapsed", on_change=_store_view, args=(pid, part, key, tool_parts, kind),
                     help="Your view of this relationship: used in the summary and the Word document. “Ask the "
                          "company” puts it into the open points; “Dismiss” removes it.")

    if status == "added back by user":
        line("<span class='lab lab-q'>Added back by you</span> <span class='sub2'>the tool found no overlap; see "
             "“Why?”</span>", "row", "row")
    elif r["decision"]["status"] == "unclear":
        line("<span class='lab lab-q'>Unclear: please check</span> <span class='sub2'>see “Why?”</span>", "row", "row",
             off=bool(o.get("dismiss")))
    for p in parts:
        detail = [] if edited else part_detail(p, r, target, portco)
        text = "  \n".join([label_html(p)] + detail)
        line(text, p["part"], p["origin"], off=p["off"])
    if edited:
        st.markdown(he(edited).replace("\n", "<br>") + " <span class='tag'>edited by you</span>",
                    unsafe_allow_html=True)
    rel = (ss.get("rel_rows") or {}).get(pid)
    if rel:
        quotes = "".join(f"<div class='it one'><span class='sub2'>{he(who)}'s sources:</span> {quoted(p)}</div>"
                         for who, p in rel)
        st.markdown(f"<details class='mkts' style='margin-top:.3rem'><summary><span class='lab lab-q'>Existing "
                    f"relationship</span> the public sources of {he(target)} and {he(portco)} mention each other "
                    f"({plural(len(rel), 'passage')})</summary>{quotes}<div class='sub2'>Check its nature (supply, "
                    "distribution, partnership, equity); the tool does not assess it.</div></details>",
                    unsafe_allow_html=True)


def quoted(passage):
    """A passage in quotation marks, unless it already starts with one (no ““…)."""
    t = (passage or "").strip()
    return he(t) if t[:1] in "“\"„«" else f"“{he(t)}”"


RESELLER_LEVELS = ("retail", "wholesale / distribution")


def set_aside_text(r, link, reason, target, portco):
    """A link the tool set aside, explained (so that it does not read as if the company had no retail at all). The
    tool compares one activity of each company at a time; a resale link needs the reseller's activity in
    THIS row to be in wholesale or retail. Where that company's shop or wholesale activity is compared in another row,
    the note points there."""
    side = "a" if reason.startswith("A ") else "b"
    who = target if side == "a" else portco
    act = r[side]
    what = esc(cmp.describe_link(link, target, portco))
    if "not active in wholesale or retail" in reason:
        here = stage_of(act).lower()
        others = [a for a in (ss.confirmed or {}).get(who, []) if a.get("value_chain_level") in RESELLER_LEVELS
                  and not a.get("excluded")]
        if others:
            names = " · ".join(f"“{esc(short_name(a))}”" for a in others)
            return (f"**Resale ({what}):** compared in the row {names}. The tool compares one activity of each company "
                    f"at a time, and here {esc(who)}'s activity is {esc(here)}.")
        return (f"**Resale not considered ({what}):** in this row {esc(who)}'s activity is {esc(here)}, and the screen "
                f"shows no wholesale or retail activity of {esc(who)}.")
    if "own use" in reason:
        return (f"**Set aside ({what}):** {esc(who)}'s activity here is only for the group's own use, so it supplies "
                "no one and resells nothing to third parties.")
    return f"**Link set aside by the tool:** {what}; {esc(who)} {esc(reason[2:])}."


def why_popover(r, target, portco):
    """'Why?': only the reasoning (the sources are in step ② and in the hover of each source, and what the AI saw is in
    the audit log)."""
    c, d = r["comparison"], r["decision"]
    why = []
    if d["horizontal"] or d["status"] in ("unclear", "screened out"):
        why.append(f"**Product** ({esc(c['product_relation'])}): {esc(c.get('product_reason', ''))}")
    ai_links = [link for link in d["vertical_links"] if d["found_by"][link] != "rule"]
    for link in d["vertical_links"]:
        up, _, down, _ = direction(link, r, target, portco)
        text = f"**Vertical** ({esc(up)} → {esc(down)}, {FOUND_BY_WORDS[d['found_by'][link]]})"
        if d["found_by"][link] == "rule":
            text += ": " + esc(RULE_WORDS[link].format(t=target, p=portco)) + "."
        why.append(text)
    if ai_links and c.get("vertical_reason"):
        why.append(esc(c.get("vertical_reason", "")))
    for link, reason in d.get("disregarded", []):
        why.append(set_aside_text(r, link, reason, target, portco))
    # say what "Why?" contains: the AI's reasoning and the app's own checks, for the lawyer to check
    st.caption("The AI's reasoning on the anonymised descriptions, and the app's own checks: who each company sells to "
               "directly, and whether supply or resale is possible in this row.")
    st.markdown("\n\n".join(why) or "No reason given.")
    if d["horizontal"] and r.get("customers") in ("●●●", "●●○", "●○○"):
        ca = words_list(_shown(r["a"].get("direct_customers")))
        cb = words_list(_shown(r["b"].get("direct_customers")))
        st.markdown(f"**Direct customers** {r['customers']}: {esc(target)} sells to {esc(ca or 'not stated')}; "
                    f"{esc(portco)} to {esc(cb or 'not stated')}, so {CUSTOMER_TEXT[r['customers']]}. This compares "
                    "only who each company sells to directly, not the products. Different customers alone do not rule "
                    "out an overlap: customers form a separate market only if the seller can tell which group a "
                    "customer belongs to at the time of sale, customers cannot resell to each other, and the different "
                    "treatment is lasting (Market Definition Notice (88)).")
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


@st.dialog("Edit this row", width="large")
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
    st.markdown("**Add a label** (marked “added by you”; to remove one of the tool's labels, use “Dismiss” next to it)")
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
    Commission's view, the user's note, and Edit / Why?; in step ④ the Commission's markets for this pair on request,
    full width under the row."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    s = status[pid]
    w = col_widths()
    step4 = len(w) == 6
    cols = st.columns(w, vertical_alignment="top")
    if first:
        cols[0].markdown(table_cell(r["a"], target, r), unsafe_allow_html=True)
    cols[1].markdown(table_cell(r["b"], portco, r), unsafe_allow_html=True)
    with cols[2]:
        assessment_cell(r, s, rv, target, portco)
    markets = ""
    if step4:
        with cols[3]:
            markets = commission_cell(r, target, portco)
    with cols[4 if step4 else 3]:
        key = f"note_{rv}_{pid}"
        st.text_area("Note", value=o.get("note", ""), key=key, placeholder="Note (optional)",
                     label_visibility="collapsed", height=68, on_change=_store_override, args=(pid, "note", key))
    with cols[5 if step4 else 4]:
        if st.button("Edit", key=f"edit_row_{rv}_{pid}", width="stretch"):
            edit_row(pid, target, portco)
        with st.popover("Why?", width="stretch"):
            why_popover(r, target, portco)
    if markets:
        st.markdown(f"<details class='mkts'><summary>Show the Commission's markets for this row</summary>{markets}"
                    "</details>", unsafe_allow_html=True)


def table_header(target, portco):
    """The header of a company's table, in ink with white text (as in the Word document)."""
    w = col_widths()
    _THEAD[0] += 1
    labels = [f"{esc(target)} activity", f"{esc(portco)} activity", "Preliminary assessment"]
    labels += (["Commission market definition"] if len(w) == 6 else []) + ["Notes", ""]
    with st.container(key=f"thead_{_THEAD[0]}"):
        for col, label in zip(st.columns(w), labels):
            if label:                      # an empty "****" would render as a horizontal line
                col.markdown(f"**{label}**")


def short_name(a):
    return OTHER_NAME if rules.category(a) == "other" else capital(a["product"])


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
        cols[1].markdown(f":gray[No overlap found with any of {esc(portco)}'s activities]")
    else:
        cols[1].markdown(":gray[No overlap found with:] " + " · ".join(named(r) for r in rows))
    with cols[2].popover("Why?", width="stretch"):
        st.caption("The AI's reasons, pair by pair. “Add back” moves a pair into the table, where you can add a label "
                   "with “Edit” or dismiss it again.")
        for r in rows:
            pid = cmp.pair_id(r)
            key = f"add_{rv}_{pid}"
            reasons = [x for x in (r["comparison"].get("product_reason"), r["comparison"].get("vertical_reason")) if x]
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


def portco_sentence(target, portco, pairs, status):
    """One sentence per portfolio company, counted by business area (not by pairs), assembled in code. Rows that
    involve only own use are counted separately: they sit in the collapsed section (side lines count with the main
    activities)."""
    acts = list(dict.fromkeys(r["label_b"] for r in pairs))
    live = [r for r in pairs if kept(status[cmp.pair_id(r)])]
    n_acts = plural(len(acts), "activity", "activities")
    if not live:
        return f"None of {esc(portco)}'s {n_acts} meets an activity of {esc(target)}."
    main_live = [r for r in live if not is_own_use(r)]
    own_live = [r for r in live if is_own_use(r)]
    own_note = f"{plural(len(own_live), 'potential link')} involving own use, in the collapsed section below"
    if not main_live:
        return f"No overlap with {esc(target)}'s activities except {own_note}."
    touched = {r["label_b"] for r in main_live}
    text = f"{len(touched)} of {esc(portco)}'s {n_acts} meet activities of {esc(target)}."
    return text + (f" Also {own_note}." if own_live else "")


# =============================================================== the report (step ⑤ and the Word document)
# The output is a fully usable work product for the lawyer: the main part holds only the lawyer's final choices (no "by
# you" tags, no struck labels, nothing dismissed); everything that points to the tool goes into an Annex that can be
# ignored or deleted. Step ⑤ shows the summary of the same model, so that the screen and the document always say the
# same. Built in code from the rows; no AI call.
def parse_commission(text):
    """The Commission's view as the lawyer edited it ("Edit"), back into [(label, bullets, outcome)]: the heading
    lines written by commission_plain ("Confirmed · Commission (horizontal):") keep the result
    and the relationship, so an edited row still shows its result in the summary and the Word document."""
    groups = []
    for line in (x.strip() for x in text.split("\n")):
        if not line:
            continue
        m = re.fullmatch(r"(?:(.+?)\s*·\s*)?Commission(?:\s*\((.+)\))?\s*:", line)
        if m:
            outcome = m.group(1) if m.group(1) in OUTCOME_CLASS else ""
            groups.append([m.group(2) or "", [], outcome])
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
        lab = {"kind": p["kind"], "view": label_view(pid, p), "basis": "", "regard": [], "lines": [], "up": p["up"]}
        if not edited:
            if p["kind"] == "h" and p["origin"] == "tool":
                kind = "same product" if c.get("product_relation") == "same product" else "similar product"
                sa, sb = stage_of(r["a"]).lower(), stage_of(r["b"]).lower()
                level = f"same level ({sa})" if sa == sb else f"different levels ({sa} v {sb})"
                cust = CUSTOMER_TEXT.get(r.get("customers") or "", "") if r.get("customers") in ("●●●", "●●○",
                                                                                               "●○○") else ""
                lab["basis"] = " · ".join(x for x in (kind, level, cust) if x)
                if sa != sb:
                    lab["lines"].append("Different levels: usually a vertical relationship; horizontal only if both "
                                        "sell to the same customers.")
                m = r.get("matches") or {}
                if m.get("a") or m.get("b"):
                    lab["regard"] = [(target, ", ".join(m.get("a") or []) or "–"),
                                     (portco, ", ".join(m.get("b") or []) or "–")]
            else:
                detail = part_detail(p, r, target, portco, html_out=False)
                lab["basis"] = detail[0] if detail else ""
                lab["lines"] = detail[1:]
        labels.append(lab)
    if not labels:
        if status == "added back by user" or (r["decision"]["status"] == "unclear" and not o.get("dismiss")):
            v = VIEW_WORD.get(view_of(pid, "row", bool(o.get("dismiss"))), "")
            labels.append({"kind": "q", "view": v, "basis": "", "regard": [], "lines": ["To be checked."]})
        else:
            return None
    commission = []
    if step4:
        ed = (o.get("text_commission") or "").strip()
        if ed:
            commission = parse_commission(ed)
        else:
            commission = commission_sentences(r, target, portco, html_out=False)
    views = [lab["view"] for lab in labels if lab["view"]]
    return {"pid": pid, "a": r["a"], "b": r["b"], "b_rec": activity_record(r["b"], portco), "labels": labels,
            "edited": edited.split("\n") if edited else [],
            "commission": commission, "views": views, "note": (o.get("note") or "").strip()}


def activity_record(a, company):
    return {"name": short_name(a), "stage": stage_of(a), "sources": list(a.get("source_numbers") or []),
            "items": [i for i in a.get("includes") or [] if i], "aid": a.get("aid"), "company": company}


def report_model():
    """Everything the summary and the Word document show. Pure code on the session."""
    current_overrides()
    target = ss.companies[0]["name"]
    portcos = [c["name"] for c in ss.companies[1:]]
    step4 = bool(ss.get("precedents"))
    saved_step = ss.get("step")
    ss.step = 4 if step4 else 3        # the Commission's view is assembled as in step ④
    try:
        sections, summary, annex_b, open_points, rels, cited = [], [], [], [], [], {}
        used_sources = {c["name"]: set() for c in ss.companies}
        for p in portcos:
            pairs = [r for r in ss.results if r["portco"] == p]
            status = {cmp.pair_id(r): row_status(r) for r in pairs}
            blocks, own, hor, ver = [], [], [], []
            t_acts = [ss.confirmed[target][k] for k in display_order(ss.confirmed[target])]
            kept_rows = [r for r in pairs if kept(status[cmp.pair_id(r)])]
            rel_ids, rel = relationship_rows(target, p, kept_rows)
            if rel:
                rels.append({"portco": p, "passages": rel})
            for ta in t_acts:
                rows_main, rows_own = [], []
                for r in [x for x in pairs if (x["a"].get("aid") or x["label_a"]) == ta.get("aid")]:
                    s_ = status[cmp.pair_id(r)]
                    rec = row_record(r, target, p, step4) if kept(s_) else None
                    if rec is None:
                        o = ss.override_store.get(cmp.pair_id(r), {})
                        reasons = [x for x in (r["comparison"].get("product_reason"),
                                               r["comparison"].get("vertical_reason")) if x]
                        reason = (o.get("note") or "Dismissed in the review.") if s_ == "dismissed by user" else \
                            (" ".join(reasons) or "No reason given.")
                        annex_b.append({"portco": p, "pair": f"{short_name(r['a'])} × {short_name(r['b'])}",
                                        "reason": reason})
                        continue
                    rec["relationship"] = cmp.pair_id(r) in rel_ids and bool(rel)
                    used_sources[target].update(rec["a"].get("source_numbers") or [])
                    used_sources[p].update(rec["b"].get("source_numbers") or [])
                    (rows_own if is_own_use(r) else rows_main).append(rec)
                    for label, bullets, outcome in rec["commission"]:
                        for b in bullets:
                            for m in re.finditer(r"\[(M\.\d+|Notice) \((\d+)\)", b):
                                cited.setdefault(m.group(1), set()).add(int(m.group(2)))
                    if not is_own_use(r):
                        pair = f"{short_name(r['a'])} × {short_name(r['b'])}"
                        outs = {}       # per relationship and direction; a label "" covers all
                        for lab_, _, o_ in rec["commission"]:
                            if lab_.startswith("horizontal"):
                                keys = ["h"]
                            elif lab_.startswith("vertical"):
                                keys = ["va" if lab_.startswith(f"vertical, {target} →") else "vb"]
                            else:
                                keys = ["h", "va", "vb"]
                            for k_ in keys:
                                outs.setdefault(k_, o_)
                        for lab in rec["labels"]:
                            if lab["kind"] == "h":
                                hor.append((pair, outs.get("h", ""), lab["view"]))
                            elif lab["kind"] == "v":
                                arrow = "→" if lab["up"] == "a" else "←"     # the target supplies
                                entry = (f"{short_name(r['a'])} {arrow} {short_name(r['b'])}",
                                         outs.get("va" if lab["up"] == "a" else "vb", ""), lab["view"])
                                same = [x for x in ver if x[0] == entry[0] and x[1] == entry[1]]
                                if not same:        # two links in one direction (input and resale): one entry
                                    ver.append(entry)
                                elif entry[2] and not same[0][2]:
                                    ver[ver.index(same[0])] = entry
                    for lab in rec["labels"]:
                        if lab["view"] == "open point":
                            open_points.append({"portco": p, "pair": f"{short_name(r['a'])} × {short_name(r['b'])}",
                                                "text": rec["note"] or "To be clarified with the company."})
                            break
                if rows_main:
                    blocks.append({"target": activity_record(ta, target), "rows": rows_main})
                if rows_own:
                    own.append({"target": activity_record(ta, target), "rows": rows_own})
            sections.append({"portco": p, "sentence": re.sub(r"\\(.)", r"\1", portco_sentence(target, p, pairs, status)),
                             "blocks": blocks, "own": own})
            summary.append({"portco": p, "horizontal": hor, "vertical": ver})
        sources = []
        for c in ss.companies:
            found = ((ss.mapped.get(c["name"]) or {}).get("search") or {})
            idx = {x["n"]: x for x in found.get("sources") or [] if not x.get("dead")}
            nums = sorted(n for n in used_sources[c["name"]] if n in idx)
            if nums:
                try:
                    d_ = datetime.fromisoformat(found.get("date", ""))
                    when = f"{d_.day} {d_:%B %Y}"
                except (TypeError, ValueError):
                    when = found.get("date", "")
                sources.append({"company": c["name"], "date": when,
                                "items": [(n, display_title(idx[n]), idx[n].get("url", "")) for n in nums]})
        not_compared = []
        for c in ss.companies:
            for a in ss.confirmed.get(c["name"], []):
                if a.get("excluded"):
                    not_compared.append(f"{c['name']}: {short_name(a)} (excluded as not relevant to this deal: "
                                        f"{a.get('exclusion_reason', '')})")
                elif rules.is_gap(a):
                    not_compared.append(f"{c['name']}: {rules.gap_name(a)} (named in the sources, but what it "
                                        "offers is not stated)")
        cases = sorted(c for c in cited if c != "Notice")
        decisions = []
        for case in cases + (["Notice"] if "Notice" in cited else []):
            p0 = next((x for pid, x in corpus_paragraphs().items() if pid.startswith(case + "-")), {})
            decisions.append({"case": case, "title": p0.get("title", ""), "date": str(p0.get("date") or ""),
                              "paras": sorted(cited[case], key=lambda x: (str(type(x)), x))})
        years = decision_years(cases)
        return {"target": target, "portcos": portcos, "date": f"{datetime.now().day} {datetime.now():%B %Y}",
                "step4": step4, "years": years, "summary": summary, "sections": sections,
                "open_points": open_points, "sources": sources, "decisions": decisions,
                "annex": {"run_summary": run_summary().replace("Run summary: ", ""), "pairs": annex_b,
                          "relationships": rels, "not_compared": not_compared}}
    finally:
        ss.step = saved_step


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
    """The table of one portfolio company's box: every target activity (side lines included), then the rows
    that involve only own use, collapsed. Inside the collapsed box (nested) Streamlit allows no second expander, so
    "Own use" is a plain sub-heading there."""
    table_header(target, p)
    for ta in t_acts:
        rs = rows_of(ta)
        main_rows = [r for r in rs if not is_out(r) and not is_own_use(r)]
        screened = [r for r in rs if is_out(r)]
        if main_rows or screened:
            target_block(ta, main_rows, screened, status, rv, target, p, n_portco)
    own_rows = [r for r in pairs if not is_out(r) and is_own_use(r)]
    if not own_rows:
        return
    title = (f"Own use: {plural(len(own_rows), 'potential link')} (production for the group itself, which can only be "
             "the customer side)")
    if nested:
        st.markdown(f"**{title}**")
        own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco)
    else:
        with st.expander(title):
            own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco)


def own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco):
    table_header(target, p)
    ids = {cmp.pair_id(r) for r in own_rows}
    for ta in t_acts:
        kept_rows = [r for r in rows_of(ta) if cmp.pair_id(r) in ids]
        if kept_rows:
            target_block(ta, kept_rows, [], status, rv, target, p, n_portco)


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


STEP3_TEXT = ("Every activity of the target, compared with every activity of each portfolio company. Check each row: "
              "set your view on each label (or dismiss it), add what is missing with “Edit”, or adjust the wording.")
STEP4_TEXT = ("How the European Commission defined the markets of the products in the rows you kept, quoted from its "
              "decisions. Below each row: what follows for that row.")


# A short guide at the start of steps ②–④, open the first time the step appears, folded after that. A tool that
# states its limits openly makes the lawyer more willing to dismiss and apply their own judgement.
GUIDES = {
    2: ("How the research works", """Each company is researched on its own, in two searches of public websites: one for its main business, one for its side lines and own-use activities. The AI never sees another company of this screen or the planned deal.

- **Activities:** at most five business areas per company, split by the **stage of the supply chain** at which the company sells, for example *raw materials*, *intermediate products* (sold to other manufacturers to make their own products), *manufacturing* (finished products), *wholesale*, *retail* or *services*. Side lines and own use share one line.
- **Sources:** the app opens every page itself and checks each quotation. ✔ checked · ≈ probably right · ○ not checked · ⚠ check before relying on it.

**What it cannot see:** anything the company does not publish. The split into activities can differ between runs, so check that it fits: edit, merge, add or mark an activity as not relevant before you continue."""),
    3: ("How the preliminary assessment works", """Each activity of the target is compared with each activity of every portfolio company, one pair at a time. The AI sees only the two anonymised descriptions, never company names or the planned deal.

- **Horizontal:** the AI judges whether the products are the same or similar *for the customers*: what they are, what they are used for, their price positioning.
- **Vertical:** the AI judges whether one company's type of product could be an *input* for the other's, or be *resold* by it, even if they do not trade today.
- **Checked by the app, not the AI:** the level of trade, the direct customers (the dots), whether a reseller is in wholesale or retail, and own use, which supplies no one. Different levels usually mean a vertical relationship; horizontal only if both sell to the same customers.

The assessment is **deliberately generous** and also shows unlikely links: a missed relationship is easily overlooked later, while an unlikely one takes a second to dismiss. The judgement is yours: set your view on each label, add a note or use “Edit”. Step ④ then checks each row against the Commission's decisions."""),
    4: ("How the market definitions are found", """The products of each row are sorted into types of product. Each type is searched in the tool's database of Commission decisions (listed, with links, in the sidebar), and the AI reads the paragraphs found. It sees the products only, never company names. The Commission's own sentences are quoted word for word, and the app checks each quotation against the decision.

- **The result of each row:** *Confirmed* (both products in a market the Commission defined) · *Possible* · *Not excluded* · *Not supported* (separate markets) · *No precedent*. For vertical rows, a definition identifies the two markets; it does not show that one company supplies the other. For a shop or a wholesaler, the decisions describe the markets of the products it sells, not its own retail or wholesale market.

**Limits:** the database holds a small set of decisions, and one outside it is not found. *No precedent* does not mean no market: the market is then to be assessed under the Market Definition Notice. Each decision describes the market as it was at the time ({years}), and the Commission is not bound by it (Notice (14)). Product markets only: geography and market shares, which decide whether a market is “affected”, are not assessed."""),
}


def guide_box(step):
    title, text = GUIDES[step]
    seen = set(ss.get("guides_seen") or [])
    if step not in seen:                  # the first visit of this step: open, and open it stays during the visit
        ss.guide_open = step              # (not folded by the first change on the page)
    ss.guides_seen = sorted(seen | {step})
    first = ss.get("guide_open") == step
    if step == 4:
        cases = sorted({decision_of(m) for e in used_markets().values() for m in e["markets"]} - {""})
        years = decision_years(cases)
        text = text.replace("{years}", years or "see the decisions in the sidebar")
    with st.expander(title, expanded=first):
        st.markdown(text)


def stage_overview(ai, step=3):
    st.subheader("④ Commission market definitions" if step == 4 else "③ Preliminary assessment")
    st.write(STEP4_TEXT if step == 4 else STEP3_TEXT)
    st.html(PREF_CSS)                  # the hover boxes (sources, paragraphs, markets); style only, no space
    guide_box(4 if step == 4 else 3)
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

    with st.expander(f"Target: {target} · profile and activities"):
        st.write(profile_of(target))
        for a in [ss.confirmed[target][i] for i in display_order(ss.confirmed[target])]:
            st.markdown(activity_line(a, target), unsafe_allow_html=True)

    # the decisions used are listed in the sidebar ("Commission decisions"), not above the rows
    for i, p in enumerate(portcos, start=1):
        portco_section(i, p, target, [r for r in results if r["portco"] == p], status, rv)

    # no checklist of the Market Definition Notice on screen: "No precedent" already says the market is to be assessed
    # under the Notice
    st.divider()
    precedent_button(units, todo)


def run_summary():
    """AI calls, models, cost and time of the run."""
    calls, cost, fees, searches, seconds, models = [], 0.0, 0.0, 0, 0.0, set()
    for stage in ("mapping", "confirm", "precedents"):
        part = stage_calls(stage)
        calls += part
        cost += sum(c["cost"] for c in part)
        fees += sum(c.get("search_fee", 0.0) for c in part)
        searches += sum(c.get("web_searches", 0) for c in part)
        seconds += stage_seconds(stage)
        models |= {c["model"] for c in part}
    # the web search tool's per-call fee is included (ai_client.WEB_SEARCH_FEE, to verify)
    text = (f"Run summary: {call_count(calls)} · models: {', '.join(sorted(models)) or 'none'} · USD {cost:.3f} "
            f"(of which USD {fees:.3f} for {searches} web search calls at USD {ai_client.WEB_SEARCH_FEE:g} each; "
            f"prices to verify) · {seconds:.0f} s")
    waits = sum(c.get("rate_limit_waits", 0) for c in calls)
    if waits:                            # the key's rate limit is waited out, never failed
        text += f" · waited {plural(waits, 'time')} for the API key's rate limit"
    lf = ss.get("loaded_from")
    if lf:                               # steps ①–③ restored from a saved audit log (their calls were paid then)
        before = lf.get("calls_before") or {}
        # counted like the run itself (embedding requests apart from AI calls)
        text += (f" · plus, before loading: {call_count(ss.get('loaded_calls') or [])}, USD "
                 f"{before.get('cost', 0):.3f} (the run of {lf.get('created') or 'unknown date'})")
    return text


# =============================================================== step ⑤ summary
# The same summary as page 1 of the Word document (one bullet per relationship, the Commission's result and the lawyer's
# view), the open points, and the download. Built in code from the rows, live; no AI call.
def summary_html(model):
    def cell(entries):
        if not entries:
            return "<span class='sub2'>None</span>"
        lis = "".join(f"<li>{he(pair)} {outcome_chip(res) if res else ''}"
                      + (f"<i class='sub2'>{he(view)}</i>" if view else "") + "</li>" for pair, res, view in entries)
        return f"<ul class='sumul'>{lis}</ul>"
    rows = "".join(f"<tr><td><b>{he(s['portco'])}</b></td><td>{cell(s['horizontal'])}</td>"
                   f"<td>{cell(s['vertical'])}</td></tr>" for s in model["summary"])
    return ("<table class='sumt'><thead><tr><th>Portfolio company</th><th><span class='lab lab-h'>Potential horizontal "
            "overlaps</span></th><th><span class='lab lab-v'>Potential vertical relationships</span></th></tr></thead>"
            f"<tbody>{rows}</tbody></table>")


def word_name():
    return f"Overlap_overview_{re.sub(r'[^A-Za-z0-9]+', '_', ss.companies[0]['name']).strip('_')}_" \
           f"{datetime.now():%Y-%m-%d}.docx"


def stage_summary(ai):
    st.subheader("⑤ Summary")
    st.write("The result for each portfolio company, from your review in steps ③ and ④. The Word document holds the "
             "same summary, the full tables and the sources.")
    model = report_model()
    st.markdown(summary_html(model), unsafe_allow_html=True)
    st.caption("Target activity first; the arrow points to the customer. In brackets: the Commission's result and your "
               "view.")
    if model["open_points"]:
        st.markdown("##### Open points")
        st.markdown("\n".join(f"- {esc(o['text'])} :gray[({esc(o['pair'])}, {esc(o['portco'])})]"
                               for o in model["open_points"]))
    st.download_button("Download the Word document", data=lambda: export.docx_bytes(model), type="primary",
                       file_name=word_name(), on_click="ignore",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


# =============================================================== step ④ Commission market definitions
# One search per target activity, covering the items of all its kept rows on both sides; at most one rewrite of the
# queries. The search itself is in precedents.py; everything shown here is assembled in code from its stored records.
def prec_plan():
    """(units, todo): one unit per target activity with kept rows; todo = those without a search that still covers
    them (new, changed, or rows added back since). Dismissing a row never forces a new search."""
    if not ss.get("results"):
        return [], []
    target = ss.companies[0]["name"]
    order = [ss.confirmed[target][k]["aid"] for k in display_order(ss.confirmed[target])]
    units = prec.search_units(ss.results, search_overrides(), cmp.effective_status, cmp.dismissed_parts,
                              cmp.pair_id, order)
    store = ss.get("precedents") or {}
    return units, [u for u in units if not prec.reusable(store.get(u["target_aid"]), u)]


def stale_units(todo):
    """The target activities whose rows changed since their search: their rows say "Changed since the search".
    A search that failed does not count as changed: it keeps its record and shows its failure; "Update the market
    definitions" runs it again either way."""
    store = ss.get("precedents") or {}
    out = set()
    for u in todo:
        rec = store.get(u["target_aid"])
        if not prec.reusable(rec, u, retry_failed=False):
            out.add(u["target_aid"])
    return out


def run_precedents(ai):
    """Runs the searches that are needed, in parallel (at most ai_client.MAX_PARALLEL AI requests at once), and opens
    step ④."""
    import retrieval                       # ChromaDB is loaded only when step ④ runs
    current_overrides()
    units, todo = prec_plan()
    first, t0 = ss.log.mark(), time.time()
    store = dict(ss.get("precedents") or {})
    card = WorkCard("Looking up the Commission's market definitions", "Sorting the products into types of product …",
                    "Each type of product is searched in the Commission's decisions and read on its own; the AI sees "
                    "the products only, never company names. This usually takes one to three minutes.")
    kept = [u for u in units if u not in todo]
    if kept:
        card.log(f"✔ {plural(len(kept), 'search', 'searches')} kept from before (their rows did not change)")
    try:
        retriever = retrieval.Retriever(prec.cached_embed(ai))
    except Exception as e:  # noqa: BLE001 - nothing is lost; the user can try again
        st.error(f"The search could not start: the decision database could not be opened ({type(e).__name__}: {e}). "
                 "Nothing was changed; go back and try again.")
        st.button("← Back to the assessment", on_click=go_to, args=(3,))
        return False
    # a progress bar per type of product (step ④ takes several minutes); the worker threads count, this thread
    # only reads
    progress = prec.Progress()
    with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
        futures = {ex.submit(prec.run_unit, ai, u, ss.names, retriever, retriever.paragraphs, progress): u
                   for u in todo}
        pending, finished = set(futures), 0
        while pending:
            done, pending = cf.wait(pending, timeout=1, return_when=cf.FIRST_COMPLETED)
            finished += len(done)
            if progress.planned:
                card.update(progress.done / progress.planned,
                            f"{progress.done} of {plural(progress.planned, 'type of product', 'types of product')} "
                            "looked up")
            else:
                card.tick()
            for fut in done:
                u = futures[fut]
                try:
                    rec = fut.result()
                except Exception as e:  # noqa: BLE001 - shown in the row as an error, never as "no precedent"
                    rec = prec.empty_record(u, error=f"the search failed: {type(e).__name__}: {e}")
                show_search_done(store, u, rec, card)
    card.log(f"Market definitions looked up for {plural(len(todo), 'activity', 'activities')} of the target in "
             f"{time.time() - t0:.0f} s")
    ss.precedents = store
    log_stage("precedents", first, time.time() - t0)
    ss.step = 4
    return True


def show_search_done(store, u, rec, card):
    """Stores one finished search and writes its line in the developer details."""
    store[u["target_aid"]] = rec
    name = capital(u["target_product"])
    if rec.get("error"):
        card.log(f"✖ {name}: {rec['error']}")
        return
    placed = sum(1 for p in rec["placements"].values() if prec.ids_of(p))
    failed = len(prec.failed_ids(rec))
    card.log(f"{'⚠' if failed else '✔'} {name}: {plural(len(rec['markets']), 'market')}, {placed} of "
             f"{plural(len(rec['placements']), 'product')} placed"
             + (f", the search failed for {failed}" if failed else "") + f" · {rec['stop']}")


def prec_record(r):
    return (ss.get("precedents") or {}).get(r["a"].get("aid"))


def row_view(r):
    rec = prec_record(r)
    if not rec or r["a"].get("aid") in (ss.get("prec_stale") or set()):
        return rec, None
    return rec, prec.row_view(r, rec, search_overrides(), cmp.effective_status, cmp.dismissed_parts)


# =============================================================== step ④ under each row
# The Commission's markets: under each row, full width, after the facts and the preliminary assessment, one card per
# market says what the Commission defined (its own words, checked in code), what the market covers, why it was
# separated, and which products of each company it covers. Every paragraph is cited as [M.5644 (24)]; hovering shows the
# paragraph exactly as the AI saw it, a click opens the decision.
PREF_CSS = """<style>
[data-testid="stMarkdownContainer"]{position:relative}
.pref{position:static;cursor:help;color:#3A5A80;text-decoration:none !important;border-bottom:1px dotted #3A5A80;
 white-space:nowrap}
.pref .pbox{display:none;position:absolute;z-index:1000;left:0;right:0;margin-top:1.5em;width:auto;max-width:44em;
 max-height:26em;
 overflow:auto;background:#fff;color:#1f2328;border:1px solid #c8c8c8;border-radius:6px;padding:.6em .8em;
 box-shadow:0 4px 14px rgba(0,0,0,.18);font-size:.86rem;line-height:1.45;white-space:normal;text-align:left;
 font-weight:normal;font-style:normal}
.pref:hover .pbox{display:block}
.ccell{padding:.35rem .6rem .25rem .6rem;margin:0 0 .4rem 0;border-left:3px solid #C9C2B4;background:#F2EFE8;
 line-height:1.5;font-size:.92rem;border-radius:0}
.ccell.o-conf{background:#DCE6F2;border-left-color:#2E5A88}
.ccell.o-open{background:#ECEAE5;border-left-color:#8A857C}
.ccell.o-nosup{background:#E3EDE4;border-left-color:#5E8A66}
.ccell.o-nopre{background:#FBFAF7;border:1px dashed #C9C2B4;border-left:3px solid #C9C2B4}
.ccell .chd{font-weight:600;font-size:.82rem;color:#3D3A35}
.ccell .ed{color:#55514A;font-style:italic;font-size:.8rem}
.ccell ul{margin:.2rem 0 0 0;padding-left:1.05rem}
.ccell li{margin:.12rem 0}
.cblock{margin:.3em 0 .5em 0;padding:.55em .9em .45em .9em;border-left:3px solid #C9C2B4;
 background:#F2EFE8;border-radius:4px;line-height:1.55}
.cblock .chead{font-weight:600}
.ccard{margin-top:.5em;padding-top:.45em;border-top:1px solid rgba(128,128,128,.25)}
.ccard .mname{font-weight:600}
.ccard .lbl{opacity:.68}
.ccard .qt{font-style:italic}
.ccard .aiw{opacity:.75}
.cnote{opacity:.68;font-size:.92em}
.cblock summary,.dblock summary{cursor:pointer}
.cblock[open] summary{margin-bottom:.3em}
.atab{border-collapse:collapse;width:100%;margin:.2em 0 .1em 0;font-size:.95em}
.atab th,.atab td{border-top:1px solid rgba(128,128,128,.25);border-left:none;border-right:none;border-bottom:none;
 padding:.3em .55em;vertical-align:top;text-align:left}
.atab th{font-weight:600;opacity:.8}
.defs{margin-bottom:.6em}
.dblock{padding:.35em .9em;border-left:3px solid #C9C2B4;background:#F2EFE8;
 border-radius:4px;margin:.25em 0;line-height:1.55}
.dline{margin-top:.45em;padding-top:.35em;border-top:1px solid rgba(128,128,128,.22)}
.lbl{opacity:.68}
.qt{font-style:italic}
.aiw{opacity:.75}
</style>"""

def h(text):
    """Text from the decisions, the sources or the AI, made safe inside an HTML block. Line breaks become spaces,
    because a blank line in AI text (a summary, a quotation not found) would end the HTML block and show the rest of the
    step ④ block as raw code."""
    return html.escape(re.sub(r"\s*\n\s*", " ", str(text or "")), quote=True).replace("$", "&#36;")


@st.cache_data(show_spinner=False)
def corpus_paragraphs():
    """All paragraphs of the corpus by id (for the hover of a paragraph that a stored search did not keep)."""
    try:
        return {p["id"]: p for p in json.loads(open("corpus/paragraphs.json", encoding="utf-8").read())}
    except (OSError, ValueError):
        return {}


def decision_text(d):
    """'Article 6(1)(b) in conjunction with Article 6(2), with commitments (Phase I)' -> 'Phase I, cleared with
    commitments' (a calmer hover)."""
    d = d or ""
    if not d:
        return ""
    phase = "Phase II" if ("Phase II" in d or "8(1)" in d or "8(2)" in d) else ("Phase I" if ("Phase I" in d or
                                                                                          "6(1)" in d) else "")
    out = "cleared" if any(x in d for x in ("6(1)(b)", "8(1)", "8(2)")) else ""
    if "commitment" in d:
        out = (out + " with commitments") if out else "with commitments"
    return ", ".join(x for x in (phase, out) if x) or d


def para_ref(pid, paras):
    """[M.5644 (24)]: hover shows the paragraph as the AI saw it (decision, year, part of the decision, text,
    footnotes); a click opens the decision. The second line only names the part of the decision and how the case
    ended ("Relevant product market · A. Chocolate confectionery · Phase I, cleared with commitments")
    instead of the whole path with ">" and the legal basis."""
    p = paras.get(pid) or corpus_paragraphs().get(pid)
    case, _, n = pid.rpartition("-")
    label = f"[{case} ({n})]"
    if not p:
        return f"<span class='pref'>{h(label)}</span>"
    notes = "".join(f"<br><i>Footnote {h(f.get('n'))}:</i> {h(f.get('text'))}" for f in p.get("footnotes") or [])
    heads = prec.headings_of(p) or prec.headings_of(corpus_paragraphs().get(pid) or {})
    last = re.split(r"\s*>\s*", heads)[-1].strip() if heads else ""
    meta = " · ".join(x for x in (p.get("section"), last, decision_text(p.get("decision"))) if x)
    url = p.get("url") if str(p.get("url") or "").startswith("https://") else ""
    name = p.get("title") if p["case"] == "Notice" else f"{p['case']} {p.get('title')}"
    box = (f"<b>{h(name)} ({h(str(p.get('date') or '')[:4])}), para ({h(p.get('para'))})</b>"
           + (f"<br><span style='opacity:.7'>{h(meta)}</span>" if meta else "")
           + f"<br>{h(p.get('text'))}{notes}"
           + ("<br><span style='opacity:.7'>The paragraph exactly as the AI saw it. Click to open the decision.</span>"
              if url else "<br><span style='opacity:.7'>The paragraph exactly as the AI saw it.</span>"))
    if url:
        return f"<a class='pref' href='{h(url)}' target='_blank'>{h(label)}<span class='pbox'>{box}</span></a>"
    return f"<span class='pref'>{h(label)}<span class='pbox'>{box}</span></span>"


def para_refs(pids, paras):
    return " ".join(para_ref(pid, paras) for pid in prec._sorted_ids(set(x for x in pids if x)))


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


def decision_of(m):
    """The decision a market comes from: that of its conclusion sentence, else the one most of its paragraphs cite."""
    pid = m.get("decided_paragraph") or m.get("open_paragraph") or m.get("conclusion_paragraph")
    if pid:
        return pid.rpartition("-")[0]
    cases = [pid.rpartition("-")[0] for pid in m.get("product_paragraphs") or [] if not pid.startswith("Notice")]
    return max(set(cases), key=cases.count) if cases else ""


def decision_years(cases):
    """"M.5644: 2009, M.6872: 2013" (a decision missing from the corpus is left out)."""
    out = []
    for c in cases:
        p = next((x for pid, x in corpus_paragraphs().items() if pid.startswith(c + "-")), None)
        if p and str(p.get("date") or "")[:4].isdigit():
            out.append(f"{c}: {str(p['date'])[:4]}")
    return ", ".join(out)


def decision_label(case):
    p = next((x for pid, x in corpus_paragraphs().items() if pid.startswith(case + "-")), None)
    return f"{case} {p['title']} ({str(p['date'])[:4]})" if p else case


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
    """A market's name as shown: "Market for tablets" and "tablets" are the same market, shown as "Tablets"."""
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


def decisions_html():
    """The sidebar's "Commission decisions": one line per decision used in this screen, linked to the decision; on
    hover, the markets the screen uses from it. Plus the Market Definition Notice."""
    used = used_markets()
    if not used:
        return ""
    settled = {}
    for e in used.values():
        for m in e["markets"]:
            if m.get("conclusion") in SETTLED and m.get("decided_paragraph"):
                settled.setdefault(m["decided_paragraph"], set()).add(mname(m["name"]))
    by_case = {}
    for (case, key), e in used.items():
        by_case.setdefault(case, []).append(e)
    corpus = corpus_paragraphs()
    lines = []
    for case in sorted(c for c in by_case if c):
        groups = {}
        for e in sorted(by_case[case], key=lambda x: x["name"].lower()):
            m = _best(e["markets"])
            segs = {n for pid in (m.get("product_paragraphs") or []) for n in settled.get(pid, set())} \
                - {mname(m["name"])}
            label = ("category divided into separate markets" if m.get("conclusion") == prec.NOT_STATED and segs
                     else CONCLUSION_TEXT.get(m.get("conclusion"), "defined"))
            groups.setdefault(label, []).append(mname(e["name"]))
        tip = " · ".join(f"{k}: {', '.join(v)}" for k, v in groups.items())
        url = next((p.get("url") for pid, p in corpus.items() if pid.startswith(case + "-") and
                    str(p.get("url") or "").startswith("https://")), "")
        text = h(decision_label(case))
        link = f"<a href='{h(url)}' target='_blank'>{text}</a>" if url else text
        lines.append(f"<div class='lg' title='{h(tip)}'>{link}</div>")
    notice = corpus.get("Notice-14") or {}
    if str(notice.get("url") or "").startswith("https://"):
        lines.append(f"<div class='lg' title='The Commission Notice on the definition of the relevant market, used where "
                     f"no decision covers the products'><a href='{h(notice['url'])}' target='_blank'>Market Definition "
                     "Notice (2024)</a></div>")
    return "".join(lines)


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
    if not (m.get("decided_quote") or m.get("open_quote")) and m.get("summary"):
        box += f"<br><i>AI summary:</i> {h(m['summary'])}"
    box += "<br><span style='opacity:.7'>The decision is listed in the sidebar, under “Commission decisions”.</span>"
    return f"<span class='pref'>{h(mname(m['name']))}<span class='pbox'>{box}</span></span>"


def _items_html(g, market_name=""):
    """One side's products in one market: a product that could be in several markets says where else
    it could be, e.g. “chocolate bars (or Tablets)”; a range or the activity's own name is marked “(general term)”."""
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
    return ", ".join(out) + (" <span class='or'>by analogy</span>" if g["basis"] != "precedent" else "")


def _cites(m, paras, limit=2):
    """The paragraphs a market's conclusion rests on (hover: the paragraph as the AI saw it)."""
    pids = [x for x in (m.get("decided_paragraph"), m.get("open_paragraph")) if x]
    if not pids:
        pids = prec._sorted_ids({x for x in m.get("product_paragraphs") or [] if not x.startswith("Notice")})[:limit]
    return para_refs(pids[:limit], paras)


def _side_text(entries, view, side, paras, html_out=True):
    """Where one side's products fall: the markets, else “no precedent for …” or “search failed”."""
    found = [e for e in entries if e[side]]
    if found:
        if html_out:
            return ", ".join(market_hover(e["market"], paras, e.get("category")) for e in found)
        return ", ".join(mname(e["market"]["name"]) for e in found)
    groups = view.get(side) or []
    if any(g["market_id"] == "failed" for g in groups):
        return "search failed"
    return "no precedent"


def _cites_plain(m, limit=2):
    """The same paragraphs as _cites, as plain text: "[M.5644 (24)]" (for the Word document)."""
    pids = [x for x in (m.get("decided_paragraph"), m.get("open_paragraph")) if x]
    if not pids:
        pids = prec._sorted_ids({x for x in m.get("product_paragraphs") or [] if not x.startswith("Notice")})[:limit]
    return " ".join("[" + pid.rpartition("-")[0] + " (" + pid.rpartition("-")[2] + ")]" for pid in pids[:limit])


def _rank(e):
    return max((e["a"] or {}).get("status", "specific"), (e["b"] or {}).get("status", "specific"), key=STATUS_RANK.get)


OUTCOME_CLASS = {"Confirmed": "o-conf", "Markets defined": "o-conf", "Possible": "o-open", "Not excluded": "o-open",
                 "One side defined": "o-open", "Not supported": "o-nosup", "No precedent": "o-nopre"}
OUTCOME_TIP = {
    "Confirmed": "Both products fall in a market the Commission defined: horizontal overlap at product-market level.",
    "Possible": "Both products may fall in the same market, depending on the product format: to be checked.",
    "Not excluded": "Both products fall in a market whose definition the Commission left open (or the paragraphs found "
                    "state no conclusion): the overlap cannot be excluded.",
    "Not supported": "The Commission puts the products in separate markets: no horizontal overlap at product-market "
                     "level; check for a vertical relationship.",
    "No precedent": "No decision in the database covers these products: to be assessed under the Market Definition "
                    "Notice.",
    "Markets defined": "The Commission defined both the upstream and the downstream market.",
    "One side defined": "The Commission defined the market of one side only; the other side has no precedent.",
}


def outcome_chip(outcome):
    return (f"<span class='oc {OUTCOME_CLASS[outcome]}' title='{h(OUTCOME_TIP[outcome])}'>{outcome}</span>"
            if outcome else "")


def horizontal_outcome(entries, verdict, rs=None):
    """What the Commission's view means for a horizontal row: Confirmed · Possible · Not excluded · Not supported ·
    No precedent. The strongest result of the row counts.
    A category the Commission divided into separate markets is not a market: both products in it is
    "Possible" (which segment is to be checked). A shop or wholesaler on either side: "No precedent" (its own market
    is the retail or wholesale of the products, which the decisions found do not define)."""
    if rs and (rs.get("a") or rs.get("b")):
        return "No precedent"
    if verdict and verdict.get("different"):
        return "Not supported"
    shared = [e for e in entries if e["a"] and e["b"] and not e.get("category")]
    in_category = [e for e in entries if e["a"] and e["b"] and e.get("category")]
    if any(_rank(e) == "specific" and e["market"].get("conclusion") in SETTLED for e in shared):
        return "Confirmed"
    if any(_rank(e) != "specific" for e in shared) or in_category:
        return "Possible"
    if shared:
        return "Not excluded"
    return "No precedent"


def vertical_outcome(entries, up, rs=None):
    """The same for a vertical relationship; a shop's or wholesaler's side counts as no precedent (see is_reseller)."""
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
    """The Commission's view of a horizontal row as bullets, in the Commission's own terms (wording checked against
    M.5644, M.6872 and M.9798): one bullet per group of products, a category divided into separate markets named as
    such, and the level rule for shops and wholesalers."""
    T, P = (he(target), he(portco)) if html_out else (target, portco)

    def names(es, joiner=", "):
        if html_out:
            return joiner.join(market_hover(e["market"], paras, e.get("category")) + (
                " <span class='or'>by analogy</span>" if any(x and x["basis"] != "precedent" for x in (e["a"], e["b"]))
                else "") + " " + _cites(e["market"], paras) for e in es)
        return joiner.join(mname(e["market"]["name"]) + (" (by analogy)" if any(
            x and x["basis"] != "precedent" for x in (e["a"], e["b"])) else "") + " " + _cites_plain(e["market"])
            for e in es)
    if rs and (rs.get("a") or rs.get("b")):
        acts = acts or {}
        if rs.get("a") and rs.get("b"):
            la, lb = level_word(acts.get("a")), level_word(acts.get("b"))
            if la == lb:
                text = (f"no decision in the database covers the {la} of these products: to be assessed under the "
                        "Market Definition Notice")
            else:           # retail v wholesale are different levels of trade
                text = (f"different levels of trade ({T}: {la}; {P}: {lb}): a horizontal overlap only if both sell to "
                        f"the same customers; no decision in the database covers the {la} or {lb} of these products: "
                        "to be assessed under the Market Definition Notice")
            sold = [e for e in entries if e["a"] or e["b"]]
            if sold:
                text += f"; the products sold fall in {names(sold)}"
            return [text]
        side = "a" if rs.get("a") else "b"
        who = T if side == "a" else P
        return [f"different levels of trade: {who}'s activity is {level_word(acts.get(side))}, and the decisions "
                "describe the markets of the products, not that market: a horizontal overlap only if both sell to the "
                "same customers; to be assessed under the Market Definition Notice"]
    if verdict and verdict.get("different"):
        return [f"the products fall in separate markets ({T}: {_side_text(entries, view, 'a', paras, html_out)}; "
                f"{P}: {_side_text(entries, view, 'b', paras, html_out)}): no horizontal overlap at product-market "
                "level; check for a vertical relationship"]
    shared = [e for e in entries if e["a"] and e["b"]]
    conc = lambda e: e["market"].get("conclusion")   # noqa: E731
    cat = [e for e in shared if e.get("category")]
    shared = [e for e in shared if not e.get("category")]
    both = [e for e in shared if _rank(e) == "specific" and conc(e) in SETTLED]
    partly = [e for e in both if conc(e) == prec.PARTLY]
    left = [e for e in shared if _rank(e) == "specific" and conc(e) == "left open"]
    unknown = [e for e in shared if _rank(e) == "specific" and conc(e) not in SETTLED + ("left open",)]
    possibly = [e for e in shared if _rank(e) == "possibly"]
    general = [e for e in shared if _rank(e) == "general"]
    out = []
    if both:
        word = "market" if len(both) == 1 else "markets"
        out.append(f"{_prefix(both, html_out)}both products fall in the {word} for {names(both)}: horizontal overlap "
                   "at product-market level" + ("; a further question about this market was left open" if partly
                                                else ""))
    if left:
        out.append(f"{_prefix(left, html_out)}{names(left)}; the exact definition was left open: a horizontal overlap "
                   "cannot be excluded")
    if possibly:
        out.append(f"{_prefix(possibly, html_out)}{names(possibly, ' or ')}, depending on the product format: "
                   "horizontal overlap at product-market level possible, to be checked")
    for e in cat:
        out.append(f"{_prefix([e], html_out)}within {names([e])}, which the Commission divided into separate markets "
                   f"({', '.join(e['category'])}): which of them is to be checked")
    if unknown:
        out.append(f"{_prefix(unknown, html_out)}{names(unknown)}: no market definition in the paragraphs found: "
                   "check the decision")
    if general:
        out.append(f"{_prefix(general, html_out)}both companies' products fall in {names(general)} only through a "
                   "general term: which products are in it is to be checked")
    if not out:
        if any(e["a"] or e["b"] for e in entries):
            out.append(f"no decision in the database places both companies' products in one market ({T}: "
                       f"{_side_text(entries, view, 'a', paras, html_out)}; {P}: "
                       f"{_side_text(entries, view, 'b', paras, html_out)}): the preliminary assessment of step ③ "
                       "stands; to be assessed under the Market Definition Notice")
        else:
            out.append("no decision in the database covers these products: the preliminary assessment of step ③ "
                       "stands; to be assessed under the Market Definition Notice")
    return out


def vertical_sentence(entries, view, up, target, portco, paras, html_out=True, rs=None, acts=None):
    """The Commission's view of a vertical relationship as two bullets, in the Commission's terms (M.6872 (51)–(52)):
    the upstream and the downstream market. A shop's or wholesaler's side is the retail or wholesale of the
    products it sells (no precedent); the markets of those products are named as what it sells."""
    down = "b" if up == "a" else "a"
    who = {"a": he(target) if html_out else target, "b": he(portco) if html_out else portco}
    acts = acts or {}
    if not any(e[up] or e[down] for e in entries):
        return ["no decision in the database covers either side: the preliminary assessment of step ③ stands; to be "
                "assessed under the Market Definition Notice"]

    def ms(found):
        segs = {mname(e["market"]["name"]) for e in found if not e.get("category")}
        found = [e for e in found if not (e.get("category") and set(e["category"]) & segs)] or found
        if html_out:
            return ", ".join(market_hover(e["market"], paras, e.get("category")) + " " + _cites(e["market"], paras)
                             for e in found)
        return ", ".join(mname(e["market"]["name"]) + " " + _cites_plain(e["market"]) for e in found)

    def side(s, level, role):
        found = [e for e in entries if e[s]]
        head = f"{capital(level)} ({who[s]} as {role})"
        if rs and rs.get(s):
            text = f"{capital(level)}: {level_word(acts.get(s))} of these products ({who[s]}): no precedent"
            return text + (f"; the products {who[s]} sells fall in {ms(found)}" if found else "")
        if found:
            return f"{head}: {ms(found)}"
        return f"{head}: {_side_text(entries, view, s, paras, html_out)}"
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
        if m.get("conclusion") == prec.NOT_STATED:
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


def reseller_flags(r):
    return {"a": is_reseller(r["a"]), "b": is_reseller(r["b"])}


def commission_sentences(r, target, portco, html_out=True):
    """[(label, bullets, outcome)], one per relationship shown in the row."""
    parts = commission_parts(r, target, portco)
    if not parts or parts[1] is None or parts[1].get("error"):
        return []
    rec, view, entries, h_on, ups, verdict = parts
    paras = (rec or {}).get("paragraphs") or {}
    rs, acts = reseller_flags(r), {"a": r["a"], "b": r["b"]}
    out = []
    if h_on:
        out.append(("horizontal", horizontal_sentences(entries, view, verdict, target, portco, paras, html_out, rs,
                                                       acts), horizontal_outcome(entries, verdict, rs)))
    for up in ups:
        u, d = (target, portco) if up == "a" else (portco, target)
        out.append((f"vertical, {u} → {d}", vertical_sentence(entries, view, up, target, portco, paras, html_out, rs,
                                                               acts), vertical_outcome(entries, up, rs)))
    if len(out) > 1 and all(o == "No precedent" for _, _, o in out) and not any(rs.values()):
        out = [("", ["no decision in the database covers these products: the preliminary assessment of step ③ stands; "
                     "to be assessed under the Market Definition Notice"], "No precedent")]
    if not out:          # unclear, or added back without a label: where each side's products fall
        out.append(("", [f"{he(target) if html_out else target}: {_side_text(entries, view, 'a', paras, html_out)}",
                         f"{he(portco) if html_out else portco}: {_side_text(entries, view, 'b', paras, html_out)}"],
                    ""))
    return out


def commission_plain(r, target, portco):
    """The Commission's view as plain text, for “Edit” (one line per bullet)."""
    sentences = commission_sentences(r, target, portco, html_out=False)
    if not sentences:
        return ""

    def head(label, outcome):
        return " · ".join(x for x in (outcome, "Commission" + (f" ({label})" if label else "")) if x)
    return "\n".join(f"{head(label, outcome)}:\n"
                     + "\n".join(f"- {capital(b).replace(PREFIX_SEP, ': ')}" for b in bullets)
                     for label, bullets, outcome in sentences)


def grouped_markets(view, entries, h_on, ups, target, portco, paras, rs=None, acts=None):
    """The Commission's markets for one row, grouped: for a horizontal row “Same market”, “Possibly the same market”,
    “Only one company”, “No precedent”; for a vertical row the upstream and the downstream market. One market per
    line with one line per company below; a category divided into separate markets is
    its own group; a shop's or wholesaler's side is labelled as what it sells; names escaped once (no "&amp;")."""
    rs, acts = rs or {}, acts or {}

    def item(e, lines, one=False):
        m = e["market"]
        status = ("category divided into separate markets" if e.get("category")
                  else CONCLUSION_TEXT.get(m.get("conclusion"), "defined"))
        body = "".join(f"<span class='wr'>{x}</span>" for x in lines)
        return (f"<div class='it{' one' if one else ''}'><b>{market_hover(m, paras, e.get('category'))}</b> "
                f"<span class='sub2'>· {h(status)} {_cites(m, paras)}</span>{body}</div>")

    def unplaced(side, kind):
        return [i for g in view.get(side) or [] if g["market_id"] == kind for i in g["items"]]
    t, p = he(target), he(portco)
    groups = []
    if h_on:
        pairs = [e for e in entries if e["a"] and e["b"]]
        same = [e for e in pairs if _rank(e) == "specific" and not e.get("category")]
        maybe = [e for e in pairs if _rank(e) != "specific" and not e.get("category")]
        cat = [e for e in pairs if e.get("category")]
        one = [e for e in entries if not (e["a"] and e["b"])]
        both = lambda e: [f"<i>{t}:</i> {_items_html(e['a'], e['market']['name'])}",   # noqa: E731
                          f"<i>{p}:</i> {_items_html(e['b'], e['market']['name'])}"]
        if same:
            groups.append(("Same market", "".join(item(e, both(e)) for e in same)))
        if maybe:
            groups.append(("Possibly the same market (depends on the product format)",
                           "".join(item(e, both(e)) for e in maybe)))
        if cat:
            groups.append(("Within a category the Commission divided into separate markets",
                           "".join(item(e, both(e)) for e in cat)))
        if one:
            groups.append(("Only one company", "".join(
                item(e, [f"<i>{t if e['a'] else p}:</i> {_items_html(e['a'] or e['b'], e['market']['name'])}"], True)
                for e in one)))
        sides = (("a", t), ("b", p))
    else:
        order = ups[:1] or []
        up, down = ("a", "b") if order in ([], ["a"]) else ("b", "a")
        names = {"a": target, "b": portco}

        def title(s, level, role):
            if rs.get(s):
                return f"{capital(level)} · {names[s]}: {level_word(acts.get(s))} of the products below (no precedent)"
            return f"{capital(level)} market · {names[s]} ({role})" if order else names[s]
        for s, level, role in ((up, "upstream", "supplier"), (down, "downstream", "customer")):
            body = "".join(item(e, [_items_html(e[s], e["market"]["name"])], True) for e in entries if e[s])
            none = unplaced(s, "none")
            if none:
                body += f"<div class='it one'><span class='sub2'>No precedent:</span> {he(', '.join(none))}</div>"
            failed = unplaced(s, "failed")
            if failed:
                body += f"<div class='it one'><span class='sub2'>Search failed:</span> {he(', '.join(failed))}</div>"
            if body:
                groups.append((title(s, level, role), body))
        sides = ()
    none = [(name, unplaced(s, "none")) for s, name in sides if unplaced(s, "none")]
    if none:
        groups.append(("No precedent", "".join(f"<div class='it one'><i>{n}:</i> {he(', '.join(i))} "
                                               "<span class='sub2'>· to be assessed under the Market Definition "
                                               "Notice</span></div>" for n, i in none)))
    failed = [(name, unplaced(s, "failed")) for s, name in sides if unplaced(s, "failed")]
    if failed:
        groups.append(("Search failed", "".join(f"<div class='it one'><i>{n}:</i> "
                                                f"{he(', '.join(i))}</div>" for n, i in failed)))
    return "".join(f"<div class='grp'>{h(title)}</div>{body}" for title, body in groups)


def commission_cell(r, target, portco):
    """Step ④, the Commission column of a row (after the preliminary assessment): per relationship the result chip and
    the bullets, in the colour of the result. Code only, no AI call. Returns the market list for under the row (or
    "")."""
    if not ss.get("precedents") or ss.get("step") != 4:
        return ""
    rec, view = row_view(r)
    if rec and view is None and r["a"].get("aid") in (ss.get("prec_stale") or set()):
        st.caption("Changed since the search: press “Update the market definitions” below.")
        return ""
    if view is None:
        if kept(row_status(r)):
            st.caption("Not searched yet: press “Update the market definitions” below.")
        return ""
    if view["error"]:
        st.markdown(f"<div class='ccell'><b>Commission:</b> the search failed ({he(view['error'])}): press “Update "
                    "the market definitions” below.</div>", unsafe_allow_html=True)
        return ""
    _, _, entries, h_on, ups, _ = commission_parts(r, target, portco)
    paras = rec.get("paragraphs") or {}
    o = ss.override_store.get(cmp.pair_id(r), {})
    edited = (o.get("text_commission") or "").strip()
    if edited:
        cells = (f"<div class='ccell'>{he(edited).replace(chr(10), '<br>')} <span class='ed'>edited by you</span>"
                 "</div>")
    else:
        cells = ""
        for label, bullets, outcome in commission_sentences(r, target, portco):
            head = "Commission" + (f" ({label})" if label else "")
            cells += (f"<div class='ccell {OUTCOME_CLASS.get(outcome, '')}'>{outcome_chip(outcome)}"
                      f"<span class='chd'>{he(head)}</span><ul>"
                      + "".join(f"<li>{b[:1].upper() + b[1:] if not b.startswith('<') else b}</li>" for b in bullets)
                      + "</ul></div>")
    if view.get("failed"):
        cells = (f"<div class='ccell'><b>The search failed</b> for {he(', '.join(dict.fromkeys(view['failed'])))}: "
                 "press “Update the market definitions” below.</div>") + cells
    st.markdown(cells, unsafe_allow_html=True)
    return grouped_markets(view, entries, h_on, ups, target, portco, paras, reseller_flags(r),
                           {"a": r["a"], "b": r["b"]})


def precedent_warnings(units):
    """Only what needs action (the search summary is in the saved progress file, not on the page)."""
    records = [ss.precedents[u["target_aid"]] for u in units if u["target_aid"] in ss.precedents]
    s = prec.summary(records)
    if s["errors"]:
        st.warning("Some searches failed: " + "; ".join(esc(e) for e in s["errors"]) + ". Press “Update the market "
                   "definitions” to try them again.")


def precedent_button(units, todo):
    store = ss.get("precedents") or {}
    failed = [u for u in units if (store.get(u["target_aid"]) or {}).get("error")]
    todo = todo + [u for u in failed if u not in todo]
    if not units:
        st.caption("No row is kept: there are no market definitions to look up.")
        return
    if not store:
        label = "Find Commission market definitions"
    elif todo:
        label = (f"Update the market definitions ({plural(len(todo), 'search', 'searches')} for new or changed rows, "
                 f"{len(units) - len(todo)} kept)")
    else:
        return                      # no "up to date" line; a changed row shows its own note
    if st.button(label, type="primary"):
        if failed:          # a failed search is never "reusable": drop it so that it runs again
            for u in failed:
                ss.precedents.pop(u["target_aid"], None)
        start_work("precedents")


def precedent_rows():
    """Per kept row: the markets on each side and the verdict, as the table shows them (for the audit log)."""
    if not ss.get("precedents") or not ss.get("results"):
        return {}
    out = {}
    for r in ss.results:
        rec, view = row_view(r)
        if view is None:
            continue
        out[cmp.pair_id(r)] = {
            "target_activity": r["a"].get("product"), "portco": r["portco"], "portco_activity": r["b"].get("product"),
            "target_side": [{"market": (g["market"] or {}).get("name"), "basis": g["basis"], "items": g["items"],
                             "status": g.get("status"), "notes": g.get("notes") or {}} for g in view["a"]],
            "portco_side": [{"market": (g["market"] or {}).get("name"), "basis": g["basis"], "items": g["items"],
                             "status": g.get("status"), "notes": g.get("notes") or {}} for g in view["b"]],
            "verdict": None if not view.get("verdict") else {
                "both": [(g["market"] or {}).get("name") for g in view["verdict"]["both"]],
                "possibly_both": [(g["market"] or {}).get("name") for g in view["verdict"].get("possibly", [])],
                "both_only_through_a_general_term": [(g["market"] or {}).get("name")
                                                     for g in view["verdict"].get("general", [])],
                "only_target": [(g["market"] or {}).get("name") for g in view["verdict"]["only_a"]],
                "only_portco": [(g["market"] or {}).get("name") for g in view["verdict"]["only_b"]],
                "different_markets_under_the_precedent": view["verdict"]["different"],
                "left_open": view["verdict"]["left_open"],
                "conclusion_not_in_paragraphs": view["verdict"].get("not_stated", False)},
            "search_failed_for": view.get("failed") or [],
            "error": view.get("error") or ""}
    return out


# =============================================================== continue a saved screen
# Useful e.g. for a lawyer who is only interested in step ④. Restores steps ①–③ (and ④, if the file has it) from an
# audit log downloaded from this app, without any AI call. The file stays with the lawyer; the app stores nothing.
AUDIT_REQUIRED = ("companies", "stage_1_2_activity_mapping", "stage_2_confirmed_activities",
                  "stage_3_factual_comparison")


def check_audit(data):
    """The problems that stop a file from being loaded (empty list = it can be loaded)."""
    if not isinstance(data, dict):
        return ["the file is not an audit log of this app"]
    missing = [k for k in AUDIT_REQUIRED if k not in data]
    if missing:
        return [f"the file has no {', '.join(missing)} (an audit log downloaded in step ③ or later is needed)"]
    problems = []
    companies, confirmed = data["companies"], data["stage_2_confirmed_activities"]
    if not isinstance(companies, list) or not companies or not all(isinstance(c, dict) and c.get("name")
                                                                   for c in companies):
        problems.append("the list of companies is missing or damaged")
    elif not isinstance(confirmed, dict) or any(c["name"] not in confirmed for c in companies):
        problems.append("the confirmed activities are missing or damaged")
    results = data["stage_3_factual_comparison"]
    if not isinstance(results, list) or not all(isinstance(r, dict) and {"a", "b", "decision", "comparison",
                                                                         "portco"} <= set(r) for r in results):
        problems.append("the results of step ③ are missing or damaged")
    return problems


def load_audit(data):
    """Restores the screen of an audit log into the session (after reset_all). No AI call."""
    reset_all()
    for k, v in (("stage_logs", {}), ("pf_version", 0), ("acts_version", 0)):    # removed by reset_all
        ss.setdefault(k, v)
    companies, mapped = data["companies"], data["stage_1_2_activity_mapping"] or {}
    confirmed = data["stage_2_confirmed_activities"]
    ss.companies = companies
    ss.mapped = {c["name"]: mapped.get(c["name"]) or {"extraction": {"activities": confirmed[c["name"]]}}
                 for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    # found again from the saved research, with the current rule (a saved file may hold false matches)
    ss.relationships = am.find_relationships(ss.mapped, companies,
                                             (data.get("anonymisation") or {}).get("kept_as_ordinary_words") or ())
    cmp.ensure_ids(confirmed)
    ss.acts = copy.deepcopy(confirmed)
    ss.profiles_text = data.get("stage_2_company_profiles") or {}
    # the saved profiles count as the lawyer's version (they may have been edited); mapping a company again
    # replaces its profile, as in a live screen
    ss.profiles_edit = {n: t for n, t in ss.profiles_text.items() if isinstance(t, str)}
    anon = data.get("anonymisation") or {}
    ss.keep_words = list(anon.get("kept_as_ordinary_words") or [])
    ss.keep_proposed = list(anon.get("proposed_by_the_tool (used in lower case)") or [])
    ss.drop_words = list(anon.get("unticked_by_user (removed)") or [])
    ss.freeze_proposals = True
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in companies}
    ss.names = cmp.collect_names(companies, confirmed, group, ss.keep_words)
    ss.profiles_meta = anon.get("abstracts") or {}
    results = [{k: v for k, v in r.items() if k != "status_after_overrides"} for r in data["stage_3_factual_comparison"]]
    ss.results = results
    ss.confirmed = confirmed
    ss.confirmed_hash = ss.current_hash = activities_hash(confirmed)
    # the pair results under their content keys, so that "Update the comparison" sends only new or changed pairs
    ss.pair_cache = {}
    for r in results:
        try:
            ss.pair_cache[(cmp.activity_key(r["a"], r["abstract_a"]), cmp.activity_key(r["b"], r["abstract_b"]))] = r
        except (KeyError, TypeError):
            pass
    ss.vec_cache = {}
    ss.override_store = {pid: dict(o) for pid, o in (data.get("user_overrides") or {}).items() if isinstance(o, dict)}
    ss.results_version = 1
    ss.precedents = dict((data.get("stage_4_market_definitions") or {}).get("searches") or {})
    before = list(data.get("call_log_before_loading") or []) + list(data.get("call_log") or [])
    ss.loaded_calls = before
    ss.loaded_from = {"created": data.get("created"), "loaded": datetime.now().isoformat(timespec="seconds"),
                      "profile": data.get("profile"), "models": data.get("models"),
                      "calls_before": {"calls": len(before), "cost": round(sum(c.get("cost", 0) or 0 for c in before), 4)}}
    ss.acts_version += 1
    ss.step = 4 if ss.precedents else 3


def loader_box():
    """'Open saved progress' in the sidebar."""
    st.caption("Continues a screen from a progress file saved with this app (.json): companies, activities, the "
               "assessment and step ④, with your dismissals, notes and edits, without any AI call. The current "
               "screen is replaced. The file stays with you; the app stores nothing.")
    up = st.file_uploader("Progress file (.json)", type=["json"], key="audit_upload", label_visibility="collapsed")
    if up is None:
        return
    try:
        data = json.loads(up.getvalue().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        st.error(f"The file could not be read as JSON: {e}")
        return
    problems = check_audit(data)
    if problems:
        st.error("This file cannot be loaded: " + "; ".join(problems) + ".")
        return
    target = data["companies"][0]["name"]
    st.write(f"Saved {esc((data.get('created') or 'unknown date').replace('T', ' '))}: target **{esc(target)}**, "
             f"{plural(len(data['companies']) - 1, 'portfolio company', 'portfolio companies')}"
             + (", with step ④" if data.get("stage_4_market_definitions") else "") + ".")
    if st.button("Load this screen", type="primary"):
        load_audit(data)
        st.rerun()


# =============================================================== audit log
def audit_calls():
    """Every call of the current screen (since the screen started): the research of each company, including companies
    mapped again, and every comparison run. A comparison only sends new or changed pairs, so no call
    is repeated, and the results shown can come from any of these runs."""
    return ss.log.calls[ss.get("run_first", 0):]


def audit_snapshot(ai):
    """References to everything the audit log contains, taken in the script thread. The JSON itself is built
    only when the user clicks the download button (on another thread, which cannot read session state).
    The overrides are refreshed first: "Save progress" sits in the sidebar, which is drawn before the table, so
    without this a box ticked just before saving would be missing from the file."""
    if ss.get("results") is not None:
        current_overrides()
    return {"created": datetime.now().isoformat(timespec="seconds"), "profile": PROFILE, "dev_mode": DEV_MODE,
            "cache": USE_CACHE, "models": dict(ai.models),
            "companies": ss.get("companies"), "mapped": ss.get("mapped"), "relationships": ss.get("relationships"),
            "confirmed": ss.get("confirmed"),
            # the profiles as shown now (including an edit after the comparison)
            "profiles": {c["name"]: profile_of(c["name"]) for c in ss.get("companies") or []},
            "names": list(ss.get("names") or []), "keep_words": list(ss.get("keep_words") or []),
            "keep_proposed": list(ss.get("keep_proposed") or []), "drop_words": list(ss.get("drop_words") or []),
            "abstracts": ss.get("profiles_meta"), "results": list(ss.get("results") or []),
            "overrides": dict(ss.get("overrides") or {}), "calls": audit_calls(),
            # step ④ (one search per target activity) and, for a continued screen, where it came from
            "precedents": dict(ss.get("precedents") or {}), "precedent_rows": precedent_rows(),
            "loaded_from": ss.get("loaded_from"), "loaded_calls": list(ss.get("loaded_calls") or [])}


def audit_json(snap):
    slim = [{k: v for k, v in r.items() if k != "sims"}
            | {"sims": {k: round(v, 3) for k, v in r["sims"].items()},
               "status_after_overrides": (r["decision"]["status"] if cmp.effective_status(r, snap["overrides"])
                                          == "dismissed by user" and has_added(snap["overrides"].get(cmp.pair_id(r)))
                                          else cmp.effective_status(r, snap["overrides"]))}
            for r in snap["results"]]
    log = {
        "created": snap["created"], "profile": snap["profile"], "dev_mode": snap["dev_mode"],
        "development_cache": snap["cache"], "models": snap["models"],
        "prices": {"checked": ai_client.PRICES_CHECKED, "usd_per_1m_tokens": ai_client.PRICES},
        "thresholds": {"input_match": rules.INPUT_MATCH, "resale_match": rules.RESALE_MATCH},
        "companies": snap["companies"],
        "stage_1_2_activity_mapping": snap["mapped"],
        "existing_relationships": snap["relationships"],
        "stage_2_company_profiles": snap["profiles"],
        "stage_2_confirmed_activities": snap["confirmed"],
        "anonymisation": {"name_variants_removed": sorted(rules.name_variants(snap["names"])),
                          "kept_as_ordinary_words": snap["keep_words"],
                          "proposed_by_the_tool (used in lower case)": snap["keep_proposed"],
                          "unticked_by_user (removed)": snap["drop_words"],
                          "abstracts": snap["abstracts"]},
        "stage_3_factual_comparison": slim,
        "user_overrides": snap["overrides"],
        "call_log": snap["calls"],
    }
    if snap.get("precedents"):
        log["stage_4_market_definitions"] = {
            "settings": {"max_attempts": prec.MAX_ATTEMPTS, "types_per_search": prec.MAX_TYPES,
                         "reflection": "one call per type of product", "max_paragraphs_per_type": prec.MAX_PARAGRAPHS,
                         "conclusion": "what the Commission decided and what it left open, each only as a passage quoted "
                                       "word for word from a paragraph sent (checked in code); otherwise taken in code "
                                       "from the same market in another search of the same activity",
                         "query_forms": list(prec.QUERY_FORMS), "hits_per_form": prec.HITS_PER_FORM,
                         "unit": "one search per target activity"},
            "searches": snap["precedents"], "rows": snap["precedent_rows"]}
    if snap.get("loaded_from"):
        log["loaded_from_saved_audit"] = snap["loaded_from"]
        log["call_log_before_loading"] = snap["loaded_calls"]
    return json.dumps(log, ensure_ascii=False, indent=1, default=str)


# =============================================================== development sidebar
def deployment_check(ai):
    """Deployment test: one AI call, ChromaDB on this machine, and one hybrid search."""
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
    try:                                      # can the server open public pages and read PDFs?
        import pypdf
        t = time.time()
        page = am.source_check.fetch("https://example.com/")
        ok = page["state"] in ("readable", "no text")
        rows.append(("Source check", "✔" if ok else "✖",
                     f"{'on' if am.source_check.CHECK_SOURCES else 'OFF (CHECK_SOURCES=0)'} · test page "
                     f"{'opened' if ok else 'not opened: ' + page['reason']} in {time.time() - t:.1f} s · "
                     f"pypdf {pypdf.__version__}"))
    except Exception as e:  # noqa: BLE001
        rows.append(("Source check", "✖", f"{type(e).__name__}: {e}"))
    return rows


def legend_html(step):
    """The legend: only what the current step needs, one short line each; the full explanation on hover."""
    def line(mark, text, tip):
        return f"<div class='lg' title='{h(tip)}'>{mark} <span class='sub2'>{text}</span></div>"
    src = (line("<span class='src'>[4]</span>✔", "checked: the quotation is on the page",
                "Hover over a number for the quotation and where it comes from (company website or other public "
                "source); click to open the page, a PDF at the right page. ✔ the app found the quotation on the page "
                "word for word: can be relied on.")
           + line("<span class='src'>[4]</span>≈", "probably right: worth a quick look",
                  "The wording is not on the page word for word, but its figures and names are (reworded by the "
                  "search), or the quotation is the search's translation of a page in another language; or, for a page "
                  "cited without a quotation, the page names the activity's products or brands.")
           + line("<span class='src'>[4]</span>○", "not checked: check yourself if the row matters",
                  "The app could not check this page (the site refused its automatic visit, or the page shows almost "
                  "no text), or the search cited it without a quotation. This says nothing about the source itself; "
                  "the page usually opens normally in your browser.")
           + line("<span class='src'>[4]</span>⚠", "check before relying on it",
                  "Neither the wording of the quotation nor its figures or names are on the page."))
    labels = (line("<span class='lab lab-h'>Horizontal</span>", "same or similar products",
                   "Potential horizontal overlap: both companies offer the same or similar products (potential "
                   "competitors). “Potential” until checked against the Commission's market definitions in step ④.")
              + line("<span class='lab lab-v'>Vertical</span>", "one could supply the other",
                     "Potential vertical relationship: one company's products could be an input for the other, or could "
                     "be resold by it. The arrow points from supplier to customer.")
              + line("<span class='lab lab-off'>Struck</span>", "dismissed · <i>added</i> · <i>edited</i> by you",
                     "A label you dismissed is struck through; a label you added and a wording you changed are marked. "
                     "“Your view” next to each label: to check, likely, unlikely, ask the company, or dismiss."))
    dots = line("●●○", "direct customers (hover over the dots)",
                "●●● the same, ●●○ partly the same, ●○○ different direct customers. Compares only who each company sells "
                "to directly (e.g. shops, other manufacturers, consumers), not the products. Different customers alone "
                "do not rule out an overlap: customers form a separate market only if the seller can tell which group "
                "a customer belongs to at the time of sale, customers cannot resell to each other, and the different "
                "treatment is lasting (Market Definition Notice (88)).")
    rel = line("<span class='lab lab-q'>Existing relationship</span>", "found by the app's code, not by the AI",
               "Each company was researched on its own, in searches that never named the other companies or the "
               "planned deal. Afterwards, the app's code looked through each company's research for the names of the "
               "other companies in this screen. It only finds names: what the relationship is (supply, distribution, "
               "partnership, equity) is for you to check.")
    if step <= 2:
        return src
    if step == 3:
        return labels + dots + rel + src
    return ("".join(line(outcome_chip(o), w, OUTCOME_TIP[o]) for o, w in (
        ("Confirmed", "same market"), ("Possible", "depends on the product format"),
        ("Not excluded", "definition left open"), ("Not supported", "separate markets"),
        ("No precedent", "for the lawyer"), ("Markets defined", "vertical: both sides")))
        + line("<i>(or Tablets)</i>", "could be in either market",
               "The product could fall in either market; which one is for you to check.")
        + labels)


def sidebar_panel(ai, step):
    """The sidebar for everyone: the key, the actions for this screen, the legend and the run summary;
    the development tools collapsed at the end, in development only."""
    with st.sidebar:
        st.markdown("**This screen**")
        if ss.get("companies") and step > 1:
            n = len(ss.companies) - 1
            st.caption(f"{esc(ss.companies[0]['name'])} and {plural(n, 'portfolio company', 'portfolio companies')}")
        if st.button("Start over", width="stretch", help="Discard this screen and start again"):
            confirm_reset(audit_snapshot(ai) if ss.get("mapped") else None)
        if ss.get("mapped"):
            snap = audit_snapshot(ai)
            st.download_button("Save progress", data=lambda: audit_json(snap), mime="application/json",
                               on_click="ignore", width="stretch",
                               file_name=f"overlap_audit_{datetime.now():%Y%m%d-%H%M}.json",
                               help="Downloads everything so far as a file (.json), with your dismissals, notes and "
                                    "edits; it is also the audit log. The app stores nothing: open the file again "
                                    "with “Open saved progress”.")
        if ss.get("results") is not None and ss.get("precedents"):
            model = report_model()
            st.download_button("Download the Word document", data=lambda: export.docx_bytes(model),
                               file_name=word_name(), on_click="ignore", width="stretch",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               help="The preliminary overlap overview as a Word document: your final choices in the "
                                    "main part, how the tool prepared it in the Annex.")
        with st.expander("Open saved progress"):
            loader_box()
        if step >= 2:
            with st.expander("Legend", expanded=True):       # open in every step
                st.markdown(legend_html(step), unsafe_allow_html=True)
        if step >= 4 and ss.get("precedents"):
            decisions = decisions_html()
            if decisions:
                with st.expander("Commission decisions", expanded=True):
                    st.caption("The decisions used in this screen; hover for the markets, click to open the decision.")
                    st.markdown(decisions, unsafe_allow_html=True)
        if ss.get("stage_logs") or ss.get("loaded_from"):
            with st.expander("About this run"):
                st.caption(run_summary())
        if DEV_MODE:
            dev_sidebar(ai)


def dev_sidebar(ai):
    with st.expander("Developer"):
        st.caption(f"**DEV_MODE** · profile **{PROFILE}** · cache {'on' if USE_CACHE else 'off'}")
        for name, label in (("mapping", "Step ②"), ("confirm", "Step ③"), ("precedents", "Step ④")):
            if name in ss.stage_logs:
                st.caption(f"{label}: {stage_cost(name)}")
        s = ss.log.summary()
        st.metric("Session cost (USD, tokens and web searches)", f"{s['cost']:.4f}")
        st.caption(f"{call_count(ss.log.calls)} ({s['cached']} from cache) · {s['web_searches']} web searches "
                   f"(USD {s['search_fees']:.4f} in search fees at USD {ai_client.WEB_SEARCH_FEE:g} per call) · "
                   f"prices: {ai_client.PRICES_CHECKED}")
        if s["steps"]:
            st.dataframe(pd.DataFrame([{"Step": k, "Calls": v["calls"], "Cached": v["cached"],
                                        "USD": round(v["cost"], 4)} for k, v in s["steps"].items()]),
                         hide_index=True)
        st.markdown("**Models per step**")      # no expanders inside an expander (Streamlit)
        st.dataframe(pd.DataFrame([{"Step": k, "Model": v, "Effort": ai.effort(k)} for k, v in ai.models.items()]
                                  + [{"Step": "embed", "Model": ai_client.EMBED_MODEL, "Effort": ""}]),
                     hide_index=True)
        st.markdown("**Deployment check**")
        st.caption("One AI call, the ChromaDB index and one hybrid search (about USD 0.0001).")
        if st.button("Run the check"):
            ss.deploy_check = deployment_check(ai)
        for what, mark, detail in ss.get("deploy_check", []):
            st.markdown(f"{mark} **{what}**: {detail}")


# =============================================================== page
# The landing page explains the tool in steps, as a vertical timeline. The same block is shown under "How this tool
# works" on the later steps.
INTRO_STEPS = [
    ("Companies", "Enter the company to be bought (the target) and the companies the buyer already owns (the portfolio "
                  "companies)."),
    ("Activities", "The tool researches each company on public websites, or reads a description you provide. You check "
                   "and correct what it found."),
    ("Preliminary assessment", "It compares every activity of the target with every activity of each portfolio "
                               "company. The AI sees descriptions only, never company names; relationships between "
                               "the companies are found by the code, never by asking the AI about two companies "
                               "together."),
    ("Market definitions", "It checks how the European Commission defined the markets of these products in its past "
                           "decisions, and what follows for each row."),
]


def intro_html():
    steps = "".join(
        f"<div class='tl-step'>{'<div class=tl-line></div>' if k < len(INTRO_STEPS) else ''}"
        f"<span class='tl-num'>{k}</span><div><div class='tl-title'>{h(title)}</div>"
        f"<div class='sub2'>{h(text)}</div></div></div>"
        for k, (title, text) in enumerate(INTRO_STEPS, start=1))
    return (f"<div class='tl-lead'>A preliminary overlap screen for EU merger control: is the company to be bought "
            f"(the <i>target</i>) active in the same or related markets as the companies the buyer already owns (the "
            f"<i>portfolio companies</i>)?</div>"
            f"<div class='tl'>{steps}</div>"
            "<div style='margin-top:.8rem'><span class='lab lab-h'>Horizontal</span> <span class='sub2'>both offer the "
            "same or similar products</span> &nbsp;&nbsp; <span class='lab lab-v'>Vertical</span> <span class='sub2'>"
            "one could supply the other</span></div>"
            "<div class='tl-note sub2'>A working document for a lawyer to verify, not a legal conclusion. Product "
            "markets only: geography and market shares are not assessed.</div>")


STEPS = {1: "Companies", 2: "Activities", 3: "Preliminary assessment", 4: "Market definitions", 5: "Summary"}
SCROLL_TOP = """<script>
const d = window.parent.document;
for (const s of ['[data-testid="stMain"]', 'section.stMain', 'section.main', '[data-testid="stAppViewContainer"]']) {
  const e = d.querySelector(s); if (e) { e.scrollTo({top: 0}); }
}
window.parent.scrollTo(0, 0);
</script>"""


def scroll_to_top_on_new_step(step):
    """Streamlit keeps the scroll position when the screen changes, so a new step would open in the middle of the
    page. A small script jumps to the top once per change of step."""
    slot = st.empty()          # always one element here, so that everything below keeps its position
    if ss.get("_shown_step") != step:
        ss._shown_step = step
        if ss.get("guide_open") != step:      # a guide opened on its first visit stays open for that visit only
            ss.guide_open = None
        with slot:
            st.iframe(SCROLL_TOP, height=1)      # our own constant script, never user input


def progress_nav(step):
    """The steps as tabs (plain words, the current step underlined in ink, steps not reached yet pale). Every step
    already reached can be opened again; nothing is deleted by going back."""
    reachable = {1: True, 2: bool(ss.get("acts")), 3: ss.get("results") is not None,
                 4: ss.get("results") is not None and bool(ss.get("precedents")),
                 5: ss.get("results") is not None and bool(ss.get("precedents"))}
    with st.container(horizontal=True, key="stepnav", gap="large"):
        for k, name in STEPS.items():
            st.button(f"{k} {name}", key=f"nav_{k}", type="primary" if k == step else "secondary",
                      disabled=not reachable[k], on_click=go_to, args=(k,))


st.title("EU Overlap Screen")
api_key = credentials()        # the first screen until the password (or key) is entered
step = ss.get("step", 1)
# The start page: the explanation in steps on a page of its own (step ① shows only the companies). Shown once per
# session, before anything is entered; a saved screen that is opened skips it, and
# "Start over" leads straight to step ①.
if not ss.get("started") and step == 1 and not ss.get("companies"):
    st.markdown(intro_html(), unsafe_allow_html=True)
    if st.button("Start", type="primary"):
        ss.started = True
        st.rerun()
    with st.sidebar:
        with st.expander("Open saved progress"):
            loader_box()
    st.stop()
with st.expander("How this tool works"):
    st.markdown(intro_html(), unsafe_allow_html=True)
ai = make_ai(api_key)
if step == 2 and not ss.get("acts"):
    step = ss.step = 1
if step in (3, 4, 5) and ss.get("results") is None:
    step = ss.step = 2 if ss.get("acts") else 1
if step in (4, 5) and not ss.get("precedents"):
    step = ss.step = 3
scroll_to_top_on_new_step(step)
progress_nav(step)
sidebar_panel(ai, step)
# Two slots: the working screen and the page. During long work the page slot is set to empty, which removes
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
        elif step == 5:
            stage_summary(ai)
        else:
            stage_overview(ai, step)