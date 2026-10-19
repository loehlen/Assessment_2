# EU Overlap Screen (LAWS90286 Assignment 2)

A preliminary EU merger control overlap screen: does the target of an acquisition overlap, horizontally or
vertically, with any of the buyer's portfolio companies? The app researches each company on public sources (or reads
a description the lawyer provides), lets the lawyer check the activities, and compares every activity of the target
with every activity of each portfolio company on anonymised descriptions. The result is a working document for a
lawyer to verify, not a legal conclusion.

> Draft of 19 October 2026. The final README (deployed URL, the test cases with their exact inputs and expected
> results, the cost per run) follows before submission.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # do NOT overwrite requirements.txt with `pip freeze`
cp .env.example .env                 # then fill in APP_PASSWORD and OPENAI_API_KEY for development
streamlit run app.py
```

On Streamlit Cloud: main file `app.py`; the settings of `.env.example` go into the app's Secrets. With `DEV_MODE=0`
the app asks each user for their own OpenAI API key and uses it only for that session.

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
| `app.py` | the interface (Streamlit): steps ① companies, ② activities, ③ preliminary assessment |
| `ai_client.py` | the one gate for every AI call: models per step, retries, call log and cost |
| `activity_mapping.py` | step ②: confidentiality guard, two web searches and one extraction per company |
| `sources.py` | opens every cited page or PDF and checks the quoted passages; removes dead links |
| `comparison.py` | step ③: anonymisation, embeddings, one anonymised pair per AI call |
| `rules.py` | the sector-neutral rules in plain Python (answer lists, name removal, decision rule) |
| `schemas.py` | the AI instructions and the fixed answer forms |
| `examples.py` | the inputs of the example buttons |
| `ingest.py`, `build_corpus.py`, `build_index.py`, `retrieval.py`, `corpus/` | the decision corpus and its ChromaDB index (for step ④) |
| `test_compare.py`, `benchmark.py`, `save_searches.py`, `retrieval_check.py`, `no_rag_check.py`, `test_results/` | development tools and test results |