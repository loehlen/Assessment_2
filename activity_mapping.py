"""
activity_mapping.py - stages 1-2: the activity overview, ONE company per call (spec section 7, steps 1-2).

    map_company(ai, company, companies)     web search + extraction for one company (two isolated calls)
    find_relationships(mapped, companies)   the 🔗 notes: public sources of one company that mention another

A company is a dict: {"name", "role" ("target" / "portco"), "hint", "aliases": [...], "pasted": ""}.
  hint     optional identifying description ("Swiss-Ghanaian company making products from cocoa fruit pulp")
  aliases  other names of the company (removed from every abstract, like the name itself)
  pasted   optional description pasted by the user; added as an extra source "provided by the user"

Ported from test_compare.py (same prompts, same source check, same cache keys), without global state, so that
several Streamlit sessions can run at the same time.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import rules
import schemas
from ai_client import setting

# Development only: the Sol searches of 14 Oct for the seven test companies (spec section 8, dev profile)
SAVED_SEARCH_FILE = Path(setting("SAVED_SEARCH_FILE", "test_results/search_20261014-0130.json"))
SAVED_SEARCH_MODEL = "gpt-6.1-sol"


class Blocked(RuntimeError):
    """Raised by the confidentiality guard: the text names a company that this call may not contain."""


# =============================================================== names and the guard
def names_of(company):
    return [company["name"]] + [a for a in company.get("aliases", []) if a]


def guard(text, permitted, companies):
    """Text the app builds itself may contain at most the one permitted company (spec section 7)."""
    others = [n for c in companies if c["name"] != permitted for n in names_of(c)]
    found = rules.find_names(text, others)
    if found:
        raise Blocked(f"Blocked by the confidentiality guard: the text for {permitted} names {', '.join(found)}")


# =============================================================== sources
def clean_url(url):
    url = re.sub(r"([?&])utm_source=openai(&|$)", lambda m: m.group(1) if m.group(2) else "", url)
    return url.rstrip("?&")


def cited_sources(resp):
    """The url_citation annotations of a web search answer, merged and numbered in code."""
    seen = {}
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) != "message":
            continue
        for part in getattr(item, "content", []) or []:
            for a in getattr(part, "annotations", None) or []:
                if getattr(a, "type", None) == "url_citation":
                    url = clean_url(a.url)
                    seen.setdefault(url, getattr(a, "title", "") or url)
    return [{"n": i + 1, "url": u, "title": t} for i, (u, t) in enumerate(seen.items())]


def _domain_words(name):
    return {w for w in re.findall(r"[a-z0-9]+", rules._german_spelling(rules._without_accents(name)).lower())
            if len(w) >= 4}


def label_sources(sources, company, group_companies):
    """Labels each source 'company' (own or group website) or 'third party', unless already labelled.
    A simple domain check: a word of the company, alias or group company name appears in the domain."""
    words = set()
    for n in names_of(company) + list(group_companies or []):
        words |= _domain_words(n)
    for s in sources:
        if s.get("type"):
            continue
        domain = urlparse(s.get("url", "")).netloc.lower()
        s["type"] = "company" if domain and any(w in domain for w in words) else "third party"
    return sources


# =============================================================== step 1-2a: search (web search, one company)
def saved_search(name):
    """The saved Sol search of 14 Oct for this company (development only), or None."""
    if not SAVED_SEARCH_FILE.exists():
        return None
    for e in json.loads(SAVED_SEARCH_FILE.read_text(encoding="utf-8")):
        if e["company"] == name and e["search_model"] == SAVED_SEARCH_MODEL:
            sources = [{"n": s["number"], "url": clean_url(s["url"]), "title": s.get("title") or s["url"],
                        "type": s.get("type", "")} for s in e["sources"]]
            return {"company": name, "model": f"{SAVED_SEARCH_MODEL} (saved {SAVED_SEARCH_FILE.name})",
                    "date": "2026-10-14", "notes": e["notes"], "sources": sources}
    return None


def search(ai, company, companies, use_saved=False):
    name = company["name"]
    if use_saved:
        found = saved_search(name)
        if found:
            ai.log_cached("search", SAVED_SEARCH_MODEL, f"{name} (saved search)", names=[name])
            return found
    prompt = schemas.search_prompt(name, company.get("hint", ""))
    guard(prompt, name, companies)
    model = ai.model("search")
    path, hit = ai.cache_get("search", [model, prompt])
    if hit:
        ai.log_cached("search", model, name, names=[name])
        return hit
    resp = ai.respond("search", prompt, web_search=True, note=name, names=[name])
    from datetime import date
    data = {"company": name, "model": model, "date": date.today().isoformat(),
            "notes": resp.output_text, "sources": cited_sources(resp)}
    ai.cache_put(path, data)
    return data


def add_pasted(found, pasted):
    """A description pasted by the user becomes one more numbered source, 'provided by the user'."""
    if not (pasted or "").strip():
        return found
    n = max([s["n"] for s in found["sources"]], default=0) + 1
    return {**found,
            "notes": (found["notes"] + "\n\n" if found["notes"] else "")
            + f"DESCRIPTION PROVIDED BY THE USER (source [{n}])\n{pasted.strip()}",
            "sources": found["sources"] + [{"n": n, "url": "", "title": "Description provided by the user",
                                            "type": "provided by user"}]}


# =============================================================== step 1-2b: extraction (no search, one company)
class ExtractionFailed(RuntimeError):
    pass


def extract(ai, company, found, companies):
    name = company["name"]
    text = schemas.extraction_input(name, found["notes"], found["sources"])
    guard(schemas.extraction_input(name, "", []), name, companies)      # the part the app writes itself
    model = ai.model("extract")
    path, hit = ai.cache_get("extract", [model, schemas.EXTRACTION_INSTRUCTIONS,
                                         schemas.ActivityList.model_json_schema(), text])
    if hit:
        ai.log_cached("extract", model, name, names=[name])
        return hit
    # Retrieved public text that names another company in the run is allowed, but recorded (spec section 7)
    others = [n for c in companies if c["name"] != name for n in names_of(c)]
    flagged = rules.find_names(found["notes"], others)
    resp = None
    for attempt_model in (model, model, ai.fallback()):     # invalid output: one retry, then the fallback model
        resp = ai.respond("extract", text, instructions=schemas.EXTRACTION_INSTRUCTIONS,
                          schema=schemas.ActivityList, model=attempt_model,
                          note=name + (f" (mentions in sources: {', '.join(flagged)})" if flagged else ""),
                          names=[name])
        if resp.output_parsed is not None:
            break
    if resp is None or resp.output_parsed is None:
        raise ExtractionFailed(f"The extraction for {name} returned no valid activity list, also after a retry "
                               f"and with the fallback model: {(getattr(resp, 'output_text', '') or '')[:300]}")
    data = resp.output_parsed.model_dump()
    data["warnings"] = []
    data["extracted_activities"] = len(data["activities"])
    data["activities"] = consolidate(ai, name, data["activities"], data["warnings"])
    data["activities"] = rules.merge_other(data["activities"])        # exactly one "Other activities" line
    valid = {s["n"] for s in found["sources"]}
    data["profile_source_numbers"] = [n for n in data.get("profile_source_numbers", []) if n in valid]
    for act in data["activities"]:          # code check: only source numbers the search actually returned
        act["invalid_source_numbers"] = [n for n in act["source_numbers"] if n not in valid]
        act["source_numbers"] = [n for n in act["source_numbers"] if n in valid]
        act["verified_source"] = bool(act["source_numbers"])
    ai.cache_put(path, data)
    return data


def consolidate(ai, name, activities, warnings):
    """Code check of the limit of rules.MAX_MAIN main activities (decided 15 Oct). If the extraction returned more,
    ONE extra call (same company, no other names) merges the main activities; the 'other' activities are left to
    code. If that call fails or still returns too many, the longer list is kept with a warning: nothing is lost."""
    main = [a for a in activities if rules.category(a) == "main"]
    other = [a for a in activities if rules.category(a) == "other"]
    if len(main) <= rules.MAX_MAIN:
        return activities
    try:
        resp = ai.respond("extract", schemas.consolidation_input(name, main),
                          instructions=schemas.CONSOLIDATION_INSTRUCTIONS, schema=schemas.ActivityGroup,
                          note=f"{name} (consolidate {len(main)} -> max {rules.MAX_MAIN})", names=[name])
        merged = resp.output_parsed.activities if resp.output_parsed is not None else None
    except Exception as e:  # noqa: BLE001
        warnings.append(f"The {len(main)} main activities could not be merged ({type(e).__name__}); please merge "
                        "them in the table.")
        return activities
    if not merged:
        warnings.append(f"The {len(main)} main activities could not be merged; please merge them in the table.")
        return activities
    merged = [dict(a.model_dump(), category="main") for a in merged]
    if len(merged) > rules.MAX_MAIN:
        warnings.append(f"Still {len(merged)} main activities after merging; please check whether some belong "
                        "together.")
    return merged + other


# =============================================================== one company, end to end
def map_company(ai, company, companies, use_saved=False):
    """Search + extraction for one company. Never raises: errors are returned, so the other companies'
    results are kept and the user can paste a description for this one (spec section 7, fallbacks)."""
    name = company["name"]
    result = {"company": name, "role": company["role"], "search": None, "extraction": None, "error": None}
    try:
        if company.get("pasted"):
            guard(company["pasted"], name, companies)
        found = search(ai, company, companies, use_saved)
        found = add_pasted(found, company.get("pasted", ""))
        result["search"] = found
        if not found["sources"]:
            result["error"] = ("The search returned no usable sources. Paste a description of the company "
                               "below and map it again.")
            return result
        data = extract(ai, company, found, companies)
        label_sources(found["sources"], company, data.get("group_companies"))
        result["extraction"] = data
    except Blocked as e:
        result["error"] = str(e)
    except Exception as e:  # noqa: BLE001 - API errors, timeouts, invalid output
        result["error"] = f"{type(e).__name__}: {e}"
    return result


# =============================================================== existing relationships (🔗)
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")


def passages(text, names, limit=3, width=400):
    """The sentences of a text that mention one of the names (shown to the user only, never sent to an AI)."""
    out = []
    for sentence in SENTENCE.split(text or ""):
        if sentence.strip() and rules.find_names(sentence, names):
            s = sentence.strip()
            out.append(s if len(s) <= width else s[:width - 1] + "…")
            if len(out) >= limit:
                break
    return out


def find_relationships(mapped, companies):
    """For every company: the other companies of the run (names, aliases, group companies) that its public
    sources mention, with the passages. Also sets mapped[name]["mentions"] (the format benchmark.py reads)."""
    found = {}
    for c in companies:
        m = mapped.get(c["name"])
        notes = (m or {}).get("search", {}) or {}
        notes = notes.get("notes", "")
        found[c["name"]] = []
        for other in companies:
            if other["name"] == c["name"]:
                continue
            group = ((mapped.get(other["name"]) or {}).get("extraction") or {}).get("group_companies", [])
            names = names_of(other) + [g for g in group if g]
            hits = rules.find_names(notes, names)
            if hits:
                found[c["name"]].append({"other": other["name"], "names": hits, "passages": passages(notes, names)})
        if m is not None:
            m["mentions"] = [r["other"] for r in found[c["name"]]]
    return found