"""
no_rag_check.py - the "comparison without RAG" for A3 (spec section 15): what does the model know about the
Commission's market definitions WITHOUT the decision corpus? Does it know M.5644? Does it invent paragraph numbers?

    python no_rag_check.py                               Luna and Sol, three questions, no web search
    python no_rag_check.py --models gpt-6-luna           one model only

Each answer is checked in code: every case number and paragraph number the model cites is looked up in
corpus/paragraphs.json and compared with the paragraphs the retrieval check verified for the same question.
  ✔ cited and among the verified paragraphs
  ◐ in the corpus, but not one of the verified paragraphs (read it: right decision, wrong paragraph?)
  ? not in the corpus: outside the market-definition ranges of the four decisions, or invented (check the PDF)
  ✖ a case number that is not one of the four decisions (may exist, but cannot be checked here)
Cost: a few cents (Sol about USD 0.01-0.03 per answer). Development tool: stays out of the final app.
"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import ai_client

QUESTIONS = [
    {"q": "Under EU merger control, how has the European Commission defined the relevant product market for "
          "chocolate tablets? Name the decisions by case number and cite the paragraph numbers.",
     "expected": ["M.5644-15", "M.5644-21", "M.5644-24"]},
    {"q": "What relevant geographic market has the European Commission considered for industrial chocolate "
          "supplied to food manufacturers? Name the decisions by case number and cite the paragraph numbers.",
     "expected": ["M.7408-74", "M.7408-75", "M.7408-61"]},
    {"q": "Has the European Commission treated chocolate compound coatings as a market separate from industrial "
          "chocolate? Name the decisions by case number and cite the paragraph numbers.",
     "expected": ["M.7408-49", "M.7408-50", "M.7408-51"]},
]
INSTRUCTION = ("Answer as a competition lawyer would, from your own knowledge only. Cite Commission decisions by case "
               "number (e.g. M.1234) and paragraph number, e.g. 'M.1234, para (56)'. If you are not sure of a "
               "paragraph number, say so instead of guessing.")

CASE = re.compile(r"\bM\.?\s?(\d{4,5})\b")
CASE_PARA = re.compile(r"\bM\.?\s?(\d{4,5})\s*,?\s*\((\d{1,3})\)")              # "M.5644 (24)"
PARA = re.compile(r"(?:paras?\.?|paragraphs?|recitals?|¶)\s*((?:\(?\d{1,3}\)?(?:\s*(?:-|–|to|and|,|&)\s*)?)+)",
                  re.IGNORECASE)                                                       # "paras (21)-(24), 15 and 30"


def numbers(group):
    """'(21)-(24), 15 and 30' -> [21, 22, 23, 24, 15, 30] (ranges capped at 10 paragraphs)."""
    tokens, out, i = re.findall(r"\d{1,3}|-|–|to", group), [], 0
    while i < len(tokens):
        t = tokens[i]
        if t.isdigit():
            if i + 2 < len(tokens) and tokens[i + 1] in ("-", "–", "to") and tokens[i + 2].isdigit():
                lo, hi = int(t), int(tokens[i + 2])
                out += list(range(lo, min(hi, lo + 10) + 1))
                i += 3
                continue
            out.append(int(t))
        i += 1
    return out


def citations(answer):
    """(case, paragraph) pairs. A paragraph reference belongs to the last case number named before it;
    a case named without any paragraph is listed with None."""
    cases = [(m.start(), f"M.{m.group(1)}") for m in CASE.finditer(answer)]
    found = [(f"M.{m.group(1)}", int(m.group(2))) for m in CASE_PARA.finditer(answer)]
    for m in PARA.finditer(answer):
        before = [c for pos, c in cases if pos < m.start()]
        if before:
            found += [(before[-1], n) for n in numbers(m.group(1))]
    out = []
    for c in found + [(c, None) for _, c in cases]:
        if c not in out and not (c[1] is None and any(f == c[0] for f, n in out if n is not None)):
            out.append(c)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", default=["gpt-6-luna", "gpt-6.1-sol"])
    args = p.parse_args()
    corpus = {x["id"]: x for x in json.loads(Path("corpus/paragraphs.json").read_text(encoding="utf-8"))}
    cases = {x["case"] for x in corpus.values()}
    ai = ai_client.AI(profile="dev", use_cache=True)
    L = [f"# Comparison without RAG ({datetime.now():%Y%m%d-%H%M})", "",
         "No corpus, no web search: the model answers from its own knowledge. Citations checked in code against "
         "corpus/paragraphs.json and the paragraphs verified in the retrieval check.", "",
         "✔ verified paragraph · ◐ in the corpus, not a verified paragraph · ? not in the corpus (outside the "
         "market-definition ranges, or invented) · ✖ case not in the corpus", ""]
    summary = []
    for model in args.models:
        for i, item in enumerate(QUESTIONS, start=1):
            key = [model, INSTRUCTION, item["q"]]
            path, hit = ai.cache_get("no_rag", key)
            if hit:
                answer = hit["answer"]
            else:
                resp = ai.respond("check", item["q"], instructions=INSTRUCTION, model=model, note=f"no RAG Q{i}")
                answer = resp.output_text
                ai.cache_put(path, {"answer": answer})
            marks = []
            for case, n in citations(answer):
                pid = f"{case}-{n}" if n is not None else None
                if case not in cases:
                    marks.append(("✖", f"{case}" + (f" ({n})" if n else ""), "case not in the corpus"))
                elif n is None:
                    marks.append(("–", case, "case named, no paragraph"))
                elif pid in item["expected"]:
                    marks.append(("✔", f"{case} ({n})", corpus[pid]["text"][:110] + "…"))
                elif pid in corpus:
                    marks.append(("◐", f"{case} ({n})", corpus[pid]["text"][:110] + "…"))
                else:
                    marks.append(("?", f"{case} ({n})", "not in the corpus: check the PDF"))
            counts = {m: sum(x[0] == m for x in marks) for m in ("✔", "◐", "?", "✖")}
            summary.append((model, i, counts))
            L += [f"## {model} · question {i}", "", f"> {item['q']}", "",
                  f"Verified paragraphs: {', '.join(item['expected'])}", "", answer.strip(), "",
                  "| | Citation | Check |", "|---|---|---|"]
            L += [f"| {m} | {c} | {d.replace('|', '/')} |" for m, c, d in marks] or ["| | (no citation) | |"]
            L.append("")
    L += ["## Summary", "", "| Model | Q | ✔ | ◐ | ? | ✖ |", "|---|---|---|---|---|---|"]
    L += [f"| {m} | {i} | {c['✔']} | {c['◐']} | {c['?']} | {c['✖']} |" for m, i, c in summary]
    s = ai.log.summary()
    L += ["", f"{s['calls']} calls · USD {s['cost']:.4f} (token prices)"]
    out = Path("test_results") / f"no_rag_{datetime.now():%Y%m%d-%H%M}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    for m, i, c in summary:
        print(f"{m} Q{i}: {c}")
    print(f"report: {out}")


if __name__ == "__main__":
    main()