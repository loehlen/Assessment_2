# logic/ – the workflow without the interface

The AI calls, prompts, rules and searches. None of these files draws anything on the screen, so each can be read (and
tested) on its own.

| File | What it does |
|---|---|
| `ai_client.py` | the one gate for every AI call: models per step, retries, rate limits, call log and cost |
| `schemas.py` | the AI instructions (prompts) and the fixed answer forms (Pydantic, Structured Outputs) |
| `rules.py` | the sector-neutral rules in plain Python: answer lists, levels of trade, name removal, the decision rule of step ③ |
| `activity_mapping.py` | steps ① and ②: confidentiality guard, two web searches and one extraction per company, existing relationships |
| `sources.py` | opens every cited page or PDF and checks the quoted passages; removes dead links |
| `comparison.py` | step ③: anonymisation, embeddings, one anonymised pair of activities per AI call |
| `precedents.py` | step ④: one search per target activity (types of product, hybrid retrieval, reflection, at most one rewrite with STOP conditions), the citation and item checks |
| `retrieval.py` | the decision corpus in ChromaDB and the hybrid search (vector + BM25) |
| `ingest.py`, `build_corpus.py` | turning a decision into numbered paragraphs; `build_corpus.py` built `corpus/` from the official PDFs (`python -m logic.build_corpus`) and is also used when the lawyer adds a decision |
| `uploads.py` | a decision added by the lawyer for one screen: reading the PDF or pasted text, the case details, the paragraphs, the embeddings |
| `export.py` | the Word document (python-docx); the progress copy with the screen's data inside, and reading it back |
| `examples.py` | the inputs of the example buttons, including the two typed descriptions of TC2 and TC3 |
