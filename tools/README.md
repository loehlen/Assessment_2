# tools/ – building and checking the decision database

Development scripts, not used by the running app. Run them from the repository's main folder, e.g.
`python -m tools.build_index`.

| File | What it does |
|---|---|
| `build_index.py` | embeds every chunk of `corpus/paragraphs.json` into the ChromaDB index `corpus/chroma` and writes `corpus/chunks.json` (run once, after `logic/build_corpus.py`) |
| `retrieval_check.py` | checks that the retrieval finds the right Commission paragraphs (with and without context headers, query forms); reports in `test_results/` |
| `no_rag_check.py` | the "comparison without RAG": what the model says about the markets without the corpus; report in `test_results/` |
