"""
rules.py - the sector-neutral rules of the overlap screen (replaces the cocoa-specific categories.py).

Only rules that hold in every sector live here:
  - the fixed answer lists for the activity overview (value-chain levels, direct-customer types, ...)
  - anonymisation: the abstract that is sent for comparison, and the name check
  - customer overlap (sorts horizontal candidates, never removes them)
  - vertical signals from the facts (input supply, resale)
  - the decision rule that combines the AI comparison with the code signals
  - the EEA check

No sector knowledge lives here: which products are related, or which inputs go into which
outputs, is judged by the AI on anonymised pairs of activities (stage 3), and what the
Commission found comes from the decisions in the corpus (stage 4).

Pure Python, no API calls, so it can be tested for free:  python rules.py
"""
import math
import re
import unicodedata

# =============================================================== answer lists (used by schemas.py)
VALUE_CHAIN_LEVELS = {
    "raw materials": "growing, extracting, sourcing or trading unprocessed commodities",
    "intermediate products": "processed goods sold to other businesses to make their own products "
                             "(ingredients, components, semi-finished goods)",
    "finished products": "goods ready for use, sold by the company that makes them",
    "wholesale / distribution": "reselling goods made by others to businesses",
    "retail": "selling to consumers through own shops, outlets or an own online shop",
    "services": "services rather than goods",
    "other": "fits none of the above",
}

DIRECT_CUSTOMER_TYPES = {
    "consumers": "private individuals buying for their own use",
    "retailers": "shops and online retailers that resell to consumers (including travel retail)",
    "wholesalers / distributors": "businesses that resell to other businesses",
    "manufacturers / processors": "businesses that use the product to make their own products "
                                  "(including craft businesses)",
    "other businesses": "businesses that use the product themselves (e.g. hotels, restaurants, offices)",
    "public sector": "public authorities and institutions",
    "internal use (captive)": "used within the company's own group, not sold",
    "not stated": "the sources do not say",
}

END_USERS = ["consumers", "businesses", "consumers and businesses", "not stated"]
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

# =============================================================== thresholds (to calibrate)
# Cosine similarity of text-embedding-3-large vectors. Placeholders until test_compare.py has
# printed the similarities of all test-case pairs; then set them so that no benchmark overlap
# is lost (over-inclusive by design).
SIMILARITY_UNCLEAR = 0.50   # AI says "different product", but the descriptions are this close -> unclear
INPUT_MATCH = 0.50          # A's product is this close to one of B's listed inputs -> input signal
RESALE_MATCH = 0.50         # A's product is this close to B's retail / wholesale range -> resale signal
                            # (TC1, 15 Oct: real resale pairs 0.68 and 0.82; wrong links to merchandise shops 0.41-0.46)


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


def _join(values):
    values = [v for v in (values or []) if v and v != "not stated"]
    return ", ".join(values) if values else "not stated"


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


def product_text(activity):
    """The text that is embedded to measure how close two products are (no customers, no levels)."""
    return f"{activity.get('product', '')}. {activity.get('description', '')} Used for: {activity.get('intended_use', '')}"


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
    Different customers alone never make separate markets (Notice (24), (88)-(89)).
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
    para 103(i)). Shown as a flag on every pair with this activity, never used to screen a pair out."""
    customers = set(activity.get("direct_customers") or []) - {"not stated"}
    return customers == {"internal use (captive)"}


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


def check_ai_links(ai_links, a, b):
    """
    Applies the one condition of the vertical definition that the structured facts can check: a resale link
    needs a reseller. An AI resale link whose reseller side is not at retail or wholesale level is disregarded,
    and the reason is recorded. Input links are left to the AI (any product, by-product or service may be an
    input, Draft Merger Guidelines para 250), so code does not second-guess them.
    Returns (valid links, [(disregarded link, reason)]).
    """
    valid, disregarded = set(), []
    for link in ai_links:
        reseller = b if link == "A could be resold by B" else a if link == "B could be resold by A" else None
        if reseller is not None and reseller.get("value_chain_level") not in RESELLER_OR_UNCLEAR_LEVELS:
            side = "B" if reseller is b else "A"
            disregarded.append((link, f"{side} is not active in wholesale or retail "
                                      f"(level: {reseller.get('value_chain_level')})"))
        else:
            valid.add(link)
    return valid, disregarded


# =============================================================== decision rule (if/then)
def decide(comparison, code_signals, similarity, a=None, b=None):
    """
    Combines the AI comparison of one anonymised pair with the code signals.
    The AI can put a pair on the list on its own, but never take one off on its own:
    a pair is screened out only if the AI finds a different product and no vertical link,
    the code finds no vertical link, and the descriptions are not close.
    If the two activities are passed, AI resale links are checked against the reseller condition
    (check_ai_links); a disregarded link is recorded in the rule text, never silently dropped.
    """
    relation = comparison["product_relation"]
    ai_links = set(comparison.get("vertical_links") or [])
    disregarded = []
    if a is not None and b is not None:
        ai_links, disregarded = check_ai_links(ai_links, a, b)
    rule_links = {link for link, _ in code_signals}
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
    elif relation == "not enough information":
        status = "unclear"
        rule = "Unclear, please check: the descriptions do not allow a comparison"
    elif similarity >= SIMILARITY_UNCLEAR:
        status = "unclear"
        rule = (f"Unclear, please check: AI found a different product, but the descriptions are close "
                f"({similarity:.2f} >= {SIMILARITY_UNCLEAR}), so the signals disagree")
    else:
        status = "screened out"
        rule = (f"Screened out: AI found a different product and no vertical link, no vertical signal in code, "
                f"descriptions not close ({similarity:.2f} < {SIMILARITY_UNCLEAR})")
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
    # Deliberately from a sector outside the test cases, to show that nothing here is sector-specific.
    paint_maker = {
        "product": "Interior wall paint", "description": "Water-based emulsion paint in tins.",
        "intended_use": "Painting interior walls", "main_inputs": ["titanium dioxide", "acrylic binder"],
        "value_chain_level": "finished products", "direct_customers": ["retailers", "other businesses"],
        "customer_details": "DIY stores; painting contractors", "end_users": "consumers and businesses",
        "sales_channels": "DIY stores; trade counters", "status": "on the market",
        "brands": ["Wallglow"], "countries_of_sale": ["Germany", "Switzerland"],
    }
    hardware_store = {
        "product": "Retail of DIY and home improvement goods", "description": "Store chain selling paint and tools.",
        "intended_use": "Home improvement", "main_inputs": ["not stated"], "value_chain_level": "retail",
        "direct_customers": ["consumers"], "customer_details": "not stated", "end_users": "consumers",
        "sales_channels": "Own stores; own online shop", "status": "on the market",
        "countries_of_sale": ["not stated"],
    }
    names = ["Wallglow Paints GmbH", "Wallglow", "Hammerhaus AG"]

    text, leftover = build_abstract({**paint_maker, "description": "Wallglow emulsion paint in tins."}, names)
    print(text, "\nnames left:", leftover)
    print("variants:", sorted(name_variants(names)))
    print("customers paint maker v store:", customer_overlap(paint_maker["direct_customers"],
                                                              hardware_store["direct_customers"]))
    sims = {"product": 0.46, "input_a_to_b": 0.10, "input_b_to_a": 0.05}
    signals = code_vertical_signals(paint_maker, hardware_store, sims)
    print("code signals:", signals)
    ai = {"product_relation": "different product", "vertical_links": []}
    print("decision:", decide(ai, signals, sims["product"]))
    print("decision without signals, close texts:", decide(ai, [], 0.55)["rule"])
    print("decision without signals, distant texts:", decide(ai, [], 0.20)["rule"])
    ai_resale = {"product_relation": "different product", "vertical_links": ["B could be resold by A"]}
    print("AI says the paint maker resells the store's goods:",
          decide(ai_resale, [], 0.20, a=paint_maker, b=hardware_store)["rule"])
    print("EEA:", eea_status(paint_maker["countries_of_sale"]), "|", eea_status(["Switzerland"]), "|",
          eea_status(["more than 100 countries"]))