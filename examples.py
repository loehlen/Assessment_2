"""
examples.py - the ready-made examples behind "Try an example".

Only the inputs a user would type: names, websites and other names. The run itself is live.
TC1: markets the Commission has defined; TC2: a precedent for only one side; TC3: no precedent.
OS: a run in another sector (paints, facade systems, DIY retail, adhesives), to show that the design contains no
sector knowledge. No decision of this sector is in the corpus.

The real companies form a hypothetical portfolio; no real transaction is implied.
"""
COMPANIES = {
    # ------------------------------------------------------------------ cocoa test cases
    "Lindt & Sprüngli": {"website": "lindt-spruengli.com", "aliases": ["Lindt", "Sprüngli", "Lindt & Sprüngli AG"]},
    "Planet A Foods": {"website": "planet-a-foods.com", "aliases": ["Planet A", "ChoViva"]},
    "Koa": {"website": "koa-impact.com", "aliases": ["Koa Impact", "Koa Switzerland AG", "Koa Germany GmbH"]},
    "Ritter Sport": {"website": "ritter-sport.com", "aliases": ["Ritter", "Alfred Ritter GmbH & Co. KG"]},
    "Barry Callebaut": {"website": "barry-callebaut.com", "aliases": ["Callebaut", "Barry Callebaut AG"]},
    "FRoSTA": {"website": "frosta-ag.com", "aliases": ["FRoSTA AG"]},
    # ------------------------------------------------------------------ other sector
    "Brillux": {"website": "brillux.com", "aliases": ["Brillux GmbH & Co. KG"]},
    "Hornbach": {"website": "hornbach-holding.de", "aliases": ["HORNBACH Holding AG & Co. KGaA", "Hornbach Baumarkt"]},
    "Sto": {"website": "sto.com", "aliases": ["Sto SE & Co. KGaA"]},
    "Henkel": {"website": "henkel.com", "aliases": ["Henkel AG & Co. KGaA"]},
}

# The same three portfolio companies for every cocoa test case; FRoSTA is the control without a real overlap.
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
