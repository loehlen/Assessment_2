"""
build_index.py - builds the ChromaDB index of the decision corpus, once, before deployment (spec section 14).

    python build_index.py        embeds every chunk of corpus/paragraphs.json into corpus/chroma (two collections:
                                 "decisions" with context headers, used by the app, and "decisions_no_header", used
                                 only by retrieval_check.py) and prints the number of calls, tokens and the cost

Run in the Codespace after build_corpus.py; then commit corpus/ including corpus/chroma (never cache/ or .env).
The chunking and the storage are in retrieval.build_index; this script supplies the embedding function.

Also imported by retrieval_check.py:
    openai_embed(texts)   a list of texts -> a list of vectors (text-embedding-3-large), cached in cache/embed_corpus/
                          during development, so a re-run or a retrieval check costs nothing twice
    USAGE                 calls, cache hits and tokens of this process, for the cost line of the reports

Rebuilt on 19 Oct 2026: the file had been overwritten by a copy of comparison.py. Same interface as before
(USAGE, openai_embed, the build when run on its own); the committed index in corpus/chroma does not need rebuilding.
"""
import hashlib
import json
import threading
from pathlib import Path

import retrieval
from ai_client import PRICES, setting

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


if __name__ == "__main__":
    paragraphs, chunks = retrieval.build_index(openai_embed, batch=BATCH)
    print(f"Index built in {retrieval.CHROMA_DIR}: {paragraphs} paragraphs, {chunks} chunks, "
          f"collections '{retrieval.COLLECTION}' and '{retrieval.COLLECTION_NO_HEADER}'")
    print(f"Embeddings: {USAGE['calls']} requests ({USAGE['cached']} from cache), {USAGE['tokens']:,} tokens, "
          f"about USD {cost():.4f}")