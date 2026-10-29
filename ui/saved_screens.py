"""
ui/saved_screens.py - continuing a saved screen ("Save progress" Word document, or an audit log), and the audit
log itself: every AI call with what it was sent and returned.
"""
import copy
import json

import streamlit as st

from logic import activity_mapping as am
from logic import ai_client
from logic import comparison as cmp
from logic import export
from logic import precedents as prec
from logic import rules
from logic import uploads

from ui.common import DEV_MODE, esc, now_local, plural, PROFILE, ss, USE_CACHE
from ui.working_screen import reset_all
from ui.activity_display import profile_of
from steps.step1_companies import company_key, extracted
from steps.step3_assessment import activities_hash, current_overrides, has_added
from steps.step4_search import precedent_rows


# Useful e.g. for a lawyer who is only interested in step ④. Restores the screen from an audit log downloaded from this
# app (steps ①–② from a file saved before the comparison; ①–③, and ④ if the file has it, from a later one), without any
# AI call. The file stays with the lawyer; the app stores nothing.
AUDIT_REQUIRED = ("companies", "stage_1_2_activity_mapping")


def _activities_for(acts, companies):
    """acts if it holds an activity list for every company, else None."""
    ok = isinstance(acts, dict) and all(isinstance(acts.get(c["name"]), list) for c in companies)
    return acts if ok else None


def check_audit(data):
    """The problems that stop a file from being loaded (empty list = it can be loaded). A file saved in step ② has no
    comparison yet ("stage_2_confirmed_activities" is empty) and continues in step ②."""
    if not isinstance(data, dict):
        return ["the file is not an audit log of this app"]
    missing = [k for k in AUDIT_REQUIRED if k not in data]
    if missing:
        return [f"the file has no {', '.join(missing)} (a progress file saved with this app is needed)"]
    companies = data["companies"]
    if not isinstance(companies, list) or not companies or not all(isinstance(c, dict) and c.get("name")
                                                                   for c in companies):
        return ["the list of companies is missing or damaged"]
    problems = []
    confirmed = data.get("stage_2_confirmed_activities")
    if confirmed is not None:                  # saved after a comparison (step ③ or later)
        if _activities_for(confirmed, companies) is None:
            problems.append("the confirmed activities are missing or damaged")
        results = data.get("stage_3_factual_comparison")
        if not isinstance(results, list) or not all(isinstance(r, dict) and {"a", "b", "decision", "comparison",
                                                                             "portco"} <= set(r) for r in results):
            problems.append("the results of step ③ are missing or damaged")
    else:                                      # saved in step ②, before a comparison
        mapping = data.get("stage_1_2_activity_mapping")
        researched = isinstance(mapping, dict) and all(isinstance(mapping.get(c["name"]), dict) for c in companies)
        if _activities_for(data.get("stage_2_current_activities"), companies) is None and not researched:
            problems.append("the activities are missing or damaged")
    return problems


def load_audit(data):
    """Restores the screen of an audit log into the session (after reset_all). No AI call. A file saved after a
    comparison continues in step ③ (or ④); one saved in step ②, before a comparison, continues in step ②. Edits made
    in step ② after the last comparison come back as they were saved."""
    reset_all()
    for k, v in (("stage_logs", {}), ("acts_version", 0)):    # removed by reset_all
        ss.setdefault(k, v)
    companies, mapped = data["companies"], data["stage_1_2_activity_mapping"] or {}
    confirmed = _activities_for(data.get("stage_2_confirmed_activities"), companies)
    compared = confirmed is not None
    current = _activities_for(data.get("stage_2_current_activities"), companies)
    if current is None:          # a file without them: the confirmed activities, else those of the research
        current = confirmed if compared else {c["name"]: copy.deepcopy(extracted(mapped.get(c["name"]) or {}))
                                             for c in companies}
    ss.companies = companies
    ss.mapped = {c["name"]: mapped.get(c["name"]) or {"extraction": {"activities": current[c["name"]]}}
                 for c in companies}
    ss.map_keys = {c["name"]: company_key(c) for c in companies}
    if compared:
        cmp.ensure_ids(confirmed)
        # the research the comparison was made on: saved apart only where a company was mapped again afterwards
        saved = data.get("stage_3_research_compared") or {}
        ss.compared_research = {c["name"]: saved.get(c["name"]) or (ss.mapped[c["name"]].get("search"))
                                for c in companies}
        ss.compared_names = [c["name"] for c in companies]
        basis = {n: dict(m, search=ss.compared_research.get(n)) for n, m in ss.mapped.items()}
    else:
        basis = ss.mapped
    # found again from the saved research, with the current rule (a saved file may hold false matches)
    ss.relationships = am.find_relationships(basis, companies,
                                             (data.get("anonymisation") or {}).get("kept_as_ordinary_words") or ())
    ss.acts = copy.deepcopy(current)
    cmp.ensure_ids(ss.acts)
    ss.profiles_text = data.get("stage_2_company_profiles") or {}
    # the saved profiles count as the lawyer's version (they may have been edited); mapping a company again
    # replaces its profile, as in a live screen
    ss.profiles_edit = {n: t for n, t in ss.profiles_text.items() if isinstance(t, str)}
    anon = data.get("anonymisation") or {}
    ss.keep_words = list(anon.get("kept_as_ordinary_words") or [])
    ss.keep_proposed = list(anon.get("proposed_by_the_tool (used in lower case)") or [])
    ss.drop_words = list(anon.get("unticked_by_user (removed)") or [])
    ss.freeze_proposals = True
    group = {c["name"]: ((ss.mapped[c["name"]].get("extraction") or {}).get("group_companies") or [])
             for c in companies}
    ss.names = cmp.collect_names(companies, confirmed if compared else ss.acts, group, ss.keep_words)
    ss.profiles_meta = anon.get("abstracts") or {}
    ss.pair_cache = {}
    if compared:
        results = [{k: v for k, v in r.items() if k != "status_after_overrides"}
                   for r in data["stage_3_factual_comparison"]]
        ss.results = results
        ss.confirmed = confirmed
        ss.confirmed_hash = activities_hash(confirmed)
        ss.current_hash = activities_hash(ss.acts)
        # the pair results under their content keys, so that "Update the comparison" sends only new or changed pairs
        # (and pairs whose call had failed)
        for r in results:
            if (r.get("comparison") or {}).get("error"):
                continue
            try:
                ss.pair_cache[(cmp.activity_key(r["a"], r["abstract_a"]),
                               cmp.activity_key(r["b"], r["abstract_b"]))] = r
            except (KeyError, TypeError):
                pass
    else:
        ss.results = ss.confirmed = ss.confirmed_hash = None
        ss.compared_research = {}
    ss.vec_cache = {}
    ss.override_store = {pid: dict(o) for pid, o in (data.get("user_overrides") or {}).items() if isinstance(o, dict)}
    ss.results_version = 1
    ss.uploads = uploads.from_audit(data.get("user_added_decisions"))     # embedded again when step ④ next searches
    ss.precedents = dict((data.get("stage_4_market_definitions") or {}).get("searches") or {})
    for rec in ss.precedents.values():     # the conclusion labels follow the verified passages, whatever the file holds
        if isinstance(rec, dict):
            prec.verify_labels(rec)
    prec.unify_names(ss.precedents.values())
    before = list(data.get("call_log_before_loading") or []) + list(data.get("call_log") or [])
    ss.loaded_calls = before
    ss.loaded_from = {"created": data.get("created"), "loaded": now_local().isoformat(timespec="seconds"),
                      "profile": data.get("profile"), "models": data.get("models"),
                      "calls_before": {"calls": len(before), "cost": round(sum(c.get("cost", 0) or 0 for c in before), 4)}}
    ss.acts_version += 1
    ss.step = (4 if ss.precedents else 3) if compared else 2


def loader_box():
    """'Open saved progress' in the sidebar."""
    st.caption("Continues a screen from a Word document saved with “Save progress” (or an audit log, .json): "
               "companies, activities, the assessment and step ④, with your views, notes and edits, without any AI "
               "call. The current screen is replaced. The file stays with you; the app stores nothing.")
    up = st.file_uploader("Progress file (.docx or .json)", type=["docx", "json"], key="audit_upload",
                          label_visibility="collapsed")
    if up is None:
        return
    blob = up.getvalue()
    try:
        if up.name.lower().endswith(".docx"):
            data = export.read_progress(blob)
            if data is None:
                st.error("This Word document holds no screen data. Only a document saved with “Save progress” can be "
                         "opened again (“Download the Word document” saves it without the data).")
                return
        else:
            data = json.loads(blob.decode("utf-8"))
    except ValueError as e:          # also UnicodeDecodeError and json.JSONDecodeError
        st.error(f"The file could not be read: {e}")
        return
    problems = check_audit(data)
    if problems:
        st.error("This file cannot be loaded: " + "; ".join(problems) + ".")
        return
    target = data["companies"][0]["name"]
    reached = (", with step ④" if data.get("stage_4_market_definitions")
               else ", with the assessment (step ③)" if data.get("stage_2_confirmed_activities") is not None
               else ", activities only (continues in step ②)")
    added = [u.get("case", "") for u in data.get("user_added_decisions") or [] if isinstance(u, dict)]
    st.write(f"Saved {esc((data.get('created') or 'unknown date').replace('T', ' '))}: target **{esc(target)}**, "
             f"{plural(len(data['companies']) - 1, 'portfolio company', 'portfolio companies')}{reached}"
             + (f", with the {plural(len(added), 'decision')} you added ({esc(', '.join(added))})" if added else "")
             + ".")
    if st.button("Load this screen", type="primary"):
        load_audit(data)
        st.rerun()


def audit_calls():
    """Every call of the current screen (since the screen started): the research of each company, including companies
    mapped again, and every comparison run. A comparison only sends new or changed pairs, so no call
    is repeated, and the results shown can come from any of these runs."""
    return ss.log.calls[ss.get("run_first", 0):]


def audit_snapshot(ai):
    """References to everything the audit log contains, taken in the script thread. The JSON itself is built
    only when the user clicks the download button (on another thread, which cannot read session state).
    The overrides are refreshed first: "Save progress" sits in the sidebar, which is drawn before the table, so
    without this a box ticked just before saving would be missing from the file."""
    compared = ss.get("results") is not None
    if compared:
        current_overrides()
    return {"created": now_local().isoformat(timespec="seconds"), "profile": PROFILE, "dev_mode": DEV_MODE,
            "cache": USE_CACHE, "models": dict(ai.models),
            "companies": ss.get("companies"), "mapped": ss.get("mapped"), "relationships": ss.get("relationships"),
            "confirmed": ss.get("confirmed") if compared else None,
            # the activities as they are in step ② now, with edits not compared yet
            "acts": ss.get("acts"), "compared_research": ss.get("compared_research") or {},
            # the profiles as shown now (including an edit after the comparison)
            "profiles": {c["name"]: profile_of(c["name"]) for c in ss.get("companies") or []},
            "names": list(ss.get("names") or []), "keep_words": list(ss.get("keep_words") or []),
            "keep_proposed": list(ss.get("keep_proposed") or []), "drop_words": list(ss.get("drop_words") or []),
            "abstracts": ss.get("profiles_meta"), "results": list(ss.get("results") or []),
            # before a comparison (or after the companies changed): every view, dismissal and note kept so far, so
            # that they apply again once the activities are compared
            "overrides": dict(ss.get("overrides") or {}) if compared else dict(ss.get("override_store") or {}),
            "calls": audit_calls(),
            # step ④ (one search per target activity) and, for a continued screen, where it came from
            "precedents": dict(ss.get("precedents") or {}), "precedent_rows": precedent_rows(),
            # the decisions the lawyer added for this screen (their paragraphs; the embeddings are made again)
            "uploads": uploads.for_audit(ss.get("uploads")),
            "loaded_from": ss.get("loaded_from"), "loaded_calls": list(ss.get("loaded_calls") or [])}


def audit_json(snap):
    slim = [{k: v for k, v in r.items() if k != "sims"}
            | {"sims": {k: round(v, 3) for k, v in r["sims"].items()},
               "status_after_overrides": (r["decision"]["status"] if cmp.effective_status(r, snap["overrides"])
                                          == "dismissed by user" and has_added(snap["overrides"].get(cmp.pair_id(r)))
                                          else cmp.effective_status(r, snap["overrides"]))}
            for r in snap["results"]]
    log = {
        "created": snap["created"], "profile": snap["profile"], "dev_mode": snap["dev_mode"],
        "development_cache": snap["cache"], "models": snap["models"],
        "prices": {"checked": ai_client.PRICES_CHECKED, "usd_per_1m_tokens": ai_client.PRICES},
        "thresholds": {"input_match": rules.INPUT_MATCH, "resale_match": rules.RESALE_MATCH},
        "companies": snap["companies"],
        "stage_1_2_activity_mapping": snap["mapped"],
        "existing_relationships": snap["relationships"],
        "stage_2_company_profiles": snap["profiles"],
        "stage_2_confirmed_activities": snap["confirmed"],
        "stage_2_current_activities": snap["acts"],
        "anonymisation": {"name_variants_removed": sorted(rules.name_variants(snap["names"])),
                          "kept_as_ordinary_words": snap["keep_words"],
                          "proposed_by_the_tool (used in lower case)": snap["keep_proposed"],
                          "unticked_by_user (removed)": snap["drop_words"],
                          "abstracts": snap["abstracts"]},
        "stage_3_factual_comparison": slim,
        "user_overrides": snap["overrides"],
        "call_log": snap["calls"],
    }
    # a company mapped again after the comparison: the research the compared activities' source numbers refer to
    mapped = snap["mapped"] or {}
    earlier = {n: r for n, r in (snap.get("compared_research") or {}).items()
               if r is not None and r is not ((mapped.get(n) or {}).get("search"))}
    if snap["confirmed"] is not None and earlier:
        log["stage_3_research_compared"] = earlier
    if snap.get("precedents"):
        log["stage_4_market_definitions"] = {
            "settings": {"max_attempts": prec.MAX_ATTEMPTS, "types_per_search": prec.MAX_TYPES,
                         "reflection": "one call per type of product", "max_paragraphs_per_type": prec.MAX_PARAGRAPHS,
                         "conclusion": "what the Commission decided and what it left open, each only as a passage quoted "
                                       "word for word from a paragraph sent (checked in code); otherwise taken in code "
                                       "from the same market in another search of the same activity",
                         "query_forms": list(prec.QUERY_FORMS), "hits_per_form": prec.HITS_PER_FORM,
                         "unit": "one search per target activity"},
            "searches": snap["precedents"], "rows": snap["precedent_rows"]}
    if snap.get("uploads"):
        log["user_added_decisions"] = snap["uploads"]
    if snap.get("loaded_from"):
        log["loaded_from_saved_audit"] = snap["loaded_from"]
        log["call_log_before_loading"] = snap["loaded_calls"]
    return json.dumps(log, ensure_ascii=False, indent=1, default=str)
