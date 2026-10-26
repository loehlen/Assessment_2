"""
rules.py - the sector-neutral rules of the overlap screen.

Only rules that hold in every sector live here:
  - the fixed answer lists for the activity overview (value-chain levels, direct-customer types, ...)
  - anonymisation: the abstract that is sent for comparison, and the name check
  - customer overlap (sorts horizontal candidates, never removes them)
  - vertical signals from the facts (input supply, resale)
  - the decision rule that combines the AI comparison with the code signals
  - the EEA check

No sector knowledge lives here: which products are related, or which inputs go into which
outputs, is judged by the AI on anonymised pairs of activities (step ③), and what the
Commission found comes from the decisions in the corpus (step ④).

Pure Python, no API calls, so it can be tested for free:  python rules.py
"""
import math
import re
import unicodedata

# =============================================================== answer lists (used by schemas.py)
VALUE_CHAIN_LEVELS = {
    "raw materials": "growing, extracting, sourcing or trading unprocessed commodities",
    # Defined by the BUYER'S USE, not by the nature of the goods, following the Vertical Guidelines (2022/C 248/01)
    # para 287 ("Intermediate goods or services are sold to undertakings for use as an input to produce other goods or
    # services [...]. Final goods or services are, directly or indirectly, sold to end users") and para 3 (end users
    # include undertakings).
    "intermediate products": "processed goods sold to businesses that use them as an input to produce their own goods "
                             "or services (processed, built in or used up; usually no longer recognisable in the "
                             "result), whatever the goods are called",
    "finished products": "goods the company makes and sells, directly or through distributors, to end users: "
                         "consumers, or businesses that use them themselves rather than as an input",
    # Selling one's own goods through distributors is not wholesale (otherwise the AI tends to call it wholesale)
    "wholesale / distribution": "reselling goods made by OTHER companies to businesses (selling the company's own goods "
                                "through its own sales companies or distributors is not wholesale)",
    "retail": "selling to consumers through own shops, outlets or an own online shop",
    "services": "services rather than goods",
    "other": "fits none of the above",
}

DIRECT_CUSTOMER_TYPES = {
    "consumers": "private individuals buying for their own use",
    "retailers": "shops and online retailers that resell to consumers",
    "wholesalers / distributors": "businesses that resell to other businesses",
    "manufacturers / processors": "businesses that use the product to make their own products "
                                  "(including craft businesses)",
    "other businesses": "businesses that use the product themselves (e.g. hotels, restaurants, offices)",
    "public sector": "public authorities and institutions",
    "internal use (captive)": "used within the company's own group, not sold",
    "not stated": "the sources do not say",
}

END_USERS = ["consumers", "businesses", "consumers and businesses", "not stated"]
# Defined, not listed by example (sector-neutral): main = offered to customers as a business in its
# own right (at most MAX_MAIN per company); other = not offered on the market (own use), or a side line that exists
# to support or promote the main business. Size is never a criterion. All "other" lines of a company are merged in
# code into ONE line, "Other activities", which is compared once, like any activity.
CATEGORIES = ["main", "other"]
MAX_MAIN = 5
# Fields of an activity that record what the lawyer did with it (saved in the edit form, edited, names confirmed), not
# what the activity is: they never make an activity count as changed, so they never send its pairs to the AI again or
# make its step ④ search out of date (the content keys in comparison.py, app.py and precedents.py leave them out).
STATE_FIELDS = ("level_checked", "edited_by_user", "typed_names_confirmed")
STATUS = ["on the market", "in development", "not stated"]

# Answer lists for the factual comparison (one anonymised pair per AI call)
PRODUCT_RELATIONS = [
    "same product",
    "similar product, possibly substitutable",
    "different product",
    "not enough information",
]
HORIZONTAL_RELATIONS = {"same product", "similar product, possibly substitutable"}
VERTICAL_LINKS = [
    "A could be an input for B",
    "B could be an input for A",
    "A could be resold by B",
    "B could be resold by A",
]

# Groups used by the vertical signals
RESELLERS = {"retailers", "wholesalers / distributors"}
INPUT_BUYERS = {"manufacturers / processors"}
RESELLER_LEVELS = {"retail", "wholesale / distribution"}
INPUT_SELLER_LEVELS = {"raw materials", "intermediate products"}
# A resale link needs a reseller: Form CO (25)(f) requires activity in the downstream market, and selling one's
# own products to retailers is not itself retail or wholesale. "other" is kept because it cannot be told.
RESELLER_OR_UNCLEAR_LEVELS = {"retail", "wholesale / distribution", "other"}

# =============================================================== thresholds
# Cosine similarity of text-embedding-3-large vectors, set low enough that no expected overlap of the test cases is
# lost (over-inclusive by design).
INPUT_MATCH = 0.50          # A's product is this close to one of B's listed inputs -> input signal
RESALE_MATCH = 0.50         # A's product is this close to B's retail / wholesale range -> resale signal
                            # (in testing, real resale pairs scored well above it, wrong links just below it)


# =============================================================== anonymisation
AND_CO = re.compile(r"\s*&\s*Co\.?(?!\w)", re.IGNORECASE)
LEGAL_FORMS = re.compile(
    r"\s*,?\s*(?<!\w)(AG|SE|GmbH|mbH|KG|KGaA|OHG|Co\.|S\.A\.|SA|SAS|Ltd\.?|Limited|plc|Inc\.?|"
    r"LLC|B\.V\.|BV|N\.V\.|NV|S\.p\.A\.|SpA|S\.r\.l\.|Srl|Group|Holding)(?!\w)\.?",
    re.IGNORECASE,
)
MIN_NAME_LENGTH = 3


def name_variants(names):
    """All forms of the entered names, group companies and brands that must never reach a comparison."""
    variants = set()
    for name in names:
        name = (name or "").strip()
        if not name or name.lower() == "not stated":
            continue
        short = LEGAL_FORMS.sub("", AND_CO.sub("", name)).strip(" ,&")
        for form in {name, short}:
            if not form:
                continue
            for spelling in {form, _without_accents(form), _german_spelling(form)}:
                variants.update({spelling, spelling.replace("&", "and"), spelling.replace(" & ", " ")})
    return {v for v in variants if len(v) >= MIN_NAME_LENGTH}


# "&", "+" and "and" only (language-neutral)
NAME_JOINER = re.compile(r"\s*(?:&|\+|\band\b)\s*", re.IGNORECASE)
MIN_PART_LENGTH = 4


def name_parts(names):
    """The parts of company names joined by "&", "and" or "+": "Smith & Jones" -> "Smith", "Jones".
    Everyday language uses the short forms, which the guard and the name removal must also recognise. Only for the
    entered company names and their other names (brands such as "Salt & Pepper" may be ordinary words); each part
    needs at least 4 letters after the legal form is removed."""
    parts = []
    for name in names or []:
        short = LEGAL_FORMS.sub("", AND_CO.sub("", (name or "").strip())).strip(" ,&")
        pieces = [p.strip(" ,.") for p in NAME_JOINER.split(short)]
        if len(pieces) > 1:
            parts += [p for p in pieces if len(re.sub(r"\W", "", p)) >= MIN_PART_LENGTH]
    return list(dict.fromkeys(parts))


def _without_accents(text):
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))


def _german_spelling(text):
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss")):
        text = text.replace(a, b)
    return text


def _name_pattern(variant):
    # word boundaries that also work for names ending in punctuation (e.g. "PiCK UP!")
    return re.compile(r"(?<!\w)" + re.escape(variant) + r"(?!\w)", re.IGNORECASE)


def find_names(text, names):
    """Returns the names (or name variants) that appear in the text. Empty list = clean."""
    found = []
    for variant in sorted(name_variants(names), key=len, reverse=True):
        if _name_pattern(variant).search(text or ""):
            found.append(variant)
    return found


def redact(text, names):
    """Replaces every name variant with [name removed], longest first."""
    for variant in sorted(name_variants(names), key=len, reverse=True):
        text = _name_pattern(variant).sub("[name removed]", text or "")
    return text


def _join(values, sep=", "):
    values = [v for v in (values or []) if v and v != "not stated"]
    return sep.join(values) if values else "not stated"


def build_abstract(activity, names):
    """
    The anonymised profile of one activity, as sent to the factual comparison.
    Left out on purpose: entity, brands, business area, sector, countries (geography is a later,
    separate step), sources and evidence. Names and brands are removed in code; the second
    return value lists any name that is still found (must be empty, otherwise the call is blocked).
    """
    customers = _join(activity.get("direct_customers"))
    details = activity.get("customer_details") or "not stated"
    if details != "not stated":
        customers += f" ({details})"
    lines = [
        f"Product: {activity.get('product', 'not stated')}",
        # items separated by semicolons: an item may itself contain commas, and the comparison names the
        # items that meet, which code then checks against this list (check_items)
        f"Includes: {_join(activity.get('includes'), sep='; ')}",
        f"Description: {activity.get('description', 'not stated')}",
        f"Intended use: {activity.get('intended_use', 'not stated')}",
        f"Main inputs: {_join(activity.get('main_inputs'))}",
        f"Level of trade: {activity.get('value_chain_level', 'not stated')}",
        f"Direct customers: {customers}",
        f"End users: {activity.get('end_users', 'not stated')}",
        f"Sales channels: {activity.get('sales_channels', 'not stated')}",
        f"Status: {activity.get('status', 'not stated')}",
    ]
    text = redact("\n".join(lines), names)
    return text, find_names(text, names)


def activity_items(activity):
    """The items of one activity as the comparison sees them: its product line, then each entry of 'includes'."""
    items = [activity.get("product", "")] + [i for i in activity.get("includes") or [] if i and i != "not stated"]
    return [i for i in items if i and i.strip()]


def _norm(text):
    return re.sub(r"\s+", " ", text or "").strip(" .;,:").lower()


def check_items(given, items, names):
    """
    Code check of the items the AI says meet (like the check of source numbers): each must be one of
    the activity's own items as the AI saw them (product line or an entry of 'includes', names removed). An item the
    AI shortened or extended is accepted only if it matches exactly one item. Returns (items in their original
    wording, rejected items); a rejected item is shown in the audit trail, never in the assessment.
    """
    shown = [_norm(redact(i, names)) for i in items]
    found, rejected = [], []
    for g in given or []:
        n = _norm(g)
        idx = shown.index(n) if n in shown else None
        if idx is None and n:
            near = [k for k, s in enumerate(shown) if s and (n in s or s in n)]
            idx = near[0] if len(near) == 1 else None
        if idx is None:
            rejected.append(g)
        elif items[idx] not in found:
            found.append(items[idx])
    return found, rejected


def product_text(activity):
    """The text that is embedded to measure how close two products are (no customers, no levels)."""
    includes = _join(activity.get("includes"))
    includes = f" Includes: {includes}." if includes != "not stated" else ""
    return (f"{activity.get('product', '')}.{includes} {activity.get('description', '')} "
            f"Used for: {activity.get('intended_use', '')}")


# =============================================================== similarity
def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return dot / (nu * nv) if nu and nv else 0.0


def best_input_match(product_vector, input_vectors):
    """Highest similarity between a product and any of the other activity's listed inputs."""
    return max((cosine(product_vector, v) for v in input_vectors), default=0.0)


# =============================================================== customer overlap (tier 2)
def customer_overlap(customers_a, customers_b):
    """
    Sorts horizontal candidates by direct customers; never removes a pair.
    ●●● same direct customers, ●●○ partly overlapping, ●○○ different, ? not stated on one side.
    A customer group forms a distinct market only where suppliers can discriminate between groups and the three
    cumulative conditions of the Market Definition Notice are met ((24), (88)-(89)); the code cannot check them, so
    the customer score only sorts and is never a reason to remove a pair.
    """
    a = set(customers_a or []) - {"not stated"}
    b = set(customers_b or []) - {"not stated"}
    if not a or not b:
        return "?"
    if a == b:
        return "●●●"
    if a & b:
        return "●●○"
    return "●○○"


# =============================================================== vertical signals (code)
def sells_inputs(activity):
    """The activity supplies other producers: sold to manufacturers / processors, or upstream level."""
    return bool(set(activity.get("direct_customers") or []) & INPUT_BUYERS) or \
        activity.get("value_chain_level") in INPUT_SELLER_LEVELS


def sells_to_resellers(activity):
    return bool(set(activity.get("direct_customers") or []) & RESELLERS)


def is_reseller(activity):
    return activity.get("value_chain_level") in RESELLER_LEVELS


def captive_only(activity):
    """Produced only for the group's own use: not active on the merchant market (Draft Merger Guidelines
    para 103(i)). Shown as a flag on every pair with this activity. An own-use activity cannot be the supplying side
    of a vertical link (check_ai_links); the pair is then listed under "No overlap found" with the reason, and can be
    added back."""
    customers = set(activity.get("direct_customers") or []) - {"not stated"}
    return customers == {"internal use (captive)"}


def category(activity):
    """'main' or 'other'. Production only for the group's own use is always 'other', whatever the AI said."""
    if captive_only(activity) or activity.get("category") == "other":
        return "other"
    return "main"


def level_hint(activity, own_names=()):
    """A hint for step ② (deliberately rare): 'finished products' although the only buyers named are manufacturers or
    processors, i.e. businesses that probably use the goods as an input (Vertical Guidelines para 287). The tool
    proposes, the lawyer decides: nothing is changed, and the hint disappears once the activity has been saved in the
    edit form (even unchanged).
    Second case: "wholesale / distribution" although every brand on the line is the company's own (own_names:
    its entered names, group companies and the brands of its other lines). Wholesale means reselling goods made by
    others; selling one's own goods through own sales companies or distributors is not wholesale."""
    if activity.get("level_checked"):
        return ""
    if activity.get("value_chain_level") == "wholesale / distribution":
        brands = [b for b in activity.get("brands") or [] if b and b != "not stated"]
        if brands and own_names and all(find_names(b, own_names) for b in brands):
            return ("Level of trade possibly not “wholesale”: the brands on this line are the company's own. Wholesale "
                    "means reselling goods made by other companies; selling one's own goods through own sales "
                    "companies, distributors or retailers keeps the level of the goods (usually “finished products”). "
                    "Check, and correct with “Edit” if needed.")
        return ""
    if activity.get("value_chain_level") != "finished products":
        return ""
    buyers = {c for c in activity.get("direct_customers") or [] if c and c != "not stated"}
    if "manufacturers / processors" in buyers and buyers <= {"manufacturers / processors", "other businesses"}:
        return ("Level of trade possibly “intermediate products”: the only buyers named are manufacturers or "
                "processors, who usually use goods as an input to produce their own (Vertical Guidelines para 287: "
                "intermediate goods are “sold to undertakings for use as an input to produce other goods or "
                "services”; final goods are sold to end users). Check, and correct with “Edit” if needed.")
    return ""


def merge_other(activities):
    """The extraction's "other" lines, sorted in code into the two things they can be:
    - a side line sold to third parties (e.g. a café, merchandise, sales to businesses): an activity like any other.
      It keeps its own line and level of trade and is compared like a main activity (category "main", marked
      "side_line" for the display);
    - production or services only for the group's own use: not offered on the market, so not compared. All of a
      company's own-use lines become ONE line, "Own use", listed item by item under "includes" and marked as not
      compared (excluded, "own_use"); the lawyer can include it with "Edit". The original lines are kept under
      "merged_from" for the audit trail."""
    # A line whose product is not stated is never merged (it would become the item "not stated" and its name would
    # disappear); it stays its own question for the company, as a main line.
    gaps = [dict(a, category="main") for a in activities if is_gap(a)]
    main = [a for a in activities if category(a) == "main" and not is_gap(a)]
    others = [a for a in activities if category(a) == "other" and not is_gap(a)]
    side = [dict(a, category="main", side_line=True) for a in others if not captive_only(a)]
    own = [a for a in others if captive_only(a)]
    if not own:
        return main + side + gaps

    def uniq(values):
        out = []
        for v in values:
            if v and v != "not stated" and v not in out:
                out.append(v)
        return out

    items = []
    for a in own:
        inc = [i for i in a.get("includes") or [] if i and i.strip().lower() != a.get("product", "").strip().lower()]
        items.append(a.get("product", "") + " " + OWN_USE_MARK + (f" ({', '.join(inc[:4])})" if inc else ""))
    merged = {
        "business_area": "own use", "sector": "; ".join(uniq(a.get("sector") for a in own)) or "not stated",
        "entity": ", ".join(uniq(a.get("entity") for a in own)) or "not stated",
        "brands": uniq(b for a in own for b in a.get("brands") or []),
        "category": "other",
        "category_reason": "Production or services only for the group's own use, merged into one line",
        "product": "Own use",
        "includes": items,
        "description": " ".join(f"{a.get('product', '')}: {a.get('description', '')}" for a in own),
        "intended_use": "; ".join(uniq(a.get("intended_use") for a in own)) or "not stated",
        "main_inputs": uniq(i for a in own for i in a.get("main_inputs") or []) or ["not stated"],
        "value_chain_level": "other",
        "direct_customers": ["internal use (captive)"],
        "customer_details": "; ".join(uniq(a.get("customer_details") for a in own)) or "not stated",
        "end_users": "not stated",
        "sales_channels": "not stated",
        "countries_of_sale": uniq(c for a in own for c in a.get("countries_of_sale") or []) or ["not stated"],
        "status": "on the market" if any(a.get("status") == "on the market" for a in own) else "not stated",
        "source_numbers": sorted({n for a in own for n in a.get("source_numbers") or []}),
        "evidence": " | ".join(uniq(a.get("evidence") for a in own))[:800] or "not stated",
        "quotes": [q for a in own for q in a.get("quotes") or []],       # unchanged, per source
        "merged_from": own,
        "merged_levels": uniq(a.get("value_chain_level") for a in own),
        # not offered on the market: not compared, unless the lawyer includes it ("Edit")
        "excluded": True, "own_use": True,
        "exclusion_reason": "own use only: produced for the group itself, not offered on the market",
    }
    return main + side + gaps + [merged]


def is_gap(activity):
    """A line the sources name without saying what it offers (e.g. a brand named only in a company overview):
    product "not stated". Shown as a question for the company and not compared until the user fills it
    in, because a comparison of an empty description can only come back "not enough information"."""
    return (activity.get("product") or "").strip().lower() in {"not stated", "unknown", "n/a"}


def gap_name(activity):
    """What a gap line is called on screen: its brands, else the entity, else a neutral label."""
    brands = [b for b in activity.get("brands") or [] if b and b != "not stated"]
    if brands:
        return ", ".join(brands)
    entity = (activity.get("entity") or "").strip()
    return entity if entity and entity.lower() != "not stated" else GAP_FALLBACK


GAP_FALLBACK = "A business named in the sources"


def compared_pair(a, b):
    """Whether a target activity and a portco activity are compared at all: never two "Other activities" lines with
    each other. Own use and side lines of one company against those of the other cannot compete, and nobody supplies
    anybody; in testing these pairs only produced noise. Each "Other activities" line is still compared with every
    main activity of the other company."""
    return not (category(a) == "other" and category(b) == "other")


_WORD = re.compile(r"[a-z]{4,}")
_COMMON = set("with from that this their other products product sold sales sale goods services service".split())


def _words(activity):
    text = " ".join([activity.get("product", "")] + list(activity.get("includes") or [])).lower()
    text = re.sub(r"\bnon[- ]\w+", " ", text)          # "non-alcoholic" must not count as "alcoholic"
    return {w for w in _WORD.findall(_without_accents(text)) if w not in _COMMON}


def possible_duplicates(activities, threshold=0.4):
    """Pairs of activities of ONE company that may be the same activity split twice: same level of trade, same
    category and largely the same words (Jaccard >= threshold). Only a hint for the review in step ②."""
    out = []
    for i in range(len(activities)):
        for j in range(i + 1, len(activities)):
            a, b = activities[i], activities[j]
            if a.get("value_chain_level") != b.get("value_chain_level") or category(a) != category(b):
                continue
            # the same name is always flagged, even if the word overlap is below the threshold
            if (a.get("product") or "").strip().lower() == (b.get("product") or "").strip().lower():
                out.append((i, j))
                continue
            wa, wb = _words(a), _words(b)
            if wa and wb and len(wa & wb) / len(wa | wb) >= threshold:
                out.append((i, j))
    return out


def code_vertical_signals(a, b, sims):
    """
    Vertical links that follow from the facts alone, independent of the AI comparison.
    sims: {"product": similarity of the two products,
           "input_a_to_b": best match of A's product with B's inputs,
           "input_b_to_a": best match of B's product with A's inputs}
    Returns a list of (link, reason).
    """
    signals = []
    if sells_inputs(a) and sims["input_a_to_b"] >= INPUT_MATCH:
        signals.append(("A could be an input for B",
                        f"A is sold to producers and is close to one of B's inputs ({sims['input_a_to_b']:.2f})"))
    if sells_inputs(b) and sims["input_b_to_a"] >= INPUT_MATCH:
        signals.append(("B could be an input for A",
                        f"B is sold to producers and is close to one of A's inputs ({sims['input_b_to_a']:.2f})"))
    if sells_to_resellers(a) and is_reseller(b) and sims["product"] >= RESALE_MATCH:
        signals.append(("A could be resold by B",
                        f"A is sold to resellers, B resells a close range ({sims['product']:.2f})"))
    if sells_to_resellers(b) and is_reseller(a) and sims["product"] >= RESALE_MATCH:
        signals.append(("B could be resold by A",
                        f"B is sold to resellers, A resells a close range ({sims['product']:.2f})"))
    return signals


def selling_levels(activity):
    """The levels of trade at which an activity sells. The merged 'Other activities' line has the level 'other' by
    construction; there the levels of the lines it was merged from count (merged_levels, or merged_from in older
    saved data), unless the user has set a level of their own."""
    level = activity.get("value_chain_level")
    if level == "other":
        merged = activity.get("merged_levels") or [m.get("value_chain_level") for m in activity.get("merged_from") or []]
        if merged:
            return {m for m in merged if m}
    return {level}


OWN_USE_MARK = "(own use)"


def own_use_side(activity, items):
    """Whether this side of a link is own use only: the activity serves only the group itself, or (for the merged
    "Other activities" line) every item the AI named for the link is marked "(own use)"."""
    if captive_only(activity):
        return True
    items = [i for i in items or [] if i]
    return bool(items) and all(OWN_USE_MARK in i for i in items)


def check_ai_links(ai_links, a, b, vertical_items=None):
    """
    Applies the conditions of the vertical definition that the structured facts can check:
    1. a resale link needs a reseller. An AI resale link whose reseller side is not at retail or wholesale level is
       disregarded. Input links are otherwise left to the AI (any product, by-product or service may be an input,
       Draft Merger Guidelines para 250), so code does not second-guess them.
       For the merged 'Other activities' line, the levels of the merged lines are checked.
    2. the supplying side, and a reseller, must deal with third parties. Production or
       services only for the group's own use are not on the market (Draft Merger Guidelines para 103(i)): they supply
       nobody, so they cannot be an input for the other company or resell its goods. Such a link is disregarded; the
       pair then appears under "No overlap found", with this reason under "Why?", and can be added back.
    The reason is recorded, never silently dropped. Returns (valid links, [(disregarded link, reason)]).
    """
    items = {v.get("link"): v for v in vertical_items or []}
    valid, disregarded = set(), []
    for link in ai_links:
        reseller = b if link == "A could be resold by B" else a if link == "B could be resold by A" else None
        supplier = a if link in ("A could be an input for B", "A could be resold by B") else b
        side_items = items.get(link, {}).get("items_a" if supplier is a else "items_b")
        levels = selling_levels(reseller) if reseller is not None else set()
        if reseller is not None and not levels & RESELLER_OR_UNCLEAR_LEVELS:
            side = "B" if reseller is b else "A"
            disregarded.append((link, f"{side} is not active in wholesale or retail "
                                      f"(level: {', '.join(sorted(levels))})"))
        elif own_use_side(supplier, side_items):
            side = "A" if supplier is a else "B"
            disregarded.append((link, f"{side} is only for the group's own use, not supplied to third parties"))
        elif reseller is not None and captive_only(reseller):
            side = "B" if reseller is b else "A"
            disregarded.append((link, f"{side} is only for the group's own use and resells nothing to third parties"))
        else:
            valid.add(link)
    return valid, disregarded


# =============================================================== decision rule (if/then)
def decide(comparison, code_signals, similarity, a=None, b=None):
    """
    Combines the AI comparison of one anonymised pair with the code signals.
    The AI decides whether the products are the same or similar; code keeps a pair the AI would drop only where the
    structured facts show a vertical relationship (input or resale signal), and corrects the AI where they show a
    legal condition is not met (a resale link needs a reseller). Errors and blocked calls are never screened out.
    If the two activities are passed, AI resale links are checked against the reseller condition
    (check_ai_links); a disregarded link is recorded in the rule text, never silently dropped.
    """
    relation = comparison["product_relation"]
    ai_links = set(comparison.get("vertical_links") or [])
    disregarded = []
    if a is not None and b is not None:
        ai_links, disregarded = check_ai_links(ai_links, a, b, comparison.get("vertical_items"))
    rule_links = {link for link, _ in code_signals}
    if a is not None and b is not None:          # the own-use condition applies to the code signals too
        kept_rules, dropped = check_ai_links(rule_links, a, b)
        disregarded += [(link, why) for link, why in dropped if link not in {x for x, _ in disregarded}]
        rule_links = kept_rules
    links = [link for link in VERTICAL_LINKS if link in ai_links | rule_links]
    found_by = {
        link: "AI and rule" if link in ai_links and link in rule_links else ("AI" if link in ai_links else "rule")
        for link in links
    }
    horizontal = relation in HORIZONTAL_RELATIONS

    if horizontal or links:
        status = "candidate"
        rule = "Kept: " + ", ".join(
            (["horizontal (AI: " + relation + ")"] if horizontal else [])
            + [f"vertical: {link} ({found_by[link]})" for link in links]
        )
    # Blocked and failed calls are checked before "not enough information": compare() records them as "not enough
    # information", but the lawyer should see the real reason.
    elif comparison.get("blocked"):
        status = "unclear"
        rule = ("Unclear, please check: the call was blocked because a company name was still in a description "
                "(see the reason)")
    elif comparison.get("error"):
        status = "unclear"
        rule = ("Unclear, please check: the comparison call failed (see the reason); “Update the comparison” in step ② "
                "sends it again, or compare the two activities by hand")
    elif relation == "not enough information":
        status = "unclear"
        rule = "Unclear, please check: the descriptions do not allow a comparison"
    else:
        status = "screened out"
        rule = (f"Screened out: AI found a different product and no vertical link, and no vertical signal in code "
                f"(similarity of the descriptions {similarity:.2f}, for information only)")
    if disregarded:
        rule += " | AI link disregarded: " + "; ".join(f"{link} ({why})" for link, why in disregarded)
    return {"status": status, "horizontal": horizontal, "vertical_links": links,
            "found_by": found_by, "disregarded": disregarded, "rule": rule}


# =============================================================== EEA
EEA_COUNTRIES = {
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia", "denmark", "estonia", "finland", "france",
    "germany", "greece", "hungary", "ireland", "italy", "latvia", "lithuania", "luxembourg", "malta", "netherlands",
    "poland", "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
    "iceland", "liechtenstein", "norway",
}
COUNTRY_ALIASES = {"czech republic": "czechia", "the netherlands": "netherlands", "holland": "netherlands"}
NON_EEA_EXAMPLES = {
    "switzerland", "united kingdom", "uk", "united states", "usa", "us", "canada", "china", "japan", "ghana",
    "australia", "brazil", "india", "russia", "turkey", "ukraine", "mexico", "south africa",
}


def is_eea(country):
    """True if in the EEA, False if recognisably outside, None if it cannot be told (e.g. 'not stated')."""
    name = COUNTRY_ALIASES.get((country or "").strip().lower(), (country or "").strip().lower())
    if name in EEA_COUNTRIES:
        return True
    if name in NON_EEA_EXAMPLES:
        return False
    return None


def eea_status(countries):
    """'EEA', 'outside the EEA only' (flagged, not deleted) or 'unknown' (treated as a potential overlap)."""
    results = [is_eea(c) for c in countries or []]
    if any(r is True for r in results):
        return "EEA"
    if results and all(r is False for r in results):
        return "outside the EEA only"
    return "unknown"


# =============================================================== self-test (no API, no sector)
if __name__ == "__main__":
    # Deliberately from a sector outside the test cases (bicycles), to show that nothing here is sector-specific.
    bike_maker = {
        "product": "City bicycles", "description": "Aluminium city bicycles with hub gears.",
        "intended_use": "Everyday cycling", "main_inputs": ["aluminium frames", "hub gears"],
        "value_chain_level": "finished products", "direct_customers": ["retailers", "other businesses"],
        "customer_details": "bicycle shops; rental companies", "end_users": "consumers and businesses",
        "sales_channels": "bicycle shops; direct to fleets", "status": "on the market",
        "brands": ["Spokewell"], "countries_of_sale": ["Germany", "Switzerland"],
    }
    bike_shop = {
        "product": "Retail of bicycles and accessories", "description": "Shop chain selling bicycles and parts.",
        "intended_use": "Cycling", "main_inputs": ["not stated"], "value_chain_level": "retail",
        "direct_customers": ["consumers"], "customer_details": "not stated", "end_users": "consumers",
        "sales_channels": "Own shops; own online shop", "status": "on the market",
        "countries_of_sale": ["not stated"],
    }
    names = ["Spokewell Bikes GmbH", "Spokewell", "Pedalhaus AG", "Gear & Chain Ltd"]

    text, leftover = build_abstract({**bike_maker, "description": "Spokewell city bicycles with hub gears."}, names)
    print(text, "\nnames left:", leftover)
    print("variants:", sorted(name_variants(names)))
    print("name parts:", name_parts(names))
    print("customers bike maker v shop:", customer_overlap(bike_maker["direct_customers"],
                                                           bike_shop["direct_customers"]))
    sims = {"product": 0.46, "input_a_to_b": 0.10, "input_b_to_a": 0.05}
    signals = code_vertical_signals(bike_maker, bike_shop, sims)
    print("code signals:", signals)
    ai = {"product_relation": "different product", "vertical_links": []}
    print("decision:", decide(ai, signals, sims["product"]))
    print("decision without signals, close texts (no longer kept):", decide(ai, [], 0.55)["rule"])
    print("decision without signals, distant texts:", decide(ai, [], 0.20)["rule"])
    print("blocked call:", decide({"product_relation": "not enough information", "vertical_links": [], "blocked": True},
                                  [], 0.2)["rule"])
    ai_resale = {"product_relation": "different product", "vertical_links": ["B could be resold by A"]}
    print("AI says the bicycle maker resells the shop's goods:",
          decide(ai_resale, [], 0.20, a=bike_maker, b=bike_shop)["rule"])
    print("EEA:", eea_status(bike_maker["countries_of_sale"]), "|", eea_status(["Switzerland"]), "|",
          eea_status(["more than 100 countries"]))