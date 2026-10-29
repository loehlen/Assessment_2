"""
logic/build_corpus.py - builds the built-in decision corpus from the official PDFs.

Run once:   python -m logic.build_corpus
Reads:      corpus_src/*.pdf   (the four Commission decisions and the Market Definition Notice; not in the
                                repository: download them from the addresses in SOURCES below, under the file names
                                given there)
Writes:     corpus/paragraphs.json   one record per numbered paragraph in the corpus ranges, with footnotes,
                                     section headings and the context header that will be embedded
            corpus/corpus_report.md  a readable overview to check the result by eye

No API calls and no cost. The embeddings are a separate step (tools/build_index.py), so this file can be re-run and
checked freely. Needs pdftotext (Codespace: sudo apt-get install -y poppler-utils); pypdf is not used, because it loses
the paragraph layout of several of the documents (see ingest.pdf_text).
"""
import json
from pathlib import Path

from logic.ingest import ingest_text, pdf_text

SRC, OUT = Path("corpus_src"), Path("corpus")

# Corpus ranges: only the market definition paragraphs, plus the few
# competitive-assessment paragraphs that define market segments.
SOURCES = [
    {"file": "M5644.pdf", "short": "Kraft Foods / Cadbury", "case": "M.5644", "title": "Kraft Foods / Cadbury", "date": "2010-01-06",
     "decision": "Article 6(1)(b) in conjunction with Article 6(2), with commitments (Phase I)",
     "url": "https://ec.europa.eu/competition/mergers/cases/decisions/m5644_20100106_20212_en.pdf",
     "levels": ["finished products", "retail"],
     "ranges": [(12, 49), (92, 93), (117, 117), (135, 135)]},
    {"file": "M6872.pdf", "short": "Barry Callebaut / Petra Foods", "case": "M.6872", "title": "Barry Callebaut / Petra Foods (Cocoa Ingredients Division)",
     "date": "2013-06-06", "decision": "Article 6(1)(b) (Phase I)",
     "url": "https://ec.europa.eu/competition/mergers/cases/decisions/m6872_20130606_20310_3190791_EN.pdf",
     "levels": ["raw materials", "intermediate products"],
     "ranges": [(9, 37), (47, 47), (51, 58)]},
    {"file": "M7120.pdf", "short": "Ecom / Armajaro", "case": "M.7120", "title": "Ecom Agroindustrial / Armajaro Trading", "date": "2014-05-23",
     "decision": "Article 6(1)(b) (Phase I)",
     "url": "https://ec.europa.eu/competition/mergers/cases/decisions/m7120_1451_2.pdf",
     "levels": ["raw materials", "intermediate products"],
     # the coffee paragraphs (42)-(51) and (67) onwards are kept out on purpose, as a hold-out for testing
     "ranges": [(9, 41), (52, 66)]},
    {"file": "M7408.pdf", "short": "Cargill / ADM", "case": "M.7408", "title": "Cargill / ADM Chocolate Business", "date": "2015-07-17",
     "decision": "Article 8(2) with commitments (Phase II)",
     "url": "https://ec.europa.eu/competition/mergers/cases/decisions/m7408_2987_3.pdf",
     "levels": ["intermediate products"],
     "ranges": [(19, 81)]},
    {"file": "NOTICE.pdf", "short": "Market Definition Notice", "case": "Notice", "title": "Commission Notice on the definition of the relevant market "
     "(OJ C/2024/1645)", "date": "2024-02-22", "decision": "Market Definition Notice",
     "url": "https://eur-lex.europa.eu/eli/C/2024/1645/oj", "levels": [], "style": "oj",
     "source_type": "Commission notice",
     "ranges": [(11, 75), (85, 93)]},
]


def context_header(rec):
    """Embedded together with the text, so that paragraphs that never name the product ('the exact market
    definition can be left open') are still found."""
    year = rec["date"][:4]
    # the short party label, not the full title: words such as "Chocolate Business" or "Cocoa Ingredients
    # Division" in every header would pull all chocolate or cocoa queries towards one decision
    parts = [f"{rec['case']} {rec['short']} ({year})", rec["section"]] + rec["headings"] + [f"para {rec['para']}"]
    seen, out = set(), []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return " · ".join(out)


# Corrections after the check of every paragraph against the PDFs: the parser cannot know these.
# M.6872: the Commission's correction note "∗ Should read: B (i)." belongs to the "B (ii)∗" in paragraph (55); pdftotext
# prints it at the foot of the page of (57), so the parser had appended it to the text of (57).
CORRECTIONS = [
    {"case": "M.6872", "para": 57, "remove": " ∗ Should read: B (i).", "why": "correction note of (55), printed at the page foot"},
    {"case": "M.6872", "para": 55, "add_note": {"n": "∗", "text": "Should read: B (i)."},
     "why": "the Commission's correction note to 'section B (ii)∗'"},
    # Notice: two words broken at a line end kept a space after the hyphen (the same footnotes spell them without it)
    {"case": "Notice", "para": 30, "footnote": 55, "replace": ("profit- maximising", "profit-maximising"),
     "why": "line-end hyphenation"},
    {"case": "Notice", "para": 51, "footnote": 78, "replace": ("pre- impregnated", "pre-impregnated"),
     "why": "line-end hyphenation"},
    # M.6872: the unnumbered headings "Relevant product markets" (before (10)) and "Relevant geographic markets" (before
    # (26)) were not recognised, so (10)-(25) carried only the generic section "Market definition", while M.7120's
    # equivalent paragraphs say "Relevant product market"; section and headings are part of the keyword search and the
    # embedded context header
    {"case": "M.6872", "paras": (10, 25), "section": "Relevant product market",
     "insert_heading": ("A. Relevant market definitions", "Relevant product markets"), "why": "heading not recognised"},
    {"case": "M.6872", "paras": (26, 37), "section": "Relevant geographic market",
     "insert_heading": ("A. Relevant market definitions", "Relevant geographic markets"), "why": "heading not recognised"},
]


def apply_corrections(records):
    for c in CORRECTIONS:
        for r in records:
            if c.get("paras") and r["case"] == c["case"] and c["paras"][0] <= r["para"] <= c["paras"][1]:
                r["section"] = c.get("section", r["section"])
                after, heading = c.get("insert_heading") or (None, None)
                if heading and heading not in r["headings"] and after in r["headings"]:
                    r["headings"].insert(r["headings"].index(after) + 1, heading)
                continue
            if r["case"] == c["case"] and r["para"] == c.get("para"):
                if c.get("remove") and c["remove"] in r["text"]:
                    r["text"] = r["text"].replace(c["remove"], "").rstrip()
                if c.get("add_note") and c["add_note"] not in r["footnotes"]:
                    r["footnotes"].append(dict(c["add_note"]))
                if c.get("replace"):
                    for f in r["footnotes"]:
                        if f["n"] == c.get("footnote"):
                            f["text"] = f["text"].replace(*c["replace"])
    return records


def build():
    OUT.mkdir(exist_ok=True)
    corpus, report = [], ["# Decision corpus", ""]
    for src in SOURCES:
        records, style, n_notes = ingest_text(pdf_text(SRC / src["file"]), {**src, "style": src.get("style", "auto")})
        wanted = {n for a, b in src["ranges"] for n in range(a, b + 1)}
        found = {r["para"] for r in records}
        missing = sorted(wanted - found)
        kept = apply_corrections([r for r in records if r["para"] in wanted])
        for r in kept:
            r["decision"] = src["decision"]
            r["short"] = src["short"]
            r["header"] = context_header(r)
        corpus += kept
        ranges = ", ".join(f"({a})" if a == b else f"({a})–({b})" for a, b in src["ranges"])
        report += [f"## {src['case']} {src['title']} ({src['date']})", "",
                   f"Parsed: {len(records)} paragraphs, {n_notes} footnotes (style '{style}'). "
                   f"Corpus ranges {ranges}: {len(kept)} of {len(wanted)} paragraphs"
                   + (f" · **missing: {missing}**" if missing else " · none missing"), ""]
        for r in kept:
            notes = "; ".join(f"fn {f['n']}" + (" (by page)" if f.get("placed_by_page") else "") for f in r["footnotes"])
            report.append(f"- **({r['para']})** {r['section'] or '–'} · {' · '.join(r['headings'][-1:])} — "
                          f"{r['text'][:140]}…" + (f" [{notes}]" if notes else ""))
        report.append("")
        print(f"{src['case']}: {len(kept)}/{len(wanted)} paragraphs" + (f", MISSING {missing}" if missing else ""))
    (OUT / "paragraphs.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "corpus_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    words = sorted(len(r["text"].split()) for r in corpus)
    print(f"{len(corpus)} paragraphs written to corpus/paragraphs.json · words per paragraph: "
          f"median {words[len(words) // 2]}, max {words[-1]}")


if __name__ == "__main__":
    build()