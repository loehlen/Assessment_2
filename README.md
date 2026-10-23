# EU Overlap Screen (LAWS90286 Assignment 2)

A preliminary EU merger control overlap screen: does the target of an acquisition overlap, horizontally or
vertically, with any of the buyer's portfolio companies? The app researches each company on public sources (or reads
a description the lawyer provides), lets the lawyer check the activities, compares every activity of the target with
every activity of each portfolio company on anonymised descriptions, looks up how the European Commission defined the
markets of the products in its decisions, and produces a Word document. The result is a working document for a lawyer
to verify, not a legal conclusion. Product markets only: geography and market shares are not assessed.

> Updated 23 October 2026. The final README (deployed URL, the test cases with their exact inputs and expected
> results, the cost per run) follows before submission.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # do NOT overwrite requirements.txt with `pip freeze`
cp .env.example .env                 # then fill in APP_PASSWORD and OPENAI_API_KEY for development
streamlit run app.py
```

On Streamlit Cloud: main file `app.py`; the settings of `.env.example` go into the app's Secrets (TOML: `KEY = "value"`).
With `DEV_MODE` off the app asks each user for their own OpenAI API key and uses it only for that session. After a
push that changes any file other than `app.py`, reboot the app (Manage app → ⋮ → Reboot app).

## The steps

1. **Companies**: the target and up to five portfolio companies (names, optional websites, other names; web search,
   your own description, or both).
2. **Activities**: two web searches and one extraction per company, each company in its own calls; every cited page
   is opened and every quotation checked (✔ checked · ≈ probably right · ○ not checked · ⚠ check before relying on
   it). The lawyer edits, adds or excludes activities.
3. **Preliminary assessment**: one anonymised pair per AI call; the decision rule, the reseller and own-use checks and
   the customer comparison in code. The lawyer sets a view on each label ("Likely", "Unlikely", "Ask the company",
   "Dismiss"), adds labels and rewrites the wording.
4. **Market definitions**: one search per target activity in the database of Commission decisions (hybrid retrieval,
   one reflection per type of product, at most one rewrite); every quotation of the Commission is checked word for
   word.
5. **Summary**: the result per portfolio company and the Word document (the lawyer's final choices in the main part,
   how the tool prepared them in an Annex).

"Save progress" in the sidebar downloads everything as a file (.json), which is also the audit log; "Open saved
progress" continues a screen from such a file without any AI call.

## Try it

The buttons under "Try an example" fill in the test cases. They use real companies in a **hypothetical** portfolio;
no real transaction is implied.

| Example | Target | Portfolio |
|---|---|---|
| TC1 | Lindt & Sprüngli | Ritter Sport, Barry Callebaut, FRoSTA |
| TC2 | Planet A Foods | same portfolio |
| TC3 | Koa | same portfolio |
| Other sector | Brillux | Hornbach, Sto, Henkel |

## Files

| File | Role |
|---|---|
| `app.py` | the interface (Streamlit): steps ① to ⑤, the sidebar (save and open progress, legend, Commission decisions, run summary) |
| `ai_client.py` | the one gate for every AI call: models per step, retries, rate limits, call log and cost |
| `activity_mapping.py` | steps ① and ②: confidentiality guard, two web searches and one extraction per company, existing relationships |
| `sources.py` | opens every cited page or PDF and checks the quoted passages; removes dead links |
| `comparison.py` | step ③: anonymisation, embeddings, one anonymised pair per AI call |
| `rules.py` | the sector-neutral rules in plain Python (answer lists, name removal, decision rule) |
| `schemas.py` | the AI instructions and the fixed answer forms |
| `precedents.py` | step ④: one search per target activity (types of product, hybrid retrieval, reflection, at most one rewrite), the citation and item checks |
| `export.py` | the Word document (python-docx) |
| `examples.py` | the inputs of the example buttons |
| `ingest.py`, `build_corpus.py`, `build_index.py`, `retrieval.py`, `corpus/` | the decision corpus: `corpus/paragraphs.json` (the 265 paragraphs with footnotes), `corpus/chroma/` (the ChromaDB index with the 266 chunks and their embeddings, used by step ④), `corpus/chunks.json` (the same chunks, readable, without vectors) and `corpus/corpus_report.md`. The decision PDFs that `build_corpus.py` reads (`corpus_src/`) are not in the repository; `build_corpus.py` lists where to download them |
| `.env.example` | every setting, with its effect |
| `retrieval_check.py`, `no_rag_check.py`, `test_results/` | development checks of the retrieval (with and without context headers, query forms) and of the model without the corpus; `test_results/` holds the reports of the retrieval checks (`no_rag_check.py` writes its report there when it is run); not part of the app |