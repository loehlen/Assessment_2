# steps/ – the screens of the app

One file per step, in the order the user goes through them. `app.py` decides which one to show.

| File | What it does |
|---|---|
| `start_page.py` | the start page: what a preliminary overlap screen is, the five steps, what the lawyer can rely on |
| `step1_companies.py` | **① Companies**: the target and the portfolio companies (name, website, other names, where the activities come from), the example buttons, the confidentiality warnings; then the research of each company (`logic/activity_mapping.py`) |
| `step2_activities.py` | **② Activities**: each company's profile and activities with their sources, for the lawyer to check, edit, add, delete or mark as not relevant; mapping a company again; the button that starts step ③ |
| `step3_assessment.py` | **③ Preliminary Assessment**, the logic: running the comparison (`logic/comparison.py`), the labels of each row (potential horizontal overlap, potential vertical relationship), the rules checked in code ("less likely", own use, direct customers), the sentences of the assessment, and the lawyer's views, notes and edits |
| `step3_4_table.py` | the table screen of steps ③ and ④: one box per portfolio company, one block per activity of the target, one row per activity that meets it; step ④ adds the Commission's result to each row |
| `step4_search.py` | **④ Commission Market Definitions**, the search: which rows need one, running it in the decision database (`logic/precedents.py`), the button that starts or updates it |
| `step4_results.py` | **④**, the results: in which markets the decisions place the products of both sides, the result per label ("Confirmed", "Possible", "Not supported", "No precedent", …) with the Commission's sentences on hover, and the table of all markets of the screen |
| `step5_summary.py` | **⑤ Summary**: the result of the screen (what the lawyer kept, strongest first), the content of the Word document (written by `logic/export.py`) and the "Save progress" copy |

Shared pieces (sidebar, style, source marks, labels, the decision reader) are in `ui/`; the AI calls, prompts and
rules in `logic/`.
