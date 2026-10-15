# Retrieval check (20261015-0634)

14 test queries · correct paragraph in the top 3 · embeddings: text-embedding-3-large

| Configuration | Hits in top 3 | incl. neighbouring paragraphs (only C uses them) |
|---|---|---|
| A  no headers, vector | 13/14 | 13/14 |
| B  headers, vector | 14/14 | 14/14 |
| C  headers + BM25 + neighbours | 14/14 | 14/14 |

## Per query

| Query | A  no headers, vector | B  headers, vector | C  headers + BM25 + neighbours |
|---|---|---|---|
| relevant product market for chocolate tablets (correct: M.5644-24, M.5644-15, M.5644-21…) | ✖ M.5644-14, M.5644-19, M.5644-92 | ✔ M.5644-15, M.5644-22, M.5644-23 | ✔ M.5644-23, M.5644-14, M.5644-15 |
| geographic market for chocolate confectionery national or wider (correct: M.5644-42, M.5644-43) | ✔ M.5644-42, M.5644-48, M.5644-12 | ✔ M.5644-42, M.5644-44, M.5644-43 | ✔ M.5644-42, M.5644-43, M.5644-24 |
| relevant geographic market industrial chocolate catchment area around plants (correct: M.7408-74, M.7408-75, M.7408-61…) | ✔ M.7408-61, M.7408-74, M.7408-58 | ✔ M.7408-61, M.7408-74, M.6872-35 | ✔ M.7408-61, M.7408-74, M.7408-75 |
| chocolate compound coatings separate market from industrial chocolate (correct: M.7408-51, M.7408-49, M.7408-50…) | ✔ M.7408-49, M.7408-51, M.7408-47 | ✔ M.7408-49, M.7408-31, M.7408-51 | ✔ M.7408-49, M.7408-51, M.7408-31 |
| geographic scope of the market for cocoa butter, cocoa liquor and cocoa powder (correct: M.7120-66, M.7120-65, M.6872-30…) | ✔ M.7408-76, M.7120-61, M.6872-30 | ✔ M.7120-66, M.6872-30, M.7120-59 | ✔ M.7120-66, M.6872-30, M.7408-76 |
| procurement of cocoa beans geographic market (correct: M.7120-55, M.7120-54, M.6872-26…) | ✔ M.6872-27, M.7120-55, M.6872-26 | ✔ M.7120-55, M.6872-27, M.7120-53 | ✔ M.7120-55, M.6872-27, M.6872-28 |
| are cocoa liquor, cocoa butter and cocoa powder separate product markets (correct: M.6872-21, M.6872-22, M.7120-30…) | ✔ M.6872-22, M.7408-44, M.7408-43 | ✔ M.7120-31, M.7408-43, M.7120-26 | ✔ M.7408-43, M.6872-22, M.7120-26 |
| chocolate sold in airport shops and travel retail as a separate market (correct: M.5644-39, M.5644-40, M.5644-41) | ✔ M.5644-39, M.5644-41, M.5644-40 | ✔ M.5644-39, M.5644-40, M.5644-45 | ✔ M.5644-39, M.5644-41, M.5644-40 |
| private label chocolate tablets competitive constraint on branded tablets (correct: M.5644-117, M.5644-48, M.5644-49) | ✔ M.5644-117, M.5644-48, M.5644-23 | ✔ M.5644-117, M.5644-49, M.5644-92 | ✔ M.5644-117, M.5644-49, M.5644-92 |
| liquid versus solid industrial chocolate segmentation (correct: M.7408-37, M.7408-38, M.7408-39…) | ✔ M.7408-25, M.7408-33, M.7408-38 | ✔ M.7408-38, M.7408-39, M.7408-25 | ✔ M.7408-38, M.7408-39, M.7408-33 |
| different customer groups forming separate relevant markets (correct: Notice-88, Notice-89, Notice-24) | ✔ N-89, N-88, N-58 | ✔ N-88, N-89, N-35 | ✔ N-88, N-89, N-24 |
| do imports widen the relevant geographic market (correct: Notice-42, Notice-43) | ✔ N-42, N-43, N-41 | ✔ N-42, N-43, N-44 | ✔ N-42, N-43, N-44 |
| chocolate supplied by manufacturers to retailers and wholesalers, two levels of the supply chain (correct: M.5644-47) | ✔ M.5644-47, M.5644-48, M.5644-39 | ✔ M.5644-47, M.5644-48 | ✔ M.5644-47, M.5644-48, M.5644-45 |
| market definition left open for sugar confectionery (correct: M.5644-25, M.5644-26, M.5644-27) | ✔ M.5644-26, M.5644-13, M.5644-48 | ✔ M.5644-25, M.5644-26, M.5644-27 | ✔ M.5644-13, M.5644-27, M.5644-25 |

✔ correct paragraph in the top 3 · ◐ only as a neighbouring paragraph · ✖ missed

Query embeddings: 14 calls (28 from cache), 137 tokens
