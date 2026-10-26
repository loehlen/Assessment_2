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
With DEV_MODE off (the submitted version) the user enters their own OpenAI key in the course's API Credentials sidebar
module (api_key.py); it is kept for the session only.
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
from zoneinfo import ZoneInfo

import openai
import pandas as pd
import streamlit as st

import activity_mapping as am
import ai_client
import api_key
import comparison as cmp
import examples
import export
import precedents as prec
import rules

st.set_page_config(page_title="EU Overlap Screen", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")

# =============================================================== visual design
# The theme (colours, fonts) is in .streamlit/config.toml. Here: the few things the theme cannot reach, in one place:
# the flat labels, the Commission line, the step tabs, the row rules and the hover boxes. Colours carry meaning only:
# red = potential horizontal overlap, yellow = potential vertical relationship; in step ④ the result of the
# Commission's view, as rounded chips (the labels of step ③ are square): the colour of the relationship it belongs to,
# filled only where the decisions back the overlap itself (Confirmed); red outline = possible / not excluded; yellow
# outline = a vertical row's markets (a definition identifies the markets, not the supply); green = not supported;
# grey outline = no precedent. Neutral bands (an unclear row, a rewritten line, a decision entry) are sand.
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
.dots{cursor:help;border-bottom:1px dotted #8A857C;padding-bottom:.1rem}
.dts{display:inline-flex;gap:.13em;align-items:center;vertical-align:.1em}
.dts + .dts{margin-left:.45em}
.dts i{display:inline-block;width:.46em;height:.46em;border-radius:50%;border:1.2px solid currentColor;
 box-sizing:border-box}
.dts i.on{background:currentColor}
.src{text-decoration:none;font-size:.85em;color:#3A5A80}
.cline{background:#F2EFE8;color:#3D3A35;border-left:3px solid #C9C2B4;padding:.4rem .8rem;margin:.35rem 0 .2rem 0;
 line-height:1.55;border-radius:0}
.cline .ed{color:#55514A;font-style:italic;font-size:.8rem}
.cline.o-conf{background:#DCE6F2;border-left-color:#2E5A88;color:#1F3F66}
.cline.o-open{background:#ECEAE5;border-left-color:#8A857C;color:#3D3A35}
.cline.o-nosup{background:#E3EDE4;border-left-color:#5E8A66;color:#2F5D3A}
.cline.o-nopre{background:#EAE7F0;border-left-color:#7F7898;color:#4A4361}
.oc{display:inline-block;font-size:.75rem;font-weight:600;padding:0 .5rem;border-radius:10px;margin:0 .3rem;
 white-space:nowrap;border:1px solid transparent;line-height:1.5}
.oc.o-conf{background:#FDECEA;color:#8A1C12;border-color:#FDECEA}
.oc.o-open{background:transparent;color:#8A1C12;border-color:#E7A9A2}
.oc.o-vert{background:transparent;color:#6E4B00;border-color:#E6C66E}
.oc.o-nosup{background:#E3EDE4;color:#2F5D3A;border-color:#E3EDE4}
.oc.o-nopre{background:transparent;color:#55514A;border-color:#BDB7AC}
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
[data-testid="stSidebar"]{min-width:20.5rem;max-width:20.5rem}
.lgg{font-size:.86rem;line-height:1.45;display:grid;grid-template-columns:fit-content(8.2rem) 1fr;column-gap:.5rem;
 row-gap:.3rem;align-items:baseline}
.lgg .oc,.lgg .lab{font-size:.72rem;padding:0 .4rem}
.lgl{display:contents}
.lgl>span{cursor:help}
.lgm .lab,.lgm .oc{margin:0;white-space:nowrap}
.lgm .lab.lab-q{white-space:normal}
.lgh{grid-column:1/-1;font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.92rem;
 margin:.45rem 0 0 0}
.lgh:first-child{margin-top:0}
.lp-title{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:2.3rem;line-height:1.2;color:#22313F;
 margin:0 0 .9rem 0}
.lp-lead{font-size:1.2rem;line-height:1.5;color:#3D3A35;margin:0 0 1.6rem 0}
.lp-lead,.lp-why p,.lp-item>div{text-align:justify;hyphens:auto;-webkit-hyphens:auto}
.lp-lead{hyphens:manual;-webkit-hyphens:manual}
.lp-split{display:flex;flex-wrap:wrap;gap:2.8rem;align-items:flex-start;margin:.4rem 0 2.4rem 0}
.lp-main{flex:3 1 28rem;min-width:0}
.lp-h2{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.35rem;margin:0 0 .7rem 0;color:#22313F}
.lp-why p{margin:0 0 .75rem 0;color:#3D3A35;line-height:1.6}
.lp-why b{color:#1F1D1A}
.lp-panel{flex:2 1 22rem;min-width:0;background:#F2EFE8;border-radius:8px;padding:1.6rem 1.7rem .6rem 1.7rem}
.lp-item{display:flex;gap:.85rem;align-items:flex-start;margin:0 0 1rem 0;line-height:1.55}
.lp-item svg{flex:none;margin-top:.15rem}
.lp-item span{color:#3D3A35}
.lp-steps-sec{border-top:1px solid #E2DDD2;padding-top:1.9rem;margin-bottom:2.4rem}
.lp-steps{list-style:none;margin:1.7rem 0 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));
 gap:1.7rem 1.5rem}
.lp-steps li{border-top:2px solid #E2DDD2;display:flex;flex-direction:column;gap:.45rem;margin:0;padding:0}
.lp-num{display:inline-flex;align-items:center;justify-content:center;width:1.9rem;height:1.9rem;margin-top:-1rem;
 border-radius:50%;background:#22313F;color:#fff;font-size:.88rem;font-weight:600}
.lp-st{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.12rem}
.lp-sx{font-size:.9rem;color:#3D3A35}
.lp-foot{font-size:.82rem;color:#55514A;border-top:1px solid #E2DDD2;padding-top:1rem;margin-top:1.8rem}
.st-key-ctaband{background:#22313F;border-radius:8px;padding:1.9rem 2.3rem}
.lp-cta-t{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.75rem;line-height:1.2;color:#fff;
 margin:0 0 .3rem 0}
.lp-cta-x{color:#D9DEE4;font-size:1rem}
.st-key-cta_start button{background:#fff !important;color:#22313F !important;border:1px solid #fff !important;
 min-height:3.2rem;padding:0 1.8rem}
.st-key-cta_start button p{font-weight:700;font-size:1.05rem;color:#22313F !important}
.st-key-ctaband [data-testid="stPopover"] button{background:transparent !important;border:1px solid #8C9AAA !important;
 min-height:3.2rem}
.st-key-ctaband [data-testid="stPopover"] button p,.st-key-ctaband [data-testid="stPopover"] button svg{color:#fff !important}
.chip{display:inline-block;font-size:.76rem;padding:.02rem .5rem;border-radius:10px;background:#ECEAE5;color:#4A463F;
 margin:0 .2rem;white-space:nowrap}
.k{display:inline-block;min-width:6.8rem;color:#55514A;font-size:.85rem}
.act>div{margin:.1rem 0;line-height:1.6}
.fld{display:flex;align-items:baseline}
.fld .k{flex:none;width:6.8rem;min-width:6.8rem;padding-right:.4rem}
.fld .v{flex:1;min-width:0}
.prof{background:#F2EFE8;border-radius:6px;padding:.55rem .8rem;margin:.2rem 0 .7rem 0;line-height:1.6}
.sec{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.65rem;line-height:1.25;color:#22313F;
 margin:.8rem 0 .1rem 0}
.sec.next{margin-top:2.2rem;border-top:2px solid #22313F;padding-top:.9rem}
.secsub{color:#55514A;font-size:.9rem;margin:0 0 .6rem 0}
.gate-space{height:16vh}
.gate-title{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:2.3rem;line-height:1.2;color:#22313F;
 text-align:center;margin-bottom:.3rem}
.gate-lead{font-size:1.05rem;text-align:center;color:#3D3A35;margin-bottom:1.4rem}
.gate-key{text-align:center;line-height:1.6;border:1px solid #E2DDD2;border-radius:6px;padding:.9rem 1.1rem}
.gate-key span{display:block;margin-top:.4rem;font-size:.88rem;color:#55514A}
.basis{color:#6E6A63}
.sumt{border-collapse:collapse;width:100%;margin:.4rem 0 .3rem 0}
.sumt th{background:#22313F;color:#fff;text-align:left;padding:.45rem .7rem;font-weight:600}
.sumt th .lab{margin:0}
.sumt td{border-bottom:1px solid #C9C2B4;padding:.5rem .7rem;vertical-align:top}
.sumul{margin:0;padding-left:1.1rem}.sumul li{margin:.15rem 0}
[class*="st-key-thead"]{background:#22313F;border-radius:4px;padding:.5rem .7rem .05rem .7rem;margin-top:.3rem}
[class*="st-key-thead"] p{color:#FFFFFF !important;font-weight:600}
[class*="st-key-thead"] [data-testid="stTooltipIcon"],[class*="st-key-thead"] [data-testid="stTooltipIcon"] *{
 color:#FFFFFF !important;opacity:1 !important;filter:none !important}
[class*="st-key-thead"] [data-testid="stTooltipIcon"] svg,[class*="st-key-thead"] [data-testid="stTooltipIcon"] svg *{
 stroke:#FFFFFF !important}
[class*="st-key-pfrow"]{border-bottom:1px solid #E2DDD2;padding:.4rem 0 .45rem 0;gap:.4rem}
.st-key-thead_pf{margin-bottom:-.6rem;padding:.55rem 0 !important}
.st-key-thead_pf p{font-size:.875rem;font-weight:400;margin:0 !important;line-height:1.4}
.st-key-thead_pf [data-testid="stMarkdownContainer"],.st-key-thead_pf [data-testid="stMarkdown"]{margin:0 !important}
.st-key-thead_pf [data-testid="stMarkdownContainer"]>div{margin:0 !important}
.st-key-thead_pf strong{font-weight:600}
.st-key-thead_pf [data-testid="stColumn"]{padding-left:.75rem}
.st-key-thead_pf [data-testid="stColumn"]:nth-child(4){padding-left:.5rem}
.wr{display:block;margin:.05rem 0 0 0}
.aext{margin-top:.5rem}
.guide{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:.1rem 0 .2rem 0}
.guide>div{padding:0 1.1rem;border-left:1px solid #E2DDD2}
.guide>div:first-child{padding-left:0;border-left:none}
.guide>div:last-child{padding-right:0}
.guide .gh{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.1rem;color:#22313F;margin:0 0 .35rem 0}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,[data-testid="stMain"] h4{color:#22313F}
.guide ul{margin:0;padding-left:1.1rem}
.guide li{margin:.25rem 0;line-height:1.5;font-size:.93rem}
.guide .lab{margin:0 .15rem 0 0}
@media (max-width:900px){.guide{grid-template-columns:1fr;gap:.8rem}.guide>div{border-left:none;padding:0}}
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
ss.setdefault("acts_version", 0)              # a new version = fresh widgets for the activity lists in step ②


# =============================================================== credentials
def key_problem(key):
    """Asks OpenAI whether it accepts the key (listing the models costs nothing). Only a rejected key is refused: if
    OpenAI cannot be reached just now, the key is accepted and a real problem shows at the first AI call."""
    try:
        ai_client.client_factory(key, 20).models.list()
    except openai.AuthenticationError:
        return "OpenAI did not accept this key. Check it and click “Update API Key” again."
    except Exception:  # noqa: BLE001 - network or service problem: not a reason to refuse the key
        return None
    return None


def gate_page(lead_html):
    """The first screen on its own, in the middle of the page: a narrow centred column, pushed down from the top."""
    st.markdown("<div class='gate-space'></div>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.3, 1])
    mid.markdown("<div class='gate-title'>EU Overlap Screen</div>"
                 f"<div class='gate-lead'>A preliminary overlap screen for EU merger control.</div>{lead_html}",
                 unsafe_allow_html=True)
    return mid


def credentials():
    """The OpenAI key for this session.
    Submitted version (DEV_MODE off): the user's own key, entered in the course's API Credentials sidebar module
    (api_key.py); until then the page only says where to enter it. Afterwards the module stays at the end of the
    sidebar, folded, so the key can be changed.
    Development: an app password on the first screen, then the developer's key from .env or Secrets.
    The key is kept for the session only (never stored)."""
    if not DEV_MODE:
        if ss.get("openai_api_key"):
            return ss.openai_api_key
        if api_key.api_key_input(check=key_problem):          # entered just now: start with the module folded
            st.rerun()
        gate_page("<div class='gate-key'>To start, enter your OpenAI API key in the sidebar under <b>API Key "
                  "Input</b> and click <b>Update API Key</b>.<br><span>The key is used only for the calls of this "
                  "session and is not stored. A screen of one of the examples costs about USD 0.50–1 in API fees. "
                  "On a small screen, open the sidebar with the arrow at the top left.</span></div>")
        st.stop()
    if ss.get("auth_key"):
        return ss.auth_key
    expected, server_key = ai_client.setting("APP_PASSWORD"), ai_client.setting("OPENAI_API_KEY")
    if not expected:
        st.error("APP_PASSWORD is not set in .env or Secrets.")
        st.stop()
    if not server_key:
        st.error("OPENAI_API_KEY is not set in .env or Secrets.")
        st.stop()
    mid = gate_page("")
    with mid:
        value = st.text_input("App password", type="password", key="gate_input")
        st.button("Continue", type="primary", width="stretch")       # Enter in the field does the same
    if value:
        if value != expected:
            mid.error("This password is not correct.")
            st.stop()
        ss.auth_key = server_key
        st.rerun()
    st.stop()


def key_sidebar():
    """After the key is entered: the course module at the end of the sidebar, folded (submitted version only)."""
    if not DEV_MODE:
        old = ss.get("openai_api_key")
        with st.sidebar.expander("API Key Input"):
            new = api_key.api_key_input(check=key_problem, box=st.container(), title=False)
        if new != old:
            st.rerun()


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


def now_local():
    """The date and time where the user is (the browser's time zone), not the server's: Streamlit Cloud runs on UTC,
    so in Australia a document made before 11 am would otherwise carry the previous day's date."""
    try:
        tz = st.context.timezone
        if tz:
            return datetime.now(ZoneInfo(tz)).replace(tzinfo=None)
    except Exception:  # noqa: BLE001 - no browser time zone (e.g. a test run): the server's time
        pass
    return datetime.now()


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
            self.dev = st.expander("Developer Details") if DEV_MODE else None

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
KEEP_ON_RESET = {"log", "auth_key", "openai_api_key", api_key.FIELD, "deploy_check", "started"}


def reset_all():
    """Discards everything of the current screen; keeps the key or password and, in development, the cost counter.
    The call log continues, but the audit log of the next screen starts here."""
    for k in list(ss.keys()):
        if k not in KEEP_ON_RESET:
            del ss[k]
    ss.run_first = ss.log.mark()


@st.dialog("Start Over?")
def confirm_reset(snap):
    st.write("This discards the companies, activities and results of the current screen.")
    if snap is not None:
        model, note = progress_model()
        st.download_button("Save progress first (Word)", data=lambda: progress_bytes(snap, model, note),
                           mime=DOCX_MIME, on_click="ignore", file_name=progress_name())
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
OTHER_NAME = "Side lines and own use"      # the merged line of files saved before side lines were split off
OWN_USE_NAME = "Own use"
SIDE_LINE_TIP = ("A side line: sold to third parties alongside the main business (e.g. a café, merchandise, sales to "
                 "businesses). Compared like every other activity.")


def other_name(a):
    """The name of the merged line: "Own use" (production for the group itself), or, in files saved before side lines
    became activities of their own, "Side lines and own use"."""
    items = [i for i in a.get("includes") or [] if i]
    return OWN_USE_NAME if a.get("own_use") or (items and all(rules.OWN_USE_MARK in i for i in items)) else OTHER_NAME


def side_tag(a):
    return f" <span class='tag' title='{h(SIDE_LINE_TIP)}'>side line</span>" if a.get("side_line") else ""


def stage_of(a):
    if rules.category(a) == "other":
        return "Own use" if rules.captive_only(a) else "Mixed"
    return STAGE.get(a.get("value_chain_level"), "Other")


def stage_text(a):
    """The stage as plain grey text (no highlight)."""
    return f":gray[{stage_of(a)}]"


def research_of(company):
    """The research whose numbered sources the activities on screen refer to. Steps ③–⑤ show the activities as they
    were compared, so their source numbers belong to the research the comparison was made on (a company mapped again
    since keeps its earlier sources there until the comparison is updated); steps ① and ② show the current research."""
    if (ss.get("step") or 1) >= 3:
        saved = (ss.get("compared_research") or {}).get(company)
        if saved is not None:
            return saved
    return ((ss.get("mapped") or {}).get(company) or {}).get("search") or {}


def source_index(company):
    return {s["n"]: s for s in research_of(company).get("sources") or []}


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
# on and where a check is worth it. ✔ checked · ≈ probably right, worth a quick look · ○ read by the search only · ⚠
# check before relying on it. The search reads pages through the AI provider's own access; the app's check is a second,
# separate visit, which some sites refuse: ○ says nothing about the source itself ("not checked" would sound as if nobody
# had looked at the page).
TRUST_HEAD = {"found": "✔ Checked: the quotation is on the page",
              "close": "≈ Probably right: worth a quick look",
              "not found": "⚠ Check before relying on it",
              "not checked": "○ Read by the search only",
              "no quote": "○ Read by the search only"}
NOT_CHECKED_WHY = {
    "blocked": "The search read this page and the activity is based on it, but the app could not open the page itself "
               "to confirm the quotation ({reason}).",
    "no text": "The search read this page and the activity is based on it, but the page shows the app almost no text "
               "(probably built by JavaScript), so the app could not confirm the quotation.",
    "error": "The search read this page and the activity is based on it, but the app could not open the page itself to "
             "confirm the quotation ({reason}).",
    "off": "The search read this page and the activity is based on it; the app's own check is switched off.",
}
NOT_CHECKED_END = " This says nothing about the source; open the link if the row matters."


def check_result(c):
    """The result as shown, also for progress files saved by earlier versions of the check. A result without
    "substance_on_page" comes from the check of the wording only, which knew no "close": a quotation whose words are
    mostly on the page is shown as ≈ (the figure check needs the page text, which a saved file does not keep). A
    "translation" without "same_language" was judged by the share of its words alone, without checking the page's
    language; that is no evidence of a translation, so it is shown as ⚠, with the possibility in the hover."""
    r = (c or {}).get("result", "")
    if r == "close" and c.get("basis") == "translation" and "same_language" not in c:
        return "not found"
    if r == "not found" and "substance_on_page" not in c and (c.get("words_on_page") or 0) >= \
            am.source_check.WORDING_SHARE:
        return "close"
    return r


def source_tip(s, c, kind_text):
    tip = f"{display_title(s)}\n{am.site_of(s.get('url'))} · {kind_text}"
    if s.get("origin") == "text link":
        tip += "\nLink written by the AI in its notes (not a search citation)"
    if not c:
        return (tip + f"\n\n{TRUST_HEAD['not checked']}\nThe app's own check did not run (source check off, or an older "
                      "saved file)." + NOT_CHECKED_END)
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
            "The wording is not on the page word for word, but most of its words are: probably reworded by the search")
        return tip + f"\n\n{TRUST_HEAD['close']}\n{why}.\nQuotation given by the search:\n“{quote}”"
    if r == "not found":
        if "same_language" in c:            # the current check: the reason says what was and was not found
            what = reason[:1].upper() + reason[1:] if reason else "The quotation is not on the page"
        elif c.get("translated") or c.get("basis") == "translation":
            # an earlier check: few of its words on the page, the page's language not checked
            what = ("The wording is not on the page, and few of its words are: either the page is in another language "
                    "and the quotation the search's translation, or the quotation is not on the page")
        elif "substance_on_page" in c:      # an earlier check (its reason said "neither ... nor" even when some were found)
            keys = c.get("keys_found") or []
            if keys and not reason.startswith("only the first"):
                what = f"The wording is not on the page, and only some of its figures and names are ({', '.join(keys[:4])})"
            else:
                what = reason[:1].upper() + reason[1:] if reason else "The quotation is not on the page"
        else:                               # the check of the wording only: claim no more
            what = "The wording was not found on the page"
        return (tip + f"\n\n{TRUST_HEAD['not found']}\n{what.rstrip('.')}{page}"
                + f".\nQuotation given by the search:\n“{quote}”\n\nOpen the page and check.")
    if r == "no quote":
        return (tip + f"\n\n{TRUST_HEAD['no quote']}\nThe search read this page and cited it without quoting it, so "
                "the app had nothing to confirm." + NOT_CHECKED_END)
    why = NOT_CHECKED_WHY.get((s.get("check") or {}).get("state"),
                              "The search read this page, but the app could not confirm the quotation ({reason}).")
    return (tip + f"\n\n{TRUST_HEAD['not checked']}\n" + why.format(reason=reason or "no reason given")
            + NOT_CHECKED_END
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
                r_ = check_result(c)
                tip += ("\n\n✔ Passage found in your description:" if r_ == "found" else
                        "\n\n≈ Passage not word for word in your description, but its substance is (probably "
                        "reworded by the extraction):" if r_ == "close" else
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
    """'Try an example' (button callback): fills in one of the examples (examples.py). The run itself is live."""
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
        st.caption(f"One row per company, up to {MAX_PORTCOS}.")
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
                    st.text_area(f"Description of {name}'s activities", key=pf_key("desc", i), height=110,
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
               f"in {name}'s own research call, so the AI would see both names together. Change the text, or send it "
               "anyway if the sentence reveals nothing confidential.")


def typed_text_warnings(companies):
    for c in companies:
        found = typed_names(c, companies)
        if found:
            typed_warning(c["name"], found)
            st.checkbox(SEND_ANYWAY, key=send_key(c["name"], found))


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
    st.header("① Companies")
    st.markdown("Enter the company to be bought (the *target*) and the companies the buyer already owns (the "
                "*portfolio companies*). Each portfolio company is looked at together with its subsidiaries and brands. "
                "For the target, enter only the business being sold, for example a division rather than the seller's "
                "whole group.")
    restore_inputs()
    example_buttons()
    target_card()
    portfolio_card()
    typed_text_warnings(read_companies()[0])
    st.caption("Each company is researched separately; the AI never sees two company names together. With web search "
               "this takes about one to four minutes.")
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
        return f"<div class='fld'><span class='k'>{label}</span><span class='v'>{value}</span></div>"

    def block(lines):              # one block per line: a long value wraps under itself, not under its label
        return "<div class='act'>" + "".join(x if x.startswith("<div") else f"<div>{x}</div>" for x in lines) + "</div>"
    if a.get("excluded") and a.get("own_use"):       # listed, not compared (the lawyer can include it with "Edit")
        items = [i.replace(" " + rules.OWN_USE_MARK, "") for i in a.get("includes") or [] if i]
        return block([f"<b>{OWN_USE_NAME}</b> {stage} {markers}",
                      field("Includes", "; ".join(item_html(i) for i in items[:6]) + more_items(items, 6)),
                      field("Not compared", "produced for the group itself, not offered on the market; use “Edit” "
                                            "to include it")])
    if a.get("excluded"):
        return block([f"<s><b>{he(capital(a['product']))}</b></s> {stage} {markers}",
                      field("Not relevant", f"<i>{he(a.get('exclusion_reason', ''))}</i> (excluded by you)")])
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
        return block(lines)
    includes = [i for i in a.get("includes") or [] if i]
    if rules.category(a) == "other":
        # every item in full, the text in brackets in the secondary colour (it often says what the item is)
        return block([f"<b>{other_name(a)}</b> {stage} {markers}",
                      field("Includes", "; ".join(item_html(i) for i in includes[:6]) + more_items(includes, 6))])
    first = f"<b>{he(capital(a['product']))}</b> {stage}{side_tag(a)}"
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
    return block(lines)


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
    """Business areas first, then side lines, then the merged line, then what is not compared (indices)."""
    main = [i for i, a in enumerate(acts) if not a.get("excluded") and rules.category(a) == "main"]
    main = [i for i in main if not acts[i].get("side_line")] + [i for i in main if acts[i].get("side_line")]
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
                        "companies the buyer already owns, each with its subsidiaries and brands</div>",
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


SOURCE_STATE = {
    "readable": "read",
    "blocked": "○ read by the search only (the app could not open it)",
    "no text": "○ read by the search only (the app could not read it)",
    "error": "○ read by the search only (the app could not open it)",
    "off": "○ read by the search only (source check off)",
}


def sources_list(found):
    """All sources of one company with the result of the check; links that no longer exist are listed apart, as
    'no longer available (cited by the search, not used)', and not as links."""
    check = found.get("source_check") or {}
    st.markdown(f"**Sources** · {found.get('model', '')} · accessed {found.get('date', '')}"
                + (f" · checked by the app on the same day ({check.get('seconds')} s)" if check.get("checked") else ""))
    # links that no longer exist were not used and are not listed (the progress file keeps them)
    live = [s for s in found["sources"] if not s.get("dead")]
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


def activities_hash(activities):
    """What the comparison depends on: the activities and the words the lawyer keeps in the descriptions."""
    # the fields that only record the lawyer's handling (e.g. saved unchanged in the edit form) are no change
    content = {c: [{k: v for k, v in a.items() if k not in rules.STATE_FIELDS} for a in acts]
               for c, acts in (activities or {}).items()}
    state = {"activities": content, "keep_words": sorted(ss.get("keep_words") or [])}
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
WIDTHS4 = [1.3, 1.3, 3.4, 2.65, 1.2, 0.95]
STEP3_INNER = [4.6, 1.9]           # the assessment column of step ③: the labels, your view
STEP4_INNER = [2.04, 2.65, 1.36]   # step ④: the labels, the Commission, your view (the sum of WIDTHS4[2:4])
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


def he_lines(text):
    """The lawyer's own wording (from "Edit") with its line breaks: each line escaped like he(), joined by <br> (he()
    alone turns line breaks into spaces)."""
    return "<br>".join(he(x) for x in str(text or "").splitlines() if x.strip())


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
        a = f"{target}'s {word_list(vitems.get('a')) or r['a']['product']}"
        b = f"{portco}'s {word_list(vitems.get('b')) or r['b']['product']}"
    return {
        "A could be an input for B": f"{a} could be an input for {b}",
        "B could be an input for A": f"{b} could be an input for {a}",
        "A could be resold by B": f"{a} could be resold through {b}",
        "B could be resold by A": f"{b} could be resold through {a}",
    }.get(link, link)


def dots_html(score):
    """The customer score as three drawn circles (filled = shared customers), so that they have the same size in every
    font; the score itself stays "●●○" in the data and in the Word document."""
    return ("<span class='dts'>" + "".join(f"<i class='{'on' if ch == '●' else ''}'></i>" for ch in score)
            + "</span>")


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
    tag = " <span class='tag'>added by you</span>" if p["origin"] == "lawyer" else (
        " <span class='tag'>dismissed by you</span>" if p["off"] else
        " <span class='tag' title='Different levels of trade and not the same direct customers: often different "
        "markets, so a horizontal overlap is less likely; to be checked.'>less likely</span>" if less else "")
    return f"<span class='lab {cls}'>{LABEL_TEXT[p['kind']]}</span>{tag}"


def assessment_plain(r, target, portco):
    """The app's wording of a row as plain text: what the lawyer starts from in "Edit"."""
    lines = []
    for p in label_parts(r, target, portco):
        if not p["off"]:
            lines += [LABEL_TEXT[p["kind"]] + (" (added by you)" if p["origin"] == "lawyer" else "")]
            lines += ["  " + x for x in part_detail(p, r, target, portco, html_out=False)]
    return "\n".join(lines)


def assessment_cell(r, status, rv, target, portco, commission=False):
    """The preliminary assessment column: one line per label, each with its own "Your view" and, in step ④
    (commission=True), the Commission's part for that label beside it. The lawyer's wording, if any, replaces the
    app's lines under the labels."""
    pid = cmp.pair_id(r)
    o = ss.override_store.get(pid, {})
    parts = label_parts(r, target, portco)
    tool_parts = [p["part"] for p in parts if p["origin"] == "tool"]
    edited = (o.get("text_assessment") or "").strip()

    def line(html_text, part, kind, off=False, comm=""):
        if commission:          # step ④: the assessment, the Commission, then the lawyer's view (the lawyer last)
            c1, c3, c2 = st.columns(STEP4_INNER, vertical_alignment="top")
            if comm:
                c3.markdown(comm, unsafe_allow_html=True)
        else:
            c1, c2 = st.columns(STEP3_INNER, vertical_alignment="top")
        c1.markdown(html_text, unsafe_allow_html=True)
        safe = re.sub(r"\W", "", part)         # no backslash inside an f-string (Python before 3.12)
        key = f"view_{rv}_{pid}_{safe}"
        c2.selectbox("Your view", VIEWS, index=VIEWS.index(view_of(pid, part, off)), key=key,
                     format_func=lambda v: "Your view" if v == "To check" else v,
                     label_visibility="collapsed", on_change=_store_view, args=(pid, part, key, tool_parts, kind),
                     help="Your view of this relationship: used in the summary and the Word document. “Ask the "
                          "company” puts it into the open points; “Dismiss” removes it.")

    items = []                          # [text, part, kind, off], one line (with its own "Your view") each
    metas = []                          # the label of each line, for the Commission's parts (assign_commission)
    if status == "added back by user":
        items.append(["<span class='lab lab-q'>Added back by you</span> <span class='sub2'>the tool found no overlap; "
                      "see “Why?”</span>", "row", "row", False])
        metas.append({"kind": "row"})
    elif r["decision"]["status"] == "unclear":
        items.append(["<span class='lab lab-q'>Unclear: please check</span> <span class='sub2'>see “Why?”</span>",
                      "row", "row", bool(o.get("dismiss"))])
        metas.append({"kind": "row"})
    for p in parts:
        detail = [] if edited else part_detail(p, r, target, portco)
        items.append(["  \n".join([label_html(p, less=p["kind"] == "h" and p["origin"] == "tool"
                                               and weak_horizontal(r))] + detail),
                      p["part"], p["origin"], p["off"]])
        metas.append(p)
    comms = commission_htmls(r, target, portco, metas) if commission else [""] * len(items)
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
    for (text, part, kind, off), comm in zip(items, comms):
        line(text, part, kind, off=off, comm=comm)
    if not items:
        for x in extra:
            st.markdown(x, unsafe_allow_html=True)
        if commission and comms and comms[0]:
            st.markdown(comms[0], unsafe_allow_html=True)


def relationship_html(rel, target, portco):
    """The existing relationship, folded: one line, the passages behind it on request."""
    quotes = "".join(f"<div class='it one'><span class='sub2'>{he(who)}'s sources:</span> {quoted(p)}</div>"
                     for who, p in rel)
    return (f"<details class='mkts' style='margin-top:.3rem'><summary><span class='lab lab-q'>Existing "
            f"relationship</span> the public sources of {he(target)} and {he(portco)} mention each other "
            f"({plural(len(rel), 'passage')})</summary>{quotes}<div class='sub2'>Check its nature (supply, "
            "distribution, partnership, equity); the tool does not assess it.</div></details>")


def quoted(passage):
    """A passage in quotation marks, unless it already starts with one (no ““…)."""
    t = (passage or "").strip()
    return he(t) if t[:1] in "“\"„«" else f"“{he(t)}”"


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
                    f"company at a time, and here {e(who)}'s activity is {e(here)}.")
        return (f"{head(f'Resale not considered ({what})')} in this row {e(who)}'s activity is {e(here)}, and the "
                f"screen shows no wholesale or retail activity of {e(who)}.")
    if "own use" in reason:
        return (f"{head(f'Set aside ({what})')} {e(who)}'s activity here is only for the group's own use, so it "
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
    names = {"A": target, "B": portco}
    t = str(text or "")

    def label(m, group=1):
        """The name, unless the letter follows a word like "vitamin" or "type" (then it is not the label)."""
        before = t[:m.start()].split()
        if before and before[-1].lower().strip("(") in _AB_NOT_LABEL:
            return m[0]
        return names[m[group]]

    t = re.sub(r"\b(?:[Aa]ctivity|[Cc]ompany|[Ss]ide|[Pp]arty)\s+([AB])['’]s\b", lambda m: f"{names[m[1]]}'s", t)
    t = re.sub(r"\b[Aa]ctivity\s+([AB])\b(?![-\w])", lambda m: f"{names[m[1]]}'s activity", t)
    t = re.sub(r"\b(?:[Cc]ompany|[Ss]ide|[Pp]arty)\s+([AB])\b(?![-\w])", lambda m: names[m[1]], t)
    t = re.sub(r"(?<![\w-])([AB])['’]s\b", lambda m: f"{names[m[1]]}'s", t)
    t = re.sub(r"(?<![\w-])(B)(?![\w-])", label, t)
    # "A" inside a sentence is the label; at the start of a sentence only before "and/or", a comma, a bracket or a verb
    t = re.sub(r"(?<=[a-z,;(]\s)(A)(?![\w-])|(?<=[a-z,;(])(A)(?![\w-])",
               lambda m: label(m, 1 if m[1] else 2), t)
    t = re.sub(r"(?:(?<=^)|(?<=[.!?:]\s))(A)(?=\s+(?:and|or|" + _AB_VERBS + r")\b|[,);:.])", label, t)
    return t


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


def short_name(a):
    return other_name(a) if rules.category(a) == "other" else capital(a["product"])


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
        cols[1].markdown(f":gray[No overlap found with {esc(portco)}'s only activity]" if n_portco == 1 else
                         f":gray[No overlap found with any of {esc(portco)}'s activities]")
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


# A horizontal label across different levels of trade, where the two companies do not have the same direct customers
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
        return (f"{P}'s only activity does not meet any activity of {T}." if n == 1 else
                f"None of {P}'s {n} activities meets an activity of {T}.")
    main_live = [r for r in live if not is_own_use(r) and not is_less_likely(r)]
    own_live = [r for r in live if is_own_use(r)]
    less_live = [r for r in live if is_less_likely(r)]
    notes = ([f"{plural(len(less_live), 'less likely horizontal label')} (different levels of trade, not the same "
              f"direct customers), {less_where}"] if less_live else []) + \
            ([f"{plural(len(own_live), 'potential link')} involving own use, {own_where}"] if own_live else [])
    if not main_live:
        return f"No overlap with {T}'s activities except {' and '.join(notes)}."
    k = len({r["label_b"] for r in main_live})
    text = (f"{P}'s only activity meets activities of {T}." if n == 1 else
            f"{k} of {P}'s {n} activities {'meets' if k == 1 else 'meet'} activities of {T}.")
    return text + "".join(f" Also {x}." for x in notes)


# =============================================================== the report (step ⑤ and the Word document)
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
        lab = {"kind": p["kind"], "view": label_view(pid, p), "basis": "", "regard": [], "lines": [], "up": p["up"]}
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


def long_date(iso):
    """'2010-01-06' -> '6 January 2010', the form of every date in the Word document ('' stays '', anything else
    as it is)."""
    try:
        d = datetime.fromisoformat(str(iso or ""))
    except ValueError:
        return str(iso or "")
    return f"{d.day} {d:%B %Y}"


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
            for ta in t_acts:
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
                        pair = f"{short_name(r['a'])} × {short_name(r['b'])}"
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
            summary.append({"portco": p, "horizontal": hor, "vertical": ver})
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
                              "paras": sorted(cited[case], key=lambda x: (str(type(x)), x))})
        years = decision_years(cases)
        today = now_local()
        pending = sum(1 for sec in sections for b in sec["blocks"] + sec["less"] + sec["own"] for x in b["rows"]
                      if x["pending"])
        return {"target": target, "portcos": portcos, "date": f"{today.day} {today:%B %Y}", "pending": pending,
                "step4": step4, "years": years, "summary": summary, "sections": sections, "markets": markets,
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
    that involve only own use, collapsed. Inside the collapsed box (nested) Streamlit allows no second expander, so
    "Own use" is a plain sub-heading there."""
    table_header(target, p)
    for ta in t_acts:
        rs = rows_of(ta)
        main_rows = [r for r in rs if not is_out(r) and not is_own_use(r) and not is_less_likely(r)]
        screened = [r for r in rs if is_out(r)]
        if main_rows or screened:
            target_block(ta, main_rows, screened, status, rv, target, p, n_portco)
    less_rows = [r for r in pairs if not is_out(r) and is_less_likely(r)]
    own_rows = [r for r in pairs if not is_out(r) and is_own_use(r)]
    less_title = (f"Less Likely: {plural(len(less_rows), 'horizontal label')} across different levels of trade, "
                  "without the same direct customers")
    for rows, title in ((less_rows, less_title),
                        (own_rows, f"Own Use: {plural(len(own_rows), 'potential link')} (production for the group "
                                   "itself, which can only be the customer side)")):
        if not rows:
            continue
        if nested:
            st.markdown(f"**{title}**")
            own_table(t_acts, rows_of, rows, status, rv, target, p, n_portco)
        else:
            with st.expander(title):
                if rows is less_rows:
                    st.caption("Different levels of trade are often different markets; where the two companies "
                               "also have different direct customers, a horizontal overlap is less likely. Set a view "
                               "or add a note to move a row back into the table.")
                own_table(t_acts, rows_of, rows, status, rv, target, p, n_portco)


def own_table(t_acts, rows_of, own_rows, status, rv, target, p, n_portco):
    """The rows of a folded section ("Less likely", "Own use"), in the target's order."""
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
              "decisions: first each market once, then in each row what follows for its labels.")


# A short guide at the start of steps ②–④, always open (the lawyer can fold it), in the same three columns on every
# step: how it works, how to read the result (with the marks, labels and colours of the step), the limits. A tool that
# states its limits openly makes the lawyer more willing to dismiss and apply their own judgement.
def _src(mark):
    return f"<span class='src'>[1]</span>{mark}"


def _chips(*outcomes):
    """Placeholders for the result chips, filled in when the guide is shown (OUTCOME_CLASS is defined further down)."""
    return " ".join(f"{{chip:{o}}}" for o in outcomes)


GUIDES = {
    2: ("How the Research Works", [
        ("How It Works", [
            "Each company is researched on its own, in two searches of public websites: one for its main business, one "
            "for what such a search easily misses (smaller brands, sales to other businesses, own shops and cafés, side "
            "lines).",
            "The AI never sees another company of this screen or the planned deal.",
            "At most five main activities per company, split by the <b>stage of the supply chain</b> at which it "
            "sells: "
            "<i>raw materials</i>, <i>intermediate products</i> (sold to other manufacturers), <i>manufacturing</i>, "
            "<i>wholesale</i>, <i>retail</i> or <i>services</i>. Production for the group's <b>own use</b> is listed "
            "as one line but not compared."]),
        ("How to Read the Sources", [
            f"{_src('✔')} <b>checked:</b> the app found the quotation on the page word for word.",
            f"{_src('≈')} <b>probably right:</b> reworded or translated by the search; worth a quick look.",
            f"{_src('○')} <b>read by the search only:</b> the app could not open the page itself.",
            f"{_src('⚠')} <b>check before relying on it:</b> the quotation is not on the page.",
            "Hover over a source for what was found; click to open it."]),
        ("Limits", [
            "Only what the company publishes: internal facts are for the client or the company to confirm.",
            "The split into activities can differ between runs. Check that it fits: edit, merge, add or mark an "
            "activity as not relevant before you continue."])]),
    3: ("How the Preliminary Assessment Works", [
        ("How It Works", [
            "Each activity of the target is compared with each activity of every portfolio company, one pair at a "
            "time. The AI sees only the two anonymised descriptions, never company names or the planned deal.",
            "<b>Horizontal:</b> are the products the same or similar <i>for the customers</i> (what they are, their "
            "use, their price positioning)?",
            "<b>Vertical:</b> could one company's product be an <i>input</i> for the other, or be <i>resold</i> by "
            "it, even if they do not trade today?",
            "<b>Checked by the app, not the AI:</b> the level of trade, the direct customers and own use. Different "
            "levels usually mean a vertical relationship; a horizontal overlap across levels is less likely unless "
            "both compete for the same customers."]),
        ("How to Read a Row", [
            "<span class='lab lab-h'>Horizontal</span> same or similar products: potential competitors.",
            "<span class='lab lab-v'>Vertical</span> one could supply the other; the arrow points from supplier to "
            "customer.",
            f"{dots_html('●●●')} {dots_html('●●○')} {dots_html('●○○')} the same, partly the same or different "
            "direct customers; “customers not stated” if one side's sources do not say.",
            "<span class='lab lab-q'>Existing relationship</span> the companies' own sources name each other."]),
        ("Limits", [
            "<b>Deliberately generous:</b> unlikely links are shown too. A missed relationship is easily overlooked "
            "later; an unlikely one takes a second to dismiss.",
            "“Potential” until checked against the Commission's decisions in step ④.",
            "The judgement is yours: set your view on each label, add a note or use “Edit”."])]),
    4: ("How the Market Definitions Are Found", [
        ("How It Works", [
            "The products of each row are sorted into types; each type is searched in the database of Commission "
            "decisions.",
            "The AI places each product in a market. It sees products only, never company names.",
            "The app checks every quotation from the Commission word for word against the decision.",
            "Each market is listed once, in the table above the rows, with the paragraph it rests on; the rows name "
            "the markets (hover for the Commission's sentence)."]),
        ("How to Read a Row", [
            f"{_chips('Confirmed')} both products in a market the Commission defined.",
            f"{_chips('Not supported')} the Commission puts them in separate markets.",
            f"{_chips('Possible', 'Not excluded')} same market possible, or the definition was left open.",
            f"{_chips('No precedent')} nothing in the database: to be assessed under the Market Definition Notice.",
            f"{_chips('Markets defined', 'One side defined')} vertical rows: the two markets whose shares decide the "
            "30 % tests; not proof that one company supplies the other."]),
        ("Limits", [
            "{database}; a decision outside the database is not found.",
            "Each decision describes the market at its time; the Commission is not bound by it (Notice (14)).",
            "Shops and wholesalers: the decisions describe the products they sell, not their own retail or wholesale "
            "market.",
            "Product markets only: geography and market shares, which decide whether a market is “affected”, are not "
            "assessed."])]),
}


def database_text():
    """'The database holds a limited set of decisions (2010–2015) and the Market Definition Notice', from the corpus."""
    paras = corpus_paragraphs().values()
    years = sorted({str(p.get("date") or "")[:4] for p in paras if p.get("source_type") == "Commission decision"}
                   - {""})
    span = f" ({years[0]}–{years[-1]})" if len(years) > 1 else (f" ({years[0]})" if years else "")
    notice = any(p.get("source_type") == "Commission notice" for p in paras)
    return f"The database holds a limited set of decisions{span}" + (" and the Market Definition Notice" if notice else "")


def guide_html(step):
    title, cols = GUIDES[step]
    out = []
    for head, items in cols:
        lis = "".join("<li>" + re.sub(r"\{chip:([^}]+)\}", lambda m: f"<span class='oc {OUTCOME_CLASS[m.group(1)]}' "
                                      f"style='margin:0'>{m.group(1)}</span>",
                                      t.replace("{database}", database_text())) + "</li>" for t in items)
        out.append(f"<div><div class='gh'>{head}</div><ul>{lis}</ul></div>")
    return f"<div class='guide'>{''.join(out)}</div>"


def guide_box(step):
    with st.expander(GUIDES[step][0], expanded=True):      # the same on every step: open, and the lawyer can fold it
        st.markdown(guide_html(step), unsafe_allow_html=True)


def stage_overview(ai, step=3):
    st.header("④ Commission Market Definitions" if step == 4 else "③ Preliminary Assessment")
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
    failed = failed_pairs()
    if failed:
        st.warning(f"{plural(len(failed), 'comparison')} could not be made: the AI call returned an error (the rows "
                   "marked “Unclear”; see “Why?”). Go back to step ② and press “Update the comparison” to send "
                   f"{'it' if len(failed) == 1 else 'them'} again.")
    if step == 4 and ss.get("precedents"):
        ov = market_overview()
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
    precedent_button(units, todo, step)


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
    return ("<table class='sumt'><thead><tr><th>Portfolio Company</th><th><span class='lab lab-h'>Potential horizontal "
            "overlaps</span></th><th><span class='lab lab-v'>Potential vertical relationships</span></th></tr></thead>"
            f"<tbody>{rows}</tbody></table>")


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
        st.write("The result for each portfolio company, from your review in steps ③ and ④. The Word document holds "
                 "the same summary, the full tables and the sources.")
    else:
        st.write("The result for each portfolio company, from your review in step ③: no row is kept, so there were no "
                 "market definitions to look up. The Word document lists every pair compared, with the reason.")
    pending_warning(model)
    st.markdown(summary_html(model), unsafe_allow_html=True)
    st.caption("Target activity first; the arrow points to the customer. After each entry: the Commission's result "
               "and your view.")
    if model["open_points"]:
        st.markdown("##### Open Points")
        st.markdown("\n".join(f"- {esc(o['text'])} :gray[({esc(o['pair'])}, {esc(o['portco'])})]"
                               for o in model["open_points"]))
    st.download_button("Download the Word document", data=lambda: export.docx_bytes(model), type="primary",
                       file_name=word_name(), on_click="ignore", mime=DOCX_MIME)
    st.caption("The document to share, without the app's data. To continue this screen later, use “Save progress” in "
               "the sidebar: a Word document that the app can open again.")


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
    """The target activities whose rows changed since their search: those of their rows that the search no longer
    covers say "Changed since the search" (or "Not looked up yet"), the others keep their result (row_view).
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
    card = WorkCard("Looking Up the Commission's Market Definitions", "Sorting the products into types of product …",
                    "Each type of product is searched in the Commission's decisions and read on its own; the AI sees "
                    "the products only, never company names. This usually takes one to four minutes.")
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
    prec.unify_names(store.values())
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
    """(stored search, what the row shows) or (search, None) if the search does not cover the row (yet). A search that
    is out of date because of other rows of its target activity still serves the rows whose products it covers."""
    rec = prec_record(r)
    if not rec:
        return rec, None
    if r["a"].get("aid") in (ss.get("prec_stale") or set()):
        items = prec.row_items(r, search_overrides(), cmp.effective_status, cmp.dismissed_parts)
        if not prec.row_covered(rec, r, items):
            return rec, None
    return rec, prec.row_view(r, rec, search_overrides(), cmp.effective_status, cmp.dismissed_parts)


def search_gap(r, rec):
    """Why a kept row has no Commission result: never searched, or changed since the search."""
    return "Changed since the search" if prec.searched_before(rec, r) else "Not looked up yet"


def row_failed(r):
    """The products of a row whose step ④ search failed: shown as a failed search, never as a result."""
    _, view = row_view(r)
    return list(dict.fromkeys((view or {}).get("failed") or []))


# =============================================================== step ④ under each row
# The Commission's markets: under each row, full width, after the facts and the preliminary assessment, one card per
# market says what the Commission defined (its own words, checked in code), what the market covers, why it was
# separated, and which products of each company it covers. Every paragraph is cited as [M.1234 (24)]; hovering shows the
# paragraph exactly as the AI saw it, a click opens the decision.
PREF_CSS = """<style>
[data-testid="stMarkdownContainer"]{position:relative}
.pref{position:static;cursor:help;color:#3A5A80;text-decoration:none !important;border-bottom:1px dotted #3A5A80;
 white-space:nowrap}
.pref .pbox{display:block;visibility:hidden;opacity:0;position:absolute;z-index:1000;left:0;right:0;margin-top:1.5em;
 width:auto;max-width:44em;max-height:26em;overscroll-behavior:contain;
 overflow:auto;background:#fff;color:#1f2328;border:1px solid #c8c8c8;border-radius:6px;padding:.6em .8em;
 box-shadow:0 4px 14px rgba(0,0,0,.18);font-size:.86rem;line-height:1.45;white-space:normal;text-align:left;
 font-weight:normal;font-style:normal;transition:visibility 0s linear .35s,opacity .12s linear .25s}
.pref .pbox::before{content:"";position:absolute;left:0;right:0;top:-1.6em;height:1.6em}
.pref:hover .pbox{visibility:visible;opacity:1;transition-delay:0s}
.pref.mk{white-space:normal}
.ccell{overflow-wrap:anywhere}
.ccell{padding:0 0 .2rem 0;margin:0 0 .4rem 0;line-height:1.5;font-size:.92rem}
.ccell .chd{display:block;margin-top:.25rem;font-weight:600;font-size:.82rem;color:#3D3A35}
.mkt{font-size:.9rem;table-layout:fixed}
.mkt td{border-bottom:1px solid #E2DDD2}
.mkt .mgrp td{background:#F2EFE8;font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.98rem;
 padding:.35rem .7rem;border-bottom:none}
.mkt .mrow{margin:.1rem 0 .3rem 0;line-height:1.45}
.mkt .mact{font-weight:600}
.mkt .mco{font-style:italic}
.ccell .cph{font-weight:600;font-size:.82rem;color:#3D3A35;margin-left:.1rem}
.ccell .cpart + .cpart{border-top:1px solid rgba(0,0,0,.09);margin-top:.35rem;padding-top:.4rem}
.ccell .cpart .oc{margin:0 .35rem 0 0}
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


def para_ref(pid, paras, seen=True):
    """[M.1234 (24)]: hover shows the paragraph as the AI saw it (decision, year, part of the decision, text,
    footnotes); a click opens the decision. The second line only names the part of the decision and how the case
    ended ("Relevant product market · A. Bicycles · Phase I, cleared with commitments")
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
           + ("<br><span style='opacity:.7'>" + ("The paragraph exactly as the AI saw it." if seen else
                                                "The paragraph this rule of the app rests on.")
              + (" Click to open the decision." if url else "") + "</span>"))
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


def may_be_category(m):
    """A market without a conclusion in its paragraphs, which may be a category the Commission divided into other
    markets (see commission_parts). Not a market whose AI label failed the word-for-word check: that one was found as a
    market of its own, only its conclusion is unverified."""
    return m.get("conclusion") == prec.NOT_STATED and not m.get("label_not_verified")


def decision_of(m):
    """The decision a market comes from: that of its conclusion sentence, else the one most of its paragraphs cite."""
    pid = m.get("decided_paragraph") or m.get("open_paragraph") or m.get("conclusion_paragraph")
    if pid:
        return pid.rpartition("-")[0]
    cases = [pid.rpartition("-")[0] for pid in m.get("product_paragraphs") or [] if not pid.startswith("Notice")]
    return max(set(cases), key=cases.count) if cases else ""


def decision_years(cases):
    """"M.1234: 2010, M.5678: 2013" (a decision missing from the corpus is left out)."""
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
            label = ("category divided into separate markets" if may_be_category(m) and segs
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
    if not (m.get("decided_quote_found") or m.get("open_quote_found")) and m.get("summary"):
        # no passage of the Commission verified word for word: the AI's summary, marked as such
        box += f"<br><i>AI summary (not a quotation):</i> {h(m['summary'])}"
    box += "<br><span style='opacity:.7'>The decision is listed in the sidebar, under “Commission decisions”.</span>"
    return f"<span class='pref mk'>{h(mname(m['name']))}<span class='pbox'>{box}</span></span>"


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


def _cites(m, paras, limit=2):
    """The paragraphs a market's conclusion rests on (hover: the paragraph as the AI saw it)."""
    pids = [x for x in (m.get("decided_paragraph"), m.get("open_paragraph")) if x]
    if not pids:
        pids = prec._sorted_ids({x for x in m.get("product_paragraphs") or [] if not x.startswith("Notice")})[:limit]
    return para_refs(pids[:limit], paras)


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
        return market_list(found, paras, html_out, sides=(side,))
    groups = view.get(side) or []
    if any(g["market_id"] == "failed" for g in groups):
        return "search failed"
    return "no precedent"


def _cites_plain(m, limit=2):
    """The same paragraphs as _cites, as plain text: "[M.1234 (24)]" (for the Word document)."""
    pids = [x for x in (m.get("decided_paragraph"), m.get("open_paragraph")) if x]
    if not pids:
        pids = prec._sorted_ids({x for x in m.get("product_paragraphs") or [] if not x.startswith("Notice")})[:limit]
    return " ".join("[" + pid.rpartition("-")[0] + " (" + pid.rpartition("-")[2] + ")]" for pid in pids[:limit])


def _rank(e):
    return max((e["a"] or {}).get("status", "specific"), (e["b"] or {}).get("status", "specific"), key=STATUS_RANK.get)


OUTCOME_CLASS = {"Confirmed": "o-conf", "Markets defined": "o-vert", "Possible": "o-open", "Not excluded": "o-open",
                 "One side defined": "o-vert", "Not supported": "o-nosup", "No precedent": "o-nopre"}
OUTCOME_TIP = {
    "Confirmed": "Both products fall in a market the Commission defined: horizontal overlap at product-market level.",
    "Possible": "Both products may fall in the same market, depending on the product format, or the market is not an "
                "exact match for one of them: to be checked.",
    "Not excluded": "Both products fall in a market whose definition the Commission left open (or the paragraphs found "
                    "state no conclusion): the overlap cannot be excluded.",
    "Not supported": "The Commission puts the products in separate markets: no horizontal overlap at product-market "
                     "level; check for a vertical relationship.",
    "No precedent": "No decision in the database covers these products, or, for a shop or wholesaler, its own retail "
                    "or wholesale market (the markets of the products it sells are named in the text): to be assessed "
                    "under the Market Definition Notice.",
    "Markets defined": "The decisions define the market of each side's products. They do not show a link between "
                       "the two companies: that comes from the preliminary assessment (step ③).",
    "One side defined": "The decisions define the market of one side's products only; the other side has no "
                        "precedent. They do not show a link between the two companies."
}


def outcome_chip(outcome):
    return (f"<span class='oc {OUTCOME_CLASS[outcome]}' title='{h(OUTCOME_TIP[outcome])}'>{outcome}</span>"
            if outcome else "")


def exact_match(e):
    """Both sides' products placed in the market on the decision's own terms (basis "precedent")."""
    return all((e[s] or {}).get("basis") == "precedent" for s in ("a", "b") if e.get(s))


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
        n14, n25 = ((para_ref("Notice-14", {}, seen=False), para_ref("Notice-25", {}, seen=False)) if html_out
                    else ("(Market Definition Notice (14))", "(Market Definition Notice (25))"))
        return [f"{who}'s side is {lw}: the decisions define the markets of the products, not the {lw} market. "
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


# =============================================================== step ④: the markets in this screen, once
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
    """The paragraphs a market's conclusion rests on (as _cites)."""
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


def reseller_flags(r):
    return {"a": is_reseller(r["a"]), "b": is_reseller(r["b"])}


# One Commission box per row, with one part per label of the row: its result and what the decisions give for it (the
# market of both products, or of each side's products). The heading of a part names the label of step ③ it belongs
# to: the relationship itself comes from the app's comparison, the decisions only define markets. The internal label
# ("horizontal", "vertical, X → Y", "vertical, both directions") is what the summary and an edited text use.
BOTH_DIRECTIONS = "vertical, both directions"


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
    if len(ups) > 1:                   # supply in both directions: each side's market once
        out.append((BOTH_DIRECTIONS, vertical_sentence(entries, view, "both", target, portco, paras, html_out, rs,
                                                       acts), vertical_outcome(entries, ups[0], rs)))
    for up in ups if len(ups) == 1 else []:
        u, d = (target, portco) if up == "a" else (portco, target)
        out.append((f"vertical, {u} → {d}", vertical_sentence(entries, view, up, target, portco, paras, html_out, rs,
                                                               acts), vertical_outcome(entries, up, rs)))
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


def commission_htmls(r, target, portco, parts):
    """Step ④: the Commission's part for each line of a row (parts as in assign_commission), as HTML; the chip says
    the result, the line beside it says which label it belongs to. Code only, no AI call."""
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
    for i, p in enumerate(parts):      # a second vertical label in the same direction (input and resale): same markets
        if (p.get("kind") == "v" and not p.get("off") and not groups[i] and any(
                q.get("kind") == "v" and not q.get("off") and q.get("up") == p.get("up") and groups[j]
                for j, q in enumerate(parts[:i]))):
            out[i] = "<div class='ccell'><span class='sub2'>Same markets as the vertical label above.</span></div>"
    for i, g in enumerate(groups[:len(out)]):
        if g:
            out[i] = "<div class='ccell'>" + "".join(
                f"<div class='cpart'>{outcome_chip(outcome)}"
                + (f"<span class='cph'>{he(commission_heading(label))}</span>" if label == BOTH_DIRECTIONS else "")
                + "<ul>" + "".join(f"<li>{b[:1].upper() + b[1:] if not b.startswith('<') else b}</li>" for b in bullets)
                + "</ul></div>" for label, bullets, outcome in g) + "</div>"
    return out


def commission_cell(r, target, portco):
    """Step ④, the Commission column of a row (after the preliminary assessment): one box, with one part per label of
    the row (its result chip, the label it belongs to, and the markets as names; hover for the Commission's sentence).
    The paragraphs are cited once, in the market table above the rows. Code only, no AI call."""
    if not ss.get("precedents") or ss.get("step") != 4:
        return ""
    rec, view = row_view(r)
    if view is None:
        if kept(row_status(r)):
            st.caption(f"{search_gap(r, rec)}: press “Update the market definitions” below.")
        return ""
    if view["error"]:
        st.markdown(f"<div class='ccell'><b>Commission:</b> the search failed ({he(view['error'])}): press “Update "
                    "the market definitions” below.</div>", unsafe_allow_html=True)
        return ""
    o = ss.override_store.get(cmp.pair_id(r), {})
    edited = (o.get("text_commission") or "").strip()
    if edited:
        cells = (f"<div class='ccell'>{he_lines(edited)} <span class='ed'>edited by you</span>"
                 "</div>")
    else:
        parts = "".join(
            f"<div class='cpart'>{outcome_chip(outcome)}<span class='cph'>{he(commission_heading(label))}</span><ul>"
            + "".join(f"<li>{b[:1].upper() + b[1:] if not b.startswith('<') else b}</li>" for b in bullets)
            + "</ul></div>" for label, bullets, outcome in commission_sentences(r, target, portco))
        cells = f"<div class='ccell'>{parts}</div>" if parts else ""
    if view.get("failed") and edited:       # otherwise the failure is the first part of the box (commission_sentences)
        cells = (f"<div class='ccell'><b>The search failed</b> for {he(', '.join(dict.fromkeys(view['failed'])))}: "
                 "press “Update the market definitions” below.</div>") + cells
    st.markdown(cells, unsafe_allow_html=True)


def precedent_warnings(units):
    """Only what needs action (the search summary is in the saved progress file, not on the page)."""
    records = [ss.precedents[u["target_aid"]] for u in units if u["target_aid"] in ss.precedents]
    s = prec.summary(records)
    if s["errors"]:
        st.warning("Some searches failed: " + "; ".join(esc(e) for e in s["errors"]) + ". Press “Update the market "
                   "definitions” to try them again.")


def precedent_button(units, todo, step=4):
    store = ss.get("precedents") or {}
    failed = [u for u in units if (store.get(u["target_aid"]) or {}).get("error")]
    todo = todo + [u for u in failed if u not in todo]
    if not units:
        st.caption("No row is kept: there are no market definitions to look up. The summary and the Word document "
                   "list every pair compared, with the reason.")
        st.button("Go to the summary →", type="primary", on_click=go_to, args=(5,))
        return
    if not store:
        if st.button("Find Commission market definitions", type="primary"):
            start_work("precedents")
        return
    # the market definitions exist: the way on (to step ④ from step ③, to the summary from step ④), and, if rows
    # changed or a search failed, the update first
    with st.container(horizontal=True, vertical_alignment="center"):
        if todo:
            label = (f"Update the market definitions ({plural(len(todo), 'search', 'searches')} for new or changed "
                     f"rows, {len(units) - len(todo)} kept)")
            if st.button(label, type="primary"):
                for u in failed:          # a failed search is never "reusable": drop it so that it runs again
                    ss.precedents.pop(u["target_aid"], None)
                start_work("precedents")
        nxt = "secondary" if todo else "primary"
        if step == 3:
            st.button("Go to the market definitions →", type=nxt, on_click=go_to, args=(4,), key="to_step4")
        else:
            st.button("Go to the summary →", type=nxt, on_click=go_to, args=(5,), key="to_step5")


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
# Useful e.g. for a lawyer who is only interested in step ④. Restores the screen from an audit log downloaded from this
# app (steps ①–② from a file saved before the comparison; ①–③, and ④ if the file has it, from a later one), without any
# AI call. The file stays with the lawyer; the app stores nothing.
AUDIT_REQUIRED = ("companies", "stage_1_2_activity_mapping")


def _activities_for(acts, companies):
    """acts if it holds an activity list for every company, else None."""
    ok = isinstance(acts, dict) and all(isinstance(acts.get(c["name"]), list) for c in companies)
    return acts if ok else None


def check_audit(data):
    """The problems that stop a file from being loaded (empty list = it can be loaded). A file saved in step ② has no
    comparison yet ("stage_2_confirmed_activities" is empty) and continues in step ②."""
    if not isinstance(data, dict):
        return ["the file is not an audit log of this app"]
    missing = [k for k in AUDIT_REQUIRED if k not in data]
    if missing:
        return [f"the file has no {', '.join(missing)} (a progress file saved with this app is needed)"]
    companies = data["companies"]
    if not isinstance(companies, list) or not companies or not all(isinstance(c, dict) and c.get("name")
                                                                   for c in companies):
        return ["the list of companies is missing or damaged"]
    problems = []
    confirmed = data.get("stage_2_confirmed_activities")
    if confirmed is not None:                  # saved after a comparison (step ③ or later)
        if _activities_for(confirmed, companies) is None:
            problems.append("the confirmed activities are missing or damaged")
        results = data.get("stage_3_factual_comparison")
        if not isinstance(results, list) or not all(isinstance(r, dict) and {"a", "b", "decision", "comparison",
                                                                             "portco"} <= set(r) for r in results):
            problems.append("the results of step ③ are missing or damaged")
    else:                                      # saved in step ②, before a comparison
        mapping = data.get("stage_1_2_activity_mapping")
        researched = isinstance(mapping, dict) and all(isinstance(mapping.get(c["name"]), dict) for c in companies)
        if _activities_for(data.get("stage_2_current_activities"), companies) is None and not researched:
            problems.append("the activities are missing or damaged")
    return problems


def load_audit(data):
    """Restores the screen of an audit log into the session (after reset_all). No AI call. A file saved after a
    comparison continues in step ③ (or ④); one saved in step ②, before a comparison, continues in step ②. Edits made
    in step ② after the last comparison come back as they were saved."""
    reset_all()
    for k, v in (("stage_logs", {}), ("acts_version", 0)):    # removed by reset_all
        ss.setdefault(k, v)
    companies, mapped = data["companies"], data["stage_1_2_activity_mapping"] or {}
    confirmed = _activities_for(data.get("stage_2_confirmed_activities"), companies)
    compared = confirmed is not None
    current = _activities_for(data.get("stage_2_current_activities"), companies)
    if current is None:          # a file without them: the confirmed activities, else those of the research
        current = confirmed if compared else {c["name"]: copy.deepcopy(extracted(mapped.get(c["name"]) or {}))
                                             for c in companies}
    ss.companies = companies
    ss.mapped = {c["name"]: mapped.get(c["name"]) or {"extraction": {"activities": current[c["name"]]}}
                 for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    if compared:
        cmp.ensure_ids(confirmed)
        # the research the comparison was made on: saved apart only where a company was mapped again afterwards
        saved = data.get("stage_3_research_compared") or {}
        ss.compared_research = {c["name"]: saved.get(c["name"]) or (ss.mapped[c["name"]].get("search"))
                                for c in companies}
        ss.compared_names = [c["name"] for c in companies]
        basis = {n: dict(m, search=ss.compared_research.get(n)) for n, m in ss.mapped.items()}
    else:
        basis = ss.mapped
    # found again from the saved research, with the current rule (a saved file may hold false matches)
    ss.relationships = am.find_relationships(basis, companies,
                                             (data.get("anonymisation") or {}).get("kept_as_ordinary_words") or ())
    ss.acts = copy.deepcopy(current)
    cmp.ensure_ids(ss.acts)
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
    ss.names = cmp.collect_names(companies, confirmed if compared else ss.acts, group, ss.keep_words)
    ss.profiles_meta = anon.get("abstracts") or {}
    ss.pair_cache = {}
    if compared:
        results = [{k: v for k, v in r.items() if k != "status_after_overrides"}
                   for r in data["stage_3_factual_comparison"]]
        ss.results = results
        ss.confirmed = confirmed
        ss.confirmed_hash = activities_hash(confirmed)
        ss.current_hash = activities_hash(ss.acts)
        # the pair results under their content keys, so that "Update the comparison" sends only new or changed pairs
        # (and pairs whose call had failed)
        for r in results:
            if (r.get("comparison") or {}).get("error"):
                continue
            try:
                ss.pair_cache[(cmp.activity_key(r["a"], r["abstract_a"]),
                               cmp.activity_key(r["b"], r["abstract_b"]))] = r
            except (KeyError, TypeError):
                pass
    else:
        ss.results = ss.confirmed = ss.confirmed_hash = None
        ss.compared_research = {}
    ss.vec_cache = {}
    ss.override_store = {pid: dict(o) for pid, o in (data.get("user_overrides") or {}).items() if isinstance(o, dict)}
    ss.results_version = 1
    ss.precedents = dict((data.get("stage_4_market_definitions") or {}).get("searches") or {})
    for rec in ss.precedents.values():     # the conclusion labels follow the verified passages, whatever the file holds
        if isinstance(rec, dict):
            prec.verify_labels(rec)
    prec.unify_names(ss.precedents.values())
    before = list(data.get("call_log_before_loading") or []) + list(data.get("call_log") or [])
    ss.loaded_calls = before
    ss.loaded_from = {"created": data.get("created"), "loaded": now_local().isoformat(timespec="seconds"),
                      "profile": data.get("profile"), "models": data.get("models"),
                      "calls_before": {"calls": len(before), "cost": round(sum(c.get("cost", 0) or 0 for c in before), 4)}}
    ss.acts_version += 1
    ss.step = (4 if ss.precedents else 3) if compared else 2


def loader_box():
    """'Open saved progress' in the sidebar."""
    st.caption("Continues a screen from a Word document saved with “Save progress” (or an audit log, .json): "
               "companies, activities, the assessment and step ④, with your views, notes and edits, without any AI "
               "call. The current screen is replaced. The file stays with you; the app stores nothing.")
    up = st.file_uploader("Progress file (.docx or .json)", type=["docx", "json"], key="audit_upload",
                          label_visibility="collapsed")
    if up is None:
        return
    blob = up.getvalue()
    try:
        if up.name.lower().endswith(".docx"):
            data = export.read_progress(blob)
            if data is None:
                st.error("This Word document holds no screen data. Only a document saved with “Save progress” can be "
                         "opened again (“Download the Word document” saves it without the data).")
                return
        else:
            data = json.loads(blob.decode("utf-8"))
    except ValueError as e:          # also UnicodeDecodeError and json.JSONDecodeError
        st.error(f"The file could not be read: {e}")
        return
    problems = check_audit(data)
    if problems:
        st.error("This file cannot be loaded: " + "; ".join(problems) + ".")
        return
    target = data["companies"][0]["name"]
    reached = (", with step ④" if data.get("stage_4_market_definitions")
               else ", with the assessment (step ③)" if data.get("stage_2_confirmed_activities") is not None
               else ", activities only (continues in step ②)")
    st.write(f"Saved {esc((data.get('created') or 'unknown date').replace('T', ' '))}: target **{esc(target)}**, "
             f"{plural(len(data['companies']) - 1, 'portfolio company', 'portfolio companies')}{reached}.")
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
    compared = ss.get("results") is not None
    if compared:
        current_overrides()
    return {"created": now_local().isoformat(timespec="seconds"), "profile": PROFILE, "dev_mode": DEV_MODE,
            "cache": USE_CACHE, "models": dict(ai.models),
            "companies": ss.get("companies"), "mapped": ss.get("mapped"), "relationships": ss.get("relationships"),
            "confirmed": ss.get("confirmed") if compared else None,
            # the activities as they are in step ② now, with edits not compared yet
            "acts": ss.get("acts"), "compared_research": ss.get("compared_research") or {},
            # the profiles as shown now (including an edit after the comparison)
            "profiles": {c["name"]: profile_of(c["name"]) for c in ss.get("companies") or []},
            "names": list(ss.get("names") or []), "keep_words": list(ss.get("keep_words") or []),
            "keep_proposed": list(ss.get("keep_proposed") or []), "drop_words": list(ss.get("drop_words") or []),
            "abstracts": ss.get("profiles_meta"), "results": list(ss.get("results") or []),
            # before a comparison (or after the companies changed): every view, dismissal and note kept so far, so
            # that they apply again once the activities are compared
            "overrides": dict(ss.get("overrides") or {}) if compared else dict(ss.get("override_store") or {}),
            "calls": audit_calls(),
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
        "stage_2_current_activities": snap["acts"],
        "anonymisation": {"name_variants_removed": sorted(rules.name_variants(snap["names"])),
                          "kept_as_ordinary_words": snap["keep_words"],
                          "proposed_by_the_tool (used in lower case)": snap["keep_proposed"],
                          "unticked_by_user (removed)": snap["drop_words"],
                          "abstracts": snap["abstracts"]},
        "stage_3_factual_comparison": slim,
        "user_overrides": snap["overrides"],
        "call_log": snap["calls"],
    }
    # a company mapped again after the comparison: the research the compared activities' source numbers refer to
    mapped = snap["mapped"] or {}
    earlier = {n: r for n, r in (snap.get("compared_research") or {}).items()
               if r is not None and r is not ((mapped.get(n) or {}).get("search"))}
    if snap["confirmed"] is not None and earlier:
        log["stage_3_research_compared"] = earlier
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
        res = r.search("whether the exact relevant product market can be left open", k=3)    # any sector
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
    def line(mark, text, tip):       # the mark and its explanation in two columns (see .lgg)
        return (f"<div class='lgl'><span class='lgm' title='{h(tip)}'>{mark}</span>"
                f"<span class='sub2' title='{h(tip)}'>{text}</span></div>")
    src = (line("<span class='src'>[4]</span>✔", "checked: the quotation is on the page",
                "Hover over a number for the quotation and where it comes from (company website or other public "
                "source); click to open the page, a PDF at the right page. ✔ the app found the quotation on the page "
                "word for word: can be relied on.")
           + line("<span class='src'>[4]</span>≈", "probably right: worth a quick look",
                  "The wording is not on the page word for word, but its figures and names are (reworded by the "
                  "search), or the quotation is the search's translation of a page in another language; or, for a page "
                  "cited without a quotation, the page names the activity's products or brands.")
           + line("<span class='src'>[4]</span>○", "read by the search only",
                  "The search read this page and the activity is based on it, but the app could not open the page "
                  "itself to confirm the quotation (the site refused its automatic visit, or the page shows almost no "
                  "text), or the search cited it without a quotation. This says nothing about the source; open the "
                  "link if the row matters.")
           + line("<span class='src'>[4]</span>⚠", "check before relying on it",
                  "The wording of the quotation is not on the page, and neither are (most of) its figures and names; "
                  "or the page is in the quotation's own language but has few of its words. Hover for what was found."))
    labels = (line("<span class='lab lab-h'>Horizontal</span>", "same or similar products",
                   "Potential horizontal overlap: both companies offer the same or similar products (potential "
                   "competitors). “Potential” until checked against the Commission's market definitions in step ④.")
              + line("<span class='lab lab-v'>Vertical</span>", "one could supply the other",
                     "Potential vertical relationship: one company's products could be an input for the other, or could "
                     "be resold by it. The arrow points from supplier to customer.")
              + line("<span class='tag'>less likely</span>", "horizontal across levels, other customers",
                     "A horizontal label across different levels of trade (e.g. manufacturing v retail) where the two "
                     "companies do not have the same direct customers. Different levels of trade are often "
                     "different markets (Market Definition Notice (14)), so a horizontal overlap is less likely; "
                     "whether both compete for the same customers is to be checked. Rows with only "
                     "such a label are folded under “Less likely”; setting a view or a note moves a row back into "
                     "the table."))
    dots = line(dots_html("●●○"), "direct customers (hover over the dots)",
                "Three filled dots: the same direct customers; two: partly the same; one: different; “customers not stated”: one "
                "side's sources do not say. Compares only who each company sells "
                "to directly (e.g. shops, other manufacturers, consumers), not the products. Different customers alone "
                "do not rule out an overlap: customers form a separate market only if the seller can tell which group "
                "a customer belongs to at the time of sale, customers cannot resell to each other, and the different "
                "treatment is lasting (Market Definition Notice (88)).")
    rel = line("<span class='lab lab-q'>Existing relationship</span>", "found by the app's code, not by the AI",
               "Each company was researched on its own, in searches that never named the other companies or the "
               "planned deal. Afterwards, the app's code looked through each company's research for the names of the "
               "other companies in this screen. It only finds names: what the relationship is (supply, distribution, "
               "partnership, equity) is for you to check.")
    def group(title, body):           # the legend in small groups, each with its own heading
        return f"<div class='lgh'>{title}</div>{body}"
    if step <= 2:
        return group("Sources", src)
    if step == 3:
        return group("Labels", labels + dots + rel) + group("Sources", src)
    return group("Commission Results", "".join(line(outcome_chip(o), w, OUTCOME_TIP[o]) for o, w in (
        ("Confirmed", "same market"), ("Possible", "same market possible: to be checked"),
        ("Not excluded", "definition left open"), ("Not supported", "separate markets"),
        ("No precedent", "for the lawyer"), ("Markets defined", "vertical: both sides"),
        ("One side defined", "vertical: one side")))) + group("Labels", labels)


def sidebar_panel(ai, step):
    """The sidebar for everyone: the key, the actions for this screen, the legend and the run summary;
    the development tools collapsed at the end, in development only."""
    with st.sidebar:
        st.markdown("**This Screen**")
        if ss.get("companies") and step > 1:
            n = len(ss.companies) - 1
            st.caption(f"{esc(ss.companies[0]['name'])} and {plural(n, 'portfolio company', 'portfolio companies')}")
        if st.button("Start over", width="stretch", help="Discard this screen and start again"):
            confirm_reset(audit_snapshot(ai) if ss.get("mapped") else None)
        snap = None
        if ss.get("mapped"):
            snap = audit_snapshot(ai)
            p_model, p_note = progress_model()
            st.download_button("Save progress", data=lambda: progress_bytes(snap, p_model, p_note), mime=DOCX_MIME,
                               on_click="ignore", width="stretch", file_name=progress_name(),
                               help="Downloads the screen so far as a Word document, with your views, notes and edits. "
                                    "The document also holds the screen's data, so that “Open saved progress” can "
                                    "continue it later (changes made in Word are not read back). The app stores "
                                    "nothing.")
        if summary_ready():
            model = p_model if ss.get("mapped") else report_model()
            pending_warning(model, sidebar=True)
            st.download_button("Download the Word document", data=lambda: export.docx_bytes(model),
                               file_name=word_name(), on_click="ignore", width="stretch", mime=DOCX_MIME,
                               help="The preliminary overlap overview as a Word document, to share: your final "
                                    "choices in the main part, how the tool prepared it in the Annex; without the "
                                    "app's data.")
        with st.expander("Open Saved Progress"):
            loader_box()
        if step >= 2:
            with st.expander("Legend", expanded=True):       # open in every step
                st.markdown(f"<div class='lgg'>{legend_html(step)}</div>", unsafe_allow_html=True)
        if step >= 4 and ss.get("precedents"):
            decisions = decisions_html()
            if decisions:
                with st.expander("Commission Decisions", expanded=True):
                    st.caption("The decisions used in this screen; hover for the markets, click to open the decision.")
                    st.markdown(decisions, unsafe_allow_html=True)
        if ss.get("stage_logs") or ss.get("loaded_from"):
            with st.expander("About This Run"):
                st.caption(run_summary())
                if snap is not None:
                    st.download_button("Audit log (.json)", data=lambda: audit_json(snap), mime="application/json",
                                       on_click="ignore", file_name=f"overlap_audit_{now_local():%Y%m%d-%H%M}.json",
                                       help="The full record of this screen: every AI call with what it was sent "
                                            "and returned, the sources, the checks and your changes. The same data "
                                            "as in a progress copy; “Open saved progress” opens it too.")
        if DEV_MODE:
            dev_sidebar(ai)
    key_sidebar()                  # the course's API key module, folded at the end (submitted version)


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
        st.markdown("**Models per Step**")      # no expanders inside an expander (Streamlit)
        st.dataframe(pd.DataFrame([{"Step": k, "Model": v, "Effort": ai.effort(k)} for k, v in ai.models.items()]
                                  + [{"Step": "embed", "Model": ai_client.EMBED_MODEL, "Effort": ""}]),
                     hide_index=True)
        st.markdown("**Deployment Check**")
        st.caption("One AI call, the ChromaDB index and one hybrid search (about USD 0.0001).")
        if st.button("Run the check"):
            ss.deploy_check = deployment_check(ai)
        for what, mark, detail in ss.get("deploy_check", []):
            st.markdown(f"{mark} **{what}**: {detail}")


# =============================================================== page
# The landing page: the question the tool answers; why overlaps matter at the start of a deal next to what the lawyer
# can rely on; the five steps; at the end, below the explanation, one clear call to action. The same content (without
# the call to action) is under "How this tool works" on the later steps.
LANDING_WHY = [
    ("The assessment", "Where the two sides overlap, the deal is most likely to change competition: these are the "
                       "markets the Commission looks at first."),
    ("The data room", "Between competitors, or a supplier and its customer, competitively sensitive information must not "
                      "be disclosed freely in due diligence: it goes through a clean team, a clean room or redaction."),
    ("Clearance", "Above the EU turnover thresholds, the deal may not be implemented before the Commission clears it, so "
                  "clearance is usually a condition for closing. The overlaps, and the market shares in them, largely "
                  "decide how much the Commission needs to see."),
]
_ICON = ("<svg width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#22313F' stroke-width='1.8' "
         "stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>{}</svg>")
LANDING_RELY = [
    ("<circle cx='11' cy='11' r='7'></circle><path d='M20 20l-3.5-3.5'></path>", "Thorough, on purpose.",
     "Every pair of activities compared; generous by design, so nothing is missed and an unlikely link takes a second "
     "to dismiss."),
    ("<circle cx='12' cy='12' r='9'></circle><path d='M8 12.5l2.7 2.7L16 9.5'></path>", "Every point can be checked.",
     "The app opens every source and checks each quotation itself, the Commission's too."),
    ("<rect x='5' y='11' width='14' height='9' rx='2'></rect><path d='M8 11V8a4 4 0 0 1 8 0v3'></path>",
     "Confidential by design.", "The AI never sees two company names together or the planned deal; the app stores "
                                "nothing."),
    ("<path d='M4 20h4L19 9l-4-4L4 16v4z'></path><path d='M13.5 6.5l4 4'></path>", "Your judgement, recorded.",
     "Your views, notes and wording go into the Word document."),
]
LANDING_STEPS = [
    ("Companies", "The target and up to five portfolio companies."),
    ("Activities", "Researched on public websites; you check and correct."),
    ("Preliminary assessment", "Every activity against every activity, <span class='lab lab-h'>Horizontal</span> and "
                               "<span class='lab lab-v'>Vertical</span>"),
    ("Market definitions", "The Commission's decisions, quoted and checked."),
    ("Summary", "Your result, and a Word document to edit."),
]
LANDING_FOOT = ("A working document for a lawyer to verify, not a legal conclusion. Product markets only: geography and "
                "market shares are not assessed. Legal basis: EU Merger Regulation, Articles 4(1), 7(1) and 14(2); "
                "Article 101 TFEU and the Horizontal Guidelines (2023); Notice on the simplified procedure (2023), "
                "point 5.")


def landing_html(title=False):
    """The explanation of the landing page (our own constant text, with a little markup only). On the start page the
    title, the question and "Why It Matters" share the left column, so the panel on the right starts level with the
    title; under "How This Tool Works" (title already above) the question heads the left column."""
    why = "".join(f"<p><b>{t}.</b> {x}</p>" for t, x in LANDING_WHY)
    rely = "".join(f"<div class='lp-item'>{_ICON.format(icon)}<div><b>{t}</b> <span>{x}</span></div></div>"
                   for icon, t, x in LANDING_RELY)
    steps = "".join(f"<li><span class='lp-num'>{k}</span><span class='lp-st'>{t}</span><span class='lp-sx'>{x}</span>"
                    "</li>" for k, (t, x) in enumerate(LANDING_STEPS, start=1))
    head = "<div class='lp-title'>EU Overlap Screen</div>" if title else ""
    return ("<div class='lp-split' lang='en'>"
            f"<div class='lp-main'>{head}<div class='lp-lead'>A preliminary overlap screen for EU merger control: where "
            "does the company to be bought (the <i>target</i>) meet the companies the buyer already owns (the "
            "<i>portfolio companies</i>)?</div>"
            f"<div class='lp-why'><div class='lp-h2'>Why It Matters</div>{why}</div></div>"
            f"<div class='lp-panel'><div class='lp-h2'>What You Can Rely On</div>{rely}</div>"
            "</div>"
            f"<div class='lp-steps-sec' lang='en'><div class='lp-h2'>How It Works</div><ol class='lp-steps'>{steps}</ol></div>")


def _start():
    ss.started = True


def landing_page():
    """The start page: the explanation, then the call to action below it, then the small print. The sidebar holds only
    the API key module (submitted version); "Open saved progress" sits next to "Start now"."""
    st.markdown(landing_html(title=True), unsafe_allow_html=True)
    with st.container(key="ctaband"):
        c1, c2 = st.columns([3, 2], vertical_alignment="center")
        c1.markdown("<div class='lp-cta-t'>Ready to Screen a Deal?</div><div class='lp-cta-x'>Enter the target and up "
                    "to five portfolio companies, or try one of the examples.</div>", unsafe_allow_html=True)
        with c2, st.container(horizontal=True, gap="small", vertical_alignment="center", horizontal_alignment="right"):
            st.button("Start now →", key="cta_start", on_click=_start)
            with st.popover("Open Saved Progress"):
                loader_box()
    st.markdown(f"<div class='lp-foot'>{LANDING_FOOT}</div>", unsafe_allow_html=True)


STEPS = {1: "Companies", 2: "Activities", 3: "Preliminary Assessment", 4: "Market Definitions", 5: "Summary"}
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
        with slot:
            st.iframe(SCROLL_TOP, height=1)      # our own constant script, never user input


def progress_nav(step):
    """The steps as tabs (plain words, the current step underlined in ink, steps not reached yet pale). Every step
    already reached can be opened again; nothing is deleted by going back."""
    reachable = {1: True, 2: bool(ss.get("acts")), 3: ss.get("results") is not None,
                 4: ss.get("results") is not None and bool(ss.get("precedents")),
                 5: summary_ready()}
    with st.container(horizontal=True, key="stepnav", gap="large"):
        for k, name in STEPS.items():
            st.button(f"{k} {name}", key=f"nav_{k}", type="primary" if k == step else "secondary",
                      disabled=not reachable[k], on_click=go_to, args=(k,))


user_key = credentials()       # the first screen until the key (or, in development, the password) is entered
step = ss.get("step", 1)
# The start page: the explanation in steps on a page of its own (step ① shows only the companies). Shown once per
# session, before anything is entered; a saved screen that is opened skips it, and
# "Start over" leads straight to step ①.
if not ss.get("started") and step == 1 and not ss.get("companies"):
    key_sidebar()                  # the only thing in the sidebar on the start page
    landing_page()                 # draws the title itself, in its left column
    st.stop()
st.title("EU Overlap Screen")
with st.expander("How This Tool Works"):
    st.markdown(landing_html() + f"<div class='lp-foot'>{LANDING_FOOT}</div>", unsafe_allow_html=True)
ai = make_ai(user_key)
if step == 2 and not ss.get("acts"):
    step = ss.step = 1
if step in (3, 4, 5) and ss.get("results") is None:
    step = ss.step = 2 if ss.get("acts") else 1
if (step == 4 and not ss.get("precedents")) or (step == 5 and not summary_ready()):
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