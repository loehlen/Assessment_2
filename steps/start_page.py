"""
steps/start_page.py - the start page: what a preliminary overlap screen is, how the tool works in five steps,
and what the lawyer can rely on.
"""
import streamlit as st

from ui.common import ss
from ui.saved_screens import loader_box


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
    ("Companies", "The target, and up to five companies the buyer owns, or simply the buyer itself."),
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
            "does the company to be bought (the <i>target</i>) meet the businesses the buyer already has (the "
            "<i>portfolio companies</i>)? For an investor such as a private equity fund, these are the companies it "
            "owns; for a company buying another, the buyer itself.</div>"
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
