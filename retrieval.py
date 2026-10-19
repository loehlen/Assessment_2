"""
retrieval.py - the decision corpus in ChromaDB and the hybrid search of stage 4 (spec section 12).

    build_index(embed)          once, before deployment: chunks, embeds and stores the corpus in corpus/chroma
    Retriever(embed).search()   in the app: vector search + keyword search (BM25), combined by reciprocal rank
                                fusion, optional filter by value-chain level, neighbouring paragraphs (+/-1)

`embed` is a function that takes a list of texts and returns a list of vectors (text-embedding-3-large).
It is passed in, so this module makes no API calls of its own and can be tested without a key.
"""
# ChromaDB needs a newer SQLite than Streamlit Cloud provides; pysqlite3-binary replaces it there (spec section 12).
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import json
import math
import re
import threading
from collections import Counter
from pathlib import Path

CORPUS_FILE = Path("corpus/paragraphs.json")
CHROMA_DIR = Path("corpus/chroma")
COLLECTION = "decisions"
COLLECTION_NO_HEADER = "decisions_no_header"     # only for the retrieval check (with v without context headers)
EMBED_MODEL = "text-embedding-3-large"
MAX_TOKENS = 350                                 # longer paragraphs are split with semchunk (spec section 12)
RRF_K = 60                                       # standard constant of reciprocal rank fusion


# =============================================================== chunking
MIN_TAIL_TOKENS = 30      # 20 Oct: a last piece shorter than this is merged back (Notice (23) left "This is analysed in
                          # the competitive assessment." as a 7-word chunk of its own)
# 20 Oct: footnotes that only cite (earlier cases, questionnaire replies, the Form CO) are kept with the paragraph for
# display and the audit, but no longer embedded: in 34 paragraphs the footnotes were longer than the text, and the key
# defining paragraphs looked like lists of case names to the vector search (M.7120 (30): 18 words of text, 79 of
# footnotes). A footnote that says something (a finding, an example "where the Commission ...", a quotation, a second
# sentence) stays in the embedding. Legal citation patterns only, no sector knowledge.
CITATION_ONLY = re.compile(r"^\s*(see,?\s+(also\s+|for example,?\s+|in particular\s+|e\.g\.,?\s+)?)?(case\b|cases\b|"
                           r"comp/m|m\.\s?\d|commission decision|decision of|replies to|reply to|response to|ibid|"
                           r"form co|judgment|order of|oj\b|answers? to|minutes)", re.I)
SUBSTANCE = re.compile(r"\bwhere\b|left open|conclud|consider|\bfound\b|distinction|separate|segment|substitut|\bprice|"
                       r"stated|indicated|explained|[\"“]\w|[a-z0-9\)]\.\s+[\"“A-Z][a-z]")


def embedded_footnote(text):
    """Whether a footnote goes into the embedded text (False for a footnote that only cites)."""
    return not (CITATION_ONLY.search(text or "") and not SUBSTANCE.search(text or ""))


def chunk_corpus(paragraphs):
    """One chunk per paragraph; paragraphs above MAX_TOKENS are split with semchunk at the most structural
    break points. Every chunk keeps its paragraph number, so pinpoint citations stay exact."""
    import semchunk
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")        # the tokenizer of text-embedding-3-large

        def count(t):
            return len(enc.encode(t))
    except Exception:  # noqa: BLE001 - tokenizer file not downloadable: estimate (about 4 characters per token)
        def count(t):
            return max(1, len(t) // 4)
    chunker = semchunk.chunkerify(count, MAX_TOKENS)
    chunks = []
    for p in paragraphs:
        pieces = [p["text"]] if count(p["text"]) <= MAX_TOKENS else chunker(p["text"])
        if len(pieces) > 1 and count(pieces[-1]) < MIN_TAIL_TOKENS:      # no orphan tail (20 Oct)
            pieces = pieces[:-2] + [pieces[-2] + " " + pieces[-1]]
        notes = " ".join(f"[fn {f['n']}] {f['text']}" for f in p["footnotes"] if embedded_footnote(f["text"]))
        for k, piece in enumerate(pieces):
            chunks.append({
                "id": f"{p['id']}#{k}", "paragraph_id": p["id"], "case": p["case"], "para": p["para"],
                "part": k, "parts": len(pieces), "text": piece,
                # footnotes are embedded with the last piece of the paragraph (case references often sit there)
                "embed_text": f"{p['header']}\n{piece}" + (f"\nFootnotes: {notes}" if notes and k == len(pieces) - 1 else ""),
                # identical except for the header, so the retrieval check measures what the header adds
                "embed_text_no_header": piece + (f"\nFootnotes: {notes}" if notes and k == len(pieces) - 1 else ""),
            })
    return chunks


def _metadata(paragraph, chunk):
    return {"paragraph_id": paragraph["id"], "case": paragraph["case"], "para": paragraph["para"],
            "part": chunk["part"], "parts": chunk["parts"], "title": paragraph["title"], "date": paragraph["date"],
            "section": paragraph["section"] or "", "header": paragraph["header"],
            "levels": ",".join(paragraph["levels"]), "source_type": paragraph["source_type"],
            "user_provided": False}


def build_index(embed, batch=100):
    """Embeds the corpus once and stores it in corpus/chroma (committed to the repository, so markers' keys
    are used only for query embeddings). Also stores a second collection without context headers, used only
    by retrieval_check.py to measure what the headers add."""
    import chromadb
    paragraphs = {p["id"]: p for p in json.loads(CORPUS_FILE.read_text(encoding="utf-8"))}
    chunks = chunk_corpus(paragraphs.values())
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    for name, field in ((COLLECTION, "embed_text"), (COLLECTION_NO_HEADER, "embed_text_no_header")):
        try:
            client.delete_collection(name)
        except Exception:  # noqa: BLE001 - collection did not exist yet
            pass
        col = client.create_collection(name, metadata={"hnsw:space": "cosine"})
        for i in range(0, len(chunks), batch):
            part = chunks[i:i + batch]
            col.add(ids=[c["id"] for c in part], embeddings=embed([c[field] for c in part]),
                    documents=[c["text"] for c in part],
                    metadatas=[_metadata(paragraphs[c["paragraph_id"]], c) for c in part])
    return len(paragraphs), len(chunks)


# =============================================================== keyword search (BM25)
TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
STOP = set("the a an of and or in on for to by with as is are be was were that this which it its from at "
           "not can could would should may might their there these those such than also into under".split())


def _tokens(text):
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]


class BM25:
    """Okapi BM25 over the paragraph texts (with headers), for exact Commission terms such as 'countlines',
    'pralines', 'cocoa liquor' or 'compound' that vector search can rank too low."""

    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [Counter(_tokens(d)) for d in docs]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lengths) / max(len(self.lengths), 1)
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.k1, self.b = k1, b

    def scores(self, query):
        q = _tokens(query)
        out = []
        for d, length in zip(self.docs, self.lengths):
            s = 0.0
            for t in q:
                if t in d:
                    tf = d[t]
                    s += self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * length / self.avg))
            out.append(s)
        return out


# =============================================================== hybrid search
class Retriever:
    def __init__(self, embed, collection=COLLECTION):
        import chromadb
        self.embed = embed
        self._lock = threading.Lock()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.col = self.client.get_collection(collection)
        self.paragraphs = {p["id"]: p for p in json.loads(CORPUS_FILE.read_text(encoding="utf-8"))}
        self.order = list(self.paragraphs)                       # corpus order, for neighbouring paragraphs
        # keyword search on section, headings and text; party names are left out (queries never contain names)
        self.bm25 = BM25([" ".join([p["section"]] + p["headings"] + [p["text"]]) for p in self.paragraphs.values()])

    def _vector(self, query, n):
        vector = self.embed([query])             # the API request runs outside the lock (20 Oct)
        with self._lock:                         # one read of the index at a time (stage 4 searches in parallel)
            res = self.col.query(query_embeddings=vector, n_results=n, include=["metadatas", "distances"])
        ranked, seen = [], set()
        for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
            pid = meta["paragraph_id"]
            if pid not in seen:                                  # several pieces of one paragraph count once
                seen.add(pid)
                ranked.append((pid, 1 - dist))
        return ranked

    def _keyword(self, query, n):
        scores = self.bm25.scores(query)
        ranked = sorted(zip(self.order, scores), key=lambda x: -x[1])
        return [(pid, s) for pid, s in ranked[:n] if s > 0]

    def search(self, query, k=5, level=None, use_bm25=True, neighbours=True, pool=30):
        """
        Returns up to k hits, best first: {paragraph, score, found_by, rank_vector, rank_keyword, neighbours}.
        level: a value-chain level from rules.VALUE_CHAIN_LEVELS. Paragraphs of decisions at other levels are
        dropped first; if that leaves nothing, the search is repeated without the filter (spec section 12), and
        the result says so. The Notice (no level) always passes the filter.
        """
        vec = self._vector(query, pool)
        key = self._keyword(query, pool) if use_bm25 else []
        fused = Counter()
        for ranked in (vec, key):
            for rank, (pid, _) in enumerate(ranked, start=1):
                fused[pid] += 1 / (RRF_K + rank)
        rank_v = {pid: r for r, (pid, _) in enumerate(vec, start=1)}
        rank_k = {pid: r for r, (pid, _) in enumerate(key, start=1)}
        candidates = [pid for pid, _ in fused.most_common()]

        filtered, filter_used = candidates, False
        if level:
            at_level = [pid for pid in candidates if level in self.paragraphs[pid]["levels"]]
            if at_level:     # at least one decision at this level: keep those, plus the Notice (no level)
                filtered = [pid for pid in candidates
                            if level in self.paragraphs[pid]["levels"] or not self.paragraphs[pid]["levels"]]
                filter_used = True
            # otherwise no decision covers this level: search all decisions (the filter is dropped)

        hits = []
        for pid in filtered[:k]:
            p = self.paragraphs[pid]
            hits.append({
                "paragraph": p, "score": round(fused[pid], 4),
                "found_by": "+".join(x for x, r in (("vector", rank_v), ("keyword", rank_k)) if pid in r),
                "rank_vector": rank_v.get(pid), "rank_keyword": rank_k.get(pid),
                "neighbours": self.neighbours(pid) if neighbours else [],
            })
        return {"hits": hits, "level_filter": level if filter_used else None,
                "level_filter_dropped": bool(level) and not filter_used}

    def neighbours(self, pid):
        """Paragraphs n-1 and n+1 of the same decision, if they are in the corpus: the conclusion ('left open',
        'national') often comes in the next paragraph."""
        p = self.paragraphs[pid]
        out = []
        for n in (p["para"] - 1, p["para"] + 1):
            nid = f"{p['case']}-{n}"
            if nid in self.paragraphs:
                out.append(self.paragraphs[nid])
        return out


def cite(p):
    """Pinpoint citation as shown in the app, e.g. 'M.7408 Cargill / ADM Chocolate Business (2015), para (74)'."""
    return f"{p['case']} {p['title']} ({p['date'][:4]}), para ({p['para']})"