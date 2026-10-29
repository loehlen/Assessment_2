"""
app.py - EU Overlap Screen (LAWS90286 Assignment 2): a preliminary EU merger control overlap screen.

This file is the entry point (streamlit run app.py). It only sets up the page, asks for the API key and shows the
current step; each step lives in its own file:

    steps/start_page.py              the start page
    steps/step1_companies.py         ① Companies: the input, and the research of each company
    steps/step2_activities.py        ② Activities: checking and editing what each company does
    steps/step3_assessment.py        ③ Preliminary Assessment: the comparison and the labels of each row
    steps/step3_4_table.py           the table screen of steps ③ and ④
    steps/step4_search.py            ④ Commission Market Definitions: the search in the decisions
    steps/step4_results.py           ④ what the decisions say about each row
    steps/step5_summary.py           ⑤ Summary, and the content of the Word document
    ui/                              building blocks shared by the steps (sidebar, sources, labels, style, ...)
    logic/                           the workflow without the interface: AI calls, prompts, rules, search, Word export

Geography is not part of the screen. Going back never deletes anything: a changed company is researched again and
only new or changed pairs are compared again (stable activity IDs and content keys); dismissals and notes stay with
their pair.

Settings (.env locally, Secrets on Streamlit Cloud):
    DEV_MODE=1, APP_PASSWORD, OPENAI_API_KEY      development: password gate, cost counter, development tools
    MODEL_PROFILE=dev | final                      the models per step (logic/ai_client.py); default: dev with
                                                   DEV_MODE on, final with DEV_MODE off (the submitted version)
    USE_CACHE=1                                    development only: reuse calls already paid for
With DEV_MODE off (the submitted version) the user enters their own OpenAI key in the course's API Credentials sidebar
module (ui/api_key.py); it is kept for the session only.
"""
import streamlit as st

from logic import ai_client

from ui.theme import APP_CSS
from ui.common import go_to, ss
from ui.credentials import credentials, key_sidebar, make_ai
from ui.sidebar import sidebar_panel
from steps.start_page import LANDING_FOOT, landing_html, landing_page
from steps.step1_companies import run_mapping, stage_companies
from steps.step2_activities import remap_company, stage_activities
from steps.step3_assessment import confirm_activities
from steps.step3_4_table import stage_overview
from steps.step4_search import run_precedents
from steps.step5_summary import stage_summary, summary_ready

st.set_page_config(page_title="EU Overlap Screen", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
st.html(APP_CSS)            # style only: takes no space on the page
ss.setdefault("log", ai_client.CallLog())     # every AI call of this session
ss.setdefault("stage_logs", {})               # per stage: [(first, last) position in the call log, seconds], one per run
ss.setdefault("run_first", 0)                 # position in the call log where the current screen started
ss.setdefault("acts_version", 0)              # a new version = fresh widgets for the activity lists in step ②


# =============================================================== the job of a working screen
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


# =============================================================== navigation
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


# =============================================================== the page
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
