# steps/ – the screens of the app

The start page and steps ① to ⑤, one file per screen: what the user sees and does. The workflow behind them (AI
calls, prompts, rules, search, Word export) is in `logic/`; building blocks shared by several steps are in `ui/`.

| File | What it does |
|---|---|
| `start_page.py` | the start page: what a preliminary overlap screen is, why it matters, what the lawyer can rely on, how the tool works in five steps |
| `step1_companies.py` | ① Companies: the target and up to five portfolio companies (name, website, other names, how each is researched), the example buttons, the confidentiality warnings, and the research of each company |
| `step2_activities.py` | ② Activities: each company's profile and activities with their sources, for the lawyer to check, edit, add, delete or mark as not relevant; researching a company again; the button that starts step ③ |
| `step3_assessment.py` | ③ Preliminary Assessment, the logic behind the table: running the comparison, the labels of each row, the rules checked in code ("less likely", own use, direct customers), and the lawyer's views, notes and edits |
| `step3_4_table.py` | the table screen of steps ③ and ④: one box per portfolio company, one block per activity of the target, one row per activity that meets it |
| `step4_search.py` | ④ Market Definitions, the search: which rows need a search, running it in the decision database, and the button that starts or updates it |
| `step4_results.py` | ④ the results: in which markets the Commission's decisions place each side's products, the result of each label, the Commission's sentences on hover, and the table of all markets in the screen |
| `step5_summary.py` | ⑤ Summary: the result of the screen (what the lawyer kept in steps ③ and ④, strongest first), the content of the Word document, and the "Save progress" copy the app can open again |
