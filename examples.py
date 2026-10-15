"""
examples.py - the three test cases as ready-made inputs ("Try an example" in the app; also used by test_compare.py).

Only the inputs a user would type: names, an identifying description and other names. The run itself is live.
Spec section 13: TC1 a market the Commission has defined; TC2 a precedent for only one side; TC3 no precedent.
"""
COMPANIES = {
    "Lindt & Sprüngli": {"hint": "Swiss premium chocolate maker based in Kilchberg",
                         "aliases": ["Lindt", "Sprüngli", "Lindt & Sprüngli AG"]},
    "Planet A Foods": {"hint": "Munich-based maker of the cocoa-free chocolate alternative ChoViva",
                       "aliases": ["Planet A", "ChoViva"]},
    "Koa": {"hint": "Swiss-Ghanaian company making products from cocoa fruit pulp",
            "aliases": ["Koa Impact", "Koa Switzerland AG", "Koa Germany GmbH"]},
    "Ritter Sport": {"hint": "German chocolate maker Alfred Ritter GmbH & Co. KG, Waldenbuch",
                     "aliases": ["Ritter", "Alfred Ritter GmbH & Co. KG"]},
    "Barry Callebaut": {"hint": "Swiss cocoa and chocolate manufacturer based in Zurich",
                        "aliases": ["Callebaut", "Barry Callebaut AG"]},
    "Bahlsen": {"hint": "German biscuit and cake maker based in Hanover", "aliases": ["Bahlsen GmbH & Co. KG"]},
    "FRoSTA": {"hint": "German frozen food company based in Bremerhaven", "aliases": ["FRoSTA AG"]},
}
TEST_CASES = {"TC1": "Lindt & Sprüngli", "TC2": "Planet A Foods", "TC3": "Koa"}
PORTFOLIO = ["Ritter Sport", "Barry Callebaut", "Bahlsen", "FRoSTA"]
DESCRIPTIONS = {
    "TC1": "Lindt & Sprüngli: markets the Commission has defined in earlier decisions",
    "TC2": "Planet A Foods: a new product; a precedent exists for only one side",
    "TC3": "Koa: cocoa fruit products, with no precedent",
}