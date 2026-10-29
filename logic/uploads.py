"""
logic/uploads.py - a Commission merger decision that the lawyer adds to the database of step ④ for one screen.

    read_pdf(data)                      the text of an uploaded PDF (pdftotext if installed, else pypdf)
    detect(text)                        case number, title, date and legal basis, read from the first pages
    parse(text, meta, builtin)          the numbered paragraphs (ingest.ingest_text, unchanged), with the context header
    default_ranges(records)             the parts on market definition, as "12-49, 92"
    select(records, ranges)             the paragraphs in those ranges
    make_upload(...)                    the upload as the session keeps it (paragraphs; vectors added by embed_upload)
    embed_upload(upload, embed)         one embedding per chunk, chunked exactly like the built-in corpus
    signature(uploads)                  changes whenever a decision is added or removed, so that step ④ searches again

The built-in corpus is never changed: an upload lives in the session (and in the progress file) only. Its paragraphs
are processed by the same functions as the built-in corpus (ingest.ingest_text, build_corpus.context_header,
retrieval.chunk_corpus) and searched together with it (retrieval.Retriever, extra=...). Every quotation the AI takes
from them is checked word for word like any other (precedents.check_quote). No AI call here; the embeddings are the
only API requests, and they go through the AI gate (ai_client.AI.embed).

Commission merger decisions only (case numbers "M.1234"): the citation check and the pinpoint citations of step ④ read
that format, and the corpus holds official Commission sources only.
"""
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile

from logic.build_corpus import context_header
from logic.ingest import ingest_text

SOURCE_DECISION = "Commission decision"
CASE = re.compile(r"\bM\s?\.\s?(\d{3,5})\b")
# the parts of a decision on market definition (ingest.SECTIONS); the rest (competitive assessment, remedies) is left
# out by default, as in the built-in corpus. The lawyer can change the ranges.
MARKET_SECTIONS = {"Relevant product market", "Relevant geographic market", "Market definition",
                   "Products and value chain"}
MIN_PARAGRAPHS = 3        # fewer than this in a PDF: it was not read as numbered paragraphs (a pasted extract may
                          # be a single paragraph)
EMBED_BATCH = 100


# =============================================================== reading
def read_pdf(data):
    """(text with form feeds between pages, the tool used). pdftotext keeps the layout the paragraph parser needs
    (Streamlit Cloud: packages.txt with poppler-utils); pypdf in layout mode is the fallback, which reads some decisions
    less well (the caller says so if few paragraphs are found)."""
    if shutil.which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(data)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True, timeout=120)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout, "pdftotext"
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text(extraction_mode="layout") or "")
        except Exception:  # noqa: BLE001 - one unreadable page must not lose the others
            pages.append(page.extract_text() or "")
    return "\f".join(pages), "pypdf"


def _title_case(text):
    small = {"of", "and", "the", "de", "du", "des", "la", "le", "von", "van", "und", "for", "in", "on", "a"}
    words = []
    for k, w in enumerate(text.split()):
        letters = re.sub(r"[^A-Za-z]", "", w)
        if w.isupper() and len(letters) > 3:
            w = w.capitalize() if "-" not in w else "-".join(x.capitalize() for x in w.split("-"))
        elif w.lower() in small and k:
            w = w.lower()
        words.append(w)
    return " ".join(words)


def detect(text):
    """What the first pages say: {"case", "title", "date" (YYYY-MM-DD), "decision"}; '' where nothing is found.
    The lawyer checks and corrects each field before the decision is added."""
    head = (text or "")[:6000]
    flat = re.sub(r"\s+", " ", head)
    out = {"case": "", "title": "", "date": "", "decision": ""}
    m = CASE.search(flat)
    if m:
        out["case"] = f"M.{m.group(1)}"
        t = re.match(r"\s*[-–—]\s*(.{3,160}?)\s*(?:\(?Only the|REGULATION|\(Only|Only |Article |\bDate\b|$)",
                     flat[m.end():])
        if t:
            title = re.sub(r"\s*/\s*", " / ", t.group(1)).strip(" -–—,")
            title = re.sub(r"\s+-\s+", " – ", title)
            out["title"] = _title_case(title)
    d = re.search(r"Date:\s*(\d{1,2})[./](\d{1,2})[./](\d{4})", flat) or \
        re.search(r"Brussels,\s*(\d{1,2})[./](\d{1,2})[./](\d{4})", flat)
    if d:
        day, month, year = (int(x) for x in d.groups())
        if 1 <= month <= 12 and 1 <= day <= 31:
            out["date"] = f"{year:04d}-{month:02d}-{day:02d}"
    a = re.search(r"\bArticle\s+(?:6\(1\)\([abc]\)|8\(\d\)|6\(2\))[^.]{0,60}?(?=\s+(?:Date|NON-OPPOSITION|In electronic|"
                  r"Regulation|This text|$))", flat, re.IGNORECASE)
    if a:
        out["decision"] = a.group(0).strip()
    return out


def normalise_case(text):
    """'COMP/M.5644', 'M 5644', 'm.5644' -> 'M.5644'; '' if it is not a merger case number."""
    m = CASE.search((text or "").upper().replace("COMP/", ""))
    return f"M.{m.group(1)}" if m else ""


# =============================================================== paragraphs
def parse(text, meta, builtin=None):
    """The numbered paragraphs of the decision as records like those of corpus/paragraphs.json. builtin: the built-in
    corpus by id; if the decision is already in it, its own data (title, date, legal basis, link, levels) are used
    and only the paragraphs NOT yet in the corpus are returned (e.g. the parts left out of the built-in ranges).
    Returns (records, style, footnotes found, paragraphs already in the corpus)."""
    case = meta["case"]
    known = {pid: p for pid, p in (builtin or {}).items() if p.get("case") == case}
    first = next(iter(known.values()), None)
    source = {"case": case, "title": meta.get("title") or case, "date": meta.get("date") or "",
              "url": meta.get("url") or "", "levels": [], "style": "auto", "source_type": SOURCE_DECISION}
    if first:
        source.update(title=first["title"], date=first["date"], url=first.get("url") or source["url"])
    records, style, n_notes = _ingest(text, source)
    short = (first or {}).get("short") or source["title"]
    decision = (first or {}).get("decision") or meta.get("decision") or ""
    out, skipped = [], []
    for r in records:
        if r["id"] in known:
            skipped.append(r["para"])
            continue
        r["short"], r["decision"] = short, decision
        r["header"] = context_header(r)
        r["user_provided"] = True
        out.append(r)
    return out, style, n_notes, skipped


# the line a numbered paragraph starts with, in any of the styles of ingest.STYLES
FIRST_NUMBER = re.compile(r"^\s{0,8}\(?(\d{1,3})[.)]\s+[A-Za-z‘'\"“(\[]", re.M)


def _ingest(text, source):
    """ingest_text for a whole decision, or for an extract copied from a database such as LexisNexis, which starts at
    the paragraph the lawyer chose, e.g. (42). The parser accepts a paragraph only if its number follows on from the
    one before; for an extract it starts at the first numbers found in the text, and the reading that finds the most
    paragraphs is kept."""
    best = ingest_text(text, source)
    if len(best[0]) >= MIN_PARAGRAPHS:
        return best
    starts = list(dict.fromkeys(int(m.group(1)) for m in FIRST_NUMBER.finditer(text)))[:5]
    for n in starts:
        if n > 1:
            got = ingest_text(text, dict(source, first_para=n))
            if len(got[0]) > len(best[0]):
                best = got
    return best


def ranges_text(numbers):
    """[12, 13, 14, 20] -> '12–14, 20'."""
    nums = sorted(set(numbers))
    out, start = [], None
    for k, n in enumerate(nums):
        if start is None:
            start = n
        if k + 1 == len(nums) or nums[k + 1] != n + 1:
            out.append(f"{start}" if start == n else f"{start}–{n}")
            start = None
    return ", ".join(out)


def parse_ranges(text):
    """'12-49, 92, 117' -> {12, ..., 49, 92, 117}; None if the text cannot be read."""
    out = set()
    for part in re.split(r"[,;]\s*", (text or "").strip()):
        part = part.strip().strip("()")
        if not part:
            continue
        m = re.fullmatch(r"\(?(\d{1,3})\)?\s*(?:[-–—]|to)\s*\(?(\d{1,3})\)?", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b:
                return None
            out.update(range(a, b + 1))
        elif part.isdigit():
            out.add(int(part))
        else:
            return None
    return out


def default_ranges(records):
    """The paragraphs in the parts on market definition; all paragraphs if no such part was recognised."""
    nums = [r["para"] for r in records if r.get("section") in MARKET_SECTIONS]
    return ranges_text(nums or [r["para"] for r in records])


def select(records, ranges):
    wanted = parse_ranges(ranges)
    if wanted is None:
        return None
    return [r for r in records if r["para"] in wanted]


# =============================================================== the upload as the session keeps it
def make_upload(meta, records, origin, already=()):
    """meta: the fields as the lawyer confirmed them; records: the selected paragraphs; origin: the file name, or
    'pasted text'. The vectors are added by embed_upload (and again after a progress file is opened)."""
    return {"case": meta["case"], "title": records[0]["title"] if records else meta.get("title", ""),
            "date": records[0]["date"] if records else meta.get("date", ""), "url": meta.get("url") or "",
            "origin": origin, "in_builtin_corpus": bool(already), "paragraphs": records, "vectors": None,
            "chunk_ids": None}


def embed_upload(upload, embed):
    """Chunks the paragraphs exactly like the built-in corpus (retrieval.chunk_corpus: one chunk per paragraph, longer
    ones split, with the context header) and embeds them. Changes the upload in place."""
    import numpy as np

    from logic.retrieval import chunk_corpus
    chunks = chunk_corpus(upload["paragraphs"])
    vectors = []
    for i in range(0, len(chunks), EMBED_BATCH):
        vectors += embed([c["embed_text"] for c in chunks[i:i + EMBED_BATCH]])
    upload["vectors"] = np.asarray(vectors, dtype=np.float32)
    upload["chunk_ids"] = [c["paragraph_id"] for c in chunks]
    return upload


def extra_index(uploads):
    """What retrieval.Retriever needs from the uploads: (paragraphs, chunk paragraph ids, vectors) or None."""
    import numpy as np
    ready = [u for u in uploads or [] if u.get("vectors") is not None and len(u["paragraphs"])]
    if not ready:
        return None
    return {"paragraphs": [p for u in ready for p in u["paragraphs"]],
            "chunk_ids": [pid for u in ready for pid in u["chunk_ids"]],
            "vectors": np.vstack([u["vectors"] for u in ready])}


def signature(uploads):
    """'' without uploads (so that searches made without any upload stay valid); otherwise a short hash of the
    paragraphs added, stored with each search of step ④."""
    if not uploads:
        return ""
    content = [(u["case"], [(p["id"], p["text"]) for p in u["paragraphs"]]) for u in uploads]
    return hashlib.sha256(json.dumps(content, ensure_ascii=False).encode()).hexdigest()[:12]


def for_audit(uploads):
    """The uploads as the progress file and the audit log keep them: everything except the vectors (they are
    computed again, with one embedding request, when step ④ next searches)."""
    return [{k: v for k, v in u.items() if k not in ("vectors", "chunk_ids")} for u in uploads or []]


def from_audit(saved):
    """The uploads of a progress file, without vectors; only well-formed entries."""
    out = []
    for u in saved or []:
        if not isinstance(u, dict) or not normalise_case(u.get("case")) or not isinstance(u.get("paragraphs"), list):
            continue
        paras = [p for p in u["paragraphs"] if isinstance(p, dict) and {"id", "case", "para", "text"} <= set(p)]
        if paras:
            out.append(dict(u, paragraphs=paras, vectors=None, chunk_ids=None))
    return out
