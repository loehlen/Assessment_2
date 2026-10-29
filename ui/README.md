# ui/ – building blocks shared by the steps

Display code used by more than one step. Nothing here calls the AI.

| File | What it does |
|---|---|
| `theme.py` | the style sheet: colours, fonts (Times New Roman for headings, as in the Word document), labels, tables, hover boxes |
| `common.py` | small helpers used everywhere: the settings (development mode, model profile), the session state, safe text for Streamlit and HTML, plurals and dates, the cost and time of each step, moving between steps |
| `credentials.py` | the first screen: the user's own OpenAI API key (or, in development, an app password) |
| `api_key.py` | the course's API Credentials sidebar module (github.com/stoneman-mls/openai_credentials), with a password field and the key never shown on the page |
| `working_screen.py` | the progress card shown while the AI works; "Start over" |
| `activity_display.py` | how activities and sources are shown in steps ②, ③ and ⑤: the stage of the supply chain, the source marks (✔ ≈ ○ ⚠) with the quotation on hover, an existing relationship between two companies |
| `labels.py` | the customer dots (●●○) and the result chips of step ④, with their explanations |
| `guides.py` | the guide box at the start of steps ②, ③ and ④ (how it works, how to read it, limits) |
| `decisions.py` | the Commission decisions in the database and those the lawyer added: paragraphs, case numbers, titles, references with the text on hover |
| `decision_reader.py` | the decisions used in a screen (sidebar) and the reader that opens one inside the app |
| `upload_box.py` | "Add a Commission decision" at the end of step ④ (the reading itself is in `logic/uploads.py`) |
| `saved_screens.py` | opening a saved screen ("Save progress" Word document or audit log) and building the audit log |
| `sidebar.py` | the sidebar: start over, save progress, the Word document, the legend, the decisions used, the run summary, the API key; in development a deployment check |
