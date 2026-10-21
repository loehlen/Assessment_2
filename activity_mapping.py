"""
activity_mapping.py - steps ① and ②: the activity overview, ONE company per call.

    map_company(ai, company, companies)     web search + extraction for one company (isolated calls: two searches in
                                            parallel, main business and beyond it, then one extraction)
    find_relationships(mapped, companies)   the 🔗 notes: public sources of one company that mention another

A company is a dict: {"name", "role" ("target" / "portco"), "website", "aliases": [...], "source", "pasted"}.
  website  optional: identifies the company in the search and marks its own pages as "company"
  aliases  other names of the company (removed from every abstract, like the name itself)
  source   how the activities are found: "web search" (public sources), "my description" (no web search: only the
           text the user entered) or "both"
  pasted   the user's description; a numbered source "provided by the user"

The module keeps no global state, so several Streamlit sessions can run at the same time.
"""
import concurrent.futures as cf
import re
from urllib.parse import urlparse

import rules
import schemas
import sources as source_check      # opens the cited pages and checks the quotations
from ai_client import setting

# The second, complementary search per company: on by default; SECOND_SEARCH=0 switches it off. Read here, at
# import, because the searches run in worker threads, which cannot read Streamlit's Secrets.
SECOND_SEARCH = setting("SECOND_SEARCH", "1").strip().lower() not in {"0", "false", "no", "off"}
SEARCHES = (("main business", schemas.search_prompt), ("beyond the main business", schemas.search_prompt_beyond))


class Blocked(RuntimeError):
    """Raised by the confidentiality guard: the text names a company that this call may not contain."""


# =============================================================== names and the guard
def names_of(company):
    """The entered name, the other names, and their parts joined by "&" / "and" ("Smith" for "Smith & Sons")."""
    names = [company["name"]] + [a for a in company.get("aliases", []) if a]
    return names + [p for p in rules.name_parts(names) if p not in names]


def other_names_in(text, permitted, companies):
    """The names of the OTHER companies of the screen that a text contains (empty = clean)."""
    found = []
    for c in companies:
        if c["name"] != permitted and rules.find_names(text, names_of(c)):
            found.append(c["name"])        # one entry per company, under its entered name
    return found


def guard(text, permitted, companies, allowed=()):
    """Text sent in one company's call may contain at most that company. Text the app builds itself is always checked
    strictly. Text the lawyer typed (a description) may name another company if the lawyer chose "Send anyway" for
    exactly those names (what a lawyer types is the lawyer's responsibility; the choice is recorded in the audit
    log)."""
    found = other_names_in(text, permitted, companies)
    allowed = {a.lower() for a in allowed or ()}
    blocking = [f for f in found if f.lower() not in allowed]       # allowed: the companies the lawyer confirmed
    if blocking:
        raise Blocked(f"Blocked by the confidentiality guard: the text for {permitted} names {', '.join(blocking)}")


# =============================================================== sources
def clean_url(url):
    url = re.sub(r"([?&])utm_source=openai(&|$)", lambda m: m.group(1) if m.group(2) else "", url)
    return url.rstrip("?&")


TEXT_LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")


def text_links(notes):
    """Links the search wrote into its text as [title](url) instead of attaching them as citations (otherwise such a
    search would show no source at all). They become sources too, marked as such; the source check opens each one,
    so a made-up or dead link is removed and its quotation must still be found on the page."""
    seen = {}
    for title, url in TEXT_LINK.findall(notes or ""):
        seen.setdefault(clean_url(url.rstrip(".,;")), title.strip())
    return seen


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


def site_of(url):
    """'https://www.example.com/de/' or 'example.com' -> 'example.com' (empty if none)."""
    url = (url or "").strip()
    if not url:
        return ""
    if "://" not in url:
        url = "https://" + url
    host = urlparse(url).netloc.lower().split(":")[0]
    return host[4:] if host.startswith("www.") else host


def label_sources(sources, company, group_companies):
    """Labels each source 'company' (own or group website) or 'third party', unless already labelled.
    The website the user entered decides first (its domain and subdomains); otherwise a simple domain check: a word of
    the company, alias or group company name appears in the domain."""
    site = site_of(company.get("website"))
    words = set()
    for n in names_of(company) + list(group_companies or []):
        words |= _domain_words(n)
    for s in sources:
        if s.get("type"):
            continue
        domain = site_of(s.get("url", ""))
        own = bool(site) and (domain == site or domain.endswith("." + site))
        s["type"] = "company" if own or (domain and any(w in domain for w in words)) else "third party"
    return sources


# =============================================================== step ①-②a: search (web search, one company)
def search(ai, company, companies):
    """The web research for ONE company: two searches in parallel, each a separate stateless call with only this
    company's name (search 1: the main business; search 2: what lies beyond it). Their notes are joined and their
    sources merged and numbered once, in code, before the extraction reads them. If one search fails, the other is
    kept and the failure recorded; only if both fail is the error raised."""
    name = company["name"]
    plan = SEARCHES if SECOND_SEARCH else SEARCHES[:1]
    prompts = [(focus, make(name, company.get("website", ""))) for focus, make in plan]
    for _, prompt in prompts:
        guard(prompt, name, companies)
    with cf.ThreadPoolExecutor(len(prompts)) as ex:
        futures = [ex.submit(one_search, ai, name, focus, prompt, k) for k, (focus, prompt) in enumerate(prompts, 1)]
        runs = []
        for (focus, _), fut in zip(prompts, futures):
            try:
                runs.append(fut.result())
            except Exception as e:  # noqa: BLE001 - kept as a recorded gap; raised below only if every search failed
                runs.append({"focus": focus, "error": f"{type(e).__name__}: {e}", "notes": "", "sources": []})
    if all(r.get("error") for r in runs):
        raise RuntimeError(runs[0]["error"])
    return merge_searches(name, ai.model("search"), runs)


def one_search(ai, name, focus, prompt, k):
    model = ai.model("search")
    path, hit = ai.cache_get("search", [model, prompt])
    if hit:
        ai.log_cached("search", model, f"{name} (search {k}: {focus})", names=[name])
        return {**hit, "focus": focus}
    resp = ai.respond("search", prompt, web_search=True, note=f"{name} (search {k}: {focus})", names=[name])
    data = {"focus": focus, "notes": resp.output_text, "sources": cited_sources(resp)}
    ai.cache_put(path, data)
    return data


def merge_searches(name, model, runs):
    """One research record from one or two searches: the notes under a heading each, the sources merged by address
    and numbered once (the first search's numbering first). Each source records which search returned it."""
    from datetime import date
    numbered, found_by, cited = {}, {}, set()
    for k, r in enumerate(runs, 1):
        for s in r.get("sources") or []:        # attached citations first
            if s["url"] not in numbered:
                numbered[s["url"]] = s.get("title") or s["url"]
            found_by.setdefault(s["url"], []).append(k)
            cited.add(s["url"])
        for url, title in text_links(r.get("notes")).items():     # then links written only in the text
            if url not in numbered:
                numbered[url] = title or url
            if k not in found_by.setdefault(url, []):
                found_by[url].append(k)
    sources = [{"n": i + 1, "url": u, "title": t, "searches": found_by[u]}
               | ({} if u in cited else {"origin": "text link"}) for i, (u, t) in enumerate(numbered.items())]
    if len(runs) == 1:
        notes = runs[0]["notes"]
    else:
        notes = "\n\n".join(f"## Search {k}: {r['focus']}\n\n" + (r["notes"] or f"(this search failed: {r.get('error')})")
                             for k, r in enumerate(runs, 1))
    return {"company": name, "model": model, "date": date.today().isoformat(), "notes": notes, "sources": sources,
            "searches": [{"focus": r["focus"], "sources": len(r.get("sources") or []),
                          "text_links": len(text_links(r.get("notes"))), "characters": len(r["notes"] or ""),
                          "error": r.get("error")} for r in runs]}


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


# =============================================================== step ①-②b: extraction (no search, one company)
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
    # Retrieved public text that names another company in the run is allowed, but recorded
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
    move_gaps(data, company)                                          # no "not stated" activity lines
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


def move_gaps(data, company=None):
    """Names the sources mention without saying what they offer are not activities (an activity needs a product and a
    source). They are shown as one caption under the company ('named_without_activity').
    - A line the extraction still returns with product "not stated" is moved there; what is known about it (level of
      trade) is kept in brackets. Its brand or company name is the group's own, so it is added to 'group_companies'
      (name removal before the comparison, 🔗 relationship check).
    - Names the extraction lists itself are shown only if they are also among its own 'group_companies' (otherwise
      partners and customers would be removed as "names of the company" and could cause false 🔗 notes). They are
      never added to 'group_companies' by code.
    - Not shown either: names that carry the company's own name (national, holding or sales companies of the group)
      and names already on an activity line (brand or company)."""
    group = [g for g in data.get("group_companies") or [] if g]
    in_group = {g.strip().lower() for g in group}
    named = [n.strip() for n in data.get("named_without_activity") or []
             if n and n.strip() and n.strip().lower() in in_group]
    from_lines = []
    keep = []
    for a in data.get("activities") or []:
        if not rules.is_gap(a):
            keep.append(a)
            continue
        label = rules.gap_name(a)
        if label == rules.GAP_FALLBACK:         # nothing to name: nothing to show or to remove
            continue
        from_lines += [p.strip() for p in label.split(",") if p.strip()]
        level = a.get("value_chain_level")
        if level in rules.VALUE_CHAIN_LEVELS and level != "other":
            label += f" ({level}; products not stated)"
        named.append(label)
    data["activities"] = keep
    own = [n.lower() for n in (names_of(company) if company else []) if len(n) >= 3]
    covered = [b.lower() for a in keep for b in (a.get("brands") or []) if b and len(b) >= 3 and b != "not stated"]
    covered += [e.strip().lower() for a in keep for e in (a.get("entity") or "").split(",") if len(e.strip()) >= 3]
    shown = []
    for n in dict.fromkeys(named):
        low = re.sub(r"\s*\(.*\)$", "", n).lower()
        if any(re.search(rf"(?<!\w){re.escape(w)}(?!\w)", low) for w in own + covered):
            continue
        shown.append(n)
    data["named_without_activity"] = shown
    data["group_companies"] = list(dict.fromkeys(group + from_lines))
    return data


def consolidate(ai, name, activities, warnings):
    """Code check of the limit of rules.MAX_MAIN main activities. If the extraction returned more,
    ONE extra call (same company, no other names) merges the main activities; the 'other' activities are left to
    code. If that call fails or still returns too many, the longer list is kept with a warning: nothing is lost."""
    gaps = [a for a in activities if rules.is_gap(a)]      # lines without a product are not merged away
    main = [a for a in activities if rules.category(a) == "main" and not rules.is_gap(a)]
    other = [a for a in activities if rules.category(a) == "other" and not rules.is_gap(a)]
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
    return merged + other + gaps


# =============================================================== one company, end to end
SOURCE_OPTIONS = ("web search", "my description", "both")


def source_mode(company):
    """How this company's activities are found. A company without 'source' (e.g. from an older saved audit log): a
    pasted description means 'both'."""
    mode = company.get("source")
    if mode in SOURCE_OPTIONS:
        return mode
    return "both" if (company.get("pasted") or "").strip() else "web search"


def map_company(ai, company, companies):
    """Search (unless the user chose 'my description') + extraction for one company. Never raises: errors are
    returned, so the other companies' results are kept and the user can correct this one."""
    name = company["name"]
    mode = source_mode(company)
    pasted = (company.get("pasted") or "").strip() if mode != "web search" else ""
    result = {"company": name, "role": company["role"], "search": None, "extraction": None, "error": None,
              "source_mode": mode}
    try:
        if mode == "my description" and not pasted:
            result["error"] = "No description entered. Enter a description of the company's activities, or choose web search."
            return result
        if pasted:      # the lawyer's own text: names they confirmed with "Send anyway" are allowed
            guard(pasted, name, companies, company.get("typed_names_confirmed") or ())
        if mode == "my description":       # no web search at all: the extraction reads only the user's text
            from datetime import date
            found = {"company": name, "model": "no web search (description provided by the user)",
                     "date": date.today().isoformat(), "notes": "", "sources": []}
        else:
            found = search(ai, company, companies)
        found = add_pasted(found, pasted)
        result["search"] = found
        if not found["sources"]:
            result["error"] = ("The search returned no usable sources. Paste a description of the company "
                               "below and map it again.")
            return result
        data = extract(ai, company, found, companies)
        label_sources(found["sources"], company, data.get("group_companies"))
        # open the cited pages, check the quotations in code, remove dead links
        found["source_check"] = source_check.check(found, data, pasted)
        result["extraction"] = data
    except Blocked as e:
        result["error"] = str(e)
    except Exception as e:  # noqa: BLE001 - API errors, timeouts, invalid output
        result["error"] = f"{type(e).__name__}: {e}"
    return result


# =============================================================== existing relationships (🔗)
# The research notes are prose with citations as markdown links, e.g. "... a long-term partnership. ([site.com](url))".
# A passage is the sentence together with the citations that follow it, so that a citation on its own is never shown
# as the "passage" and a name that appears only in a web address is still shown with its context.
LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _clean(text):
    """A passage as plain text: links reduced to their text, table bars and bold marks removed."""
    text = LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"[*_`#>]+", "", text).replace("|", " ")
    text = re.sub(r"\(\s*\)", "", text)
    return re.sub(r"\s+", " ", text).strip(" -–")


def segments(text):
    """The sentences of a text, each with the web addresses cited in it or right after it."""
    out = []
    for line in (text or "").split("\n"):
        for piece in SENTENCE_END.split(line):
            urls = [m.group(2) for m in LINK.finditer(piece)]
            plain = _clean(LINK.sub("", piece))
            if not re.search(r"\w{3}", plain):           # only a citation (or table bars): belongs to the sentence before
                if out and urls:
                    out[-1]["urls"] += urls
                continue
            out.append({"text": _clean(piece), "plain": plain, "urls": urls})
    return out


def _url_words(urls):
    return " ".join(re.sub(r"[-_/.?=&]+", " ", u) for u in urls)


def _strict_hits(text, words):
    """Group names that are single words count only where written like a name, with their capital letter
    ("Classic", not "classic varieties")."""
    return [w for w in words if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text or "")]


def passages(text, names, limit=3, width=400, strict=()):
    """The sentences that mention one of the names, with their sources (shown to the user only, never sent to an AI).
    A name found only in a source's web address is shown with the sentence it belongs to, and marked as such.
    strict: names matched only as written (with their capital letter) and never in a web address."""
    in_text, in_url = [], []
    for seg in segments(text):
        named = bool(rules.find_names(seg["plain"], names)) or bool(_strict_hits(seg["plain"], strict))
        if not named and not rules.find_names(_url_words(seg["urls"]), names):
            continue
        s = seg["text"] if len(seg["text"]) <= width else seg["text"][:width - 1] + "…"
        sites = list(dict.fromkeys(site_of(u) for u in seg["urls"]))
        if sites and not all(site in s for site in sites):      # the source is not named twice
            s += f" (source: {', '.join(x for x in sites if x not in s)})"
        if not named:
            s += " [the name appears only in the source's web address]"
        (in_text if named else in_url).append(s)
    return (in_text + in_url)[:limit]


def relationship_names(other, mapped, ordinary=()):
    """(names matched as usual, names matched only as written) for one company of the run, so that a group name that
    is also an ordinary word does not create an "existing relationship". The entered name, the other names and their
    parts are matched as usual; a group company or brand of one word only where written like a name; a word the
    lawyer kept as an ordinary word in step ② never."""
    group = ((mapped.get(other["name"]) or {}).get("extraction") or {}).get("group_companies", []) or []
    loose = names_of(other)
    ordinary = {w.lower() for w in ordinary or ()}
    strict = []
    for g in group:
        g = (g or "").strip()
        if not g or g in loose or g.lower() in ordinary:
            continue
        if len(g.split()) == 1:
            strict.append(g)
        else:
            loose.append(g)
    return loose, strict


def find_relationships(mapped, companies, ordinary=()):
    """For every company: the other companies of the run (names, aliases, group companies) that its public
    sources mention, with the passages. Pure code on each company's own research notes: no AI call, nothing leaves
    the app. Group names of one word count only where written like a name (see relationship_names)."""
    found = {}
    for c in companies:
        m = mapped.get(c["name"])
        notes = (m or {}).get("search", {}) or {}
        notes = notes.get("notes", "")
        found[c["name"]] = []
        for other in companies:
            if other["name"] == c["name"]:
                continue
            names, strict = relationship_names(other, mapped, ordinary)
            ps = passages(notes, names, strict=strict)
            if ps:
                urls = [u for _, u in LINK.findall(notes)]
                plain = _clean(LINK.sub("", notes))
                hits = rules.find_names(plain + " " + _url_words(urls), names) + _strict_hits(plain, strict)
                found[c["name"]].append({"other": other["name"], "names": hits, "passages": ps})
    return found