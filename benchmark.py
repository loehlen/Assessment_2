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
  "observation"   reports how the matching pairs came out (vertical / kept / screened out), with the mark ○
"""
import re

# value-chain levels (same strings as rules.VALUE_CHAIN_LEVELS)
FINISHED = {"finished products"}
INTERMEDIATE = {"intermediate products", "raw materials"}
RETAIL = {"retail"}

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
                      exclude=r"shot|ready-to-drink|sold directly to consumers")

BENCHMARK = {
    # ------------------------------------------------------------------ TC1 Lindt & Sprüngli (full precedent)
    "TC1": [
        {"id": "TC1-1", "portco": "Ritter Sport", "what": "consumer chocolate ↔ consumer chocolate",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(CHOCOLATE, FINISHED), "expect": "horizontal"},
        {"id": "TC1-2", "portco": "Ritter Sport", "what": "own shops ↔ own shops (both in Berlin)",
         "target": act(RETAIL_WORDS, RETAIL), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "horizontal"},
        {"id": "TC1-3", "portco": "Ritter Sport", "what": "Lindt chocolate → Ritter shops (vertical at market level; shops sell only own products)",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "vertical"},
        {"id": "TC1-4", "portco": "Ritter Sport", "what": "Amicelli wafer rolls ↔ Lindt chocolate",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(r"amicelli|wafer"), "expect": "kept"},
        {"id": "TC1-5", "portco": "Barry Callebaut", "what": "semi-finished / industrial chocolate → Lindt",
         "target": act(CHOCOLATE, FINISHED),
         "portco_act": act(r"cocoa (butter|liquor|mass|powder)|semi-finished|industrial chocolate|couverture"),
         "expect": "vertical"},
        {"id": "TC1-6", "portco": "Barry Callebaut", "what": "industrial chocolate ↔ Lindt consumer chocolate (●○○)",
         "target": act(CHOCOLATE, FINISHED),
         "portco_act": act(r"chocolate|couverture", INTERMEDIATE, exclude=r"compound|cocoa-free|beverage|drink"),
         "expect": "horizontal"},
        {"id": "TC1-7", "portco": "Barry Callebaut", "what": "beverages ↔ Lindt hot chocolate (◐)",
         "target": act(r"hot chocolate|drinking chocolate|beverage|cocoa drink"),
         "portco_act": act(r"beverage|drink|vending|hot chocolate"), "expect": "kept"},
        {"id": "TC1-8", "portco": "Bahlsen", "what": "chocolate ↔ biscuits (must never be screened out)",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(BISCUITS, FINISHED), "expect": "kept"},
        {"id": "TC1-9", "portco": "Bahlsen", "what": "Bahlsen outlets ↔ Lindt shops",
         "target": act(RETAIL_WORDS, RETAIL), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "horizontal"},
        {"id": "TC1-10", "portco": "Bahlsen", "what": "Lindt chocolate → Bahlsen outlets (distribution, M.5644 (47))",
         "target": act(CHOCOLATE, FINISHED), "portco_act": act(RETAIL_WORDS, RETAIL), "expect": "vertical"},
        {"id": "TC1-11", "portco": "Bahlsen", "what": "Caffarel candies ↔ Bisquiva peppermint tablets (◐)",
         "target": act(r"cand(y|ies)|jell|sugar confectionery|non-chocolate"),
         "portco_act": act(r"peppermint|mint|sugar confectionery|cand(y|ies)"), "expect": "kept"},
        {"id": "TC1-12", "portco": "FRoSTA", "what": "control: nothing else in common (except TC1-13)",
         "target": ANY, "portco_act": ANY, "expect": "screened out",
         "except": [(act(CAFE), FOODSERVICE)]},
        {"id": "TC1-13", "portco": "FRoSTA", "what": "foodservice frozen food → Lindt cafés (found by the tool, 15 Oct; observation)",
         "target": act(CAFE), "portco_act": FOODSERVICE, "expect": "observation"},
    ],
    # ------------------------------------------------------------------ TC2 Planet A Foods (partial precedent)
    "TC2": [
        {"id": "TC2-1", "portco": "Barry Callebaut", "what": "ChoViva partnership (🔗 note must appear)",
         "expect": "relationship"},
        {"id": "TC2-2", "portco": "Barry Callebaut", "what": "compound / industrial chocolate ↔ ChoViva",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(r"compound|chocolate|couverture", INTERMEDIATE, exclude=r"beverage|drink"),
         "expect": "horizontal"},
        {"id": "TC2-3", "portco": "Barry Callebaut", "what": "ChoViva Butter (pipeline) ↔ cocoa butter",
         "target": act(r"butter"), "portco_act": act(r"cocoa butter|butter"), "expect": "kept"},
        {"id": "TC2-4", "portco": "Ritter Sport", "what": "ChoViva → Ritter chocolate (vertical candidate)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(CHOCOLATE, FINISHED), "expect": "vertical"},
        {"id": "TC2-5", "portco": "Ritter Sport", "what": "Ritter consumer chocolate ↔ ChoViva (related, ●○○)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(CHOCOLATE, FINISHED), "expect": "horizontal"},
        {"id": "TC2-6", "portco": "Bahlsen", "what": "ChoViva → biscuits (vertical candidate)",
         "target": act(r"cocoa-free|alternative|chocolate", exclude=r"butter"),
         "portco_act": act(BISCUITS, FINISHED), "expect": "vertical"},
        {"id": "TC2-7", "portco": "FRoSTA", "what": "control: nothing in common",
         "target": ANY, "portco_act": ANY, "expect": "screened out"},
    ],
    # ------------------------------------------------------------------ TC3 Koa (no precedent)
    "TC3": [
        {"id": "TC3-1", "portco": "Barry Callebaut", "what": "Cabosse Naturals ↔ Koa ingredients (central overlap)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"cocoa fruit|pulp|cabosse|juice|concentrate"), "expect": "horizontal"},
        {"id": "TC3-2", "portco": "Barry Callebaut", "what": "Koa ingredients → BC chocolate (vertical candidate)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"chocolate|couverture", INTERMEDIATE, exclude=r"compound|cocoa fruit|pulp"),
         "expect": "vertical"},
        {"id": "TC3-3", "portco": "Barry Callebaut", "what": "Koa drinks ↔ BC beverages (unclear is fine)",
         "target": act(r"shot|drink|beverage", FINISHED | RETAIL),
         "portco_act": act(r"beverage|drink|vending"), "expect": "kept"},
        {"id": "TC3-4", "portco": "Ritter Sport", "what": "CacaoVida ↔ Koa shots",
         "target": act(r"shot|drink|beverage", FINISHED | RETAIL),
         "portco_act": act(r"cacaovida|cocoa fruit|juice|drink|beverage"), "expect": "horizontal"},
        {"id": "TC3-5", "portco": "Ritter Sport", "what": "Koa ingredients → Ritter (chocolate, CacaoVida)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(r"chocolate|cacaovida|cocoa fruit|juice|drink"), "expect": "vertical"},
        {"id": "TC3-6", "portco": "Bahlsen", "what": "Koa ingredients → bakery (vertical candidate)",
         "target": KOA_INGREDIENTS,
         "portco_act": act(BISCUITS), "expect": "vertical"},
        {"id": "TC3-7", "portco": "FRoSTA", "what": "control (possible false positive: fruit ingredient → frozen food)",
         "target": ANY, "portco_act": ANY, "expect": "screened out"},
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


def _fulfils(result, expect):
    d = result["decision"]
    if expect == "horizontal":
        return d["horizontal"]
    if expect == "vertical":
        return bool(d["vertical_links"])
    return d["status"] != "screened out"  # "kept"


def run_checks(case, target, mapped, results, similarity_unclear):
    """Returns one row per check: id, what, mark, detail, labels (the pairs the check looked at)."""
    rows = []
    for chk in BENCHMARK.get(case, []):
        portco, expect = chk["portco"], chk["expect"]
        if portco not in mapped:
            rows.append({**chk, "mark": "–", "detail": f"{portco} not in this run", "labels": []})
            continue

        if expect == "relationship":
            found = portco in mapped[target]["mentions"] or target in mapped[portco]["mentions"]
            rows.append({**chk, "mark": "✔" if found else "∅", "labels": [],
                         "detail": "🔗 mention found in the public sources" if found
                         else "no mention in either company's search notes"})
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
            exempt = [r for r in pairs for t, p in chk.get("except", []) if matches(r["a"], t) and matches(r["b"], p)]
            exempt_ids = {id(r) for r in exempt}
            kept = [r for r in pairs if r["decision"]["status"] != "screened out" and id(r) not in exempt_ids]
            rows.append({**chk, "mark": "✔" if not kept else "⚠",
                         "labels": [f"{r['label_a']}↔{r['label_b']}" for r in kept],
                         "detail": f"all {len(pairs) - len(exempt)} pairs screened out" + (f" ({len(exempt)} expected pairs exempt)" if exempt else "") if not kept
                         else f"{len(kept)} of {len(pairs) - len(exempt)} pairs kept: check whether these are false positives"})
            continue

        t_acts = [a for a in mapped[target]["extraction"]["activities"] if matches(a, chk["target"])]
        p_acts = [a for a in mapped[portco]["extraction"]["activities"] if matches(a, chk["portco_act"])]
        if not t_acts or not p_acts:
            side = "target" if not t_acts else portco
            rows.append({**chk, "mark": "∅", "labels": [],
                         "detail": f"no matching {side} activity (extraction missed it, or adjust the keywords)"})
            continue

        hits = [r for r in pairs if matches(r["a"], chk["target"]) and matches(r["b"], chk["portco_act"])]
        good = [r for r in hits if _fulfils(r, expect)]
        kept = [r for r in hits if r["decision"]["status"] != "screened out"]
        labels = [f"{r['label_a']}↔{r['label_b']}" for r in (good or kept or hits)]
        if good:
            rows.append({**chk, "mark": "✔", "labels": labels,
                         "detail": f"{len(good)} of {len(hits)} matching pairs as expected"})
        elif kept:
            statuses = sorted({r["decision"]["status"] + (" (horizontal)" if r["decision"]["horizontal"] else "")
                               for r in kept})
            rows.append({**chk, "mark": "◐", "labels": labels,
                         "detail": f"kept, but as {', '.join(statuses)} rather than {expect}"})
        else:
            best = max(hits, key=lambda r: r["sims"]["product"])
            s = best["sims"]["product"]
            rows.append({**chk, "mark": "✖", "labels": labels,
                         "detail": f"all {len(hits)} matching pairs screened out; closest pair "
                                   f"{best['label_a']}↔{best['label_b']} sim. {s:.2f} "
                                   f"(AI: {best['comparison']['product_relation']}); it would be kept as unclear "
                                   f"if SIMILARITY_UNCLEAR ≤ {s:.2f} (now {similarity_unclear})"})
    return rows