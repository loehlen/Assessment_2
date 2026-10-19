"""
examples.py - the ready-made examples behind "Try an example" (also used by test_compare.py).

Only the inputs a user would type: names, websites and other names. The run itself is live.
Spec section 13: TC1 a market the Commission has defined; TC2 a precedent for only one side; TC3 no precedent.
OS (added 16 Oct): a run in another sector (paints, facade systems, DIY retail, adhesives), to show that the design
contains no sector knowledge (done criterion 2, spec section 16). No decision of this sector is in the corpus.

Websites: the company domains the searches of 14-16 Oct actually cited. "hint" is the earlier one-line description;
the app no longer asks for it, but test_compare.py still builds its search prompts from it.
"""
COMPANIES = {
    # ------------------------------------------------------------------ cocoa test cases
    "Lindt & Sprüngli": {"website": "lindt-spruengli.com", "hint": "Swiss premium chocolate maker based in Kilchberg",
                         "aliases": ["Lindt", "Sprüngli", "Lindt & Sprüngli AG"]},
    "Planet A Foods": {"website": "planet-a-foods.com",
                       "hint": "Munich-based maker of the cocoa-free chocolate alternative ChoViva",
                       "aliases": ["Planet A", "ChoViva"]},
    "Koa": {"website": "koa-impact.com", "hint": "Swiss-Ghanaian company making products from cocoa fruit pulp",
            "aliases": ["Koa Impact", "Koa Switzerland AG", "Koa Germany GmbH"]},
    "Ritter Sport": {"website": "ritter-sport.com", "hint": "German chocolate maker Alfred Ritter GmbH & Co. KG, Waldenbuch",
                     "aliases": ["Ritter", "Alfred Ritter GmbH & Co. KG"]},
    "Barry Callebaut": {"website": "barry-callebaut.com", "hint": "Swiss cocoa and chocolate manufacturer based in Zurich",
                        "aliases": ["Callebaut", "Barry Callebaut AG"]},
    "Bahlsen": {"website": "bahlsen.com", "hint": "German biscuit and cake maker based in Hanover",
                "aliases": ["Bahlsen GmbH & Co. KG"]},
    "FRoSTA": {"website": "frosta-ag.com", "hint": "German frozen food company based in Bremerhaven",
               "aliases": ["FRoSTA AG"]},
    # ------------------------------------------------------------------ other sector (added 16 Oct)
    "Brillux": {"website": "brillux.com", "hint": "German paint, coatings and plaster manufacturer based in Münster",
                "aliases": ["Brillux GmbH & Co. KG"]},
    "Hornbach": {"website": "hornbach-holding.de", "hint": "German DIY retail and builders' merchant group",
                 "aliases": ["HORNBACH Holding AG & Co. KGaA", "Hornbach Baumarkt"]},
    "Sto": {"website": "sto.com", "hint": "German manufacturer of facade systems and coatings",
            "aliases": ["Sto SE & Co. KGaA"]},
    "Henkel": {"website": "henkel.com", "hint": "German adhesives and consumer goods group based in Düsseldorf",
               "aliases": ["Henkel AG & Co. KGaA"]},
}

# 19 Oct (Linda): three portfolio companies instead of four, so the screen is less crowded and faster. Bahlsen's
# rows repeated kinds of row that Ritter Sport already shows (outlets v shops, resale into own shops, a downstream
# user); FRoSTA stays as the control without a real overlap. Bahlsen stays in COMPANIES, so it can still be added
# by hand, and benchmark.py marks its rows "–" (not in this run).
PORTFOLIO = ["Ritter Sport", "Barry Callebaut", "FRoSTA"]

EXAMPLES = {
    "TC1": {"button": "TC1 · Lindt & Sprüngli", "target": "Lindt & Sprüngli", "portfolio": PORTFOLIO,
            "what": "Markets the Commission has defined in earlier decisions"},
    "TC2": {"button": "TC2 · Planet A Foods", "target": "Planet A Foods", "portfolio": PORTFOLIO,
            "what": "A new product; a precedent exists for only one side"},
    "TC3": {"button": "TC3 · Koa", "target": "Koa", "portfolio": PORTFOLIO,
            "what": "Cocoa fruit products, with no precedent"},
    "OS": {"button": "Other sector · Brillux", "target": "Brillux", "portfolio": ["Hornbach", "Sto", "Henkel"],
           "what": "Paints, facade systems, DIY retail and adhesives: the same tool in a sector it was not built around"},
}

# Earlier names, still used by test_compare.py and benchmark.py
TEST_CASES = {k: v["target"] for k, v in EXAMPLES.items() if k.startswith("TC")}
DESCRIPTIONS = {k: f"{v['target']}: {v['what']}" for k, v in EXAMPLES.items()}