"""
ui/decision_reader.py - the decisions used in a screen (listed in the sidebar), and the reader that opens one
inside the app: its paragraphs as the database holds them, with those the screen uses highlighted, and the official
PDF.
"""
import os

import streamlit as st

from logic import precedents as prec

from ui.common import h, long_date, plural
from ui.decisions import added_case, builtin_paragraphs, corpus_paragraphs, decision_label, decision_text
from steps.step4_results import _best, CONCLUSION_TEXT, may_be_category, mname, SETTLED, used_markets


def decision_entries():
    """The sidebar's "Commission decisions": [(case, label, hover)] for each decision used in this screen (hover: the
    markets the screen uses from it), plus the Market Definition Notice. Each opens the reader."""
    used = used_markets()
    if not used:
        return []
    settled = {}
    for e in used.values():
        for m in e["markets"]:
            if m.get("conclusion") in SETTLED and m.get("decided_paragraph"):
                settled.setdefault(m["decided_paragraph"], set()).add(mname(m["name"]))
    by_case = {}
    for (case, key), e in used.items():
        by_case.setdefault(case, []).append(e)
    out = []
    for case in sorted(c for c in by_case if c and c != "Notice"):
        groups = {}
        for e in sorted(by_case[case], key=lambda x: x["name"].lower()):
            m = _best(e["markets"])
            segs = {n for pid in (m.get("product_paragraphs") or []) for n in settled.get(pid, set())} \
                - {mname(m["name"])}
            label = ("category divided into separate markets" if may_be_category(m) and segs
                     else CONCLUSION_TEXT.get(m.get("conclusion"), "defined"))
            groups.setdefault(label, []).append(mname(e["name"]))
        out.append((case, decision_label(case), " · ".join(f"{k}: {', '.join(v)}" for k, v in groups.items())))
    if corpus_paragraphs().get("Notice-14"):
        out.append(("Notice", "Market Definition Notice (2024)", "The Commission Notice on the definition of the "
                    "relevant market, used where no decision covers the products"))
    return out


# The reader: a decision (or the Notice) inside the app. Tab 1: its paragraphs as the app's database holds them (the
# parts on market definition the step ④ search reads), with the paragraphs this screen uses highlighted. Tab 2: the
# official document, if its PDF is stored in static/decisions/ (as downloaded from the Commission's website, or named
# "M5644.pdf" … "NOTICE.pdf"); otherwise a link to it. Display only: no AI call, no search.
NOTICE_RULES = {"14": "levels of trade (the app's rule)", "25": "same customers (the app's rule)",
                "88": "customer groups (the app's customer dots)"}
PDF_DIR = os.path.join("static", "decisions")


def paragraph_uses(case):
    """{paragraph number: [what this screen uses it for]} for one decision: the markets it defines, leaves open or
    describes (from the stored searches of the rows kept now)."""
    roles = (("decided_paragraph", "defines"), ("open_paragraph", "leaves open"),
             ("other_open_paragraph", "leaves open"), ("scope_paragraph", "scope of"))
    out = {}
    for e in used_markets().values():
        for m in e["markets"]:
            name = mname(m["name"])
            marked = set()
            for field, word in roles:
                pid = m.get(field) or ""
                if pid.rpartition("-")[0] == case:
                    out.setdefault(pid.rpartition("-")[2], []).append(f"{word} {name}")
                    marked.add(pid)
            for pid in m.get("product_paragraphs") or []:
                if pid.rpartition("-")[0] == case and pid not in marked:
                    out.setdefault(pid.rpartition("-")[2], []).append(f"on {name}")
    if case == "Notice":
        for n, why in NOTICE_RULES.items():
            out.setdefault(n, []).append(why)
    return {n: list(dict.fromkeys(v)) for n, v in out.items()}


def pdf_of(case, url):
    """The stored official PDF of a decision, as the path the app serves it under, or ''. Found by its name, whatever
    the spelling: the case number at the start ("M5644.pdf", "m5644_20100106_20212_en.pdf"); for the Notice "NOTICE.pdf"
    or the file as downloaded from EUR-Lex (its number, 202401645, in the name)."""
    try:
        files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))
    except OSError:
        return ""
    flat = case.replace(".", "").lower()
    for f in files:
        name = f.lower().replace(".", "", 1) if f.lower().startswith("m.") else f.lower()
        if (name.startswith("notice") or "202401645" in name) if case == "Notice" else name.startswith(flat):
            return f"app/static/decisions/{f}"
    return ""


def para_num(p):
    return int(p["para"]) if str(p.get("para", "")).isdigit() else 10 ** 6


def reader_body(case, markets=""):
    paras = sorted((p for pid, p in corpus_paragraphs().items() if pid.startswith(case + "-")), key=para_num)
    if not paras:
        st.write("This document is not in the app's database.")
        return
    first = paras[0]
    url = first.get("url") if str(first.get("url") or "").startswith("https://") else ""
    name = "Market Definition Notice" if case == "Notice" else f"{case} {first.get('title', '')}"
    meta = " · ".join(x for x in (long_date(first.get("date")), decision_text(first.get("decision"))
                                  if case != "Notice" else first.get("title", "")) if x)
    st.markdown(f"<div class='rd-t'>{h(name)}</div><div class='rd-m'>{h(meta)}"
                + (f" · <a href='{h(url)}' target='_blank'>official version</a>" if url else "") + "</div>"
                + (f"<div class='rd-mk'><b>Markets this screen uses from it</b> · {h(markets)}</div>"
                   if markets and case != "Notice" else ""),
                unsafe_allow_html=True)
    uses = paragraph_uses(case)
    t1, t2 = st.tabs(["In the App's Database", "Original Document"])
    with t1:
        st.caption(f"The {plural(len(paras), 'paragraph')} of this document in the database that step ④ searches "
                   "(its parts on market definition), word for word. Highlighted: the paragraphs this screen uses."
                   + (" Paragraphs you added are marked “added by you”." if added_case(case) else ""))
        only = st.toggle("Only the paragraphs used in this screen", key=f"rd_only_{case}", value=False) \
            if uses else False
        if uses and not only:
            jumps = " ".join(f"<a href='#rd-{h(case)}-{n}'>({n})</a>" for n in sorted(uses, key=lambda x: int(x)
                                                                                     if x.isdigit() else 10 ** 6))
            st.markdown(f"<div class='rd-j'>Used in this screen: {jumps}</div>", unsafe_allow_html=True)
        out, last = [], None
        for p in paras:
            n = str(p.get("para"))
            if only and n not in uses:
                continue
            heads = prec.headings_of(p)
            if heads != last:
                out.append(f"<div class='rd-h'>{h(heads.replace(' > ', ' › '))}</div>")
                last = heads
            notes = "".join(f"<div class='rd-fn'><sup>{h(f.get('n'))}</sup> {h(f.get('text'))}</div>"
                            for f in p.get("footnotes") or [])
            use = (f"<div class='rd-u'>Used in this screen: {h('; '.join(uses[n]))}</div>" if n in uses else "")
            if p.get("user_provided"):
                use = "<div class='rd-u'>Added by you</div>" + use
            out.append(f"<div class='rd-p{' used' if n in uses else ''}' id='rd-{h(case)}-{h(n)}'>"
                       f"<span class='rd-n'>({h(n)})</span>{use}<div>{h(p.get('text'))}</div>{notes}</div>")
        st.markdown("<div class='rd'>" + "".join(out) + "</div>", unsafe_allow_html=True)
    with t2:
        src = pdf_of(case, url)
        if src:
            st.markdown(f"<iframe class='rd-pdf' src='{h(src)}' title='{h(name)}'></iframe>", unsafe_allow_html=True)
            st.caption("The official document as published. Paragraph numbers are in the margin of the text.")
        elif added_case(case) and not any(p.get("case") == case for p in builtin_paragraphs().values()):
            st.write("You added this decision for this screen; the app keeps its paragraphs, not the file.")
            if url:
                st.markdown(f"[Open the official version]({url})")
        else:
            st.write("The official document is not stored in this app.")
            if url:
                st.markdown(f"[Open it on the {'EUR-Lex' if 'eur-lex' in url else 'Commission'}'s website]({url})")


@st.dialog("Commission Decision", width="large")
def decision_reader(case, markets=""):
    reader_body(case, markets)


@st.dialog("Commission Notice", width="large")
def notice_reader(case, markets=""):
    reader_body(case, markets)
