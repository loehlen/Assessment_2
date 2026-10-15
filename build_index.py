"""
build_index.py - embeds the decision corpus once and stores it in ChromaDB (corpus/chroma).

Run once, after build_corpus.py:   python build_index.py
Cost: about 265 paragraphs x 2 collections, well under USD 0.02 with text-embedding-3-large.
The folder corpus/chroma is then committed, so the deployed app never re-embeds the corpus.
"""
import hashlib
import json
import time
from pathlib import Path

from dotenv import load_dotenv

import retrieval

load_dotenv()
CACHE = Path("cache/embed_corpus")
PRICE_PER_M = 0.13      # USD per 1M tokens, text-embedding-3-large (to verify, spec section 8)
_client = None
USAGE = {"tokens": 0, "calls": 0, "cached": 0}


def openai_embed(texts):
    """Embeds a list of texts with text-embedding-3-large; cached on disk during development."""
    global _client
    key = hashlib.sha256(json.dumps([retrieval.EMBED_MODEL, texts], ensure_ascii=False).encode()).hexdigest()[:20]
    path = CACHE / f"{key}.json"
    if path.exists():
        USAGE["cached"] += 1
        return json.loads(path.read_text())
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(timeout=120)
    resp = _client.embeddings.create(model=retrieval.EMBED_MODEL, input=texts)
    USAGE["tokens"] += resp.usage.prompt_tokens
    USAGE["calls"] += 1
    vectors = [d.embedding for d in resp.data]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vectors))
    return vectors


if __name__ == "__main__":
    t = time.time()
    n_paragraphs, n_chunks = retrieval.build_index(openai_embed)
    print(f"Indexed {n_paragraphs} paragraphs as {n_chunks} chunks in {retrieval.CHROMA_DIR} "
          f"(collections '{retrieval.COLLECTION}' and '{retrieval.COLLECTION_NO_HEADER}') in {time.time() - t:.0f} s")
    print(f"Embedding calls: {USAGE['calls']} ({USAGE['cached']} from cache) · {USAGE['tokens']:,} tokens · "
          f"USD {USAGE['tokens'] / 1e6 * PRICE_PER_M:.4f}")