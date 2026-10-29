"""
logic/ingest.py - turns a Commission decision (or the Market Definition Notice) into numbered paragraphs.

One function for the built-in corpus (and, unchanged, for user uploads, should that feature be added):
    ingest_text(text, source)  ->  list of paragraph records

What it does:
  1. splits the text into pages and removes page numbers and running headers;
  2. separates the footnotes at the bottom of each page from the body text;
  3. splits the body at the numbered paragraphs. A number is accepted only if it follows on from the previous
     paragraph (n + 1), so section headings such as "1. Bicycles" or "6.2." are never mistaken for paragraphs;
  4. attaches to each paragraph the footnotes it refers to (the case references are often in the footnotes);
  5. records the nearest section headings, for the context header that is embedded with the text.

No API calls. Run on its own to check a PDF:   python -m logic.ingest corpus_src/M7408.pdf
"""
import re
import sys

# =============================================================== paragraph and footnote styles
# Each document family numbers paragraphs and footnotes differently. "auto" tries them in turn and keeps the
# style that finds the longest unbroken sequence of paragraph numbers.
STYLES = {
    # (12) Text ...      footnote: "12   Text" at the margin, or the number alone on its own line
    "brackets": {"para": r"^\s{0,3}\((\d{1,3})\)\s+(\S.*)$",
                 "foot": r"^\s{0,2}(\d{1,3})(?:\s{2,}(\S.*))?$"},
    # 12. Text ...       footnote: "12   Text" at the margin
    "dots": {"para": r"^\s{0,8}(\d{1,3})\.\s+(\S.*)$",
             "foot": r"^\s{0,2}(\d{1,3})(?:\s{2,}(\S.*))?$"},
    # Official Journal style (Notice): "12.   Text" indented; footnote "(12) Text"
    "oj": {"para": r"^\s{2,8}(\d{1,3})\.\s{2,}(\S.*)$",
           "foot": r"^\s{2,8}\((\d{1,3})\)\s+(\S.*)$"},
}

NOISE = [
    re.compile(r"^\s*\d{1,3}\s*$"),                                  # page number (only if not a footnote)
    re.compile(r"^\s*\d{1,3}/\d{1,3}\s"),                             # "2/35   ELI: ..."
    re.compile(r"^\s*ELI: http"),
    re.compile(r"^\s*OJ C, \d"),
    re.compile(r"^\s*EN\s*$"),
    re.compile(r"^\s*EN\s{5,}OJ C"),
]
HEADING = re.compile(r"^\s{0,10}((?:\d+\.)+\d*\.?|[A-Z]\.|[IVX]+\.|[a-z]\)|\((?:[a-z]|[ivx]+)\))\s{1,12}"
                     r"([A-Z‘'\"].{1,90})$")
CAPTION = re.compile(r"^\s*(Figure|Table|Chart|Graph)\s+\d+\b")
PLAIN_HEADING = re.compile(r"^\s{0,10}[A-Z][^.;:,]{2,98}$")


SECTIONS = [("geographic market", "Relevant geographic market"), ("product market", "Relevant product market"),
            ("market definition", "Market definition"), ("relevant market", "Market definition"),
            ("description of the products", "Products and value chain"), ("value chain", "Products and value chain"),
            ("competitive assessment", "Competitive assessment"), ("remed", "Remedies"),
            ("commitment", "Remedies")]


def _section(heading_text, current):
    """The part of the decision a heading opens. Kept separately because it matters most for retrieval and
    would otherwise be lost when a deep heading pushes it out of the last three headings."""
    low = heading_text.lower()
    for key, label in SECTIONS:
        if key in low:
            return label
    return current


def _push_heading(stack, heading):
    """A new heading replaces the earlier heading of the same type and everything below it. Numbered headings
    also replace deeper numbered ones (a new '6.2.' ends '6.1.2.')."""
    kind = heading[0]
    for i, (t, _) in enumerate(stack):
        same = t == kind
        deeper_number = t.startswith("digits") and kind.startswith("digits") and int(t[6:]) >= int(kind[6:])
        if same or deeper_number:
            return stack[:i] + [heading]
    return stack + [heading]


def _heading_type(marker):
    """Headings replace earlier headings of the same type (and everything below them), whatever the order of
    numbering styles in a decision (e.g. 'IV.' > 'A.' > '1.' in one decision, '6.' > '6.3.' > '6.3.2.' in another)."""
    if marker is None:
        return "plain"
    if re.fullmatch(r"[IVX]+\.", marker):
        return "roman"
    if re.fullmatch(r"[A-Z]\.", marker):
        return "letter"
    if re.fullmatch(r"[a-z]\)", marker):
        return "letter)"
    if marker.startswith("("):
        return "(i)"
    return f"digits{marker.rstrip('.').count('.')}"


def _is_noise(line):
    return any(p.match(line) for p in NOISE)


def _pages(text):
    return text.split("\f")


MAX_GAP = 15   # public versions can omit paragraphs and footnotes (confidential pages); jumps up to this size


def _paragraph_start(m, next_para):
    """A numbered line starts a paragraph if its number is the next one, or a small jump forward, and its text
    reads like prose (not an all-caps heading or a table-of-contents line with dot leaders)."""
    if not m:
        return False
    n, first = int(m.group(1)), m.group(2)
    if not (next_para <= n <= next_para + MAX_GAP):
        return False
    if ". . ." in first or "...." in first or not re.search(r"[a-z]", first):
        return False
    return n == next_para or len(first) > 25          # a jump needs a full line of prose


def _footnote_start(lines, i, foot_re, next_foot, allow_jump):
    m = foot_re.match(lines[i])
    if not m:
        return None
    n = int(m.group(1))
    if not (n == next_foot or (allow_jump and next_foot < n <= next_foot + MAX_GAP)):
        return None
    if m.group(2) is None:   # number alone on its line: footnote only if text follows (else a page number)
        nxt = next((l for l in lines[i + 1:i + 3] if l.strip()), "")
        if not nxt.strip() or re.match(r"^\s*\d{1,3}\s*$", nxt):
            return None
    return n


def _split_page(lines, foot_re, next_foot):
    """Body lines and footnote lines of one page. The footnote block starts at the first line carrying the next
    footnote number; a forward jump (omitted footnotes) is accepted only in the lower half of the page."""
    for i in range(1, len(lines)):
        if _footnote_start(lines, i, foot_re, next_foot, allow_jump=i > len(lines) * 0.5) is not None:
            return lines[:i], lines[i:]
    return lines, []


def _parse_footnotes(lines, foot_re, next_foot, page_no):
    notes, current = {}, None
    for i, line in enumerate(lines):
        n = _footnote_start(lines, i, foot_re, next_foot, allow_jump=True)
        if n is not None:
            current = n
            m = foot_re.match(line)
            notes[n] = {"text": (m.group(2) or "").strip(), "page": page_no}
            next_foot = n + 1
        elif current is not None and line.strip() and not _is_noise(line):
            notes[current]["text"] = (notes[current]["text"] + " " + line.strip()).strip()
    return notes, next_foot


def _parse(text, style, first=1):
    para_re, foot_re = re.compile(STYLES[style]["para"]), re.compile(STYLES[style]["foot"])
    paras, footnotes = [], {}
    next_para, next_foot = first, 1         # first: an extract that starts in the middle of a decision
    headings = []                    # most recent section headings, outermost first
    section = ""                     # product market / geographic market / competitive assessment / ...
    current = None
    skipping = False                 # inside a figure or table
    for page_no, page in enumerate(_pages(text)):
        lines = [l.rstrip() for l in page.split("\n")]
        body, foot = _split_page(lines, foot_re, next_foot)
        notes, next_foot = _parse_footnotes(foot, foot_re, next_foot, page_no)
        footnotes.update(notes)
        for i, line in enumerate(body):
            if not line.strip() or _is_noise(line):
                continue
            m = para_re.match(line)
            if _paragraph_start(m, next_para):
                skipping = False
                n = int(m.group(1))
                current = {"para": n, "text": m.group(2).strip(), "headings": list(headings),
                           "section": section, "pages": {page_no}}
                paras.append(current)
                next_para = n + 1
                continue
            stripped = line.strip()
            blank_before = i == 0 or not body[i - 1].strip()
            blank_after = i + 1 >= len(body) or not body[i + 1].strip()
            finished = current is None or re.search(r"[.:;)\]’”\"](\s?\d{1,3})?\s*$", current["text"]) is not None
            h = HEADING.match(line)
            heading = None
            spaced = bool(h) and re.match(r"^\s*(?:\d+\.)+\s{3,}", line) is not None   # "6.1.      Title"
            if h and len(stripped) < 100 and not stripped.endswith((",", ";", ".")) and (blank_before or finished or spaced):
                heading = (_heading_type(h.group(1)), stripped)
            elif PLAIN_HEADING.match(line) and blank_before and blank_after and finished:
                heading = ("plain", stripped)
            if heading:
                headings = _push_heading(headings, heading)
                section = _section(heading[1], section)
                skipping = False
                continue
            if CAPTION.match(line) and (":" in stripped[:20] or len(line) - len(line.lstrip()) >= 15):
                skipping = True            # figure or table: its labels are not part of the paragraph
                continue
            if skipping:
                continue
            if current is not None:
                # a word broken at a line end ("sub-" / "segment") is joined without a space
                joiner = "" if re.search(r"[A-Za-z]-$", current["text"]) else " "
                current["text"] += joiner + stripped
                current["pages"].add(page_no)
    return paras, footnotes


def _clean(text):
    return re.sub(r"\s+", " ", text).strip()


def _ref_patterns(n, style):
    """Ways an inline reference to footnote n is printed. Group 1 is the reference itself."""
    if style == "oj":
        return [re.compile(r"(\(" + str(n) + r"\))")]
    return [re.compile(r"(?<=[A-Za-z\.\,\)’'\"”;:\]])(" + str(n) + r")(?=\s|$|[,.;:)])"),   # competitors.23
            re.compile(r"(?<=\s)(" + str(n) + r")(?=\s?[,.;:](?:\s|$))"),                    # Nutricia 9 ,
            re.compile(r"(?<=[.,;:)\]’”\"]\s)(" + str(n) + r")(?=\s|$)"),                   # each other. 6
            re.compile(r"(?<=[a-z]\s)(" + str(n) + r")(?=\s[a-z])")]                          # countries 5 on
    # the last form is loose, so _attach_footnotes tries it only after the others found nothing on the page


def _attach_footnotes(paras, footnotes, style):
    """Footnote n goes to the paragraph on the same page whose text contains the reference; the reference in
    the text is replaced by "[fn n]", so footnote numbers can no longer be confused with paragraph numbers or
    spoil keyword search. If no paragraph on that page shows the reference, the footnote goes to the last
    paragraph that starts on or before that page and is marked as placed by page."""
    for n in sorted(footnotes):
        fn = footnotes[n]
        record = {"n": n, "text": _clean(fn["text"])}
        hit = None
        on_page = [p for p in paras if fn["page"] in p["pages"]]
        for pat in _ref_patterns(n, style):              # strictest form first, across the whole page
            for p in on_page:
                m = pat.search(p["text"])
                if m:
                    p["text"] = p["text"][:m.start(1)] + f"[fn {n}]" + p["text"][m.end(1):]
                    hit = p
                    break
            if hit:
                break
        if hit is None:
            before = [p for p in paras if min(p["pages"]) <= fn["page"]]
            if not before:
                continue
            hit = before[-1]
            record["placed_by_page"] = True
        hit.setdefault("footnotes", []).append(record)


def ingest_text(text, source):
    """
    text: the plain text of the decision (pdftotext / pypdf output, pages separated by form feeds).
    source: dict with case, title, date, url, levels, style ("auto" or one of STYLES), and optionally first_para: the
    number of the first paragraph, for an extract that does not start at (1) (uploads.py).
    Returns paragraph records with case, paragraph number, text, footnotes and section headings.
    """
    styles = [source["style"]] if source.get("style", "auto") != "auto" else list(STYLES)
    first = source.get("first_para", 1)       # 1 for a whole decision (the built-in corpus)
    best = max(((s, *_parse(text, s, first)) for s in styles), key=lambda r: len(r[1]))
    style, paras, footnotes = best
    _attach_footnotes(paras, footnotes, style)
    records = []
    for p in paras:
        headings = [h for _, h in p["headings"]][-3:]
        records.append({
            "id": f"{source['case']}-{p['para']}",
            "case": source["case"], "title": source["title"], "date": source["date"],
            "para": p["para"], "text": _clean(p["text"]),
            "footnotes": p.get("footnotes", []),
            "headings": [_clean(h) for h in headings], "section": p["section"],
            "levels": source.get("levels", []), "source_type": source.get("source_type", "Commission decision"),
            "url": source.get("url", ""),
        })
    return records, style, len(footnotes)


def pdf_text(path):
    """Plain text with form feeds between pages, from pdftotext (poppler). pypdf was tested and loses the
    paragraph layout of three of the five corpus documents, so it is not used as a silent fallback.
    Codespace: sudo apt-get install -y poppler-utils   ·   Streamlit Cloud: a packages.txt with poppler-utils."""
    import shutil
    import subprocess
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext not found. In the Codespace run: sudo apt-get install -y poppler-utils")
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True,
                          check=True).stdout


if __name__ == "__main__":
    recs, style, n_notes = ingest_text(pdf_text(sys.argv[1]), {"case": "TEST", "title": "", "date": ""})
    print(f"style {style}: {len(recs)} paragraphs, {n_notes} footnotes")
    for r in recs[:3] + recs[-2:]:
        print(r["para"], "|", " / ".join(r["headings"]), "|", r["text"][:120], "| fn", [f["n"] for f in r["footnotes"]])