"""
ui/activity_display.py - how a company's activities and their sources are shown (steps ②, ③ and ⑤): the stage of
the supply chain, the source marks (✔ ≈ ○ ⚠) with the quotation on hover, an activity in everyday words, and an
existing relationship between two companies.
"""
import html
import re

from logic import activity_mapping as am
from logic import comparison as cmp
from logic import rules

from ui.common import capital, h, he, ss, words_list


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
               "to confirm the quotation: {reason}.",
    "no text": "The search read this page and the activity is based on it, but the app could not read it, so it could "
               "not confirm the quotation: {reason}.",
    "error": "The search read this page and the activity is based on it, but the app could not open the page itself to "
             "confirm the quotation: {reason}.",
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
                              "The search read this page, but the app could not confirm the quotation: {reason}.")
    return (tip + f"\n\n{TRUST_HEAD['not checked']}\n" + why.format(reason=plain_reason(reason) or "no reason given")
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
    # first the rows where one company's activity names the other company (e.g. a brand of the other company that
    # it distributes): that row is the relationship itself; then the portfolio company's activity named in the
    # passages (it differs from row to row), then the target's, else every kept row
    def names_other(act, other):
        words = " ".join(_row_words(act) + [act.get("description") or ""]).lower()
        return any(re.search(r"(?<!\w)" + re.escape(n.lower()) + r"(?!\w)", words) for c in ss.companies
                   if c["name"] == other for n in am.names_of(c) if len(n) > 2)
    hit = ({cmp.pair_id(r) for r in rows if names_other(r["b"], target) or names_other(r["a"], portco)}
           or {cmp.pair_id(r) for r in rows if named(_row_words(r["b"]))}
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


SOURCE_STATE = {          # a page the app could open needs no remark; only the exceptions are marked
    "blocked": "○ read by the search only: the app could not open it",
    "no text": "○ read by the search only: the app could not read it",
    "error": "○ read by the search only: the app could not open it",
    "off": "○ read by the search only: the app's check is switched off",
}


# The reasons of the source check (sources.py) in plain words, without brackets inside brackets. Saved files keep
# the original wording; it is translated here, when shown.
PLAIN_REASON = {
    "page shows almost no text (probably built by JavaScript)":
        "the page shows almost no text, probably because it is built by JavaScript",
    "PDF without text (probably scanned)": "the PDF holds no text, probably because it is scanned",
    "the domain does not exist (any more)": "the domain no longer exists",
    "the domain could not be looked up just now (temporary failure)": "the domain could not be looked up just now",
    "the domain could not be looked up (network problem on the app's side?)":
        "the domain could not be looked up, perhaps because of a network problem on the app's side",
    "PDF reader missing (pypdf)": "the app's PDF reader is missing",
    "source check switched off (CHECK_SOURCES=0)": "the app's check is switched off",
}


def plain_reason(reason):
    """The reason in plain words; a technical code at the end (an HTTP status, the name of a Python error) is left
    out: it stays in the audit log."""
    r = (reason or "").strip()
    r = PLAIN_REASON.get(r, r)
    r = re.sub(r"\s*\((?:HTTP \d{3}|\w*(?:Error|Exception|Timeout)\w*)\)$", "", r)
    return {"could not be opened": "the app could not open it",
            "PDF could not be read": "the PDF could not be read"}.get(r, r)


def short_name(a):
    return other_name(a) if rules.category(a) == "other" else capital(a["product"])
