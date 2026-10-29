"""
ui/sidebar.py - the sidebar: start over, save progress, the Word document, the legend of the current step, the
Commission decisions used, the run summary and the API key; in development also a deployment check.
"""
import time

import pandas as pd
import streamlit as st

from logic import activity_mapping as am
from logic import ai_client
from logic import export

from ui.common import call_count, DEV_MODE, esc, h, now_local, plural, PROFILE, run_summary, ss, stage_cost, USE_CACHE
from ui.credentials import key_sidebar
from ui.working_screen import reset_all
from ui.labels import dots_html, outcome_chip, OUTCOME_TIP
from steps.step5_summary import (DOCX_MIME, pending_warning, progress_bytes, progress_model, progress_name,
                                 report_model, summary_ready, word_name)
from ui.saved_screens import audit_json, audit_snapshot, loader_box
from ui.decision_reader import decision_entries, decision_reader, notice_reader


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
        from logic import retrieval           # swaps in pysqlite3 first, if it is installed
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
              + line("<span class='tag'>less likely</span>", "horizontal across levels, customers not fully the same; an "
                     "input for a shop",
                     "A horizontal label across different levels of trade (e.g. manufacturing v retail) where the two "
                     "companies do not have fully the same direct customers: different levels of trade are often "
                     "different markets (Market Definition Notice (14)), so a horizontal overlap is less likely; "
                     "whether both compete for the same customers is to be checked. A vertical input link to a shop "
                     "or wholesaler: such a company resells, so the input could only serve its own minor use. Such "
                     "a label is shown folded (open “Details”) and counted on one line in the summary; setting a "
                     "view or a note shows it in full."))
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
            entries = decision_entries()
            if entries:
                with st.expander("Commission Decisions", expanded=True):
                    st.caption("The decisions used in this screen; click to read one here, with the markets this "
                               "screen uses from it and its paragraphs highlighted.")
                    # no hover tooltip on these buttons: the window opens over it, so it would stay on the screen
                    for case, label, tip in entries:
                        if st.button(label, key=f"read_{case}", type="tertiary"):
                            (notice_reader if case == "Notice" else decision_reader)(case, tip)
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
