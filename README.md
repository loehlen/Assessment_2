# EU Overlap Screen

**A preliminary European Union merger control overlap screen** (LAWS90286 · Assignment 2)

Deployed app: https://eu-merger-overlap-screen.streamlit.app/

Before almost every merger or acquisition, someone on the deal team has to check whether the target and the acquirer (for a private equity fund, each of its portfolio companies) are competitors, or supplier and customer. That means analysing what each company does and whether those activities fall in the same market, where the European Commission's earlier market definitions can be decisive. The app researches every company in public sources, compares every activity of the target with every activity of each portfolio company, looks up how the Commission defined the markets, and hands the lawyer a summary and a Word document.

It is a preliminary screen, not a legal conclusion: hard cases need judgment, and that judgment stays with the lawyer. Product markets only: geography and market shares are not assessed.

---

## Why this tool exists

Once two parties are competitors, or supplier and customer, sensitive information may only be exchanged through a clean team, documents must be redacted, and the overlaps decide how much the Commission needs to see. As a legal trainee in a competition law team I prepared many of these screens. The task is time-consuming and repetitive: reading often confusing corporate websites, sorting each company's activities, comparing them pair by pair and finding the Commission's market definitions, all multiplied by every portfolio company.

| | By hand | With the app |
|---|---|---|
| Research, comparison, market definitions | about 5–8 hours per screen, depending on the companies and the information available (my experience) | a few minutes of processing (TC1: about 4–5 minutes) |
| The lawyer's own work | all of it | checking and deciding: about an hour if thorough |
| Cost | trainee hours | about USD 0.50–1 in API fees per screen |
| Same care for the fifth company as for the first | varies with time pressure | yes, the same steps for every company and every pair |

## How it works

| Step | What the app does |
|---|---|
| ① Companies | the target and up to five portfolio companies, each researched by web search, by the lawyer's own description, or both |
| ② Activities | two web searches (for a company researched on the web) and one extraction per company, each company in its own calls; the app opens every cited page and checks every quotation |
| ③ Preliminary assessment | compares every target activity with every portfolio activity, one anonymised pair per AI call, with the legal conditions applied in code |
| ④ Market definitions | searches a database of Commission decisions (RAG with a reflection loop), quotes the Commission and checks every quotation word for word |
| ⑤ Summary | one page with the result per portfolio company, and the Word document |

## Reading the results

- **Horizontal**: the two companies offer products that may compete, i.e. may fall in the same market.
- **Vertical**: one company's product may be an input for the other, or be resold by it (supplier and customer).
- **Level of trade**: the stage at which a company sells, e.g. manufacturing an input, manufacturing a finished product, or retail. A Commission market only counts for a company at its own level of trade (Market Definition Notice 2024, para 14).

**Step ③** labels each pair *potential horizontal* (red) or *potential vertical* (yellow), tags labels it considers less likely (e.g. across levels of trade), and marks pairs the public sources cannot settle *Unclear: please check*. With **Your view**, the lawyer can set any label to *Likely*, *Unlikely*, *Dismiss* or *Ask the company* (which becomes an Open Point in the summary and the Word document).

**Step ④** gives each label one of these results:

| Result | Meaning |
|---|---|
| **Confirmed** | both sides' products fall in the same market the Commission defined, on the decision's own terms |
| **Possible** | both sides' products may fall in the same market depending on the product format, or the Commission's market is not an exact match for one side: to be checked |
| **Not excluded** | both sides' products fall in a market whose definition the Commission left open (or the paragraphs found state no conclusion), so the overlap cannot be excluded |
| **Not supported** | the Commission puts the products in separate markets |
| **No precedent** | no decision in the database covers the product at the company's level of trade. This does not mean that none exists: the lawyer can add one (TC3) |
| **Markets defined** · **One side defined** | for a vertical label: the decisions name a market for both sides' products, or for one side only |

---

## Designed around the lawyer

### The tool proposes, the lawyer decides

- **Every decision is the lawyer's, and it is recorded.** Activities can be corrected, added or deleted in step ②. "Your view" sits on every label and "Edit" on every row, so a lawyer who thinks a vertical link is really horizontal can add that label and dismiss the tool's. The summary and the Word document follow the lawyer's choices, never the other way round.
- **The Word document is a work product, not an AI report.** It is editable, set in Times New Roman like a final work product, and its main part shows only the lawyer's final choices. How the tool prepared them, including what the AI did, is in an Annex.
- **Gaps are results.** "Unclear: please check", "No precedent" and "Ask the company" are shown openly. The app never forces a decision onto a product it does not fit.
- **Junior prepares, senior reads.** Steps ①–④ are where the work is done and checked. Step ⑤ and page 1 of the Word document are short enough for a supervising lawyer to read on their own, with every line traceable to the step that found it.

### Generous on purpose, quick to dismiss

A missed overlap costs far more than a false one (the information exchange, the clean team, the filing). So the screen compares every pair and keeps doubtful links, but makes them quick to deal with: less likely labels are tagged and their details folded, a pair is dismissed in one click, and companies with no overlap can still be opened with the reasons. The summary is the main result and justifies the generous earlier steps, because the lawyer can check and adjust every one of them.

### Validation: every point can be checked

- **Source marks as levels of trust:** ✔ quotation found word for word on the page · ≈ probably right · ○ not checked · ⚠ check before relying on it, so the lawyer sees at a glance where a double-check is worth it. The app opens every cited page itself: dead pages are removed as sources, an activity left without one is flagged "⚠ no available source: verify, or ask the company", and pages that refuse automated visitors are marked ○.
- **The Commission is quoted, not paraphrased.** Every sentence attributed to a decision is checked word for word, and a paragraph only counts if the search actually returned it, so the AI cannot cite a decision from memory. A label that no verified passage supports reads "not stated in these paragraphs".
- **Claim only what the law supports.** "Confirmed" requires an exact match on the decision's own terms, and the app's rules of thumb cite the paragraph they rest on. "Affected market" is never used, because it depends on market shares, which the tool does not assess.
- **Inspectable evidence.** The decision reader opens each decision inside the app, with the paragraphs the screen used highlighted, next to the official PDF.

### Confidentiality by design

A planned deal is usually highly confidential, especially if a listed company is involved, so lawyers are usually not allowed to describe it to an AI. Therefore:

- **No prompt the app builds ever puts two companies of the screen, or the planned deal, together.** Each company is researched in its own call. The comparison sees only anonymised descriptions, one pair at a time, and the names are put back in code.
- **Typed text is checked before it is sent.** If it names another company of the screen, the app shows a warning. Sending it anyway is the lawyer's recorded decision (TC2).
- **An existing relationship between two companies**, a strong indicator of an overlap or vertical link, is found by the code in each company's separate research, never by asking the AI about both (TC2).
- **The app stores nothing.** "Save progress" downloads everything needed to resume the screen to the lawyer's own computer. The clean Word download carries none of it.

### Reliability: the code runs the process, the AI answers narrow questions

- **A fixed pipeline.** The code sets the order of the steps, builds every prompt and decides every result; the AI never chooses the next step. Each call answers one small question in a fixed form (Structured Outputs), so the code can check it and act on it.
- **One pair per call.** This serves both confidentiality and reliability, since the AI makes fewer mistakes when it only compares two activities. The summary groups the results for a quick overview.
- **Rules that hold in every sector live in code; sector knowledge does not.** There is no product list or relatedness table in the code, which is why the same app works for different sectors (TC3). Legal definitions are built into the answer forms, e.g. levels of trade defined by the buyer's use (Vertical Guidelines para 287).
- **An error never removes anything.** A failed or blocked call never screens a pair out, and a failed search is shown as failed, never as "No precedent".

### A calm screen, with more on demand

The task involves a lot of information. A lawyer under time pressure can work with the conclusion, while every detail stays one hover or click away. Hovering shows the quotation behind each source mark, the Commission's paragraph behind each reference such as [M.5644 (24)], and every product of an activity ("+6 more"). The guide box at the start of steps ②–④ can be folded; "Why?" (the reasoning on every row), the market table, each company's profile and sources, and the companies without an overlap are folded, never hidden.

---

## How to run

1. Open the deployed app, enter your own OpenAI API key on the first screen and click **Update API Key** (the course's API Credentials module, `ui/api_key.py`). The key is only used for your session and is not stored. From step ① on, it can be changed under **API Key Input** at the end of the sidebar.
2. Click **Start now**.
3. In step ①, click the test case's button under **Try an Example**, which fills in the editable fields, or type in the inputs below.
4. Work through the steps. Steps ②–④ each open with a short guide box (how the step works, how to read it, its limits), which you can fold.

A screen costs about USD 0.50–1 on your key. TC1 takes about 4–5 minutes of processing; TC2 makes the fewest AI calls and TC3 the most.

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

The companies are real, but the portfolios are hypothetical and no real transaction is implied.

---

## The three test cases

Each test case covers a situation the others do not. Together they show both kinds of relationship and a company with none; a Commission precedent for both sides, for one side only, and for neither until the lawyer adds one; and all three ways of researching a company.

| | TC1 · Lindt & Sprüngli | TC2 · Planet A Foods | TC3 · Brillux |
|---|---|---|---|
| **Why chosen** | the standard case: well-documented companies in markets the Commission has defined | the hard case: a new product (a cocoa-free alternative to chocolate) and a client's own description | another sector, with no decision in the built-in database |
| **Commission precedent** | for both sides | for one side only | none, until the lawyer adds M.4779 |
| **Research** | web search | web search; web search plus the lawyer's description; the lawyer's description only | web search |
| **What you do** | downgrade or dismiss a label | confirm a confidentiality warning; mark a label "Ask the company" | upload a Commission decision |
| **What it illustrates** | the full pipeline, checked sources and verified Commission quotations | the lawyer's own knowledge in the research, the confidentiality guard, and honest gaps instead of forced answers | that the app holds no sector knowledge, and that a decision added in a minute turns "No precedent" into the Commission's own market |

FRoSTA (frozen food) is the control in TC1 and TC2: it has no real overlap with either target. Depending on the run, the app still proposes none to a few generic vertical links (chocolate ingredients or fats as an input for frozen food), which the lawyer is expected to dismiss.

### What to expect from any run

- **The core results are found reliably.** The overlaps and vertical relationships listed under *Core results* appear across runs.
- **The activity split varies slightly.** Web search and AI answers vary, so a company may be split into slightly different activities from run to run, and the wording differs.
- **The app finds more than the core results, on purpose.** Because a missed overlap costs far more than a false one, the screen also keeps doubtful pairs, many tagged less likely. These are not errors but are left for the lawyer to check and dismiss. In the final test runs a screen showed about 15–30 labels (TC3 about 17, TC2 about 25, TC1 about 30), most of them *No precedent*, *One side defined* or less likely, against the three or four core results per test case below. Step ⑤ shows the result once the lawyer has dismissed what does not hold.

### TC1 · Lindt & Sprüngli: the Commission has defined the markets

**Why this case:** the baseline. Well-documented companies and defined chocolate markets show the whole pipeline working as intended.

**Input:** every company by web search.

**Core results (found reliably):**

- **Ritter Sport: horizontal overlap in chocolate confectionery.** In step ④ the Commission's separate markets for countlines (single-portion bars), tablets and pralines (M.5644 Kraft Foods / Cadbury) give *Confirmed* where both companies have products in the same one (e.g. pralines) and *Possible* where it depends on the product format (bars: countlines or tablets); chocolate confectionery as a whole was left open.
- **Ritter Sport: vertical links through the shops, both ways.** Ritter Sport's own shops could resell Lindt's chocolate, and Lindt's own shops could resell Ritter Sport's (*One side defined*). Both companies also run their own shops, which gives a horizontal label at retail level. M.5644 only defines manufacturers' markets, so the shops get "No precedent" for retail. The app names the market their products belong to, but does not treat it as the shops' own, because a market only counts for a company at its own level of trade.
- **Barry Callebaut: vertical link.** Its cocoa products and industrial chocolate are inputs for Lindt, with the Commission's markets for industrial chocolate and semi-finished cocoa products (*Markets defined*; M.6872, M.7408, in some runs also M.7120).
- **Barry Callebaut: horizontal overlap in ingredients.** Lindt also sells ingredients to professional customers (Ghirardelli: cocoa powders, chocolate chips), which meet Barry Callebaut's cocoa powder and inclusions. The result varies between runs: *Confirmed* (cocoa powder), *Possible* (chips against inclusions, industrial chocolate "not an exact match") or *No precedent*.
- **FRoSTA: no real overlap** (in some runs one or two generic vertical links, see above).

**Also expect:** further pairs for you to dismiss, such as links with Barry Callebaut's chocolate training courses or Ritter Sport's chocolate workshops, and less likely labels such as Barry Callebaut's cocoa products as an input for Lindt's shops.

**Try this:** in step ③, set that less likely label to *Unlikely*: it is then shown in full and listed in the summary with your view. Set it to *Dismiss* instead, and it leaves the summary. A row whose labels are all dismissed also leaves the main part of the Word document, while the Annex still lists it among the pairs compared.

**Known limitations:** what a company does not publish (Lindt's travel retail or business-to-business sales) can be missing.

### TC2 · Planet A Foods: a new product, a precedent for one side only, three ways of researching

**Why this case:** the situation where an AI is most tempted to overclaim. Planet A Foods makes ChoViva, a cocoa-free alternative to chocolate, on which there is no Commission decision, and the app says so instead of forcing a chocolate decision onto it. The case also shows the three ways of researching side by side, and the confidentiality guard at work.

**Input:** target Planet A Foods by web search. FRoSTA by web search, Barry Callebaut by both (web search plus the lawyer's description of its ChoViva partnership and cocoa products), and Ritter Sport by the lawyer's description only, as a client would describe its own company. Both descriptions are filled in by the button (`logic/examples.py`).

**Required input (step ①):** Barry Callebaut's description names the target, so the app warns that the AI would see both names in one call. Tick **Send anyway** (the lawyer's decision, recorded in the progress file), then click **Find activities**.

**Core results (found reliably):**

- **Barry Callebaut: the existing relationship** (the ChoViva partnership), found by the code in each company's separate research, and **a vertical link**, since Barry Callebaut distributes ChoViva to food manufacturers.
- **Barry Callebaut: horizontal overlap with its own cocoa-free alternatives.** Barry Callebaut, ChoViva's distributor, also offers non-cocoa alternatives of its own: ChoViva against them is *Possible* (Chocolate compound, "not an exact match"). This is the relationship a lawyer should look at first, and why the existing relationship matters.
- **Barry Callebaut: horizontal overlap** between its cocoa butter and cocoa powder and Planet A Foods' cocoa-butter alternative and cocoa powder replacer. The Commission has defined markets for Barry Callebaut's products (compound chocolate, cocoa butter, cocoa powder), but they fit Planet A Foods' new products only as "not an exact match". The result is therefore at most *Possible*, and for the powder replacer sometimes *Not supported*, with the product named as having no precedent.
- **Ritter Sport: vertical link**, every fact sourced to "your description". ChoViva, the cocoa powder replacer and the cocoa-butter alternative are possible inputs for Ritter Sport's chocolate bars, with Countlines and Tablets for Ritter Sport and Planet A Foods' products only as "not an exact match". The CacaoVida drinks do not meet.
- **FRoSTA: no real overlap** (depending on the run, none to five generic vertical links, see above).

**Also expect:** Planet A Foods split into two to four activities depending on the run; further horizontal labels with Barry Callebaut that read *No precedent* (e.g. ChoViva against cocoa ingredients, Planet A Foods' specialty fats against cocoa butter), and less likely ones across levels of trade; Planet A Foods' ingredients and fats as an input for frozen food, kept for you to dismiss. No horizontal overlap is expected with Ritter Sport. If a run proposes one between ChoViva and the chocolate bars, whether a cocoa-free alternative competes with chocolate is exactly the question the app leaves to the lawyer.

**Try this:** in step ③, set a label the public sources cannot settle to *Ask the company* and add a note, for example Planet A Foods' cocoa-butter alternative against Barry Callebaut's cocoa butter (the product is still in development and its customers are not stated). It then appears under Open Points in step ⑤ and in the Word document.

**Known limitations:** in some runs, the way one product is described influences how another is classified, for example a second product placed at the same level of trade as the first without its own source saying so. "Why?" and the hover show what each classification rests on, so this is quick to spot. A company described only by the lawyer has no web sources: the app can check that each fact comes from the lawyer's text, but not whether the text itself is right.

### TC3 · Brillux: another sector, and a decision the lawyer adds

**Why this case:** proof that the app is not built around chocolate. The same code screens building materials, and since the database holds no decision of this sector, the lawyer adds one, as in practice. The market table then also gives the lawyer the Commission's own terms ("decorative coatings", "RMI products for the home") to search a legal database.

**Input:** target Brillux (paints, facade insulation systems, industrial coatings); portfolio Hornbach (DIY stores and a builders' merchant), Sto (facade systems and coatings) and Henkel (adhesives); every company by web search.

**Test file:** `test_files/M4779_Akzo_Nobel_ICI.pdf`, the Commission's decision in M.4779 Akzo Nobel / ICI (2007) as published.

**Required input (step ③ or ④):** first click **Find Commission market definitions** without a decision. Every row reads *No precedent*, with one warning that no decision in the database fits, which does not mean that none exists. Then open **Add a Commission Decision or Extract** under the table and upload the PDF. The app reads the case number, title and date and proposes the paragraphs on market definition (11–19, 42–49). Click **Add M.4779 to this screen**, then **Update the market definitions**.

**Core results (found reliably):**

- **Sto: horizontal overlap in decorative paints**, *Confirmed* after the upload for exterior and interior paints: Decorative coatings (M.4779 (11)–(15)), each sentence marked "added by you". The facade insulation systems are also horizontal: *No precedent*, or *Possible* where the row compares facade paints with Sto's facade finishes (Decorative coatings, "not an exact match"). Further horizontal labels with *No precedent*: floor coatings, project consulting and training. Brillux's facade paints are also a possible input for Sto's facade finishes (vertical).
- **Hornbach: vertical link**, since Hornbach resells paints. Its DIY stores get *One side defined*: Brillux's side in Decorative coatings and, for woodstains, the woodcare segment, which the Commission left open ((15)); "no precedent" for Hornbach's retail, with the market its products fall in named at the manufacturers' level. Paints against Hornbach's DIY range also give two less likely horizontal labels (manufacturing v retail), which the summary names separately ("only less likely ones with Hornbach").
- **Henkel: horizontal overlap** between the two companies' industrial coatings, *No precedent* (M.4779 covers decorative coatings only).

**Also expect:** training against Henkel's training courses; adhesives against Brillux's adhesives where the search finds them; Hornbach's builders' merchant as a reseller of Brillux's tools; side lines such as Brillux's Academy guesthouse or Hornbach's management of its retail properties can bring theoretical vertical links (mark them "not relevant" in step ②). The distribution market of M.4779 (43)–(45) is named for the builders' merchant only on some of its rows, so it is not a core result.

**Known limitations:** Henkel's facade systems (Ceresit), and with them a further overlap, were found in only one of four runs. Whether a store chain is classed as retail decides between a resale link and a horizontal label, so it is worth a look in step ②. Quotations are checked against the uploaded text, not the official version. Only Commission merger decisions with a text layer can be added (for a scanned PDF, paste the text instead), and the proposed paragraphs follow the decision's headings and the Commission's usual wording.

### More to try (not one of the three test cases)

**Koa (cocoa fruit products):** click **More · Koa** under Try an Example. With no precedent at all, step ④ shows *No precedent* and leaves the market to the lawyer under the Market Definition Notice, rather than forcing a chocolate decision onto cocoa fruit.

---

## AI techniques used

A run makes from about 100 (TC1, TC2) to about 200–350 (TC3) AI calls: two web searches and one extraction per company, one comparison per pair of activities, and in step ④ one call that sorts the products into types and one reflection per type and attempt. Embedding requests are not counted.

| Class technique | In this app |
|---|---|
| Lab 1 · problem decomposition, fixed questions, one call per element | five steps, fixed questions per activity (level of trade, direct customers, end users) and per pair (product relation, vertical links), one call per anonymised pair (`logic/comparison.py`) |
| Lab 1 · constrained answers and if/then logic | Structured Outputs with fixed answer lists (`logic/schemas.py`). `rules.decide()` combines the AI's answer with checks in code (reseller, own use, input and resale signals); also the confidentiality guard and which rows step ④ looks up. Unlike Lab 1, there is no stop at the first negative answer, because a screen must compare every pair |
| Lab 2 · ChromaDB, chunking with metadata | text-embedding-3-large, one chunk per numbered paragraph with a context header (decision, section) and its footnotes, each decision tagged with the levels of trade of its markets (`logic/ingest.py`, `build_corpus.py`) |
| Lab 2 · retrieval beyond vector search | hybrid search: vector search plus BM25, combined by reciprocal rank fusion, with a level-of-trade filter (`logic/retrieval.py`); retrieval checks in `test_results/` |
| Lab 2 · loop with reflection and STOP conditions | `precedents.run_type()`: retrieval → reflection → at most one rewritten query. AI STOP, code STOP (nothing new found), hard STOP (two attempts); every attempt is recorded |
| Lab 2 · grounding | in code: a cited paragraph only counts if it was retrieved, and every quotation is checked word for word; the same for company websites (`logic/sources.py`) |
| Lab 2 · pause for the user, report | human checkpoints in steps ② and ③, "Save progress" and "Open saved progress", the Word document (`logic/export.py`) |

---

## Where to find what

`app.py` is the entry point. Each code folder (`steps/`, `ui/`, `logic/`, `tools/`) has a short README listing its files; `corpus/corpus_report.md` describes the decision database. `static/` holds the fonts and the official PDFs of the decisions, `test_files/` the decision added in TC3, and `test_results/` the retrieval checks. The official PDFs in `static/` are © European Union (Decision 2011/833/EU).