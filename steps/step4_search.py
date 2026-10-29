"""
steps/step4_search.py - step ④ Commission Market Definitions, the search: which rows need a search, running it in
the decision database (logic/precedents.py, logic/retrieval.py), and the button that starts or updates it.
"""
import concurrent.futures as cf
import time

import streamlit as st

from logic import ai_client
from logic import comparison as cmp
from logic import precedents as prec
from logic import uploads

from ui.common import capital, esc, go_to, log_stage, plural, ss
from ui.working_screen import start_work, WorkCard
from ui.activity_display import display_order
from steps.step3_assessment import current_overrides, search_overrides


# One search per target activity, covering the items of all its kept rows on both sides; at most one rewrite of the
# queries. The search itself is in logic/precedents.py; everything shown here is assembled in code from its stored
# records.
def prec_plan():
    """(units, todo): one unit per target activity with kept rows; todo = those without a search that still covers
    them (new, changed, or rows added back since). Dismissing a row never forces a new search."""
    if not ss.get("results"):
        return [], []
    target = ss.companies[0]["name"]
    order = [ss.confirmed[target][k]["aid"] for k in display_order(ss.confirmed[target])]
    units = prec.search_units(ss.results, search_overrides(), cmp.effective_status, cmp.dismissed_parts,
                              cmp.pair_id, order)
    store = ss.get("precedents") or {}
    sig = uploads.signature(ss.get("uploads"))
    return units, [u for u in units if not prec.reusable(store.get(u["target_aid"]), u)
                   or (store.get(u["target_aid"]) or {}).get("uploads", "") != sig]


def uploads_changed():
    """Whether a decision was added or removed after a stored search (the search then runs again with "Update the
    market definitions"; until then the rows keep the result of the earlier search)."""
    sig = uploads.signature(ss.get("uploads"))
    return any(isinstance(rec, dict) and rec.get("uploads", "") != sig for rec in (ss.get("precedents") or {}).values())


def stale_units(todo):
    """The target activities whose rows changed since their search: those of their rows that the search no longer
    covers say "Changed since the search" (or "Not looked up yet"), the others keep their result (row_view).
    A search that failed does not count as changed: it keeps its record and shows its failure; "Update the market
    definitions" runs it again either way."""
    store = ss.get("precedents") or {}
    out = set()
    for u in todo:
        rec = store.get(u["target_aid"])
        if not prec.reusable(rec, u, retry_failed=False):
            out.add(u["target_aid"])
    return out


def run_precedents(ai):
    """Runs the searches that are needed, in parallel (at most ai_client.MAX_PARALLEL AI requests at once), and opens
    step ④."""
    from logic import retrieval            # ChromaDB is loaded only when step ④ runs
    current_overrides()
    units, todo = prec_plan()
    first, t0 = ss.log.mark(), time.time()
    store = dict(ss.get("precedents") or {})
    card = WorkCard("Looking Up the Commission's Market Definitions", "Sorting the products into types of product …",
                    "Each type of product is searched in the Commission's decisions and read on its own; the AI sees "
                    "the products only, never company names. This usually takes one to four minutes.")
    kept = [u for u in units if u not in todo]
    if kept:
        card.log("✔ Rows that did not change keep their earlier result")
    added = ss.get("uploads") or []
    for u in added:                # after "Open saved progress" the added decisions come without their embeddings
        if u.get("vectors") is None:
            card.log(f"Embedding the decision you added, {u['case']} ({plural(len(u['paragraphs']), 'paragraph')})")
            try:
                uploads.embed_upload(u, lambda texts, c=u["case"]: ai.embed(texts, note=f"decision added: {c}",
                                                                            step="embed_upload"))
            except Exception as e:  # noqa: BLE001 - nothing is lost; the user can try again
                st.error(f"The search could not start: the decision you added, {u['case']}, could not be prepared for "
                         f"the search ({type(e).__name__}: {e}). Nothing was changed; go back and try again.")
                st.button("← Back to the assessment", on_click=go_to, args=(3,))
                return False
    try:
        retriever = retrieval.Retriever(prec.cached_embed(ai), extra=uploads.extra_index(added))
    except Exception as e:  # noqa: BLE001 - nothing is lost; the user can try again
        st.error(f"The search could not start: the decision database could not be opened ({type(e).__name__}: {e}). "
                 "Nothing was changed; go back and try again.")
        st.button("← Back to the assessment", on_click=go_to, args=(3,))
        return False
    # a progress bar per type of product (step ④ takes several minutes); the worker threads count, this thread
    # only reads
    progress = prec.Progress()
    with cf.ThreadPoolExecutor(ai_client.MAX_PARALLEL) as ex:
        futures = {ex.submit(prec.run_unit, ai, u, ss.names, retriever, retriever.paragraphs, progress): u
                   for u in todo}
        pending = set(futures)
        while pending:
            done, pending = cf.wait(pending, timeout=1, return_when=cf.FIRST_COMPLETED)
            if progress.planned:
                card.update(progress.done / progress.planned,
                            f"{progress.done} of {plural(progress.planned, 'type of product', 'types of product')} "
                            "looked up")
            else:
                card.tick()
            for fut in done:
                u = futures[fut]
                try:
                    rec = fut.result()
                except Exception as e:  # noqa: BLE001 - shown in the row as an error, never as "no precedent"
                    rec = prec.empty_record(u, error=f"the search failed: {type(e).__name__}: {e}")
                if added:              # the decisions added when it ran (no key without them: older records match)
                    rec["uploads"] = uploads.signature(added)
                    rec["uploaded_decisions"] = [x["case"] for x in added]
                show_search_done(store, u, rec, card)
    card.log(f"Market definitions looked up for {plural(len(todo), 'activity', 'activities')} of the target in "
             f"{time.time() - t0:.0f} s")
    prec.unify_names(store.values())
    ss.precedents = store
    log_stage("precedents", first, time.time() - t0)
    ss.step = 4
    return True


def show_search_done(store, u, rec, card):
    """Stores one finished search and writes its line in the developer details."""
    store[u["target_aid"]] = rec
    name = capital(u["target_product"])
    if rec.get("error"):
        card.log(f"✖ {name}: {rec['error']}")
        return
    placed = sum(1 for p in rec["placements"].values() if prec.ids_of(p))
    failed = len(prec.failed_ids(rec))
    card.log(f"{'⚠' if failed else '✔'} {name}: {plural(len(rec['markets']), 'market')}, {placed} of "
             f"{plural(len(rec['placements']), 'product')} placed"
             + (f", the search failed for {failed}" if failed else "") + f" · {rec['stop']}")


def prec_record(r):
    return (ss.get("precedents") or {}).get(r["a"].get("aid"))


def row_view(r):
    """(stored search, what the row shows) or (search, None) if the search does not cover the row (yet). A search that
    is out of date because of other rows of its target activity still serves the rows whose products it covers."""
    rec = prec_record(r)
    if not rec:
        return rec, None
    if r["a"].get("aid") in (ss.get("prec_stale") or set()):
        items = prec.row_items(r, search_overrides(), cmp.effective_status, cmp.dismissed_parts)
        if not prec.row_covered(rec, r, items):
            return rec, None
    return rec, prec.row_view(r, rec, search_overrides(), cmp.effective_status, cmp.dismissed_parts)


def search_gap(r, rec):
    """Why a kept row has no Commission result: never searched, or changed since the search."""
    return "Changed since the search" if prec.searched_before(rec, r) else "Not looked up yet"


def row_failed(r):
    """The products of a row whose step ④ search failed: shown as a failed search, never as a result."""
    _, view = row_view(r)
    return list(dict.fromkeys((view or {}).get("failed") or []))


def precedent_warnings(units):
    """Only what needs action (the search summary is in the saved progress file, not on the page)."""
    records = [ss.precedents[u["target_aid"]] for u in units if u["target_aid"] in ss.precedents]
    s = prec.summary(records)
    if s["errors"]:
        st.warning("Some searches failed: " + "; ".join(esc(e) for e in s["errors"]) + ". Press “Update the market "
                   "definitions” to try them again.")


def precedent_button(units, todo, step=4):
    store = ss.get("precedents") or {}
    failed = [u for u in units if (store.get(u["target_aid"]) or {}).get("error")]
    todo = todo + [u for u in failed if u not in todo]
    if not units:
        st.caption("No row is kept: there are no market definitions to look up. The summary and the Word document "
                   "list every pair compared, with the reason.")
        st.button("Go to the summary →", type="primary", on_click=go_to, args=(5,))
        return
    if not store:
        if st.button("Find Commission market definitions", type="primary"):
            start_work("precedents")
        return
    # the market definitions exist: the way on (to step ④ from step ③, to the summary from step ④), and, if rows
    # changed or a search failed, the update first
    with st.container(horizontal=True, vertical_alignment="center"):
        if todo:
            if st.button("Update the market definitions", type="primary"):
                for u in failed:          # a failed search is never "reusable": drop it so that it runs again
                    ss.precedents.pop(u["target_aid"], None)
                start_work("precedents")
        nxt = "secondary" if todo else "primary"
        if step == 3:
            st.button("Go to the market definitions →", type=nxt, on_click=go_to, args=(4,), key="to_step4")
        else:
            st.button("Go to the summary →", type=nxt, on_click=go_to, args=(5,), key="to_step5")


def precedent_rows():
    """Per kept row: the markets on each side and the verdict, as the table shows them (for the audit log)."""
    if not ss.get("precedents") or not ss.get("results"):
        return {}
    out = {}
    for r in ss.results:
        rec, view = row_view(r)
        if view is None:
            continue
        out[cmp.pair_id(r)] = {
            "target_activity": r["a"].get("product"), "portco": r["portco"], "portco_activity": r["b"].get("product"),
            "target_side": [{"market": (g["market"] or {}).get("name"), "basis": g["basis"], "items": g["items"],
                             "status": g.get("status"), "notes": g.get("notes") or {}} for g in view["a"]],
            "portco_side": [{"market": (g["market"] or {}).get("name"), "basis": g["basis"], "items": g["items"],
                             "status": g.get("status"), "notes": g.get("notes") or {}} for g in view["b"]],
            "verdict": None if not view.get("verdict") else {
                "both": [(g["market"] or {}).get("name") for g in view["verdict"]["both"]],
                "possibly_both": [(g["market"] or {}).get("name") for g in view["verdict"].get("possibly", [])],
                "both_only_through_a_general_term": [(g["market"] or {}).get("name")
                                                     for g in view["verdict"].get("general", [])],
                "only_target": [(g["market"] or {}).get("name") for g in view["verdict"]["only_a"]],
                "only_portco": [(g["market"] or {}).get("name") for g in view["verdict"]["only_b"]],
                "different_markets_under_the_precedent": view["verdict"]["different"],
                "left_open": view["verdict"]["left_open"],
                "conclusion_not_in_paragraphs": view["verdict"].get("not_stated", False)},
            "search_failed_for": view.get("failed") or [],
            "error": view.get("error") or ""}
    return out
