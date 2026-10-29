"""
ui/upload_box.py - "Add a Commission decision" at the end of step ④: the lawyer adds a decision the database does
not hold (a PDF or a pasted extract), for this screen only. The reading and embedding is in logic/uploads.py.
"""
import hashlib
import re

import streamlit as st

from logic import precedents as prec
from logic import uploads

from ui.common import esc, h, plural, ss
from ui.decisions import builtin_paragraphs


# For products the built-in database does not cover: the lawyer adds a Commission merger decision (the PDF, or its text
# pasted) for this screen. Parsed by the same functions as the built-in corpus, searched together with it, quoted and
# checked like it; kept in the session and the progress file only. No AI call: one embedding request when it is added.
UPLOAD_HELP = ("A Commission merger decision (case number M.1234), as published on the Commission's website. Its "
               "numbered paragraphs are read like those of the built-in decisions; by default only the parts on market "
               "definition are used, as in the built-in database.")


def _upload_source():
    """(text, origin, error) of the decision being added, read once per file or text (kept by its hash)."""
    mode = st.radio("The decision as", ["PDF", "Pasted text"], horizontal=True, key="up_mode",
                    label_visibility="collapsed")
    if mode == "PDF":
        f = st.file_uploader("The decision (PDF)", type=["pdf"], key=f"up_pdf_{ss.get('up_nonce', 0)}",
                             help=UPLOAD_HELP)
        if f is None:
            return None, "", ""
        data = f.getvalue()
        key = hashlib.sha256(data).hexdigest()[:12]
        cache = ss.setdefault("up_read", {})
        if key not in cache:
            try:
                cache[key] = uploads.read_pdf(data)
            except Exception as e:  # noqa: BLE001 - a damaged or protected PDF: said, never raised
                return None, f.name, f"The PDF could not be read ({type(e).__name__}: {e}). Paste its text instead."
        text, tool = cache[key]
        ss.up_tool = tool
        return text, f.name, ""
    text = st.text_area("The decision's text", key=f"up_text_{ss.get('up_nonce', 0)}", height=180,
                        placeholder="Paste the decision, or its paragraphs on market definition (e.g. as copied from "
                                    "a legal database), each with its number: “(42) In previous decisions, the "
                                    "Commission …”", help=UPLOAD_HELP)
    ss.up_tool = "pasted text"
    return (text if text.strip() else None), "pasted text", ""


def upload_box(ai):
    added = ss.setdefault("uploads", [])
    label = "Add a Commission Decision or Extract" + (f" ({len(added)} added)" if added else "")
    with st.expander(label, expanded=bool(ss.pop("up_open", False))):
        st.caption("For products the app's database does not cover, add a Commission merger decision you know, as a PDF "
                   "or as the paragraphs on market definition copied from a database: step ④ then searches it together "
                   "with the database, for this screen only, and marks it “added by you”. Quotations are checked word "
                   "for word against the text you added, not against the official version: include the paragraphs "
                   "with the Commission's own conclusion. It is kept in “Save progress”; the app stores nothing.")
        if ss.get("up_msg"):
            st.success(ss.pop("up_msg"))
        for k, u in enumerate(added):
            c = st.columns([10, 2], vertical_alignment="center")
            nums = uploads.ranges_text([p["para"] for p in u["paragraphs"]])
            c[0].markdown(f"**{esc(u['case'])} {esc(u['title'])}** ({esc(str(u.get('date') or '')[:4] or 'no date')})"
                          f" · {plural(len(u['paragraphs']), 'paragraph')}: {esc(nums)} · "
                          f":gray[{esc(u.get('origin') or '')}]")
            if c[1].button("Remove", key=f"up_rm_{u['case']}", type="tertiary"):
                added.pop(k)
                ss.up_msg = f"{u['case']} removed."
                ss.up_open = True
                st.rerun()
        text, origin, error = _upload_source()
        if error:
            st.error(error)
            return
        if text is None:
            return
        meta = uploads.detect(text)
        key = hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()[:10]
        c = st.columns([2, 5, 2])
        case_in = c[0].text_input("Case number", value=meta["case"], key=f"up_case_{key}", placeholder="M.1234")
        title_in = c[1].text_input("Title", value=meta["title"], key=f"up_title_{key}",
                                   placeholder="e.g. Alpha / Beta")
        date_in = c[2].text_input("Date", value=meta["date"], key=f"up_date_{key}", placeholder="YYYY-MM-DD")
        url_in = st.text_input("Link to the official version (optional)", key=f"up_url_{key}",
                               placeholder="https://ec.europa.eu/competition/mergers/cases/…")
        case = uploads.normalise_case(case_in)
        if not case:
            st.error("Enter the case number of a Commission merger decision, e.g. M.1234.")
            return
        if any(u["case"] == case for u in added):
            st.error(f"{case} is already added. Remove it first to add it again with other paragraphs.")
            return
        if date_in.strip() and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_in.strip()):
            st.error("Enter the date as YYYY-MM-DD, or leave it empty.")
            return
        builtin = builtin_paragraphs()
        info = {"case": case, "title": title_in.strip(), "date": date_in.strip(), "decision": meta["decision"],
                "url": url_in.strip() if url_in.strip().startswith("https://") else ""}
        # parsed once per text and details (about a second for a long decision; the page reruns on every click)
        parsed = ss.setdefault("up_parsed", {})
        pkey = (key, case, info["title"], info["date"], info["url"])
        if pkey not in parsed:
            parsed.clear()
            parsed[pkey] = uploads.parse(text, info, builtin)
        records, style, n_notes, skipped = parsed[pkey]
        if skipped:
            st.info(f"{case} is already in the app's database (paragraphs {uploads.ranges_text(skipped)}): only "
                    "its other paragraphs can be added. Title, date and link are those of the database.")
        # a pasted extract can be a single paragraph (the Commission's conclusion); a PDF with so few was not read
        if len(records) + len(skipped) < (1 if origin == "pasted text" else uploads.MIN_PARAGRAPHS):
            st.error("No numbered paragraphs were found in this text. "
                     + ("The PDF may be a scan, or its layout was not read (try pasting its text). "
                        if origin != "pasted text" else
                        "Each paragraph must start with its number, e.g. “(12) …” or “12. …”, on a new line."))
            return
        if not records:
            st.warning("Every paragraph found is already in the app's database: nothing to add.")
            return
        ranges_in = st.text_input(
            "Paragraphs to use", value=uploads.default_ranges(records), key=f"up_ranges_{key}",
            help="Proposed: the parts on market definition, as found from the decision's headings. Change the ranges "
                 "if the decision defines markets elsewhere too (e.g. in the competitive assessment).")
        chosen = uploads.select(records, ranges_in)
        if chosen is None:
            st.error("Write the paragraphs as numbers and ranges, e.g. “12-49, 92, 117”.")
            return
        st.caption(f"Read with {ss.get('up_tool', '')}: {plural(len(records), 'numbered paragraph')} "
                   f"({uploads.ranges_text([r['para'] for r in records])}), {plural(n_notes, 'footnote')}; "
                   f"{len(chosen)} selected.")
        if chosen:
            p0 = chosen[0]
            st.markdown(f"<div class='cnote' style='font-size:.85rem;margin-bottom:.6rem'><b>({p0['para']})</b> "
                        f"{h(prec.headings_of(p0).replace(' > ', ' › '))}<br>{h(p0['text'][:320])}"
                        f"{'…' if len(p0['text']) > 320 else ''}</div>", unsafe_allow_html=True)
        if st.button(f"Add {case} to this screen", type="primary", disabled=not chosen, key=f"up_add_{key}",
                     help="One embedding request (a fraction of a cent) turns its paragraphs into numbers for the "
                          "search. No AI call."):
            upload = uploads.make_upload(info, chosen, origin, skipped)
            try:
                with st.spinner(f"Preparing {plural(len(chosen), 'paragraph')} for the search …"):
                    uploads.embed_upload(upload, lambda texts: ai.embed(texts, note=f"decision added: {case}",
                                                                        step="embed_upload"))
            except Exception as e:  # noqa: BLE001 - nothing is added; the lawyer can try again
                st.error(f"{case} could not be added ({type(e).__name__}: {e}). Nothing was changed.")
                return
            added.append(upload)
            ss.up_nonce = ss.get("up_nonce", 0) + 1          # clears the file and the text field
            ss.pop("up_parsed", None)
            ss.pop("up_read", None)
            ss.up_msg = (f"{case} added ({plural(len(chosen), 'paragraph')})."
                         + ("" if ss.get("precedents") else " Press “Find Commission market definitions” to search it "
                                                            "together with the database."))
            ss.up_open = True
            st.rerun()
