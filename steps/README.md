# EU Overlap Screen

**A first-pass EU merger control overlap screen, built the way a competition lawyer actually does it, and built so
that the lawyer stays in charge.** (LAWS90286 · Assignment 2)

**Deployed app:** [ADD THE STREAMLIT URL]

Before almost every acquisition, someone on the deal team has to answer one question: *where does the target meet
the businesses the buyer already owns?* For a private equity fund these are its portfolio companies; for a company
buying another, the buyer itself (one row is enough). The app researches every company on public sources, compares
every activity of the target with every activity of each portfolio company, looks up how the European Commission
defined the markets in its decisions, and hands the lawyer a summary and a Word document to work with.

It is a working document for a lawyer to check, not a legal conclusion. Product markets only: geography and market
shares are not assessed.

---

## Why this tool exists

As a trainee in a competition law team I prepared many of these screens. The work is necessary: once two parties are
competitors, or supplier and customer, sensitive information may only be exchanged through a clean team, documents
must be redacted, and the overlaps decide how much the Commission needs to see. It is also slow: reading through
confusing corporate websites, sorting each company's activities and comparing them pair by pair, then finding the
Commission's market definitions, all multiplied by every portfolio company.

| | By hand | With the app |
|---|---|---|
| Research, comparison, market definitions | about 6–8 hours per screen (my experience) | a few minutes of processing (TC1: about 4–5) |
| The lawyer's own work | all of it | checking and deciding: about an hour (my estimate) |
| Cost | trainee hours | about USD 0.50–1 in API fees per screen |
| Same care for the fifth company as for the first | varies with time pressure | yes: the same steps for every company and every pair |

The saving does not come from skipping the lawyer's judgment. It comes from doing the searching, sorting and
looking-up for them, and presenting every result so that it can be checked in seconds.

## How it works

| Step | What the app does | What the lawyer does |
|---|---|---|
| ① Companies | | enters the target and up to five portfolio companies; per company: web search, own description, or both |
| ② Activities | two web searches and one extraction per company, each company in its own calls; opens every cited page and checks every quotation | corrects, adds or deletes activities, or marks them "not relevant to this deal" |
| ③ Preliminary assessment | compares every target activity with every portfolio activity, one anonymised pair per AI call; legal conditions applied in code | sets a view on each label: Likely · Unlikely · Ask the company · Dismiss; edits wording or reclassifies |
| ④ Market definitions | searches a database of Commission decisions (RAG with a reflection loop); quotes the Commission and checks every quotation word for word | reads the Commission's own sentences on hover; can add a decision the database does not hold |
| ⑤ Summary | one page with the result per portfolio company, and the Word document | reads, adjusts, downloads |

---

## Designed around the lawyer

Every feature was judged by one question: *does it save the lawyer time, or make checking faster?*

### The tool assists; the lawyer decides

- **The tool proposes, with its basis; the lawyer decides, and the decision is recorded.** "Your view" sits on every
  label, "Edit" on every row; a lawyer who thinks a vertical link is really horizontal adds the label and dismisses
  the tool's one. The summary and the Word document follow the lawyer's choices, never the other way round.
- **The Word document is the lawyer's work product, not an AI report.** Times New Roman, editable as usual, only the
  lawyer's final choices in the main part; how the tool prepared them, including what the AI did, is in an Annex, so
  the AI's part stays on record without cluttering the work product.
- **Gaps are results.** "Unclear: please check", "No precedent" and "Ask the company" are answers, not failures. A
  label set to "Ask the company" becomes an Open Point in the summary and the Word document. The app never forces a
  decision onto a product it does not fit.
- **Junior prepares, senior reads.** Steps ①–④ are where the work is done and checked; step ⑤ and page 1 of the Word
  document are short enough for a supervising lawyer to read on their own, with every line traceable to the step that
  found it.

### Generous on purpose, quick to dismiss

A missed overlap costs far more than a false one (the information exchange, the clean team, the filing). So the screen
compares *every* pair and keeps doubtful links, but makes them cheap to deal with: less likely labels (for example
across levels of trade) are tagged and their details folded, a dismissal is one click, and companies with no overlap
at all stay openable with the reasons rather than disappearing. Nothing is deleted; it is only folded.

### Validation: every point can be checked

- **Source marks as levels of trust:** ✔ quotation found word for word on the page · ≈ probably right · ○ not checked
  · ⚠ check before relying on it. The lawyer opens only the sources that need it. The app opens every cited page
  itself; dead links are removed rather than relied on.
- **The Commission is quoted, not paraphrased.** Every sentence the app attributes to a decision is checked word for
  word against the decision; a paragraph counts only if the search actually returned it, so the AI cannot cite a
  decision from memory. A label no verified passage supports reads "not stated in these paragraphs".
- **Claim only what the law supports.** "Confirmed" only for an exact match on the decision's own terms; "not an
  exact match" instead of "by analogy" (a term with a specific meaning in some legal systems); a market counts for a
  company only at its own level of trade (Market Definition Notice (14)); the app's rules of thumb cite the paragraph
  they rest on. "Affected market" is never used, because it depends on market shares the tool does not assess.
- **Inspectable evidence.** The decision reader opens each decision inside the app, with the paragraphs the screen
  used highlighted, next to the official PDF. The audit log records every AI call with what it was sent and returned.

### Confidentiality by design

Taken from practice: you never ask anyone "are A and B competitors?".

- **No AI call ever sees two company names together, or the planned deal.** Each company is researched in its own
  call; the comparison sees anonymised descriptions, one pair at a time; names are re-attached in code.
- **A guard in code checks every prompt before it is sent.** Text the lawyer types that names another company of the
  screen triggers a warning; sending it anyway is the lawyer's recorded decision.
- **An existing relationship** between two companies (TC2) is found by the code in each company's separate research,
  never by asking the AI about both.
- **The app stores nothing.** "Save progress" downloads a file to the lawyer's own computer; the clean Word download
  carries none of the hidden data.

### Reliability: the code runs the process, the AI answers narrow questions

- **A fixed pipeline.** The code sets the order of the steps, builds every prompt and decides every result; the AI
  never chooses the next step. Each AI call answers one small question in a fixed form (Structured Outputs), so the
  code can check and branch on it.
- **One pair per call.** It makes the results repetitive (the summary groups them), but the AI makes fewer mistakes
  comparing two activities than twenty, and no call sees more than it needs.
- **Rules that hold in every sector live in code; sector knowledge does not.** There is no product list or
  relatedness table in the code, which is why the same app works for paints (TC3). Legal definitions are built into
  the answer forms (for example levels of trade defined by the buyer's use, Vertical Guidelines para 287).
- **An error never removes anything.** A failed or blocked call never screens a pair out; a failed search is shown as
  failed, never as "No precedent".

### A calm screen, with more on demand

Many people who read a screen are not competition lawyers (the deal team, the client), and a lawyer under time
pressure does not want to scroll either. So the screen shows the conclusion, and the detail is one gesture away:

- **Hover** for the quotation behind each source mark, the Commission's paragraph behind every reference such as
  [M.5644 (24)], the Notice's paragraph behind a rule, every product of an activity ("+6 more"), and the full sentence
  behind a shortened one.
- **Folded, never hidden:** "How this step works" on every step, "Why?" with the reasoning on every row, the market
  table under each row, the profile and sources of each company, the companies without an overlap.
- **Colour carries meaning only:** red for horizontal, yellow for vertical; one calm ink-and-ivory theme; the landing
  page explains why overlaps matter before asking for any input.

---

## The three test cases

Enter your own OpenAI API key in the sidebar under **API Key Input** and click **Update API Key** (the course's API
Credentials module, `ui/api_key.py`; the key is used only for your session and is not stored). On the start page
click **Start now**. In step ① either type the inputs below, or click the test case's button under **Try an
Example**, which fills in the same editable fields.

| Company | Website | Other names | Used in |
|---|---|---|---|
| Lindt & Sprüngli | lindt-spruengli.com | Lindt, Sprüngli, Lindt & Sprüngli AG | TC1 target |
| Planet A Foods | planet-a-foods.com | Planet A, ChoViva | TC2 target |
| Ritter Sport | ritter-sport.com | Ritter, Alfred Ritter GmbH & Co. KG | portfolio, TC1 and TC2 |
| Barry Callebaut | barry-callebaut.com | Callebaut, Barry Callebaut AG | portfolio, TC1 and TC2 |
| FRoSTA | frosta-ag.com | FRoSTA AG | portfolio, TC1 and TC2 |
| Brillux | brillux.com | Brillux GmbH & Co. KG | TC3 target |
| Hornbach | hornbach-holding.de | HORNBACH Holding AG & Co. KGaA, Hornbach Baumarkt | portfolio, TC3 |
| Sto | sto.com | Sto SE & Co. KGaA | portfolio, TC3 |
| Henkel | henkel.com | Henkel AG & Co. KGaA | portfolio, TC3 |

The companies are real; the portfolios are hypothetical and no real transaction is implied. FRoSTA (frozen food) is
the control in TC1 and TC2: it has no real overlap with either target.

**In every test case:** ① **Find activities** → ② check the activities, **Compare activities** → ③ the preliminary
assessment, **Find Commission market definitions** → ④ the market definitions, **Go to the summary** → ⑤ the summary,
**Download the Word document**. Each test case names one input to try, so you can see the output follow the lawyer.

### TC1 · Lindt & Sprüngli: the Commission has defined the markets

- **Input:** every company by **web search**.
- **Shows:** the full pipeline on well-documented companies, with a precedent for both sides.
- **Expected:**
  - Ritter Sport: a **horizontal** overlap in chocolate confectionery; in step ④ the Commission's separate markets for
    countlines, tablets and pralines (M.5644 Kraft Foods / Cadbury), "Confirmed" where both sides have products in the
    same one. A **vertical** link from Lindt's chocolate to Ritter Sport's own shops (resale); M.5644 defines
    manufacturers' markets, so the shops get "no precedent for the retail …" and the markets their products fall in
    are named as such, not counted as the shops' own.
  - Barry Callebaut: a **vertical** link (cocoa products and industrial chocolate as inputs for Lindt), with the
    Commission's markets for industrial chocolate and semi-finished cocoa products (M.6872, M.7408; in some runs also
    M.7120).
  - FRoSTA: no real overlap.
- **Your input to try:** in step ③, set a label tagged *less likely* (for example Barry Callebaut's cocoa products as
  an input for Lindt's shops) to **Unlikely**: it is shown in full and listed in the summary with your view. Set it to
  **Dismiss** instead: it leaves the summary; a row whose labels are all dismissed also leaves the main part of the
  Word document, and the Annex still lists it among the pairs compared.
- **Performs well:** checked sources (✔), the overlap with Ritter Sport and the Commission's sentences, each verified
  word for word.
- **Does not:** generous by design, so some unlikely pairs are left for you to dismiss (for example links with a
  training service); the split into activities varies between runs; what a company does not publish (Lindt's travel
  retail or business-to-business sales) can be missing.

### TC2 · Planet A Foods: a new product, a precedent for only one side, three ways of researching

- **Input:** target Planet A Foods (ChoViva, a cocoa-free alternative to chocolate), researched on the web. The
  portfolio shows the three source modes side by side: **FRoSTA** by web search; **Barry Callebaut** by **both** (web
  search plus the lawyer's description of its ChoViva partnership and its cocoa products); **Ritter Sport** by **my
  description** only (the description a client would give of its own company; no web search). Both descriptions are
  filled in by the button (`logic/examples.py`).
- **Your input (required, step ①):** Barry Callebaut's description names the target, so the app shows a
  confidentiality warning: the AI would see both names in one call. Tick **Send anyway** (the lawyer's decision,
  recorded in the progress file), then **Find activities**.
- **Shows:** the lawyer adding what they know to the research; the confidentiality guard; an **existing
  relationship** found by the code in each company's separate research; a company described only by the lawyer (fast
  and cheap; its sources are marked "your description"); and how the app behaves where the Commission has defined
  only one side's market, or none.
- **Expected:**
  - Barry Callebaut: the existing relationship (ChoViva); a **vertical** link (Barry Callebaut distributes ChoViva to
    food manufacturers); its cocoa butter and cocoa powder against Planet A Foods' cocoa-butter alternative and cocoa
    powder replacer: **horizontal**. In step ④ the Commission has defined markets for Barry Callebaut's products
    (compound chocolate, cocoa butter, cocoa powder), which fit Planet A Foods' new products only as **"not an exact
    match"**: the result is at most **Possible**, and for the powder replacer sometimes **Not supported**, with the
    product named as having no precedent.
  - Ritter Sport (from the lawyer's description): ChoViva as a possible input for Ritter Sport's chocolate
    (**vertical**).
  - FRoSTA: no real overlap (fats as an input for frozen food may be kept for you to dismiss).
- **Your input to try:** in step ③, set a row the app could not settle (a **Not supported** or **Unclear: please
  check** row, for example the cocoa powder replacer or Planet A Foods' coffee, which is still in development) to
  **Ask the company** and add a note. It appears under **Open Points** in step ⑤ and in the Word document.
- **Performs well:** the partnership and the relationship shown with their sources; step ④ says which side has a
  precedent and which does not, instead of forcing a chocolate decision onto a new product.
- **Does not:** a new product has no precedent, so whether it competes with chocolate stays the lawyer's question;
  Planet A Foods splits into two to four activities between runs; in some runs one product's description colours the
  placement of another ("Why?" and the hover show what each placement rests on). A typed description has no web
  sources: the app can only check that each fact comes from the text the lawyer typed.

### TC3 · Brillux: another sector, and a decision the lawyer adds

- **Input:** target Brillux (paints, facade insulation systems, industrial coatings); portfolio Hornbach (DIY stores
  and a builders' merchant), Sto (facade systems and coatings) and Henkel (adhesives); every company by **web
  search**. Artefact: `test_files/M4779_Akzo_Nobel_ICI.pdf`, the Commission's decision in M.4779 Akzo Nobel / ICI
  (2007) as published.
- **Shows:** that the app contains no knowledge of one sector: the same code screens building materials. The
  built-in database holds no decision of this sector, so the lawyer adds one.
- **Your input (step ③ or ④):** first click **Find Commission market definitions** without a decision: every row reads
  **No precedent**, with one warning that no decision in the database fits, which does not mean that none exists. Then
  open **Add a Commission Decision or Extract** under the table, upload the PDF: the app reads the case number, title
  and date and proposes the paragraphs on market definition (**11–19, 42–49**). Click **Add M.4779 to this screen**,
  then **Update the market definitions**.
- **Expected:**
  - Sto: a **horizontal** overlap in decorative paints, **Confirmed: Decorative coatings** (M.4779 (11)–(15)), each
    sentence marked "added by you"; Brillux's woodstains in the woodcare segment (left open, (15)); the two facade
    insulation systems **horizontal** but **No precedent**, because M.4779 does not cover them.
  - Hornbach: a **vertical** link (Hornbach resells paints). Its DIY stores get "no precedent for the retail …", with
    the market their products fall in named at the manufacturers' level; its builders' merchant gets the
    distribution market of (43)–(45), left open by the Commission.
  - Henkel: industrial coatings against Brillux's industrial coatings (**horizontal**), and adhesives where the
    search finds Brillux's.
- **Performs well:** a decision added in a minute changes "No precedent" into the Commission's own market, with every
  quotation checked; the market table gives the lawyer the Commission's own terms ("decorative coatings", "RMI
  products for the home") to search further in a legal database.
- **Does not:** the web search varies most here: Henkel's facade systems (Ceresit), and with them a further overlap,
  were found in only one of four runs; side lines such as a training guesthouse can bring theoretical vertical links
  (mark them "not relevant" in step ②); whether a store chain is classed as retail decides between a resale link and
  a horizontal label, so it is worth a look in step ②. Quotations are checked against the uploaded text, not the
  official version.

### More to try (not one of the three test cases)

**More · Koa** (cocoa fruit products) is a case with no precedent at all: step ④ shows "No precedent" and leaves the
market to the lawyer under the Market Definition Notice rather than forcing a chocolate decision onto cocoa fruit.
`static/decisions/m7120_1451_2.pdf` (M.7120 Ecom / Armajaro) can be added in any screen: its coffee paragraphs
(42)–(51) were left out of the database on purpose, so it shows the app adding only what the database does not hold.

**Limits of adding a decision:** Commission merger decisions only ("M.1234"); a scanned PDF has no text (paste it
instead); the proposal follows the decision's headings and the Commission's usual wording, so a part that uses
neither is not proposed; where an added decision does not show a market's level of trade in a passage the code can
verify, that market is never an exact match ("Possible" at most).

---

## AI techniques used

A run makes from about 70 (TC2) to several hundred (TC3) AI calls: per company two web searches and one extraction;
one comparison per pair of activities; in step ④ one call that sorts the products into types and one reflection per
type and attempt. Embedding requests are counted separately; they are not AI answers.

| Class technique | In this app |
|---|---|
| **Lab 1** · problem decomposition, fixed questions, one call per element | five steps; per activity fixed questions (level of trade, direct customers, end users), per pair the product relation and vertical links; one call per anonymised pair (`logic/comparison.py`) |
| **Lab 1** · constrained answers and if/then logic | Structured Outputs with fixed answer lists (`logic/schemas.py`); `rules.decide()` combines the AI's answer with checks in code (reseller, own use, input and resale signals); the confidentiality guard; which rows step ④ looks up. Unlike Lab 1, no stop at the first negative answer: a screen must compare every pair |
| **Lab 2** · ChromaDB, chunking with metadata | `text-embedding-3-large`; one chunk per numbered paragraph with a context header (decision, section) and its footnotes; each decision tagged with the levels of trade of its markets (`logic/ingest.py`, `build_corpus.py`) |
| **Lab 2** · retrieval beyond vector search | hybrid: vector search plus BM25, combined by reciprocal rank fusion, with a level-of-trade filter (`logic/retrieval.py`); retrieval checks in `test_results/` |
| **Lab 2** · loop with reflection and STOP conditions | `precedents.run_type()`: retrieval → reflection → at most one rewritten query; AI STOP, code STOP (nothing new found), hard STOP (two attempts); every attempt recorded |
| **Lab 2** · grounding | in code: a cited paragraph counts only if retrieved; every quotation checked word for word; the same for company websites (`logic/sources.py`) |
| **Lab 2** · pause for the user, report | human checkpoints in steps ② and ③; "Save progress" / "Open saved progress"; the Word document (`logic/export.py`) |

---

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Adding a decision as a PDF uses `pdftotext` (`packages.txt` installs it on Streamlit Cloud; locally `sudo apt-get
install -y poppler-utils`; without it the app falls back to pypdf). Without settings the app runs as submitted. For
development, a `.env` file (in `.gitignore`) can set `DEV_MODE=1` with `APP_PASSWORD` and `OPENAI_API_KEY`, or
`MODEL_PROFILE`, `USE_CACHE`, `CHECK_SOURCES`, `SECOND_SEARCH`, `MAX_PARALLEL` (see `logic/ai_client.py`).

## Where to find what

```
app.py        entry point: page set-up, API key, which step to show
steps/        one file per screen (what the user sees and does)
ui/           shared building blocks: sidebar, theme, source marks, labels, decision reader, upload box
logic/        the workflow without the interface: AI calls, prompts and answer forms, rules, search, Word document
tools/        scripts that built and checked the decision database (not used by the running app)
corpus/       the decision database: paragraphs, ChromaDB index, report
static/       fonts and the official PDFs of the built-in decisions (© European Union, Decision 2011/833/EU)
test_files/   the decision to add in TC3
test_results/ reports of the retrieval checks
```

| Looking for … | File |
|---|---|
| the AI instructions and the fixed answer forms | `logic/schemas.py` |
| every AI call: models, retries, cost, call log | `logic/ai_client.py` |
| the if/then rules in code (levels of trade, resellers, own use, name removal) | `logic/rules.py` |
| company research, confidentiality guard, source check | `logic/activity_mapping.py`, `logic/sources.py` |
| the anonymised comparison | `logic/comparison.py`, `steps/step3_assessment.py` |
| the RAG loop and the quotation check | `logic/precedents.py`, `logic/retrieval.py` |
| adding a decision | `ui/upload_box.py`, `logic/uploads.py` |
| the examples behind the buttons | `logic/examples.py` |

Each folder has a short README listing its files.