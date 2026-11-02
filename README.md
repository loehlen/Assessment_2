# EU Overlap Screen

**A preliminary European Union merger control overlap screen** (LAWS90286 · Assignment 2)

Deployed app: https://eu-merger-overlap-screen.streamlit.app/

Before almost every merger or acquisition, the deal team has to check whether the target and the acquirer (for a private equity fund, each of its portfolio companies) are competitors, or supplier and customer. If they are, sensitive information may only be exchanged through a clean team, documents must be redacted, and the overlaps decide how much the Commission needs to see. As a legal trainee in a competition law team I prepared many of these screens. The work is time-consuming and repetitive. It requires reading confusing corporate websites, sorting each company's activities, comparing them pair by pair and finding the Commission's market definitions, all multiplied by every portfolio company.

The app does this groundwork. It researches every company in public sources, compares every activity of the target with every activity of each portfolio company, looks up how the Commission defined the markets, and hands the lawyer a summary and a Word document. It is a preliminary screen, not a legal conclusion. Hard cases need judgment, and that judgment stays with the lawyer. The app covers product markets only, not geography or market shares.

| | By hand | With the app |
|---|---|---|
| Research, comparison, market definitions | about 5–8 hours per screen, depending on the companies and the information available (my experience) | a few minutes of processing (TC1 about 4–5 minutes) |
| The lawyer's own work | all of it | checking and deciding, about an hour if thorough |
| Cost | trainee hours | about USD 0.50–1 in API fees per screen |
| Same care for the fifth company as for the first | varies with time pressure | yes, the same steps for every company and every pair |

## How it works

| Step | What the app does |
|---|---|
| ① Companies | the target and up to five portfolio companies, each researched by web search, by the lawyer's own description, or both |
| ② Activities | two web searches (for a company researched on the web) and one extraction per company, each company in its own calls. The app opens every cited page and checks every quotation |
| ③ Preliminary assessment | compares every target activity with every portfolio activity, one anonymised pair per AI call, with the legal conditions applied in code |
| ④ Market definitions | searches a database of Commission decisions (RAG with a reflection loop), quotes the Commission and checks every quotation word for word |
| ⑤ Summary | one page with the result per portfolio company, and the Word document |

## Reading the results

- **Horizontal**: the two companies offer products that may compete, so they may fall in the same market.
- **Vertical**: one company's product may be an input for the other, or be resold by it (supplier and customer).
- **Level of trade**: the stage at which a company sells, for example manufacturing an input, manufacturing a finished product, or retail. A Commission market only counts for a company at its own level of trade (Market Definition Notice 2024, para 14).

**Step ③** labels each pair *potential horizontal* (red) or *potential vertical* (yellow), tags labels it considers less likely (for example across levels of trade) and marks pairs the public sources cannot settle as *Unclear: please check*. With **Your view**, the lawyer sets any label to *Likely*, *Unlikely*, *Dismiss* or *Ask the company*, which becomes an Open Point in the summary and the Word document.

**Step ④** gives each label one of these results:

| Result | Meaning |
|---|---|
| **Confirmed** | both sides' products fall in the same market the Commission defined, on the decision's own terms |
| **Possible** | they may fall in the same market depending on the product format, the products are named too generally to place in one market ("only through a general term"), or the Commission's market is not an exact match for one side, so this needs checking |
| **Not excluded** | they fall in a market whose definition the Commission left open (or the paragraphs found state no conclusion), so the overlap cannot be excluded |
| **No precedent** | no decision in the database covers the product at the company's level of trade. This does not mean that none exists, and the lawyer can add one (TC3) |
| **Not supported** | the Commission puts the products in separate markets |
| **Markets defined** · **One side defined** | for a vertical label, the decisions name a market for both sides' products, or for one side only |

**Step ⑤** lists the labels per portfolio company, in the order entered in step ①, strongest support first: the lawyer's view (*Likely*, then no view, then *Unlikely*), then the Commission's result in the order of the table above. The order shows how strongly a label is supported, not how serious an overlap is. Dismissed labels are left out, and *Ask the company* labels appear as Open Points.

---

## Designed around the lawyer

### The tool proposes, the lawyer decides

- **Every decision is the lawyer's, and it is recorded.** Activities can be corrected, added or deleted in step ②, and "Your view" and "Edit" sit on every label and row. A lawyer who thinks a vertical link is really horizontal can add that label and dismiss the tool's. The summary and the Word document follow the lawyer's choices.
- **The Word document is a work product, not an AI report.** It is editable, set in Times New Roman, and its main part shows only the lawyer's final choices. How the tool prepared them, including what the AI did, is in an Annex.
- **Gaps are results.** "Unclear: please check", "No precedent" and "Ask the company" are shown openly, never forced into a decision.
- **Junior prepares, senior reads.** Steps ①–④ are where the work is done and checked. Step ⑤ and page 1 of the Word document are short enough for a supervising lawyer to read on their own, and every line traces back to the step that found it.

### Generous on purpose, quick to dismiss

A missed overlap costs far more than a false one, because of the information exchange, the clean team and the filing. So the screen keeps doubtful links but makes them quick to handle: less likely labels are tagged and folded, a pair is dismissed in one click, and companies with no overlap can still be opened with the reasons. The summary is the main result, and the lawyer can check and adjust every step behind it.

### Every point can be checked

- **Source marks show how far to trust a source.** ✔ means the quotation was found word for word on the page, ≈ probably right, ○ not checked, and ⚠ check before relying on it. The app opens every cited page itself, removes dead pages as sources (an activity left without one is flagged "⚠ no available source: verify, or ask the company") and marks pages that refuse automated visitors ○.
- **The Commission is quoted, not paraphrased.** Every quotation is checked word for word, and a paragraph only counts if the search actually returned it, so the AI cannot cite a decision from memory. A label no verified passage supports reads "not stated in these paragraphs".
- **The app claims only what the law supports.** "Confirmed" requires an exact match on the decision's own terms, rules of thumb cite the paragraph they rest on, and "affected market" is never used, because it depends on market shares.
- **The evidence can be inspected.** Each decision opens inside the app, with the paragraphs the screen used highlighted, next to the official PDF.

### Confidentiality by design

A planned deal is usually highly confidential, especially if a listed company is involved, so lawyers are usually not allowed to describe it to an AI.

- **No prompt the app builds puts two companies of the screen, or the planned deal, together.** Each company is researched in its own call, the comparison sees only anonymised descriptions one pair at a time, and the names are put back in code.
- **Typed text naming another company of the screen triggers a warning.** Sending it anyway is the lawyer's recorded decision (TC2).
- **An existing relationship between two companies**, a strong indicator of an overlap or vertical link, is found by code in each company's separate research, never by asking the AI about both (TC2).
- **The app stores nothing.** "Save progress" downloads what is needed to resume the screen to the lawyer's own computer. The clean Word download carries none of it.

### The code runs the process, the AI answers narrow questions

- **A fixed pipeline.** The code sets the order of the steps, builds every prompt and decides every result. Each AI call answers one small question in a fixed form (Structured Outputs), which the code checks and acts on.
- **One pair per call**, for confidentiality and reliability, since the AI makes fewer mistakes comparing only two activities. The summary then groups the results.
- **Rules that hold in every sector live in code, sector knowledge does not.** There is no product list or relatedness table, so the same app works for other sectors (TC3). Legal definitions are built into the answer forms, for example levels of trade defined by the buyer's use (Vertical Guidelines para 287).
- **An error never removes anything.** A failed or blocked call never screens a pair out, and a failed search is shown as failed, never as "No precedent".

### A calm screen, with more on demand

An overlap screen inherently involves a lot of information. The app lets a lawyer under time pressure work with the conclusion, while every detail stays one hover or click away. Hovering shows the quotation behind each source mark, the Commission's paragraph behind each reference such as [M.5644 (24)], and every product of an activity ("+6 more"). Guide boxes, "Why?" (the reasoning on every row), the market table, company profiles and sources, and companies without an overlap are folded, never hidden.

---

## How to run

1. Open the deployed app, enter your own OpenAI API key on the first screen and click **Update API Key** (the course's API Credentials module, `ui/api_key.py`). The key is only used for your session and is not stored. From step ① on, you can change it under **API Key Input** at the end of the sidebar.
2. Click **Start now**.
3. In step ①, click the test case's button under **Try an Example**, which fills in the editable fields, or type in your own inputs.
4. Work through the steps. Steps ②–④ each open with a foldable guide box on how the step works, how to read it and where its limits are.

A screen costs about USD 0.50–1 on your key. TC1 takes about 4–5 minutes of processing, and TC3 makes the most AI calls.

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

Each test case covers a situation the others do not. Together they show both kinds of relationship and a company with none, a Commission precedent for both sides, for one side only, and for neither until the lawyer adds one, and all three ways of researching a company. The portfolios were chosen to show how companies can overlap, including hard cases that need a lawyer's judgment, so each screen has more going on than a typical one. In a real fund, many portfolio companies have nothing to do with the target, and the app shows them as "None found", with the reasons one click away.

| | TC1 · Lindt & Sprüngli | TC2 · Planet A Foods | TC3 · Brillux |
|---|---|---|---|
| **Why chosen** | the standard case, with well-documented companies in markets the Commission has defined | the hard case, with a new product (a cocoa-free alternative to chocolate) and a client's own description | another sector, with no decision in the built-in database |
| **Commission precedent** | for both sides | for one side only | none, until the lawyer adds M.4779 |
| **Research** | web search | web search, web search plus the lawyer's description, and the lawyer's description only | web search |
| **What you do** | downgrade or dismiss a label | confirm a confidentiality warning and mark a label "Ask the company" | upload a Commission decision |
| **What it illustrates** | the full pipeline, checked sources and verified Commission quotations | the lawyer's own knowledge in the research, the confidentiality guard, and honest gaps instead of forced answers | that the app holds no sector knowledge, and that a decision added in a minute turns "No precedent" into the Commission's own market |
| **Limits it shows** | smaller lines can vary between runs | new products are left to the lawyer; typed descriptions are checked for source, not truth | the database does not cover every sector; uploads are checked against their own text |

FRoSTA (frozen food) is the control in TC1 and TC2, and no overlap is expected with either target. Some runs still propose a few generic vertical links (chocolate ingredients or fats as an input for frozen food), which the lawyer is expected to dismiss. Some show nothing at all.

### What to expect from any run

**Reliable at the core, slightly variable at the edges.** A company's main, well-documented activities are found in every run, and so is any overlap or vertical relationship they lead to. The research starts, as a lawyer's would, from each company's own website. It then widens to annual reports, brand and product pages, and what a first look easily misses, such as smaller brands, sales to other businesses, own shops and side lines, so it usually finds more than a lawyer under time pressure would. At the edges, though, results can differ between runs, because web search and AI answers are not identical each time. A page found in one run can be missed in the next, or a smaller product line can be described differently, which can change the result of a row. This is the trade-off of a preliminary screen, and why the lawyer still verifies: every activity is sourced and can be edited or added in step ②, and every label can be changed in step ③.

**Expected relationships** lists every overlap and vertical relationship a competition lawyer would expect, and says where one rests on a less prominent product line. Because the app compares activity by activity, one relationship can appear in several rows, with different wording or a different split into activities, and the result can vary within the range given. Step ④ classifies the products of each row separately, so the same product can be placed in a market on one row and in none on another. **Also on the screen** lists the extra labels by type. A screen typically shows about 15–30 labels, most of them *No precedent*, *One side defined* or less likely: not errors, but doubtful pairs kept for the lawyer to dismiss or further investigate. Until they are dismissed, they also count in the step ⑤ summary.

### TC1 · Lindt & Sprüngli

**Input:** every company is researched by web search.

**Expected relationships:**

- **Ritter Sport, horizontal overlap in chocolate confectionery** (*Possible*, in some runs *Confirmed*). M.5644 Kraft Foods / Cadbury divides chocolate confectionery into separate markets for countlines, tablets and pralines, so the lawyer has to check which of them the two companies share.
- **Ritter Sport, own chocolate shops.** Both companies run their own shops. This gives a horizontal overlap at retail level (*No precedent*, because M.5644 only defines manufacturers' markets) and vertical links both ways, since each company's shops could resell the other's chocolate (*One side defined*).
- **Barry Callebaut, vertical link.** Its cocoa products and industrial chocolate are inputs for Lindt's chocolate and for its professional ingredients (*Markets defined*, M.6872 and M.7408).
- **Barry Callebaut, horizontal overlap in ingredients.** Lindt also sells ingredients to professional customers (Ghirardelli chocolate chips and cocoa powder). This smaller line, presented mainly on Ghirardelli's own website, is an edge case. It is usually found as a line of its own. If not, the products sit in Lindt's chocolate line in step ②, and the lawyer can split them out with **Edit**. Accordingly, the result varies between runs (*Possible*, *Confirmed* or *No precedent*).
- **FRoSTA** (see above).

**Also on the screen:** horizontal labels across levels of trade (Lindt's shops against Ritter Sport's chocolate, Lindt's chocolate against Barry Callebaut's ingredients), which step ④ marks *Not supported* or *No precedent*; side lines such as Ritter Sport's workshops and café, Barry Callebaut's training courses or its cocoa cell-culture research; Barry Callebaut's products as inputs for Lindt's shops; and generic links with FRoSTA (Lindt's sauces or chips for frozen meals).

**Try this:** In step ③, set a less likely label (for example Barry Callebaut's cocoa products as an input for Lindt's shops) to *Unlikely*. It is then shown in full and listed in the summary with your view. *Dismiss* instead removes it from the summary and the main part of the Word document, while the Annex still lists the pair.

### TC2 · Planet A Foods

**Why this case:** this is where an AI is most tempted to overclaim. No Commission decision covers ChoViva, a cocoa-free alternative to chocolate, so the app places Planet A Foods' products in the nearest markets only as "not an exact match": at most *Possible*, never *Confirmed*.

**Input:** Planet A Foods and FRoSTA are researched by web search, Barry Callebaut by web search plus the lawyer's description (its ChoViva partnership and distribution, and its cocoa products), and Ritter Sport only from the lawyer's description, as a client would describe its own company. The button fills in both descriptions (`logic/examples.py`). A company described only by the lawyer has no web sources: the app can check that each fact comes from the lawyer's text, but not whether the text itself is right.

**Required input in step ①:** Barry Callebaut's description names the target, so the app warns that the AI would see both names in one call. Tick **Send anyway** (the lawyer's decision, recorded in the progress file), then click **Find activities**.

**Expected relationships:**

- **Barry Callebaut, existing relationship and vertical link.** The code finds the ChoViva partnership in each company's separate research and lists it in the Annex. Barry Callebaut distributes ChoViva as a wholesaler, so step ② lists the distribution as an activity of its own and step ③ gives a vertical link (ChoViva resold through Barry Callebaut, *One side defined*), plus a less likely horizontal label across levels of trade. If a run files ChoViva under Barry Callebaut's own ingredients instead, the existing-relationship note on its rows points to it, and the lawyer can correct the line in step ②.
- **Barry Callebaut, horizontal overlaps in cocoa ingredients.** The cocoa-powder replacer meets Barry Callebaut's cocoa powder, and the cocoa-butter alternative (named as plant-based, specialty or cocoa-butter-identical fats, depending on the run) meets its cocoa butter. The result is at most *Possible*, because the Commission's markets fit Planet A Foods' products only as "not an exact match". Depending on the run it can also be *No precedent* or, for the cocoa-powder replacer, *Not supported*. Whether food manufacturers would switch from cocoa powder or cocoa butter to a cocoa-free alternative is a question no decision in the database answers, so this is one of the hard cases left to the lawyer's judgment.
- **Barry Callebaut, vertical links the other way.** Planet A Foods' ingredients are possible inputs for Barry Callebaut's drink mixes, chocolate or pralines.
- **Ritter Sport, vertical link.** Every fact is sourced to "your description". Planet A Foods' products are possible inputs for Ritter Sport's chocolate. No horizontal overlap is expected, at most a less likely label across levels of trade. If a run proposes one, whether a cocoa-free alternative competes with chocolate is exactly the question the app leaves to the lawyer.
- **FRoSTA, none** (see above).

**Also on the screen:** further horizontal labels with Barry Callebaut reading *No precedent* or *Possible* (ChoViva against its chocolate, coatings or cocoa ingredients; nut ingredients against its nut pastes or fillings; coffee-taste ingredients against its beverage ingredients); side lines such as its event and catering services or cocoa cell-culture research; less likely labels across levels of trade; and in some runs Planet A Foods' ingredients and fats as an input for frozen food.

**Try this:** In step ③, set a label the public sources cannot settle (for example the cocoa-butter alternative against Barry Callebaut's cocoa butter) to *Ask the company* and add a note. It then appears under Open Points in step ⑤ and in the Word document.

### TC3 · Brillux

**Why this case:** the same code screens building materials, a sector with no decision in the database, so the lawyer adds one, as in practice. The market table then also gives the Commission's own terms ("decorative coatings", "RMI products for the home") to search a legal database for further decisions, which can then be added to the app in the same way. A lawyer can add a whole decision or paste only an extract, since research platforms such as LexisNexis often show just the paragraphs on market definition, which can then be copied into the app without downloading the decision.

**Input:** the target is Brillux (paints, facade insulation systems, industrial coatings), the portfolio companies Hornbach (DIY stores and a builders' merchant), Sto (facade systems and coatings) and Henkel (adhesives), all researched by web search. **Test file:** `test_files/M4779_Akzo_Nobel_ICI.pdf`, the Commission's decision of 13 December 2007 in [M.4779 Akzo Nobel / ICI](https://ec.europa.eu/competition/mergers/cases/decisions/m4779_20071213_20212_en.pdf) as published.

**Required input in step ③ or ④:** First click **Find Commission market definitions** without a decision. Every row reads *No precedent*, with one warning that no decision in the database fits, which does not mean that none exists. Then open **Add a Commission Decision or Extract** under the table and upload the PDF. The app reads the case number, title and date and proposes the paragraphs on market definition. Click **Add M.4779 to this screen**, then **Update the market definitions**. Only decisions with a text layer can be added (for a scanned PDF, paste the text instead), and quotations are checked against the uploaded text, not the official version.

**Expected relationships** (after the upload):

- **Sto, horizontal overlap in decorative paints** (*Confirmed*). The market is Decorative coatings (M.4779 (11)–(15)), each sentence marked "added by you". "A further question was left open" refers to whether decorative coatings split further, for example into paints and woodcare or into products for professionals and for DIY customers, which the Commission left open in paragraphs (13)–(15).
- **Sto, horizontal overlap in facade insulation systems.** *No precedent*, because M.4779 does not define this market, or *Possible* where a row compares Brillux's facade paints with Sto's facade finishes. Brillux's facade paints or adhesives are also possible inputs for Sto's facade systems (vertical).
- **Hornbach, vertical link.** Its DIY stores and builders' merchant resell paints and tools. The DIY stores get *One side defined* (Decorative coatings for Brillux, no precedent for Hornbach's retail). The builders' merchant can get *Markets defined*, through the market for the distribution of decorative coatings (M.4779 (45)). If step ② classes the DIY stores as manufacturing instead of retail, a horizontal label replaces the resale link, so this is worth a look in step ②.
- **Henkel, horizontal overlap in industrial coatings** (*No precedent*, since M.4779 does not define this market).
- **Henkel, overlaps in facade systems (Ceresit) and in adhesives.** Found only in some runs, since Ceresit is one brand deep within a large group's range and adhesives are a side range of Brillux. A lawyer who knows of them adds them in step ②.

**Also on the screen:** *No precedent* horizontal labels for floor coatings, project consulting and training; less likely horizontal labels between Brillux's paints or industrial coatings and Hornbach's DIY range; and theoretical links through side lines such as Brillux's Academy or Hornbach's property management, which you can mark "not relevant" in step ②.

### More to try (not one of the three test cases)

**Koa (cocoa fruit products):** click **More · Koa** under Try an Example. With no precedent at all, step ④ shows *No precedent* and leaves the market to the lawyer under the Market Definition Notice, rather than forcing a chocolate decision onto cocoa fruit.

---

## AI techniques used

A run makes from about 100 (TC1, TC2) to about 140–350 (TC3) AI calls: two web searches and one extraction per company, one comparison per pair of activities, and in step ④ one call that sorts the products into types and one reflection per type and attempt. Embedding requests are not counted.

| Class technique | In this app |
|---|---|
| Lab 1 · problem decomposition, fixed questions, one call per element | five steps, fixed questions per activity (level of trade, direct customers, end users) and per pair (product relation, vertical links), one call per anonymised pair (`logic/comparison.py`) |
| Lab 1 · constrained answers and if/then logic | Structured Outputs with fixed answer lists (`logic/schemas.py`). `rules.decide()` combines the AI's answer with checks in code (reseller, own use, input and resale signals). The same logic drives the confidentiality guard and decides which rows step ④ looks up. Unlike Lab 1, there is no stop at the first negative answer, because a screen must compare every pair |
| Lab 2 · ChromaDB, chunking with metadata | text-embedding-3-large, one chunk per numbered paragraph with a context header (decision, section) and its footnotes, each decision tagged with the levels of trade of its markets (`logic/ingest.py`, `build_corpus.py`) |
| Lab 2 · retrieval beyond vector search | hybrid search combining vector search and BM25 by reciprocal rank fusion, with a level-of-trade filter (`logic/retrieval.py`). Retrieval checks are in `test_results/` |
| Lab 2 · loop with reflection and STOP conditions | `precedents.run_type()` runs retrieval, then reflection, then at most one rewritten query. It stops when the AI says so, when nothing new is found, or after two attempts, and every attempt is recorded |
| Lab 2 · grounding | in code, a cited paragraph only counts if it was retrieved, and every quotation is checked word for word. The same applies to company websites (`logic/sources.py`) |
| Lab 2 · pause for the user, report | human checkpoints in steps ② and ③, "Save progress" and "Open saved progress", and the Word document (`logic/export.py`) |

---

## Where to find what

`app.py` is the entry point. Each code folder (`steps/`, `ui/`, `logic/`, `tools/`) has a short README listing its files, and `corpus/corpus_report.md` describes the decision database. `static/` holds the fonts and the official PDFs of the decisions, `test_files/` the decision added in TC3, and `test_results/` the retrieval checks. The official PDFs in `static/` are © European Union (Decision 2011/833/EU).