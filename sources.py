"""
sources.py - checks the sources the web search cites, and the quotations taken from them (option B, 18 Oct, Linda).

Why: the search notes cite pages, but what the extraction wrote was the AI's summary, not a passage the lawyer could
find on the page (probe of 18 Oct: 0 of 40 summaries word for word on their pages). Since 18 Oct the search quotes the
page word for word, and this module checks every quotation in code against the page itself:

    ✔ found        the quotation is on the page (for a PDF: on page N); the link jumps to the passage / the PDF page
    ≈ close        (21 Oct) not word for word, but its substance is on the page: its figures and names, most of its words
                   (reworded by the search), or it is the search's translation of a page in another language; or, for a
                   source cited without a quotation, the page names the activity's products or brands
    ⚠ not found    the page was read, but neither the quotation's wording nor its figures or names are on it
    ○ not checked  the page could not be read automatically (access refused, page built by JavaScript, file too
                   large, time-out) or the search gave no quotation for it: check by opening the link
    ✖ dead         the page no longer exists (HTTP 404/410, or the domain does not exist). It may hold outdated or
                   false information, so it is REMOVED as a source (Linda, 18 Oct): no longer a marker next to an
                   activity, no longer counted as support, only listed as "no longer available (cited by the search,
                   not used)". An activity left without any source is kept and marked for verification.

Rules (as for the whole app): only public pages are opened, with an honest user agent; a site that refuses access is
recorded as refused and never worked around (no other user agent, no cache, no mirror). Nothing is sent to an AI here,
and no company name of the run is sent anywhere: the app only opens the addresses the search itself returned for this
company. Only HTTP 404/410 and a missing domain count as dead; access refused (401/403/429) is NOT dead.
A missing domain only counts as dead if other pages of the same check could be opened (so that a network failure on
the app's side never removes sources).

CHECK_SOURCES=0 (in .env or the Streamlit secrets) switches the check off: the sources are then shown unchecked (○).
"""
import concurrent.futures as cf
import html
import io
import re
import socket
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from ai_client import setting

CHECK_SOURCES = setting("CHECK_SOURCES", "1").strip().lower() not in {"0", "false", "no", "off"}
USER_AGENT = "EU-Overlap-Screen/0.1 (research tool; checks the public sources it cites)"
TIMEOUT = 15                # seconds to connect / per read
MAX_BYTES = 40_000_000      # larger files are not read (annual reports are up to ~30 MB)
PDF_SECONDS = 40            # reading the text of a long PDF stops after this (the pages read are kept)
PARALLEL = 8
MIN_HTML_CHARS = 800        # less text: the page is probably built by JavaScript only

STATUS_MARK = {"found": "✔", "close": "≈", "not found": "⚠", "no quote": "○", "not checked": "○", "dead": "✖"}
# 21 Oct (Linda): the marks as levels of trust. "close" (≈ "probably right, worth a quick look"): the quotation is not
# on the page word for word, but its substance is (its figures and names, most of its words, or it is the search's
# translation of a page in another language); or, for a source cited without a quotation, the page names the
# activity's products or brands. "not found" (⚠) is kept for a passage of which neither the wording nor its figures
# or names are on the page.
SUBSTANCE_SHARE = 0.75      # share of a quotation's figures and names that must be on the page
WORDING_SHARE = 0.8         # share of a quotation's words on the page (in another order): reworded by the search

CACHE_SIZE = 60
_cache, _lock = {}, threading.Lock()        # url -> fetched page, for this server process (pages change rarely)
# 19 Oct: memory on Streamlit Cloud is limited and this cache is shared by every session of the server process.
# Readable PDFs (raw file up to 40 MB plus the PDF reader) are therefore never cached; they live only while one
# company's check runs. A refusal with HTTP 429 ("too many requests") is temporary and is not cached either.
# At most FETCH_SLOTS downloads run at once in the whole process, whatever the number of companies or sessions.
FETCH_SLOTS = 16
_slots = threading.BoundedSemaphore(FETCH_SLOTS)


# =============================================================== page text
class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}
    BLOCK = {"p", "br", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th", "section", "article",
             "header", "footer", "dt", "dd", "blockquote", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(raw, charset):
    p = _Text()
    try:
        p.feed(raw.decode(charset or "utf-8", errors="replace"))
        p.close()
    except Exception:  # noqa: BLE001 - broken markup: keep what was read
        pass
    return "".join(p.parts)


class Pdf:
    """A PDF whose pages are turned into text only as far as needed: the search for a quotation stops at the page where
    it is found. Reading stops for good after PDF_SECONDS in total (long annual reports); the pages read are kept."""

    def __init__(self, raw):
        from pypdf import PdfReader
        self.reader = PdfReader(io.BytesIO(raw))
        self.total = len(self.reader.pages)
        self.texts, self.spent, self.lock = [], 0.0, threading.Lock()

    def page(self, i):
        """The text of page i (0-based), or None if it is beyond the time budget or the end."""
        with self.lock:
            while len(self.texts) <= i < self.total and self.spent < PDF_SECONDS:
                t = time.time()
                try:
                    self.texts.append(self.reader.pages[len(self.texts)].extract_text() or "")
                except Exception:  # noqa: BLE001 - one unreadable page
                    self.texts.append("")
                self.spent += time.time() - t
            return self.texts[i] if i < len(self.texts) else None

    def cut_short(self):
        return len(self.texts) < self.total and self.spent >= PDF_SECONDS


_SAME = (("\u201c", '"'), ("\u201d", '"'), ("\u201e", '"'), ("\u201f", '"'), ("\u00ab", '"'), ("\u00bb", '"'),
         ("\u2019", "'"), ("\u2018", "'"), ("\u201a", "'"), ("\u2032", "'"),
         ("\u2010", "-"), ("\u2011", "-"), ("\u2012", "-"), ("\u2013", "-"), ("\u2014", "-"), ("\u2212", "-"),
         ("\u00a0", " "), ("\u202f", " "), ("\u2009", " "), ("\u200b", ""), ("\u00ad", ""), ("\u2026", "..."))


def norm(text):
    """Comparable text: same quotation marks, dashes and spaces, no soft hyphens, words that a PDF splits at a line
    end joined again, lower case."""
    text = unicodedata.normalize("NFKC", html.unescape(text or ""))
    for a, b in _SAME:
        text = text.replace(a, b)
    text = re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def words_only(text):
    """For the comparison: only the words, in order. Punctuation, quotation marks, dashes, line breaks and glyphs that
    a PDF renders oddly do not count; every word must be the same and in the same order ("word for word")."""
    return " " + re.sub(r"[\W_]+", " ", norm(text)).strip() + " "


def share_on_page(quote, page):
    """Which share of the quotation's words occurs anywhere on the page (language-neutral, 18 Oct, Linda: no list of
    languages). A quotation the search reworded in the page's own language still shares most of its words with the
    page; a quotation translated from a page in another language shares few (names and numbers at most)."""
    words = set(words_only(quote).split())
    if len(words) < 4:
        return None
    if page.get("pdf"):
        text = " ".join(t for t in page["pdf"].texts if t)
    else:
        text = page.get("text") or ""
    vocabulary = set(words_only(text).split())
    return len(words & vocabulary) / len(words)


TRANSLATED_BELOW = 0.5      # under half of the quotation's words on the page: probably translated


def _page_text(page):
    if page.get("pdf"):
        return " ".join(t for t in page["pdf"].texts if t)
    return page.get("text") or ""


def _figures(text):
    """{digit string: the figure as written}: separators removed, so that "5.92", "5,92" and "15,351" / "15 351"
    compare alike (language-neutral); the figure as written is what the hover shows (21 Oct review)."""
    out = {}
    for m in re.findall(r"\d[\d.,'\u00a0\u2009\u202f ]*\d|\d", text or ""):
        d = re.sub(r"\D", "", m)
        if len(d) >= 2:
            out.setdefault(d, m.strip(" .,'"))
    return out


def _digits(text):
    """The figures of a text as digit strings (see _figures)."""
    return set(_figures(text))


def key_terms(quote):
    """The figures and the names of a quotation (21 Oct): figures as digit strings, names as the capitalised words that
    do not open a sentence. Language- and sector-neutral; used to tell a reworded quotation (its facts are on the page)
    from one whose facts are not."""
    names = set()
    for sentence in re.split(r"(?<=[.!?:;])\s+", quote or ""):
        words = re.findall(r"[^\W\d_][\w'’&-]*", sentence)
        for w in words[1:]:
            if w[:1].isupper() and len(w) >= 3:
                names.add(w.lower())
    return _figures(quote), names


def substance_on_page(quote, page):
    """(share of the quotation's figures and names on the page, the ones found) or (None, []) if it has fewer than two."""
    digits, names = key_terms(quote)
    if len(digits) + len(names) < 2:
        return None, []
    text = _page_text(page)
    page_digits = _digits(text)
    vocabulary = set(words_only(text).split())
    found = sorted(shown for d, shown in digits.items() if d in page_digits) + sorted(n for n in names if n in vocabulary)
    return len(found) / (len(digits) + len(names)), found


def terms_on_page(terms, page):
    """The activity's products or brands that the page names (21 Oct: a source cited without a quotation)."""
    text = f" {words_only(_page_text(page))} "
    out = []
    for t in terms:
        w = words_only(t).strip()
        if len(w) >= 4 and f" {w} " in text:          # whole words only ("bars" is not in "barstool")
            out.append(t)
    return out


# =============================================================== opening a page
def _dns_failure(e):
    reason = getattr(e, "reason", e)
    return isinstance(reason, socket.gaierror) or "Name or service not known" in str(reason) \
        or "nodename nor servname" in str(reason) or "No address associated" in str(reason)


def fetch(url):
    """Opens one public page or PDF. Never raises. 'state': readable / blocked / dead / dns / no text / error."""
    with _lock:
        if url in _cache:
            return _cache[url]
    with _slots:
        out = _fetch(url)
    cacheable = out["state"] in ("readable", "dead", "blocked", "no text", "dns") and out.get("pdf") is None \
        and out.get("http") != 429
    if cacheable:
        with _lock:
            _cache[url] = out
            while len(_cache) > CACHE_SIZE:
                _cache.pop(next(iter(_cache)))
    return out


def _fetch(url):
    out = {"url": url, "state": "error", "reason": "", "kind": None, "text": "", "pdf": None, "pages_total": None}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            ctype = (r.headers.get("Content-Type") or "").lower()
            raw = r.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                out["reason"] = f"file larger than {MAX_BYTES // 1_000_000} MB, not read"
            elif "pdf" in ctype or raw[:5] == b"%PDF-" or urllib.parse.urlparse(url).path.lower().endswith(".pdf"):
                out["kind"] = "pdf"
                try:
                    pdf = Pdf(raw)
                    first = " ".join(pdf.page(i) or "" for i in range(min(5, pdf.total)))
                except ImportError:
                    out["reason"] = "PDF reader missing (pypdf)"
                except Exception as e:  # noqa: BLE001
                    out["reason"] = f"PDF could not be read ({type(e).__name__})"
                else:
                    out.update(pdf=pdf, pages_total=pdf.total)
                    if len(norm(first)) < 40:
                        out["state"], out["reason"] = "no text", "PDF without text (probably scanned)"
                    else:
                        out["state"] = "readable"
            else:
                out["kind"] = "html"
                out["text"] = html_text(raw, r.headers.get_content_charset())
                if len(norm(out["text"])) < MIN_HTML_CHARS:
                    out["state"], out["reason"] = "no text", "page shows almost no text (probably built by JavaScript)"
                else:
                    out["state"] = "readable"
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            out["state"], out["reason"] = "dead", f"page not found (HTTP {e.code})"
        elif e.code in (401, 403, 429, 451):
            out["state"], out["reason"] = "blocked", f"the site refused automatic access (HTTP {e.code})"
            out["http"] = e.code
        else:
            out["reason"] = f"the site returned an error (HTTP {e.code})"
    except Exception as e:  # noqa: BLE001 - DNS, time-out, TLS, connection
        if _dns_failure(e):
            out["state"], out["reason"] = "dns", "the domain does not exist (any more)"
        elif isinstance(e, (TimeoutError, socket.timeout)) or "timed out" in str(e):
            out["reason"] = "the site did not answer in time"
        else:
            out["reason"] = f"could not be opened ({type(e).__name__})"
    return out


# =============================================================== finding a quotation
def _parts(quote):
    """A quotation as the pieces that must be on the page: split at an ellipsis (the AI sometimes leaves words out
    and marks it); outer quotation marks and end punctuation do not count."""
    pieces = [words_only(p) for p in re.split(r"\.\.\.|\[\.\.\.\]|\(\.\.\.\)", norm(quote))]
    whole = words_only(quote)
    return [p for p in pieces if len(p.split()) >= 3] or ([whole] if whole.strip() else [])


def _in(parts, text):
    pos = 0
    for p in parts:
        i = text.find(p, pos)
        if i < 0:
            return False
        pos = i + len(p) - 1
    return True


def find(quote, page):
    """(True, PDF page number or None) if the quotation is on the page, else (False, None)."""
    parts = _parts(quote)
    if not parts:
        return False, None
    pdf = page.get("pdf")
    if pdf:
        for i in range(pdf.total):
            t = pdf.page(i)
            if t is None:
                break
            if _in(parts, words_only(t)):
                return True, i + 1
        return False, None
    return (_in(parts, words_only(page["text"])), None) if page.get("text") else (False, None)


ELLIPSIS = re.compile(r"\.\.\.|\u2026|\[\.\.\.\]|\(\.\.\.\)")
EDGE = "\"'“”„«»‘’.,;:!?()[] "


def _frag(tokens):
    """Words for a text fragment, encoded: ',', '&' and '-' are encoded too, so they never read as fragment syntax."""
    return urllib.parse.quote(" ".join(tokens).strip(EDGE), safe="").replace("-", "%2D")


def link_to(url, quote, pdf_page):
    """A link that jumps to the passage.
    Web page: a text fragment ('#:~:text=start,end'), which most browsers highlight. 19 Oct: the start and the end are
    at least six words each (before, the start was cut at the first '&' or dash, so "Lindt & Sprungli ..." started at
    the single word "Lindt", and the browser highlighted from the first "Lindt" on the page to the end of the quotation).
    A quotation of at most 12 words is matched whole; with an ellipsis, the start comes from the first part and the end
    from the last part.
    PDF: '#page=N' (every browser); 19 Oct also '&search=...&phrase=true', which the PDF viewer of Firefox uses to
    highlight the passage (other browsers ignore it and open the page)."""
    base = url.split("#")[0]
    parts = [p.split() for p in ELLIPSIS.split(quote or "") if p.strip()]
    if pdf_page:
        words = [w for w in (parts[0] if parts else []) if re.search(r"\w", w)][:6]
        search = f"&search={_frag(words)}&phrase=true" if len(words) >= 3 else ""
        return f"{base}#page={pdf_page}{search}"
    if not parts:
        return url
    if len(parts) == 1 and len(parts[0]) <= 12:
        frag = _frag(parts[0])
    else:
        frag = f"{_frag(parts[0][:6])},{_frag(parts[-1][-6:])}"
    return f"{base}#:~:text={frag}" if frag else url


def _find_read(quote, page):
    """Like find(), but only on what has already been read (for a PDF: the pages already turned into text), so that
    looking at the company's other sources (19 Oct) never starts reading another long PDF."""
    parts = _parts(quote)
    if not parts:
        return False, None
    pdf = page.get("pdf")
    if pdf:
        for i, t in enumerate(list(pdf.texts)):
            if t and _in(parts, words_only(t)):
                return True, i + 1
        return False, None
    return (_in(parts, words_only(page["text"])), None) if page.get("text") else (False, None)


CONTEXT_CHARS = 160          # characters shown before and after a found passage
PASSAGE_CHARS = 450

_INVISIBLE = dict.fromkeys(map(ord, "\u00ad\u200b\u200c\u200d\ufeff"))


def _pattern(words):
    return re.compile(r"(?<!\w)" + r"[\W_]+".join(re.escape(w) for w in words) + r"(?!\w)", re.IGNORECASE)


def context_of(quote, page, pdf_page=None):
    """The found passage in its surroundings, taken from the text the check has read (19 Oct, Linda: the lawyer can
    verify by hovering, in every browser, without opening a long report; browsers cannot highlight inside PDFs).
    Returns {"before", "passage", "after"} or None if the passage cannot be located in the original text (e.g. a word
    a PDF split at a line end). The words must follow each other as in find(); only punctuation, spaces and line
    breaks may differ."""
    if pdf_page and page.get("pdf"):
        texts = page["pdf"].texts
        text = texts[pdf_page - 1] if 0 < pdf_page <= len(texts) else ""
    else:
        text = page.get("text") or ""
    text = unicodedata.normalize("NFKC", html.unescape(text)).translate(_INVISIBLE)
    text = re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", text)      # words a PDF split at a line end, as in norm()
    parts = [words_only(p).split() for p in ELLIPSIS.split(quote or "")]
    parts = [p for p in parts if p]
    if not parts or not text:
        return None
    first = _pattern(parts[0]).search(text)
    if not first:
        return None
    start, end = first.span()
    if len(parts) > 1:
        last = _pattern(parts[-1]).search(text, first.end())
        if last and last.end() - start <= PASSAGE_CHARS * 2:
            end = last.end()

    def clean(t):
        return re.sub(r"\s+", " ", t)

    before = clean(text[max(0, start - CONTEXT_CHARS):start])
    after = clean(text[end:end + CONTEXT_CHARS])
    if start > CONTEXT_CHARS:
        before = "…" + before.split(" ", 1)[-1] if " " in before else "…" + before
    if end + CONTEXT_CHARS < len(text):
        after = (after.rsplit(" ", 1)[0] if " " in after else after) + "…"
    passage = clean(text[start:end])
    if len(passage) > PASSAGE_CHARS:
        passage = passage[:PASSAGE_CHARS].rsplit(" ", 1)[0] + " …"
    return {"before": before.lstrip(), "passage": passage, "after": after.rstrip()}


def activity_terms(act):
    """What a page cited for an activity should name (21 Oct): its brands and its products (the items it includes)."""
    out = [b for b in act.get("brands") or [] if b and b != "not stated"]
    out += [re.sub(r"\s*\(.*?\)", "", i).strip() for i in act.get("includes") or [] if i]
    return [t for t in dict.fromkeys(out) if t]


# =============================================================== checking one company
def check(found, data, pasted=""):
    """Opens every source of ONE company (in parallel), checks the quotations of its profile and activities, and
    removes dead sources. Changes 'found' and 'data' in place and returns a short summary for the audit log.
    Each source gets 'check' = {state, reason, kind, pages}; each activity 'quote_checks' (one per source number) and,
    if all its sources were dead, 'no_available_source'."""
    sources = found.get("sources") or []
    if not CHECK_SOURCES:
        for s in sources:
            s["check"] = {"state": "off", "reason": "source check switched off (CHECK_SOURCES=0)"}
        return {"checked": False}
    t = time.time()
    urls = list(dict.fromkeys(s["url"] for s in sources if s.get("url")))
    with cf.ThreadPoolExecutor(PARALLEL) as ex:
        pages = dict(zip(urls, ex.map(fetch, urls)))
    reachable = any(p["state"] in ("readable", "dead", "blocked", "no text") for p in pages.values())
    user_page = {"state": "readable", "text": pasted or "", "kind": "user", "reason": ""}
    by_n = {}
    for s in sources:
        if s.get("type") == "provided by user":
            page = user_page
        else:
            page = pages.get(s.get("url"), {"state": "error", "reason": "no web address"})
        state = page["state"]
        if state == "dns":      # a missing domain is dead only if the app itself could reach other sites
            state = "dead" if reachable else "error"
        reason = page.get("reason", "")
        if page["state"] == "dns" and state == "error":
            reason = "the domain could not be looked up (network problem on the app's side?)"
        s["check"] = {"state": state, "reason": reason, "kind": page.get("kind"), "pages": page.get("pages_total")}
        s["dead"] = state == "dead"
        by_n[s["n"]] = (s, page)
    dead = {n for n, (s, _) in by_n.items() if s["dead"]}

    def checks(numbers, quotes, terms=()):
        given = {}
        for q in quotes or []:
            if q.get("source_number") in numbers and (q.get("quote") or "").strip():
                given.setdefault(q["source_number"], []).append(q["quote"].strip())
        out = []
        for n in numbers:
            s, page = by_n[n]
            if s["dead"]:
                out.append({"n": n, "result": "dead", "quote": (given.get(n) or [""])[0], "reason": s["check"]["reason"]})
                continue
            if not given.get(n):
                named = terms_on_page(terms, page) if terms and s["check"]["state"] == "readable" else []
                if named:          # 21 Oct: the page names the activity's products or brands
                    out.append({"n": n, "result": "close", "quote": "", "basis": "activity terms",
                                "terms_found": named[:4],
                                "reason": "the search cited this page without quoting it; the page names "
                                          + ", ".join(f"“{t}”" for t in named[:3])})
                    continue
                out.append({"n": n, "result": "no quote", "quote": "", "reason": "the search gave no quotation for "
                            "this source" + (f"; {s['check']['reason']}" if s["check"]["state"] != "readable" else "")})
                continue
            if s["check"]["state"] != "readable":
                out.append({"n": n, "result": "not checked", "quote": given[n][0], "reason": s["check"]["reason"]})
                continue
            for q in given[n]:      # the first quotation found counts; otherwise the first one is shown
                ok, pdf_page = find(q, page)
                if ok:
                    out.append({"n": n, "result": "found", "quote": q, "page": pdf_page,
                                "context": context_of(q, page, pdf_page),
                                "link": link_to(s["url"], q, pdf_page) if s.get("url") else ""})
                    break
            else:
                # 19 Oct: the extraction sometimes attaches a quotation to the wrong source number (TC1 on Cloud: a
                # sentence of the "at a glance" page under the annual report page). The other sources of the company
                # were opened anyway: if the passage is on one of them, it is credited to that source, and this source
                # is marked as having no quotation of its own.
                moved = None
                for m, (s2, page2) in by_n.items():
                    if m == n or s2.get("dead") or s2["check"]["state"] != "readable" or s2.get("type") == "provided by user":
                        continue
                    for q in given[n]:
                        ok, pdf_page = _find_read(q, page2)
                        if ok:
                            moved = (m, s2, q, pdf_page)
                            break
                    if moved:
                        break
                if moved:
                    m, s2, q, pdf_page = moved
                    out.append({"n": n, "result": "no quote", "quote": "", "moved_to": m,
                                "reason": f"the quotation given for this source was found on source {m} instead"})
                    out.append({"n": m, "result": "found", "quote": q, "page": pdf_page, "moved_from": n,
                                "context": context_of(q, page2, pdf_page),
                                "link": link_to(s2["url"], q, pdf_page) if s2.get("url") else ""})
                    continue
                pdf = page.get("pdf")
                short = pdf is not None and pdf.cut_short()
                share = share_on_page(given[n][0], page)
                translated = not short and share is not None and share < TRANSLATED_BELOW
                sub, keys = substance_on_page(given[n][0], page)
                entry = {"n": n, "result": "not found", "quote": given[n][0], "translated": translated,
                         "words_on_page": None if share is None else round(share, 2),
                         "substance_on_page": None if sub is None else round(sub, 2), "keys_found": keys}
                # 21 Oct (Linda): ≈ when the substance is on the page, ⚠ only when neither wording nor facts are
                if sub is not None and sub >= SUBSTANCE_SHARE:
                    entry.update(result="close", basis="figures and names",
                                 reason="the wording is not on the page, but its figures and names are ("
                                        + ", ".join(keys[:4]) + "): probably reworded by the search")
                elif translated:
                    entry.update(result="close", basis="translation",
                                 reason=f"only {share:.0%} of the quotation's words occur on the page, so the page is "
                                        "probably in another language and the quotation the search's translation")
                elif share is not None and share >= WORDING_SHARE:
                    entry.update(result="close", basis="wording",
                                 reason=f"{share:.0%} of the quotation's words occur on the page, not in this order: "
                                        "probably reworded by the search")
                else:
                    entry["reason"] = ((f"only the first {len(pdf.texts)} of {pdf.total} PDF pages could be read in "
                                        "time, and this passage is not on them") if short else
                                       "neither the wording nor its figures or names are on the page")
                out.append(entry)
        return out

    def apply(holder, num_key, quote_key, checks_key, dead_key, terms=()):
        numbers = [n for n in holder.get(num_key) or [] if n in by_n]
        results = checks(numbers, holder.get(quote_key), terms)
        # a source credited with a quotation found on it (19 Oct) joins the activity's sources; if it already was one,
        # its own check is replaced by the one that found the passage
        moved_to = {c["n"] for c in results if c.get("moved_from")}
        kept, seen = [], set()
        for c in results:
            if c.get("moved_from") and c["n"] not in seen:
                seen.add(c["n"])
                kept.append(c)
            elif not c.get("moved_from") and c["n"] not in moved_to:
                kept.append(c)
        results = kept
        holder[checks_key] = results
        holder[dead_key] = [n for n in numbers if n in dead]
        holder[num_key] = [n for n in numbers if n not in dead] + sorted(moved_to - set(numbers))
        return bool(numbers) and not holder[num_key]

    apply(data, "profile_source_numbers", "profile_quotes", "profile_quote_checks", "profile_dead_sources")
    results = {}
    for act in data.get("activities") or []:
        lost = apply(act, "source_numbers", "quotes", "quote_checks", "dead_sources", activity_terms(act))
        act["no_available_source"] = lost
        if lost:
            act["verified_source"] = False
        for c in act["quote_checks"]:
            results[c["result"]] = results.get(c["result"], 0) + 1
    states = {}
    for s in sources:
        states[s["check"]["state"]] = states.get(s["check"]["state"], 0) + 1
    return {"checked": True, "seconds": round(time.time() - t, 1), "sources": states, "quotations": results,
            "dead_sources": sorted(dead),
            "activities_without_available_source": [a.get("product") for a in data.get("activities") or []
                                                    if a.get("no_available_source")]}