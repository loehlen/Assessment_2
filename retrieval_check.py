"""
retrieval_check.py - the half-day retrieval check of spec section 12.

Run after build_index.py:   python retrieval_check.py
Compares three configurations on test queries whose correct paragraphs are known from the precedent analysis
(spec section 19), by how often a correct paragraph is in the top 3:
  A  paragraph chunks without context headers, vector search only
  B  with context headers, vector search only
  C  with context headers + BM25 keyword search + neighbouring paragraphs (the design of the app)
The queries are worded the way the app will generate them: generic product descriptions in Commission
terminology, without company names. Cost: a few query embeddings, well under USD 0.01.
Output: test_results/retrieval_check_<time>.md (a table for A3).
"""
from datetime import datetime
from pathlib import Path

import retrieval
from build_index import USAGE, openai_embed

# (query, value-chain level of the activity, correct paragraphs: any of them in the top 3 counts as a hit)
QUERIES = [
    ("relevant product market for chocolate tablets", "finished products",
     ["M.5644-24", "M.5644-15", "M.5644-21", "M.5644-22", "M.5644-23"]),
    ("geographic market for chocolate confectionery national or wider", "finished products",
     ["M.5644-42", "M.5644-43"]),
    ("relevant geographic market industrial chocolate catchment area around plants", "intermediate products",
     ["M.7408-74", "M.7408-75", "M.7408-61", "M.7408-63"]),
    ("chocolate compound coatings separate market from industrial chocolate", "intermediate products",
     ["M.7408-51", "M.7408-49", "M.7408-50", "M.7408-46"]),
    ("geographic scope of the market for cocoa butter, cocoa liquor and cocoa powder", "intermediate products",
     ["M.7120-66", "M.7120-65", "M.6872-30", "M.6872-33", "M.7408-79", "M.7408-78"]),
    ("procurement of cocoa beans geographic market", "raw materials",
     ["M.7120-55", "M.7120-54", "M.6872-26", "M.6872-27"]),
    ("are cocoa liquor, cocoa butter and cocoa powder separate product markets", "intermediate products",
     ["M.6872-21", "M.6872-22", "M.7120-30", "M.7120-31", "M.7120-41", "M.7408-44", "M.7408-45"]),
    ("chocolate sold in airport shops and travel retail as a separate market", "finished products",
     ["M.5644-39", "M.5644-40", "M.5644-41"]),
    ("private label chocolate tablets competitive constraint on branded tablets", "finished products",
     ["M.5644-117", "M.5644-48", "M.5644-49"]),
    ("liquid versus solid industrial chocolate segmentation", "intermediate products",
     ["M.7408-37", "M.7408-38", "M.7408-39", "M.7408-40", "M.7408-41", "M.7408-42"]),
    ("different customer groups forming separate relevant markets", None,
     ["Notice-88", "Notice-89", "Notice-24"]),
    ("do imports widen the relevant geographic market", None,
     ["Notice-42", "Notice-43"]),
    ("chocolate supplied by manufacturers to retailers and wholesalers, two levels of the supply chain",
     "finished products", ["M.5644-47"]),
    ("market definition left open for sugar confectionery", "finished products",
     ["M.5644-25", "M.5644-26", "M.5644-27"]),
]

CONFIGS = {
    "A  no headers, vector": {"collection": retrieval.COLLECTION_NO_HEADER, "use_bm25": False},
    "B  headers, vector": {"collection": retrieval.COLLECTION, "use_bm25": False},
    "C  headers + BM25 + neighbours": {"collection": retrieval.COLLECTION, "use_bm25": True},
}


def run():
    results = {}
    for name, cfg in CONFIGS.items():
        r = retrieval.Retriever(openai_embed, collection=cfg["collection"])
        rows = []
        for query, level, gold in QUERIES:
            out = r.search(query, k=3, level=level, use_bm25=cfg["use_bm25"], neighbours=True)
            top = [h["paragraph"]["id"] for h in out["hits"]]
            # config C also counts a correct paragraph that arrives as a neighbour of a top-3 hit
            near = {n["id"] for h in out["hits"] for n in h["neighbours"]} if name.startswith("C") else set()
            hit = any(g in top for g in gold)
            hit_near = hit or any(g in near for g in gold)
            rows.append({"query": query, "top": top, "hit": hit, "hit_near": hit_near})
        results[name] = rows
    return results


def report(results):
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    L = [f"# Retrieval check ({stamp})", "",
         f"{len(QUERIES)} test queries · correct paragraph in the top 3 · embeddings: {retrieval.EMBED_MODEL}", "",
         "| Configuration | Hits in top 3 | incl. neighbouring paragraphs (only C uses them) |", "|---|---|---|"]
    for name, rows in results.items():
        hits = sum(r["hit"] for r in rows)
        near = sum(r["hit_near"] for r in rows)
        L.append(f"| {name} | {hits}/{len(rows)} | {near}/{len(rows)} |")
    L += ["", "## Per query", "", "| Query | " + " | ".join(results) + " |", "|---" * (len(results) + 1) + "|"]
    for i, (query, _, gold) in enumerate(QUERIES):
        cells = []
        for rows in results.values():
            r = rows[i]
            mark = "✔" if r["hit"] else ("◐" if r["hit_near"] else "✖")
            cells.append(f"{mark} {', '.join(t.replace('Notice-', 'N-') for t in r['top'])}")
        L.append(f"| {query} (correct: {', '.join(gold[:3])}{'…' if len(gold) > 3 else ''}) | " + " | ".join(cells) + " |")
    L += ["", "✔ correct paragraph in the top 3 · ◐ only as a neighbouring paragraph · ✖ missed", "",
          f"Query embeddings: {USAGE['calls']} calls ({USAGE['cached']} from cache), {USAGE['tokens']:,} tokens"]
    path = Path("test_results") / f"retrieval_check_{stamp}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    res = run()
    for name, rows in res.items():
        print(f"{name}: {sum(r['hit'] for r in rows)}/{len(rows)} in top 3"
              + (f" ({sum(r['hit_near'] for r in rows)} incl. neighbours)" if name.startswith("C") else ""))
    print("report:", report(res))