"""
tools/build_index.py - builds the ChromaDB index of the decision corpus, once, before deployment.

    python -m tools.build_index        embeds every chunk of corpus/paragraphs.json into corpus/chroma (two collections:
                                       "decisions" with context headers, used by the app, and "decisions_no_header", used
                                       only by retrieval_check.py) and prints the number of calls, tokens and the cost;
                                       then writes corpus/chunks.json (below)
    python -m tools.build_index --export-chunks
                                       only writes corpus/chunks.json from the existing index (no API call)

corpus/chunks.json: the chunks as stored in ChromaDB, readable without a database: id, case, paragraph, part,
section, value-chain levels, the context header that was embedded with the text, and the text. No vectors.

Run in the Codespace after logic/build_corpus.py; then commit corpus/ including corpus/chroma (never cache/ or .env).
The chunking and the storage are in retrieval.build_index; this script supplies the embedding function.

Also imported by retrieval_check.py:
    openai_embed(texts)   a list of texts -> a list of vectors (text-embedding-3-large), cached in cache/embed_corpus/
                          during development, so a re-run or a retrieval check costs nothing twice
    USAGE                 calls, cache hits and tokens of this process, for the cost line of the reports
"""
import hashlib
import json
import threading
from pathlib import Path

from logic import retrieval
from logic.ai_client import PRICES, setting

EMBED_MODEL = retrieval.EMBED_MODEL
CACHE_DIR = Path("cache") / "embed_corpus"
BATCH = 100
USAGE = {"calls": 0, "cached": 0, "tokens": 0}
_lock = threading.Lock()
_client = None


def _openai():
    global _client
    with _lock:
        if _client is None:
            from openai import OpenAI
            key = setting("OPENAI_API_KEY")
            if not key:
                raise SystemExit("OPENAI_API_KEY is not set in .env")
            _client = OpenAI(api_key=key, timeout=120)
        return _client


def openai_embed(texts):
    """Embeddings for a list of texts, one request (development cache in cache/embed_corpus/)."""
    texts = list(texts)
    key = hashlib.sha256(json.dumps([EMBED_MODEL, texts], ensure_ascii=False).encode()).hexdigest()[:20]
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        with _lock:
            USAGE["calls"] += 1
            USAGE["cached"] += 1
        return json.loads(path.read_text(encoding="utf-8"))
    resp = _openai().embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = [d.embedding for d in resp.data]
    with _lock:
        USAGE["calls"] += 1
        USAGE["tokens"] += getattr(getattr(resp, "usage", None), "prompt_tokens", 0) or 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vectors), encoding="utf-8")
    return vectors


def cost():
    return USAGE["tokens"] / 1e6 * PRICES.get(EMBED_MODEL, (0.0, 0.0))[0]


CHUNKS_FILE = retrieval.CORPUS_FILE.parent / "chunks.json"


def export_chunks():
    """Writes corpus/chunks.json from the index itself (what is stored is what is shown), sorted in corpus order."""
    import chromadb
    col = chromadb.PersistentClient(path=str(retrieval.CHROMA_DIR)).get_collection(retrieval.COLLECTION)
    got = col.get(include=["documents", "metadatas"])
    order = {p["id"]: k for k, p in enumerate(json.loads(retrieval.CORPUS_FILE.read_text(encoding="utf-8")))}
    rows = [{"id": cid, "case": m["case"], "paragraph": m["para"], "part": m["part"] + 1, "parts": m["parts"],
             "title": m["title"], "date": m["date"], "section": m["section"], "levels": m["levels"],
             "embedded_with_header": m["header"], "text": doc}
            for cid, doc, m in zip(got["ids"], got["documents"], got["metadatas"])]
    rows.sort(key=lambda r: (order.get(f"{r['case']}-{r['paragraph']}", 10 ** 6), r["part"]))
    CHUNKS_FILE.write_text(json.dumps({"collection": retrieval.COLLECTION, "chunks": len(rows),
                                       "embedding_model": EMBED_MODEL, "chunk_list": rows},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    import sys
    if "--export-chunks" in sys.argv:
        print(f"{export_chunks()} chunks written to {CHUNKS_FILE}")
        raise SystemExit
    paragraphs, chunks = retrieval.build_index(openai_embed, batch=BATCH)
    print(f"Index built in {retrieval.CHROMA_DIR}: {paragraphs} paragraphs, {chunks} chunks, "
          f"collections '{retrieval.COLLECTION}' and '{retrieval.COLLECTION_NO_HEADER}'")
    print(f"Embeddings: {USAGE['calls']} requests ({USAGE['cached']} from cache), {USAGE['tokens']:,} tokens, "
          f"about USD {cost():.4f}")
    print(f"{export_chunks()} chunks written to {CHUNKS_FILE}")