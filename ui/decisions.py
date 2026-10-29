"""
ui/decisions.py - the Commission decisions in the database (corpus/paragraphs.json) and those the lawyer added:
their paragraphs, case numbers, years and titles, and the paragraph references with the text on hover.
"""
import json
import re

import streamlit as st

from logic import precedents as prec

from ui.common import h, ss


@st.cache_data(show_spinner=False)
def builtin_paragraphs():
    """All paragraphs of the built-in corpus by id."""
    try:
        return {p["id"]: p for p in json.loads(open("corpus/paragraphs.json", encoding="utf-8").read())}
    except (OSError, ValueError):
        return {}


def corpus_paragraphs():
    """All paragraphs step ④ searches, by id (for the hover of a paragraph that a stored search did not keep, the
    reader and the lists of decisions): the built-in corpus, plus the decisions the lawyer added for this screen."""
    added = ss.get("uploads") or []
    if not added:
        return builtin_paragraphs()
    out = dict(builtin_paragraphs())
    for u in added:
        for p in u["paragraphs"]:
            out.setdefault(p["id"], p)
    return out


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
           + ("<br><span style='opacity:.7'>" + ("Added by you for this screen (not checked against the official "
                                                "version). " if p.get("user_provided") else "")
              + ("The paragraph exactly as the AI saw it." if seen else "The paragraph this rule of the app rests on.")
              + (" Click to open the decision." if url else "") + "</span>"))
    if url:
        return f"<a class='pref' href='{h(url)}' target='_blank'>{h(label)}<span class='pbox'>{box}</span></a>"
    return f"<span class='pref'>{h(label)}<span class='pbox'>{box}</span></span>"


def para_refs(pids, paras):
    return " ".join(para_ref(pid, paras) for pid in prec._sorted_ids(set(x for x in pids if x)))


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
    if not p:
        return case
    return f"{case} {p['title']} ({str(p['date'])[:4] or 'no date'})" + (" · added by you" if added_case(case) else "")


def added_case(case):
    """Whether paragraphs of this decision were added by the lawyer (a decision of its own, or paragraphs of a built-in
    decision that the database leaves out)."""
    return any(u["case"] == case for u in ss.get("uploads") or [])
