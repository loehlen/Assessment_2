# EU Overlap Screen (LAWS90286 Assignment 2)

A preliminary EU merger control overlap screen: does the target of an acquisition overlap, horizontally or
vertically, with any of the buyer's portfolio companies? The app researches each company on public sources (or reads
a description the lawyer provides), lets the lawyer check the activities, compares every activity of the target with
every activity of each portfolio company on anonymised descriptions, looks up how the European Commission defined the
markets of the products in its decisions, and produces a Word document. The result is a working document for a lawyer
to verify, not a legal conclusion. Product markets only: geography and market shares are not assessed.

**Deployed app:** [ADD THE STREAMLIT URL]

## Your API key

Enter your own OpenAI API key in the sidebar under **API Key Input** (the course's API Credentials sidebar module,
`api_key.py`) and click **Update API Key**. The key is used only for the calls of your session and is not stored.
Each test case below costs about USD 0.50–1 in API fees, most of it for the web searches, and takes about
[ADD] minutes.

## The three test cases

All three use the same hypothetical portfolio of real companies (Ritter Sport, Barry Callebaut, FRoSTA); no real
transaction is implied. FRoSTA (frozen food) is the control: it has no real overlap with any of the targets. Together
the three cases form a gradient: the Commission has defined the markets (TC1), only one side's market (TC2), none
(TC3). They also show the three ways of finding a company's activities: web search, the lawyer's own description, and
both.

**Entering the inputs.** On the start page click **Start now**. In step ① either type the inputs below into the fields,
or click the test case's button under **Try an Example**, which fills in the same fields for you (they stay editable).
The two descriptions are in `examples.py` (`BARRY_CALLEBAUT_ADDED`, `RITTER_SPORT_DESCRIBED`) and appear in the
description fields when the button is clicked.

| Company | Website | Other names | Used in |
|---|---|---|---|
| Lindt & Sprüngli | lindt-spruengli.com | Lindt, Sprüngli, Lindt & Sprüngli AG | TC1 (target) |
| Planet A Foods | planet-a-foods.com | Planet A, ChoViva | TC2 (target) |
| Koa | koa-impact.com | Koa Impact, Koa Switzerland AG, Koa Germany GmbH | TC3 (target) |
| Ritter Sport | ritter-sport.com | Ritter, Alfred Ritter GmbH & Co. KG | portfolio, all three |
| Barry Callebaut | barry-callebaut.com | Callebaut, Barry Callebaut AG | portfolio, all three |
| FRoSTA | frosta-ag.com | FRoSTA AG | portfolio, all three |

**Then, in every test case:** ① click **Find activities**; ② check the activities (you can edit, add, delete or mark an
activity as not relevant) and click **Compare activities**; ③ look at the preliminary assessment and click **Find
Commission market definitions**; ④ the Commission's market definitions, then **Go to the summary**; ⑤ the summary and
**Download the Word document**. On every label you can set **Your view** (not set yet, Likely, Unlikely, Ask the company,
Dismiss), add a note or use **Edit**; the summary and the Word document follow your choices. Each test case below names
one such input to try, so that you can see the output change.

### TC1 · Lindt & Sprüngli (the Commission has defined the markets)

- **Input:** target Lindt & Sprüngli; portfolio Ritter Sport, Barry Callebaut, FRoSTA; every company by **web search**.
- **What it shows:** the full pipeline on well-documented companies, with a precedent for both sides.
- **Expected:**
  - Ritter Sport: a **horizontal** overlap in chocolate (tablets and other chocolate confectionery); in step ④ the
    Commission's separate markets for countlines, tablets and pralines (M.5644 Kraft Foods / Cadbury); a **vertical**
    link from Lindt's chocolate to Ritter Sport's own shops (resale).
  - Barry Callebaut: a **vertical** link (cocoa products and industrial chocolate as inputs for Lindt's chocolate),
    with the Commission's markets for industrial chocolate and semi-finished cocoa products (M.6872, M.7120, M.7408).
  - FRoSTA: no real overlap.
- **Your input to try:** in step ③, set the labels in FRoSTA's box (the rows the generous comparison kept) to
  **Dismiss**. They leave the step ④ search and the main part
  of the Word document; the Annex of the Word document still lists them among the pairs compared without an overlap.
- **Where it performs well:** the activities with checked sources (✔ = the quotation found word for word on the page);
  the overlap with Ritter Sport and the Commission's own sentences, each checked word for word against the decision.
- **Where it does not:** the comparison is generous by design, so some unlikely pairs with FRoSTA are kept for the
  lawyer to dismiss; the split into activities can differ from run to run; facts a company does not publish clearly
  (for example Lindt's travel retail or business-to-business sales) may be missing.

### TC2 · Planet A Foods (a precedent for only one side)

- **Input:** target Planet A Foods (ChoViva, a cocoa-free alternative to chocolate); same portfolio; Barry Callebaut by
  **both**: web search plus the lawyer's description (filled in by the button) of Barry Callebaut's partnership with
  Planet A Foods for ChoViva and of its cocoa products (cocoa liquor, cocoa butter, cocoa powder).
- **Your input (required, step ①):** because the description names the target, the app shows a confidentiality warning: the text would be
  sent in Barry Callebaut's own research call, so the AI would see both names together. Tick **Send anyway** (the
  lawyer's decision; it is recorded in the progress file), then click **Find activities**.
- **What it shows:** the lawyer adding what they know to the web research; the confidentiality guard; an **existing
  relationship** between two companies of the screen, found by the app's code in each company's separate research,
  never by asking the AI about two companies together; a new product the Commission has not defined.
- **Expected:**
  - Barry Callebaut: the existing relationship (ChoViva); a **vertical** link (Barry Callebaut distributes ChoViva to
    food manufacturers) and compound and industrial chocolate as related products; in step ④ the Commission's
    markets for Barry Callebaut's products, while ChoViva itself has no market definition.
  - Barry Callebaut's cocoa products against Planet A Foods's cocoa-butter alternative and cocoa powder replacer: a
    **horizontal** label; in step ④ the Commission has defined the markets for cocoa butter and cocoa powder, which
    fit Planet A Foods's products only as "not an exact match", so the result is at most **Possible**.
  - Ritter Sport: ChoViva as a possible input for Ritter Sport's chocolate (**vertical**) and a related product.
  - FRoSTA: no real overlap (fats as an input for frozen food may be kept as a vertical link for the lawyer to check).
- **Where it performs well:** the relationship and the partnership are shown with their sources; step ④ says which
  side has a precedent and which does not.
- **Where it does not:** without the lawyer's description, the web search finds the partnership in some runs and
  not in others; a distributor of ChoViva can then look like a competitor of Planet A Foods. A new product has no
  precedent, so whether it is in the same market as chocolate remains a question for the lawyer. Where the public
  sources say too little, the row comes back **Unclear: please check** instead of a guess: a product still under
  development (in some runs Planet A Foods's coffee) and a line the sources name without its products (FRoSTA's
  industrial business). The lawyer adds what they know with "Edit" in step ② or asks the company.

### TC3 · Koa (no precedent)

- **Input:** target Koa (cocoa fruit products: pulp, juice concentrate and powder for food and drink manufacturers,
  and drinks); same portfolio; Ritter Sport by **my description** (filled in by the button): the description a
  client would give of its own company, with no web search for Ritter Sport.
- **What it shows:** a company described only by the lawyer (fast and cheap; its sources are marked "your
  description"); and how the app behaves where the database of Commission decisions has nothing to offer.
- **Expected:**
  - Ritter Sport: a **horizontal** link between Koa's cocoa fruit drinks and Ritter Sport's CacaoVida drinks; Koa's
    cocoa fruit ingredients as a possible input (**vertical**) for Ritter Sport's chocolate and drinks.
  - Barry Callebaut: a **horizontal** overlap with its cocoa fruit ingredients (Cabosse Naturals) and a **vertical**
    link (Koa's ingredients for Barry Callebaut's chocolate), if the web search finds Cabosse Naturals.
  - Step ④: **No precedent** for cocoa fruit products: the market is then for the lawyer to assess under the Market
    Definition Notice; the app does not force a chocolate decision onto cocoa fruit.
  - FRoSTA: no real overlap (fruit ingredients as an input for frozen food may be kept for the lawyer to check).
- **Your input to try:** in step ③, set the label of the row with Ritter Sport's CacaoVida drinks (if the comparison
  kept it) to **Ask the company** and write a note (for example, where CacaoVida is sold). The row then appears under **Open Points** in
  step ⑤ and in the Word document.
- **Where it performs well:** the overlap with CacaoVida from the lawyer's own description; an honest "No precedent"
  instead of an analogy the decisions do not support.
- **Where it does not:** with no precedent, the app can only show the facts; the market definition itself is the
  lawyer's work. A typed description has no web sources: the app can only check that each fact comes from the text
  the lawyer typed.

### One more example (not one of the three test cases)

**Other sector · Brillux** (paints, facade systems, DIY retail, adhesives: Brillux against Hornbach, Sto and Henkel)
shows that the app contains no knowledge of one sector: the same code works for building materials. No decision of
this sector is in the database, so step ④ shows "No precedent".

## The steps

1. **Companies**: the target and up to five portfolio companies (names, optional websites, other names; web search,
   your own description, or both).
2. **Activities**: two web searches and one extraction per company, each company in its own calls; every cited page
   is opened and every quotation checked (✔ checked · ≈ probably right · ○ not checked · ⚠ check before relying on
   it). Production for the group's own use is listed as one line, "Own use", but not compared (the lawyer can
   include it).
   The lawyer edits, adds or excludes activities.
3. **Preliminary assessment**: one anonymised pair per AI call; the decision rule, the reseller and own-use checks and
   the customer comparison in code. The lawyer sets a view on each label ("Likely", "Unlikely", "Ask the company",
   "Dismiss"), adds labels and rewrites the wording. Rows whose only label is a horizontal one across different levels
   of trade, without the same direct customers, are folded under "Less likely" (display only).
4. **Market definitions**: one search per target activity in the database of Commission decisions (hybrid retrieval,
   one reflection per type of product, at most one rewrite); every quotation of the Commission is checked word for
   word. Each result stands beside the label it belongs to.
5. **Summary**: the result per portfolio company and the Word document (the lawyer's final choices in the main part,
   how the tool prepared them in an Annex).

"Save progress" in the sidebar downloads the screen so far as a Word document that also holds the screen's data
(invisible in Word, as Custom XML), so that "Open saved progress" can continue it later without any AI call; changes made
in Word are not read back. "Download the Word document" saves the final document without the data, to share. The full
audit log (every AI call with what it was sent and returned, the sources, the checks and the lawyer's changes) is under
"About This Run" (.json); "Open saved progress" opens it too.

**AI calls.** A test case makes well over a hundred AI calls: per company two web searches and one extraction (one
extraction only with "my description"); one comparison per pair of activities; in step ④ one call that sorts the
products into types and one reflection per type and attempt. The embedding requests that turn search questions into
vectors for the database are counted separately; they are not AI answers.

## Class techniques used

**Lab 1 (problem decomposition, fixed questions, if/then logic)**

| Lab 1 | In this app |
|---|---|
| The legal task broken into elements, each with its requirements (`prompts.py`) | Five steps (`app.py`); within them fixed questions with fixed answer lists: per activity the level of trade, direct customers, end users and status (`rules.py`, used by `schemas.Activity`); per pair of activities the product relation and the vertical links (`schemas.Comparison`). The answer lists carry their definitions (e.g. the levels of trade defined by the buyer's use, Vertical Guidelines para 287). |
| One AI call per element, in a loop | One AI call per anonymised pair of activities (`comparison.compare`); two web searches and one extraction per company, each company in its own calls (`activity_mapping.py`). |
| A constrained answer that code can branch on (`ask_ai_yes_no`) | Structured Outputs: every AI answer fills a fixed Pydantic form (`ai_client.AI.respond` → `responses.parse`), with fixed answer lists as `Literal` types (`schemas.py`). |
| if/then control of the result | `rules.decide()`: combines the AI's answer with checks in code (input and resale signals from the facts, the reseller condition, own use); a failed or blocked call is never screened out. Further if/then routing: the source modes, the confidentiality guard (`activity_mapping.guard`), which rows step ④ looks up (`precedents.search_units`). |

Unlike Lab 1, the app does not stop at the first negative answer: an overlap screen must compare every pair, so that no
overlap is missed.

**Lab 2 (RAG with ChromaDB, loops with STOP conditions, reflection, report)**

| Lab 2 | In this app |
|---|---|
| ChromaDB (`PersistentClient`) with `text-embedding-3-large` | The same (`retrieval.py`, `build_index.py`, `corpus/chroma`); the evidence is a corpus of Commission merger decisions and the Market Definition Notice. |
| Chunking with metadata (`store_doc_in_chroma_db.py`) | Built for legal text (`ingest.py`, `build_corpus.py`, `retrieval.py`): one chunk per numbered paragraph, longer paragraphs split with semchunk (350 tokens); each chunk carries a context header (decision, section) and its footnotes; each decision is tagged with the levels of trade it concerns. |
| The AI writes the search query (`ask_ai_with_retrieval`) | One AI call sorts the products to look up into types of product, in generic terms and with their level of trade (`schemas.QueryPlan`); code turns each type into two legal questions (`precedents.QUERY_FORMS`). |
| Search beyond vector search (`home.py`, "additional features") | Hybrid retrieval: vector search plus BM25 keyword search, combined by reciprocal rank fusion, with a level-of-trade filter in the first attempt (`retrieval.Retriever.search`). |
| Answer from the retrieved documents only, with citations | The reflection (one AI call per type of product, `schemas.Reflection`) places each product in a market that the retrieved paragraphs define, or in none, citing the paragraph numbers. |
| Grounding check (`grounding.py`) | In code (`precedents.check`): a cited paragraph counts only if the retrieval returned it; every quotation of what the Commission decided or left open is checked word for word (`check_quote`); a label that no verified passage supports is shown as "not stated in these paragraphs". The same idea for company websites in step ② (`sources.py`). |
| The loop with a work record and STOP conditions (`progress_objective.py`, `application.py`) | `precedents.run_type()`: retrieval → reflection → at most one rewrite of the query, suggested by the reflection. STOP conditions (`precedents.STOP_WORDS`): AI STOP (every product placed, or no further search suggested), code STOP (the rewrite found no new paragraphs), hard STOP (two attempts). Every attempt (queries, paragraphs, why it stopped) is recorded and saved in the progress file. Unlike Lab 2, no separate AI call judges whether the objective is met: code applies the STOP conditions to the reflection's answer. |
| Report generation (.docx) | The Word document (`export.py`). |
| Pause for user input and resume (`home.py`) | Human checkpoints: the lawyer reviews and edits the activities (step ②) and sets a view on every label (step ③) before the next step; "Save progress" and "Open saved progress" continue a screen later. |
| Showing what the system does, so that a lawyer can verify it (`home.py`) | Progress cards per step; source marks (✔ ≈ ○ ⚠) next to every fact; the Commission's paragraphs on hover; "Why?" on every row; the progress file as audit log. |

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # do NOT overwrite requirements.txt with `pip freeze`
streamlit run app.py
```

Without any settings the app runs as submitted: the key is entered in the sidebar module. For development, a `.env`
file (never committed; it is in `.gitignore`) or the Secrets on Streamlit Cloud (TOML: `KEY = "value"`) can hold:

| Setting | Effect |
|---|---|
| `DEV_MODE=1` with `APP_PASSWORD` and `OPENAI_API_KEY` | development: an app password instead of the user's key, the developer's key, cost counter, development tools |
| `MODEL_PROFILE=dev` or `final` | the models per step (`ai_client.py`); default: `dev` with DEV_MODE on, `final` otherwise |
| `USE_CACHE=1` | development only: reuse AI answers already paid for |
| `CHECK_SOURCES=0` | skip opening the cited pages (default 1: every page is opened and checked) |
| `SECOND_SEARCH=0` | one web search per company instead of two |
| `MAX_PARALLEL` | AI requests at once (default 16) |
| `MODEL_FALLBACK` | a model to use if a model of the profile is not available |
| `WEB_SEARCH_FEE` | USD per web search, for the cost shown (default 0.01) |

After a push that changes any file other than `app.py`, reboot the app on Streamlit Cloud (Manage app → ⋮ → Reboot app).

## Files

| File | Role |
|---|---|
| `app.py` | the interface (Streamlit): steps ① to ⑤, the sidebar (save and open progress, legend, Commission decisions, run summary, API key) |
| `api_key.py` | the course's API Credentials sidebar module (github.com/stoneman-mls/openai_credentials), run on every rerun, with a password field and the key never shown on the page |
| `ai_client.py` | the one gate for every AI call: models per step, retries, rate limits, call log and cost |
| `activity_mapping.py` | steps ① and ②: confidentiality guard, two web searches and one extraction per company, existing relationships |
| `sources.py` | opens every cited page or PDF and checks the quoted passages; removes dead links |
| `comparison.py` | step ③: anonymisation, embeddings, one anonymised pair per AI call |
| `rules.py` | the sector-neutral rules in plain Python (answer lists, name removal, decision rule) |
| `schemas.py` | the AI instructions and the fixed answer forms |
| `precedents.py` | step ④: one search per target activity (types of product, hybrid retrieval, reflection, at most one rewrite), the citation and item checks |
| `export.py` | the Word document (python-docx); the progress copy with the screen's data inside, and reading it back |
| `examples.py` | the inputs of the example buttons, including the two typed descriptions of TC2 and TC3 |
| `ingest.py`, `build_corpus.py`, `build_index.py`, `retrieval.py`, `corpus/` | the decision corpus: `corpus/paragraphs.json` (the 265 paragraphs with footnotes), `corpus/chroma/` (the ChromaDB index with the 266 chunks and their embeddings, used by step ④), `corpus/chunks.json` (the same chunks, readable, without vectors) and `corpus/corpus_report.md`. The decision PDFs that `build_corpus.py` reads (`corpus_src/`) are not in the repository; `build_corpus.py` lists where to download them |
| `retrieval_check.py`, `no_rag_check.py`, `test_results/` | development checks of the retrieval (with and without context headers, query forms) and of the model without the corpus; `test_results/` holds the reports of the retrieval checks (`no_rag_check.py` writes its report there when it is run); not part of the app |