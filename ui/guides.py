"""
ui/guides.py - the guide box at the start of steps ②, ③ and ④: how the step works, how to read it, its limits.
"""
import re

import streamlit as st

from ui.common import plural, ss
from ui.labels import dots_html, OUTCOME_CLASS
from ui.decisions import builtin_paragraphs, para_ref


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
            "<span class='lab lab-q'>Existing relationship</span> the companies' own sources name each other.",
            "<span class='tag'>less likely</span> a horizontal label across levels without fully the same customers, or an input "
            "for a shop or wholesaler: shown folded, open “Details” for what it concerns; a view or a note shows it "
            "in full."]),
        ("Limits", [
            "<b>Deliberately generous:</b> unlikely links are shown too. A missed relationship is easily overlooked "
            "later; an unlikely one takes a second to dismiss.",
            "“Potential” until checked against the Commission's decisions in step ④.",
            "The judgement is yours: set your view on each label, add a note or use “Edit”. What you keep is the "
            "summary of step ⑤."])]),
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
            "{database}; a decision outside the database is not found. “No precedent” therefore means: not in this "
            "database, not: never defined by the Commission. A decision you find yourself can be added at the end of "
            "this step.",
            "Each decision describes the market at its time; the Commission is not bound by it {ref:Notice-14}.",
            "Levels of trade: a market counts for a company only at its own level (for a shop: the retail of the "
            "products it sells; for a manufacturer: the supply of its products). A market at another level is named "
            "as such, never counted as the company's own {ref:Notice-14}.",
            "Product markets only: geography and market shares, which decide whether a market is “affected”, are not "
            "assessed."])]),
}


def database_text():
    """'The database holds a limited set of decisions and the Market Definition Notice', from the corpus."""
    paras = builtin_paragraphs().values()
    notice = any(p.get("source_type") == "Commission notice" for p in paras)
    added = [u["case"] for u in ss.get("uploads") or []]
    return ("The database holds a limited set of decisions" + (" and the Market Definition Notice" if notice else "")
            + (f", plus {plural(len(added), 'decision')} you added ({', '.join(added)})" if added else ""))


def _refs(text):
    """{ref:Notice-14}: the paragraph with its text on hover, as everywhere in steps ③ and ④."""
    return re.sub(r"\{ref:([^}]+)\}", lambda m: para_ref(m.group(1), {}, seen=False), text)


def guide_html(step):
    title, cols = GUIDES[step]
    out = []
    for head, items in cols:
        def chip(m):
            return f"<span class='oc {OUTCOME_CLASS[m.group(1)]}' style='margin:0'>{m.group(1)}</span>"
        lis = "".join("<li>" + _refs(re.sub(r"\{chip:([^}]+)\}", chip, t.replace("{database}", database_text())))
                      + "</li>" for t in items)
        out.append(f"<div><div class='gh'>{head}</div><ul>{lis}</ul></div>")
    return f"<div class='guide'>{''.join(out)}</div>"


def guide_box(step):
    with st.expander(GUIDES[step][0], expanded=True):      # the same on every step: open, and the lawyer can fold it
        st.markdown(guide_html(step), unsafe_allow_html=True)
