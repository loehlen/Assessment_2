"""
logic/examples.py - the ready-made examples behind "Try an example": the three test cases of the README, and one more.

Only the inputs a user would type: names, websites, other names and, where a test case uses one, the description a
lawyer would type in step ① (source mode "my description" or "both"). The run itself is live.
TC1: markets the Commission has defined; every company researched on the web.
TC2: a precedent for only one side, and products with none; the three ways of finding a company's activities side by
     side: web search, web search AND the lawyer's description ("both"), the lawyer's description only.
TC3: another sector (paints, facade systems, DIY retail and adhesives), to show that the design contains no sector
     knowledge. No decision of this sector is in the database until the lawyer adds one (test_files/).
Koa (not one of the three test cases): cocoa fruit products, with no precedent.

The real companies form a hypothetical portfolio; no real transaction is implied. The typed descriptions state only
facts from public sources.
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

# TC2, "both": what the lawyer knows in addition to the web search. It names the target's brand and the target, so
# step ① shows the confidentiality warning; the lawyer decides with "Send anyway".
BARRY_CALLEBAUT_ADDED = (
    "Since November 2025, Barry Callebaut has had a commercial partnership with Planet A Foods for ChoViva, a "
    "cocoa-free alternative to chocolate made from oats and sunflower seeds. Since May 2026, Barry Callebaut has been "
    "the exclusive distributor of ChoViva to food manufacturers in the United States, for use in coatings, fillings, "
    "snacks, bakery products and confectionery. Barry Callebaut also processes cocoa beans into cocoa liquor, cocoa "
    "butter and cocoa powder, which it sells to food manufacturers.")

# TC2 and Koa, "my description": how the client would describe its own portfolio company; no web search for it.
RITTER_SPORT_DESCRIBED = (
    "Alfred Ritter GmbH & Co. KG (Ritter Sport) is a family-owned chocolate manufacturer based in Waldenbuch, Germany. "
    "It makes square chocolate bars (100 g bars, large bars and minis) in many varieties, including organic and vegan "
    "bars, and Amicelli wafer rolls. It sells them to food retailers and travel retail in more than 100 countries. "
    "It runs its own chocolate shops in Waldenbuch and Berlin and an online shop, which sell its products to "
    "consumers. Through its subsidiary Hang zur Sonne GmbH it makes and sells CacaoVida drinks made from cocoa fruit "
    "(an iced tea, a lemonade and a sparkling secco). It runs its own cocoa plantation in Nicaragua, which grows cocoa "
    "for its own chocolate production.")

EXAMPLES = {
    "TC1": {"button": "TC1 · Lindt & Sprüngli", "target": "Lindt & Sprüngli", "portfolio": PORTFOLIO,
            "what": "Markets the Commission has defined in earlier decisions; every company researched on the web"},
    "TC2": {"button": "TC2 · Planet A Foods", "target": "Planet A Foods", "portfolio": PORTFOLIO,
            "sources": {"Barry Callebaut": ("both", BARRY_CALLEBAUT_ADDED),
                        "Ritter Sport": ("my description", RITTER_SPORT_DESCRIBED)},
            "what": "A new product with a precedent for only one side; Barry Callebaut researched on the web and "
                    "described by you (“both”), Ritter Sport described by you only (“my description”, no web search)"},
    "TC3": {"button": "TC3 · Brillux", "target": "Brillux", "portfolio": ["Hornbach", "Sto", "Henkel"],
            "what": "Paints, facade systems, DIY retail and adhesives: the same tool in a sector it was not built "
                    "around, with a Commission decision you add"},
    "Koa": {"button": "More · Koa", "target": "Koa", "portfolio": PORTFOLIO,
            "sources": {"Ritter Sport": ("my description", RITTER_SPORT_DESCRIBED)},
            "what": "Cocoa fruit products, with no precedent; Ritter Sport described by you only (“my description”, no "
                    "web search)"},
}