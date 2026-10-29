"""
ui/labels.py - the small marks used in several places: the customer dots (●●○) and the result chips of step ④
("Confirmed", "Possible", ...), with their explanations.
"""
from ui.common import h


def dots_html(score):
    """The customer score as three drawn circles (filled = shared customers), so that they have the same size in every
    font; the score itself stays "●●○" in the data and in the Word document."""
    return ("<span class='dts'>" + "".join(f"<i class='{'on' if ch == '●' else ''}'></i>" for ch in score)
            + "</span>")


OUTCOME_CLASS = {"Confirmed": "o-conf", "Markets defined": "o-vert", "Possible": "o-open", "Not excluded": "o-open",
                 "One side defined": "o-vert", "Not supported": "o-nosup", "No precedent": "o-nopre"}
OUTCOME_TIP = {
    "Confirmed": "Both products fall in a market the Commission defined: horizontal overlap at product-market level.",
    "Possible": "Both products may fall in the same market, depending on the product format, or the market is not an "
                "exact match for one of them: to be checked.",
    "Not excluded": "Both products fall in a market whose definition the Commission left open (or the paragraphs found "
                    "state no conclusion): the overlap cannot be excluded.",
    "Not supported": "The Commission puts the products in separate markets: no horizontal overlap at product-market "
                     "level; check for a vertical relationship.",
    "No precedent": "No decision in the database covers these products, or, for a shop or wholesaler, its own retail "
                    "or wholesale market (the markets of the products it sells are named in the text): to be assessed "
                    "under the Market Definition Notice.",
    "Markets defined": "The decisions name a market for each side's products (defined, or left open). They do not "
                       "show a link between the two companies: that comes from the preliminary assessment (step ③).",
    "One side defined": "The decisions name a market for one side's products only (defined, or left open); the other "
                        "side has no precedent. They do not show a link between the two companies."
}


def outcome_chip(outcome):
    return (f"<span class='oc {OUTCOME_CLASS[outcome]}' title='{h(OUTCOME_TIP[outcome])}'>{outcome}</span>"
            if outcome else "")
