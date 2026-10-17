"""
benchmark.py - the expert benchmark of spec section 13 as automatic checks for test_compare.py.

Only the rows the tool can see ("expected from the tool" ✔ or ◐). Rows the web search cannot find
(Lindt's travel retail and B2B, Ritter's industrial chocolate) are left out; they are documented weaknesses.

How a check works: activities are found by keywords (regex, case-insensitive) in the NAMED activity
(product, description, intended use, business area, entity, brands) and, optionally, by value-chain level.
This file stays on your machine and is never sent to an AI, so names may be used here.

Each check gets one of six results:
  ✔  expected result
  ◐  kept (candidate or unclear), but not in the expected form, e.g. "unclear" instead of "horizontal".
     Still on the list, so nothing is lost (over-inclusive principle).
  ✖  MISSED BY THE COMPARISON: the activities exist, but every matching pair was screened out.
     This is what the checkpoint of Wed 21 Oct is about.
  ∅  NOT FOUND: no matching activity on one side. Either the search / extraction missed it
     (a finding for A3), or the keywords below need adjusting (check the activity overview in the report).
  ⚠  FALSE POSITIVE (control rows only): pairs were kept where the benchmark expects none.
  ○  OBSERVATION: reported, never pass/fail. For links the tool found that the original benchmark missed and
     that depend on how an activity is extracted (TC1-13; spec section 17), so a run-to-run change is recorded
     as non-determinism (A3), not as a missed overlap.

Expectations:
  "horizontal"    at least one matching pair is a horizontal candidate
  "vertical"      at least one matching pair has a vertical link (AI or rule)
  "kept"          at least one matching pair is a candidate or unclear
  "screened out"  every pair with this portco is screened out (control for false positives), except the
                  pairs listed under "except" (real links the tool found that the original benchmark missed)
  "relationship"  the public sources of one company mention the other (🔗 note)
  "relationship observation"  the same, reported with the mark ○ (never pass/fail)
  "observation"   reports how the matching pairs came out (vertical / kept / screened out), with the mark ○

Corrections of 17 Oct (double-check after the live runs):
  - vertical rows name the direction ("down": the target supplies or is resold by the portco; "up": the portco
    supplies the target). A link in the other direction no longer counts as the expected result.
  - controls ("screened out") count only candidates as false positives; "unclear" pairs (not enough information)
    are named in the detail, because "please check" is not a claimed overlap.
  - keywords: generic words ("drink", "juice") no longer stand for CacaoVida; "chocolate drink" now finds Lindt's
    drinks; TC2-2 and TC3-2 no longer require the level "intermediate" (the extraction varies it between runs);
    the exception of TC2-7 (food fats) applies only to the fats line, not to the chocolate alternative, whose
    description also mentions fats (before, it exempted every pair and the control checked nothing).
"""
import re

# value-chain levels (same strings as rules.VALUE_CHAIN_LEVELS)
FINISHED = {"finished products"}
INTERMEDIATE = {"intermediate products", "raw materials"}
RETAIL = {"retail"}
RESELLING = {"retail", "wholesale / distribution"}

CHOCOLATE = r"(?<!non-)(?<!non )chocolate|praline|truffle"  # not "non-chocolate confectionery"
BISCUITS = r"biscuit|cookie|wafer|cake"
RETAIL_WORDS = r"shop|store|boutique|outlet|retail|café|cafe"
CAFE = r"café|cafe|catering"


def act(words=None, levels=None, exclude=None):
    """Describes which activities a check is about."""
    return {"words": words, "levels": levels, "exclude": exclude}


ANY = act()
# FRoSTA's frozen food for professional kitchens (not its consulting, which sits in the same business area)
FOODSERVICE = act(r"foodservice|food service|professional kitchen", exclude=r"consult|advis|development")
# Koa's ingredients for manufacturers, whatever level the extraction chooses (its drinks and shots excluded)
KOA_INGREDIENTS = act(r"pulp|juice|concentrate|powder|flakes|sweetener|cocoa fruit",
                      exclude=r"shot|ready-to-drink|beverage|drink|sold (directly )?to consumers|other activities")

BENCHMARK = {
    # ------------------------------------------------------------------ TC1 Lindt & Sprüngli (full precedent)
    "TC1": [
        {"id": "TC1-1", "portco": "Ritter Sport", "what": "consumer chocolate ↔ consumer chocolate",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(CHOCOLATE, FINISHED), "expect": "horizontal"},
        {"id": "TC1-2", "portco": "Ritter Sport", "what": "own shops ↔ own shops (both in Berlin)",
         "target": act(RETAIL_WORDS, RETAIL), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "horizontal"},
        {"id": "TC1-3", "portco": "Ritter Sport", "what": "Lindt chocolate → Ritter shops (vertical at market level; shops sell only own products)",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "vertical",
         "direction": "down"},
        {"id": "TC1-4", "portco": "Ritter Sport", "what": "Amicelli wafer rolls ↔ Lindt chocolate",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(r"amicelli|wafer"), "expect": "kept"},
        {"id": "TC1-5", "portco": "Barry Callebaut", "what": "semi-finished / industrial chocolate → Lindt",
         "target": act(CHOCOLATE, FINISHED),
         "portco_act": act(r"cocoa (butter|liquor|mass|powder)|semi-finished|industrial chocolate|couverture"),
         "expect": "vertical", "direction": "up"},
        {"id": "TC1-6", "portco": "Barry Callebaut", "what": "industrial chocolate ↔ Lindt consumer chocolate (●○○; public evidence for Lindt's sales to "
         "businesses in the EEA is thin, check of 17 Oct)",
         "target": act(CHOCOLATE, FINISHED),
         "portco_act": act(r"chocolate|couverture", INTERMEDIATE, exclude=r"compound|cocoa-free|beverage|drink"),
         "expect": "horizontal"},
        {"id": "TC1-7", "portco": "Barry Callebaut", "what": "beverages ↔ Lindt hot chocolate (◐)",
         "target": act(r"hot chocolate|drinking chocolate|chocolate drink|beverage|cocoa drink"),
         "portco_act": act(r"beverage|drink|vending|hot chocolate"), "expect": "kept"},
        {"id": "TC1-8", "portco": "Bahlsen", "what": "chocolate ↔ biscuits (must never be screened out)",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(BISCUITS, FINISHED), "expect": "kept"},
        {"id": "TC1-9", "portco": "Bahlsen", "what": "Bahlsen outlets ↔ Lindt shops",
         "target": act(RETAIL_WORDS, RETAIL), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "horizontal"},
        {"id": "TC1-10", "portco": "Bahlsen", "what": "Lindt chocolate → Bahlsen outlets (distribution, M.5644 (47))",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "vertical",
         "direction": "down"},
        {"id": "TC1-11", "portco": "Bahlsen", "what": "Caffarel candies ↔ Bisquiva peppermint tablets (◐; Caffarel's sugar confectionery unverified, "
         "check of 17 Oct)",
         "target": act(r"cand(y|ies)|jell|sugar confectionery|non-chocolate"),
         "portco_act": act(r"peppermint|mint|sugar confectionery|cand(y|ies)"), "expect": "kept"},
        {"id": "TC1-12", "portco": "FRoSTA", "what": "control: nothing else in common (except TC1-13)",
         "target": ANY, "portco_act": ANY, "expect": "screened out",
         "except": [(act(CAFE), FOODSERVICE)]},
        {"id": "TC1-13", "portco": "FRoSTA", "what": "foodservice frozen food → Lindt cafés (found by the tool, 15 Oct; observation)",
         "target": act(CAFE), "portco_act": FOODSERVICE, "expect": "observation"},
        # Added 17 Oct (check against public sources): Bahlsen's outlets sell selected other brands, including Lindt
        # (brand logos on bahlsen-outlet.de; a local listing found by the Sol run of 17 Oct). A real supply
        # relationship; recorded as an observation, because whether the search notes mention it varies by run.
        {"id": "TC1-14", "portco": "Bahlsen", "what": "Bahlsen outlets sell Lindt products (🔗 relationship; observation)",
         "expect": "relationship observation"},
    ],
    # ------------------------------------------------------------------ TC2 Planet A Foods (partial precedent)
    "TC2": [
        {"id": "TC2-1", "portco": "Barry Callebaut", "what": "ChoViva partnership (🔗 note must appear)",
         "expect": "relationship"},
        {"id": "TC2-2", "portco": "Barry Callebaut", "what": "compound / industrial chocolate ↔ ChoViva",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(r"compound|chocolate|couverture", exclude=r"beverage|drink|cocoa-free|alternative"),
         "expect": "horizontal"},
        {"id": "TC2-3", "portco": "Barry Callebaut", "what": "ChoViva Butter (pipeline) ↔ cocoa butter",
         "target": act(r"butter"), "portco_act": act(r"cocoa butter|butter"), "expect": "kept"},
        {"id": "TC2-4", "portco": "Ritter Sport", "what": "ChoViva → Ritter chocolate (vertical candidate)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(CHOCOLATE, FINISHED), "expect": "vertical", "direction": "down"},
        # Linda, 16 Oct (after the run of 05:35): horizontal (related, ●○○) and vertical (ChoViva as an input) are both
        # possible; a lawyer has to look at it. So any kept form is the expected result.
        {"id": "TC2-5", "portco": "Ritter Sport", "what": "Ritter consumer chocolate ↔ ChoViva (horizontal ●○○, vertical, or both)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(CHOCOLATE, FINISHED), "expect": "kept"},
        {"id": "TC2-6", "portco": "Bahlsen", "what": "ChoViva → biscuits (vertical candidate)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(BISCUITS, FINISHED), "expect": "vertical", "direction": "down"},
        # Linda, 16 Oct (after the run of 05:35): a supplier of food fats and a frozen-food maker can be vertically
        # related at market level (fats as an ingredient, e.g. in puff pastry); a lawyer checks it. Those pairs are
        # expected results, not false positives.
        {"id": "TC2-7", "portco": "FRoSTA", "what": "control: nothing in common, except food fats as an input",
         "target": ANY, "portco_act": ANY, "expect": "screened out", "except": [(act(r"\bfats?\b|\boils?\b|butter",
                                                                    exclude=r"other activities|chocolate alternative|chocolate-like|cocoa-free"), ANY)]},
    ],
    # ------------------------------------------------------------------ TC3 Koa (no precedent)
    "TC3": [
        {"id": "TC3-1", "portco": "Barry Callebaut", "what": "Cabosse Naturals ↔ Koa ingredients (central overlap)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"cocoa fruit|pulp|cabosse|juice|concentrate"), "expect": "horizontal"},
        {"id": "TC3-2", "portco": "Barry Callebaut", "what": "Koa ingredients → BC chocolate (vertical candidate)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"chocolate|couverture", exclude=r"compound|cocoa fruit|cocoa-free|pulp"),
         "expect": "vertical", "direction": "down"},
        {"id": "TC3-3", "portco": "Barry Callebaut", "what": "Koa drinks ↔ BC beverages (unclear is fine)",
         "target": act(r"shot|drink|beverage", FINISHED | RETAIL),
         "portco_act": act(r"beverage|drink|vending"), "expect": "kept"},
        # Linda, 17 Oct: CacaoVida is hardly visible in public sources (own website, press of 2021, one mention in a
        # 2025 company overview); a lawyer would probably not find it either, so a miss is acceptable (A3).
        {"id": "TC3-4", "portco": "Ritter Sport", "what": "CacaoVida ↔ Koa shots (hard to find publicly; a miss is "
         "acceptable, Linda 17 Oct; whether CacaoVida is still sold in 2026 is unverified)",
         "target": act(r"shot|drink|beverage", FINISHED | RETAIL),
         "portco_act": act(r"cacao ?vida|cocoa[- ]fruit|cacao[- ]?fruit"), "expect": "horizontal"},
        {"id": "TC3-5", "portco": "Ritter Sport", "what": "Koa ingredients → Ritter (chocolate, CacaoVida)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"chocolate|cacao ?vida|cocoa[- ]fruit"), "expect": "vertical", "direction": "down"},
        {"id": "TC3-6", "portco": "Bahlsen", "what": "Koa ingredients → bakery (vertical candidate)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(BISCUITS), "expect": "vertical", "direction": "down"},
        # The same principle as TC2-7 (Linda, 16 Oct): an ingredient supplier and a frozen-food maker can be vertically
        # related at market level, so Koa's ingredients → FRoSTA are expected results for the lawyer to check.
        {"id": "TC3-7", "portco": "FRoSTA", "what": "control: nothing in common, except Koa's ingredients as an input",
         "target": ANY, "portco_act": ANY, "expect": "screened out", "except": [(KOA_INGREDIENTS, ANY)]},
    ],
    # ------------------------------------------------------------------ OS Brillux (other sector, added 16 Oct)
    # Expert view from what the companies publicly make and sell: done criterion 2 (spec section 16) asks whether the
    # generic design gives sensible results outside cocoa. Written after the first run of 16 Oct, so it is a check of
    # plausibility, not a blind benchmark (A3). No precedent of this sector is in the corpus, so only the factual
    # comparison is checked.
    "OS": [
        {"id": "OS-1", "portco": "Sto", "what": "Sto facade systems, paints and renders ↔ Brillux paints and plasters",
         "target": act(r"paint|coating|plaster"), "portco_act": act(r"facade|façade|paint|coating|render|plaster"),
         "expect": "horizontal"},
        {"id": "OS-2", "portco": "Hornbach", "what": "Brillux paints → Hornbach DIY stores / builders' merchants (resale)",
         "target": act(r"paint|coating"), "portco_act": act(levels=RESELLING), "expect": "vertical", "direction": "down"},
        {"id": "OS-3", "portco": "Henkel", "what": "Henkel construction adhesives and sealants ↔ Brillux (both sell "
         "building products to trades)", "target": act(r"paint|coating|plaster|adhesive"),
         "portco_act": act(r"construction|craftsman|building|professional"), "expect": "kept"},
        {"id": "OS-4", "portco": "Henkel", "what": "control: Henkel laundry, home care and hair products",
         "target": ANY, "portco_act": act(r"laundry|detergent|home.care|hair"), "expect": "screened out"},
    ],
}


# =============================================================== matching
def activity_text(a):
    return " ".join([a.get("product", ""), " ".join(a.get("includes") or []), a.get("description", ""),
                     a.get("intended_use", ""),
                     a.get("business_area", ""), a.get("entity", ""), " ".join(a.get("brands") or [])])


def matches(activity, spec):
    text = activity_text(activity)
    if spec["levels"] and activity.get("value_chain_level") not in spec["levels"]:
        return False
    if spec["words"] and not re.search(spec["words"], text, re.IGNORECASE):
        return False
    # broad activities list everything under "includes"; an exclusion applies to what the activity IS (its name and
    # business area), not to everything it includes
    name = " ".join([activity.get("product", ""), activity.get("business_area", "")])
    if spec["exclude"] and re.search(spec["exclude"], name, re.IGNORECASE):
        return False
    return True


DOWN = {"A could be an input for B", "A could be resold by B"}     # the target (A) supplies the portco (B)
UP = {"B could be an input for A", "B could be resold by A"}


def _fulfils(result, expect, direction=None):
    d = result["decision"]
    if expect == "horizontal":
        return d["horizontal"]
    if expect == "vertical":
        links = set(d["vertical_links"])
        if direction == "down":
            links &= DOWN
        elif direction == "up":
            links &= UP
        return bool(links)
    return d["status"] != "screened out"  # "kept"


def run_checks(case, target, mapped, results, similarity_unclear):
    """Returns one row per check: id, what, mark, detail, labels (the pairs the check looked at)."""
    rows = []
    for chk in BENCHMARK.get(case, []):
        portco, expect = chk["portco"], chk["expect"]
        if portco not in mapped:
            rows.append({**chk, "mark": "–", "detail": f"{portco} not in this run", "labels": []})
            continue

        if expect in ("relationship", "relationship observation"):
            found = portco in mapped[target]["mentions"] or target in mapped[portco]["mentions"]
            observation = expect == "relationship observation"
            rows.append({**chk, "mark": "○" if observation else ("✔" if found else "∅"), "labels": [],
                         "detail": ("observation: " if observation else "")
                         + ("🔗 mention found in the public sources" if found
                            else "no mention in either company's search notes")})
            continue

        pairs = [r for r in results if r["portco"] == portco]
        if expect == "observation":
            hits = [r for r in pairs if matches(r["a"], chk["target"]) and matches(r["b"], chk["portco_act"])]
            if not hits:
                rows.append({**chk, "mark": "○", "labels": [], "detail": "observation: no matching pair in this run "
                                                                         "(activity not extracted separately)"})
                continue
            vertical = [r for r in hits if r["decision"]["vertical_links"]]
            kept = [r for r in hits if r["decision"]["status"] != "screened out"]
            best = max(hits, key=lambda r: r["sims"]["product"])
            detail = (f"observation: {len(vertical)} of {len(hits)} matching pairs vertical, {len(kept)} kept"
                      + ("" if kept else f"; all screened out (closest {best['label_a']}↔{best['label_b']} "
                                         f"sim. {best['sims']['product']:.2f}, AI: {best['comparison']['product_relation']})"))
            rows.append({**chk, "mark": "○", "labels": [f"{r['label_a']}↔{r['label_b']}" for r in (vertical or kept or hits)],
                         "detail": detail})
            continue
        if expect == "screened out":
            # a control row may cover only some activities of the portco (OS-4); TC rows use ANY on both sides
            pairs = [r for r in pairs if matches(r["a"], chk.get("target", ANY)) and matches(r["b"], chk.get("portco_act", ANY))]
            exempt = [r for r in pairs for t, p in chk.get("except", []) if matches(r["a"], t) and matches(r["b"], p)]
            exempt_ids = {id(r) for r in exempt}
            kept = [r for r in pairs if r["decision"]["status"] == "candidate" and id(r) not in exempt_ids]
            unclear = [r for r in pairs if r["decision"]["status"] == "unclear" and id(r) not in exempt_ids]
            note = (f" ({len(exempt)} expected pairs exempt)" if exempt else "") + \
                (f"; {len(unclear)} unclear (not enough information): "
                 + ", ".join(f"{r['label_a']}↔{r['label_b']}" for r in unclear) if unclear else "")
            rows.append({**chk, "mark": "✔" if not kept else "⚠",
                         "labels": [f"{r['label_a']}↔{r['label_b']}" for r in kept],
                         "detail": (f"no candidate among {len(pairs) - len(exempt)} pairs" + note) if not kept
                         else f"{len(kept)} of {len(pairs) - len(exempt)} pairs kept as candidates: check whether these "
                              f"are false positives" + note})
            continue

        t_acts = [a for a in mapped[target]["extraction"]["activities"] if matches(a, chk["target"])]
        p_acts = [a for a in mapped[portco]["extraction"]["activities"] if matches(a, chk["portco_act"])]
        if not t_acts or not p_acts:
            side = "target" if not t_acts else portco
            rows.append({**chk, "mark": "∅", "labels": [],
                         "detail": f"no matching {side} activity (extraction missed it, or adjust the keywords)"})
            continue

        hits = [r for r in pairs if matches(r["a"], chk["target"]) and matches(r["b"], chk["portco_act"])]
        if not hits:     # both sides exist, but no pair of them was compared (e.g. "Other" x "Other", 17 Oct)
            rows.append({**chk, "mark": "∅", "labels": [],
                         "detail": "the matching activities exist, but none of their pairs was compared"})
            continue
        good = [r for r in hits if _fulfils(r, expect, chk.get("direction"))]
        kept = [r for r in hits if r["decision"]["status"] != "screened out"]
        labels = [f"{r['label_a']}↔{r['label_b']}" for r in (good or kept or hits)]
        if good:
            rows.append({**chk, "mark": "✔", "labels": labels,
                         "detail": f"{len(good)} of {len(hits)} matching pairs as expected"})
        elif kept:
            statuses = sorted({r["decision"]["status"] + (" (horizontal)" if r["decision"]["horizontal"] else "")
                               for r in kept})
            wrong_way = expect == "vertical" and chk.get("direction") and any(r["decision"]["vertical_links"] for r in kept)
            rows.append({**chk, "mark": "◐", "labels": labels,
                         "detail": f"kept, but as {', '.join(statuses)} rather than {expect}"
                                   + (f" in the expected direction ({chk['direction']}stream: the link found runs the "
                                      "other way)" if wrong_way else "")})
        else:
            best = max(hits, key=lambda r: r["sims"]["product"])
            s = best["sims"]["product"]
            rows.append({**chk, "mark": "✖", "labels": labels,
                         "detail": f"all {len(hits)} matching pairs screened out; closest pair "
                                   f"{best['label_a']}↔{best['label_b']} sim. {s:.2f} "
                                   f"(AI: {best['comparison']['product_relation']}); it would be kept as unclear "
                                   f"if SIMILARITY_UNCLEAR ≤ {s:.2f} (now {similarity_unclear})"})
    return rows