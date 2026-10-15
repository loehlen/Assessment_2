# Factual comparison TC2: Planet A Foods (20261015-0555)

Models: search saved gpt-6.1-sol · extraction gpt-6-luna · comparison gpt-6-luna · text-embedding-3-large  
Thresholds: unclear ≥ 0.5 · input match ≥ 0.5 · resale ≥ 0.5

## Benchmark check (spec section 13)

6 ✔ as expected · 0 ◐ kept in another form · **0 ✖ missed by the comparison** · 0 ∅ activity not found · 1 ⚠ false positives in a control row

Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py need adjusting: compare with the activity overview below).

| Check | Portco | Pair | Expected | Result | Pairs | Detail |
|---|---|---|---|---|---|---|
| TC2-1 | Barry Callebaut | ChoViva partnership (🔗 note must appear) | relationship | ✔ |  | 🔗 mention found in the public sources |
| TC2-2 | Barry Callebaut | compound / industrial chocolate ↔ ChoViva | horizontal | ✔ | T-1↔P2-1, T-1↔P2-2, T-1↔P2-4, T-1↔P2-6 (+1) | 5 of 5 matching pairs as expected |
| TC2-3 | Barry Callebaut | ChoViva Butter (pipeline) ↔ cocoa butter | kept | ✔ | T-2↔P2-3, T-2↔P2-5 | 2 of 2 matching pairs as expected |
| TC2-4 | Ritter Sport | ChoViva → Ritter chocolate (vertical candidate) | vertical | ✔ | T-1↔P1-1, T-1↔P1-3, T-1↔P1-4, T-1↔P1-5 | 4 of 4 matching pairs as expected |
| TC2-5 | Ritter Sport | Ritter consumer chocolate ↔ ChoViva (related, ●○○) | horizontal | ✔ | T-1↔P1-1, T-1↔P1-3, T-1↔P1-4, T-1↔P1-5 | 4 of 4 matching pairs as expected |
| TC2-6 | Bahlsen | ChoViva → biscuits (vertical candidate) | vertical | ✔ | T-1↔P3-1, T-1↔P3-2, T-1↔P3-3, T-1↔P3-4 (+1) | 5 of 5 matching pairs as expected |
| TC2-7 | FRoSTA | control: nothing in common | screened out | ⚠ | T-1↔P4-2, T-1↔P4-4, T-1↔P4-6, T-2↔P4-1 (+11) | 15 of 30 pairs kept: check whether these are false positives |

## Activity overview (stages ①–②)

### Target: Planet A Foods (3 activities, 12 sources)
🔗 The public sources for Planet A Foods mention: Barry Callebaut (check for an existing relationship)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| T-1 | not stated | Cocoa-free chocolate alternative ingredient | intermediate products | manufacturers / processors | not stated | on the market | [1, 3, 4, 5, 6, 7, 8, 10, 11] |
| T-2 | not stated | Yeast-derived cocoa-butter alternative | intermediate products | manufacturers / processors | not stated | in development | [1, 9] |
| T-3 | not stated | Custom specialty fats and oils | intermediate products | manufacturers / processors | not stated | in development | [9] |

### Portco 1: Ritter Sport (12 activities, 23 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P1-1 | not stated | Packaged chocolate bars and chocolate confec… | finished products | retailers, wholesalers / distributors | Germany, Italy, United Kingdo… | on the market | [2, 3, 4, 5] |
| P1-2 | not stated | Packaged chocolate and chocolate confectione… | retail | consumers | Germany | on the market | [8, 9] |
| P1-3 | not stated | Cream-filled, chocolate-covered wafer rolls | finished products | not stated | not stated | on the market | [6, 7] |
| P1-4 | not stated | Custom chocolate products and small-batch ch… | finished products | consumers | Germany | on the market | [8, 9] |
| P1-5 | not stated | Corporate gifts and promotional chocolate | finished products | other businesses, public sector | not stated | on the market | [10] |
| P1-6 | not stated | Cocoa-fruit beverages | finished products | consumers, other businesses | Germany | not stated | [11, 12] |
| P1-7 | not stated | Chocolate-making workshops and visitor exper… | services | consumers, other businesses | Germany | on the market | [8, 9] |
| P1-8 | not stated | Bistro food and beverages and event-space hi… | services | consumers, other businesses | Germany | on the market | [8] |
| P1-9 | not stated | Non-food gifts and merchandise | retail | consumers | Germany | on the market | [9] |
| P1-10 | not stated | Cocoa cultivation and post-harvest operations | raw materials | internal use (captive) | Nicaragua | on the market | [13] |
| P1-11 | not stated | Hazelnut cultivation | raw materials | internal use (captive) | France | on the market | [14] |
| P1-12 | not stated | Electricity and heat generation for own oper… | other | internal use (captive) | not stated | on the market | [15] |

### Portco 2: Barry Callebaut (10 activities, 21 sources)
🔗 The public sources for Barry Callebaut mention: Planet A Foods (check for an existing relationship)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P2-1 | Global Chocolate | Industrial chocolate and couverture | intermediate products | manufacturers / processors | not stated | on the market | [1, 2] |
| P2-2 | Global Chocolate | Professional chocolate and cocoa ingredients | intermediate products | wholesalers / distributors, other businesses | Belgium, Czechia, France, Ger… | on the market | [19] |
| P2-3 | Global Cocoa | Cocoa liquor, cocoa butter and cocoa powder | intermediate products | manufacturers / processors, other businesses, internal use (captive) | not stated | on the market | [1] |
| P2-4 | Global Chocolate | Confectionery coatings, fillings, inclusions… | intermediate products | manufacturers / processors, wholesalers / distributors, other businesses | Indonesia | on the market | [3, 4, 8, 9, 10] |
| P2-5 | Global Chocolate | Nut ingredients and almond preparations | intermediate products | manufacturers / processors, wholesalers / distributors, other businesses | United States, Belgium, Franc… | on the market | [5, 6] |
| P2-6 | Global Chocolate | Biscuit, cookie, cereal and meringue inclusi… | intermediate products | manufacturers / processors, other businesses | not stated | on the market | [7] |
| P2-7 | Global Chocolate | Instant beverage mixes and milk-based bevera… | intermediate products | retailers, wholesalers / distributors, other businesses | Germany, Poland | on the market | [11, 12, 13] |
| P2-8 | Global Chocolate | Cocoa-fruit ingredients | intermediate products | manufacturers / processors, other businesses | not stated | on the market | [14] |
| P2-9 | Global Chocolate | Cocoa-free chocolate alternative ingredients | intermediate products | manufacturers / processors | not stated | on the market | [15] |
| P2-10 | Corporate and other | Professional chocolate and pastry training | services | consumers, other businesses | Belgium, France, Italy, Polan… | on the market | [17] |

### Portco 3: Bahlsen (8 activities, 19 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P3-1 | not stated | Packaged biscuits, cookies, wafers and sweet… | finished products | retailers, wholesalers / distributors | Germany, United States | on the market | [1, 2, 4] |
| P3-2 | not stated | Biscuit-based snack bars | finished products | retailers, wholesalers / distributors | Germany, United States, Unite… | on the market | [1, 4, 5, 11] |
| P3-3 | not stated | Packaged cakes | finished products | retailers, wholesalers / distributors | Germany | on the market | [1, 6] |
| P3-4 | not stated | Seasonal baked goods | finished products | retailers, wholesalers / distributors | Germany | on the market | [1, 6] |
| P3-5 | not stated | Private-label biscuits, wafers and confectio… | finished products | retailers | not stated | on the market | [7, 8] |
| P3-6 | not stated | Organic fruit-and-nut bars and protein bars | finished products | consumers, retailers, not stated | Germany, Austria | on the market | [9, 10] |
| P3-7 | not stated | Retail sale of packaged foods | retail | consumers | Germany | on the market | [12, 13, 14] |
| P3-8 | not stated | Branded clothing and fabric bags | retail | consumers | Germany, Austria | on the market | [10, 15, 16] |

### Portco 4: FRoSTA (10 activities, 14 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P4-1 | FRoSTA-branded consumer … | Frozen ready meals, fish, vegetables, fruit … | finished products | retailers | Germany, Austria, Italy, Pola… | on the market | [1, 3] |
| P4-2 | Private label | Customer-branded frozen foods | finished products | retailers, wholesalers / distributors | not stated | on the market | [3, 4] |
| P4-3 | Own brands | Branded frozen foods | finished products | retailers, wholesalers / distributors | not stated | on the market | [5] |
| P4-4 | Foodservice | Frozen foods for professional kitchens | finished products | wholesalers / distributors, other businesses | Germany, Italy, Poland | on the market | [1, 6, 7, 8] |
| P4-5 | Industrial customers | Frozen food production and supply for indust… | intermediate products | manufacturers / processors | not stated | on the market | [1] |
| P4-6 | Home-delivery customers | Frozen foods supplied to home-delivery busin… | finished products | other businesses | not stated | on the market | [1, 4, 9] |
| P4-7 | Direct online sales | Frozen meals, fish, vegetables and herbs | retail | consumers | Germany, Austria | on the market | [10, 11] |
| P4-8 | B2B online meals | Frozen meals and team meal boxes | finished products | other businesses | Germany | on the market | [12] |
| P4-9 | Product development and … | Food product development and assortment cons… | services | retailers, wholesalers / distributors, other businesses | not stated | on the market | [13] |
| P4-10 | Merchandise | Non-food merchandise | retail | consumers | Germany, Austria | on the market | [14, 11] |

## Factual comparison (stage ③)

120 pairs: 76 candidates · 2 unclear · 42 screened out

### Ritter Sport

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-free chocolate alternat… | P1-1 Packaged chocolate bars and c… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.56 | A is a cocoa-free chocolate alternative ingredient used to make confectionery coatings, fillings and other products; B consists of ready-to-eat chocolate confe… |  |
| T-1 Cocoa-free chocolate alternat… | P1-4 Custom chocolate products and… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.52 | A is a cocoa-free chocolate alternative ingredient used in confectionery and other finished foods, while B is finished chocolate confectionery for eating or gi… |  |
| T-1 Cocoa-free chocolate alternat… | P1-2 Packaged chocolate and chocol… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.52 | A is a cocoa-free chocolate alternative ingredient for making confectionery and other foods, while B is ready-to-eat chocolate and confectionery. They differ i… |  |
| T-1 Cocoa-free chocolate alternat… | P1-6 Cocoa-fruit beverages | candidate | different product |  | A could be an input for B (AI) | 0.48 | A is a bulk ingredient used by manufacturers in confectionery and other foods, whereas B consists of ready-to-drink beverages intended for refreshment or adult… |  |
| T-1 Cocoa-free chocolate alternat… | P1-5 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.47 | Both activities involve chocolate-like products that may be used in finished chocolate items, but A is a bulk cocoa-free ingredient for manufacturing while B i… |  |
| T-1 Cocoa-free chocolate alternat… | P1-10 Cocoa cultivation and post-ha… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.47 | A is a cocoa-free chocolate alternative ingredient used in confectionery and other food products, while B supplies cocoa for chocolate production. Their materi… | captive (not on the merchant market) |
| T-1 Cocoa-free chocolate alternat… | P1-3 Cream-filled, chocolate-cover… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.45 | A is a cocoa-free chocolate alternative ingredient used in confectionery coatings and fillings, while B is a finished wafer confectionery product with a chocol… |  |
| T-2 Yeast-derived cocoa-butter al… | P1-1 Packaged chocolate bars and c… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.44 | A is an ingredient fat intended to replicate cocoa butter’s composition and functionality for confectionery, while B consists of finished chocolate confectione… |  |
| T-2 Yeast-derived cocoa-butter al… | P1-4 Custom chocolate products and… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.44 | A is an ingredient designed to replicate cocoa butter’s composition and functionality, while B is finished chocolate sold for eating or gifting. A could plausi… |  |
| T-2 Yeast-derived cocoa-butter al… | P1-2 Packaged chocolate and chocol… | candidate | different product |  | A could be an input for B (AI) | 0.43 | A is an ingredient fat intended for use by confectionery manufacturers, while B is ready-to-eat chocolate and confectionery for eating or gifting. Customers wo… |  |
| T-1 Cocoa-free chocolate alternat… | P1-11 Hazelnut cultivation | candidate | different product |  | B could be an input for A (AI) | 0.43 | A is a processed cocoa-free chocolate alternative ingredient used in food products, while B is the cultivation of hazelnuts. Customers would not use hazelnut c… | captive (not on the merchant market) |
| T-3 Custom specialty fats and oils | P1-11 Hazelnut cultivation | candidate | different product |  | B could be an input for A (AI) | 0.42 | Custom specialty fats and oils are functional fat ingredients intended for use in food formulations; hazelnuts are cultivated raw nuts for ingredient supply. T… | captive (not on the merchant market) |
| T-3 Custom specialty fats and oils | P1-4 Custom chocolate products and… | candidate | different product |  | A could be an input for B (AI) | 0.40 | Activity A supplies tailored food fats for manufacturers to use as functional ingredients in food products. Activity B sells finished chocolate for eating or g… |  |
| T-2 Yeast-derived cocoa-butter al… | P1-11 Hazelnut cultivation | candidate | similar product, possibly substitutable | ●○○ |  | 0.40 | The yeast-derived fat is intended to replicate cocoa butter for use in confectionery, while hazelnuts are a food ingredient supplied for food production. They … | captive (not on the merchant market) |
| T-2 Yeast-derived cocoa-butter al… | P1-5 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is an ingredient intended for confectionery manufacture, while B is finished chocolate sold as a gift or promotional item. Customers would not use the ingred… |  |
| T-2 Yeast-derived cocoa-butter al… | P1-3 Cream-filled, chocolate-cover… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.39 | A is designed to perform cocoa butter’s function as a confectionery fat, while B is a finished chocolate-covered wafer confectionery. They are different produc… |  |
| T-3 Custom specialty fats and oils | P1-1 Packaged chocolate bars and c… | candidate | different product |  | A could be an input for B (AI) | 0.36 | Activity A is a developing intermediate fat ingredient intended to provide functionality in food manufacturing, while Activity B is finished chocolate confecti… |  |
| T-3 Custom specialty fats and oils | P1-2 Packaged chocolate and chocol… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.35 | A is a tailored food-fat ingredient for use in food products, while B is ready-to-eat chocolate confectionery. They are not the same product, but A’s potential… |  |
| T-3 Custom specialty fats and oils | P1-3 Cream-filled, chocolate-cover… | candidate | different product |  | A could be an input for B (AI) | 0.28 | A is a food-fat ingredient intended to provide functionality in food products, while B is a finished confectionery product eaten as a snack or gift. They are n… |  |
| T-3 Custom specialty fats and oils | P1-8 Bistro food and beverages and… | candidate | different product |  | A could be an input for B (AI) | 0.27 | A develops specialty fats and oils intended as ingredients for food manufacturers, whereas B provides prepared food and beverages for consumption and event-spa… |  |
| T-1 Cocoa-free chocolate alternat… | P1-8 Bistro food and beverages and… | candidate | different product |  | A could be an input for B (AI) | 0.18 | A is a bulk chocolate-alternative ingredient used by manufacturers to make confectionery and other foods. B provides prepared food and beverages for consumptio… |  |

<details><summary>15 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.44): A is a bulk cocoa-free chocolate ingredient used by manufacturers to make food products, whereas B …
- T-1 Cocoa-free chocolate alternative i… ↔ P1-9 Non-food gifts and merchandise (sim. 0.26): Activity A is a bulk cocoa-free chocolate ingredient for manufacturers to use in food products. Act…
- T-1 Cocoa-free chocolate alternative i… ↔ P1-12 Electricity and heat generation fo… (sim. 0.20): A is a cocoa-free chocolate ingredient for use in food products, while B is electricity and heat ge…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-6 Cocoa-fruit beverages (sim. 0.48): A is a fat intended to replicate cocoa butter for use in confectionery, while B consists of beverag…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.39): A is an intermediate food fat intended for manufacturers to use as an ingredient in confectionery. …
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-8 Bistro food and beverages and even… (sim. 0.22): A is an ingredient for confectionery manufacturers, designed to function like cocoa butter. B provi…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-9 Non-food gifts and merchandise (sim. 0.24): A is an ingredient fat intended for confectionery manufacturing, while B consists of non-food gift …
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-10 Cocoa cultivation and post-harvest… (sim. 0.47): A is a food fat designed to replicate cocoa butter’s functionality for confectionery, while B is co…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P1-12 Electricity and heat generation fo… (sim. 0.24): A is a food fat intended to function as a cocoa-butter alternative in confectionery, whereas B gene…
- T-3 Custom specialty fats and oils ↔ P1-5 Corporate gifts and promotional ch… (sim. 0.35): A is a development-stage food-fat ingredient for manufacturers seeking particular fat functionality…
- T-3 Custom specialty fats and oils ↔ P1-6 Cocoa-fruit beverages (sim. 0.37): A consists of tailored fats and oils intended to provide fat functionality in food products; B cons…
- T-3 Custom specialty fats and oils ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.26): A is a food ingredient in development, intended to provide fat functionality in manufactured food p…
- T-3 Custom specialty fats and oils ↔ P1-9 Non-food gifts and merchandise (sim. 0.29): A is a food ingredient designed to provide specific fat functionality in food products, whereas B c…
- T-3 Custom specialty fats and oils ↔ P1-10 Cocoa cultivation and post-harvest… (sim. 0.42): A develops tailored food fats and oils for use as ingredients in food products, while B grows cocoa…
- T-3 Custom specialty fats and oils ↔ P1-12 Electricity and heat generation fo… (sim. 0.32): A develops specialty fats and oils for use as ingredients in food products, while B generates elect…

</details>

### Barry Callebaut

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-free chocolate alternat… | P2-9 Cocoa-free chocolate alternat… | candidate | same product | ●●● |  | 0.78 | Both activities supply cocoa-free chocolate-alternative ingredients for food manufacturers to use in coatings and finished foods. The descriptions differ on fo… |  |
| T-1 Cocoa-free chocolate alternat… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● |  | 0.69 | Both are chocolate-type ingredients supplied to manufacturers for use in coatings, fillings, confectionery, bakery products, and ice cream. A is cocoa-free whi… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●● |  | 0.68 | A is a yeast-derived fat designed to replicate cocoa butter’s composition and functionality, while B consists of sunflower-seed-based chocolate-like ingredient… |  |
| T-1 Cocoa-free chocolate alternat… | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●○○ |  | 0.64 | Both are professional chocolate-type ingredients used in coatings, fillings, confectionery, bakery and ice-cream applications. A is cocoa-free while B contains… |  |
| T-1 Cocoa-free chocolate alternat… | P2-4 Confectionery coatings, filli… | candidate | same product | ●●○ | A could be an input for B (AI) | 0.60 | Both activities supply intermediate confectionery ingredients for manufacturers and professional food businesses. Activity A is a cocoa-free chocolate alternat… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.60 | A is designed to replicate cocoa butter’s composition and functionality for confectionery, while B includes cocoa butter as well as cocoa liquor and powder. A … |  |
| T-1 Cocoa-free chocolate alternat… | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.59 | Both are intermediate ingredients for food manufacturers and can be used in confectionery and bakery applications, including chocolate products. The cocoa-free… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● |  | 0.53 | The yeast-derived fat is designed to replicate cocoa butter’s composition and function, while industrial chocolate and couverture are chocolate formulations us… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.52 | A is a cocoa-butter alternative intended for use in confectionery, while B includes chocolate and cocoa ingredients used by professional food makers. A could p… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-8 Cocoa-fruit ingredients | candidate | different product |  | A could be an input for B (rule) | 0.52 | A is a fat intended to replicate cocoa butter’s composition and functionality in confectionery, while B consists of cocoa-fruit pulp, juice and concentrates us… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-4 Confectionery coatings, filli… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.52 | A is a cocoa-butter alternative intended as a fat ingredient in confectionery, while B comprises finished coatings and other confectionery components. A could … |  |
| T-3 Custom specialty fats and oils | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●● |  | 0.50 | Both are intermediate food ingredients intended for manufacturers to use in finished foods, but they have different compositions and functions: A provides tail… |  |
| T-1 Cocoa-free chocolate alternat… | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.49 | A is a cocoa-free chocolate alternative ingredient used in confectionery and other foods, while B comprises mixes and ingredients for preparing beverages. They… |  |
| T-1 Cocoa-free chocolate alternat… | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.48 | Both are intermediate ingredients used by food manufacturers in confectionery, bakery and ice cream products, including fillings and inclusions. Cocoa-free cho… |  |
| T-3 Custom specialty fats and oils | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● |  | 0.48 | Both are intermediate food ingredients for manufacturers, and specialty fats may plausibly replace some of the fat functionality in particular chocolate formul… |  |
| T-3 Custom specialty fats and oils | P2-4 Confectionery coatings, filli… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.48 | A develops tailored food fats for use in food products, while B includes coatings and fillings that are confectionery products. A’s fats could plausibly replac… |  |
| T-3 Custom specialty fats and oils | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.46 | Both are food ingredients used by manufacturers for fat functionality in food products. The yeast-derived specialty fats are designed as tailored fats and pote… |  |
| T-1 Cocoa-free chocolate alternat… | P2-6 Biscuit, cookie, cereal and m… | candidate | similar product, possibly substitutable | ●●○ |  | 0.45 | Both are intermediate ingredients sold to food manufacturers and can be used in some of the same finished products, including bakery items and ice cream. Their… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.45 | The yeast-derived fat is intended to replicate cocoa butter’s composition and functionality for use in confectionery, while the other activity supplies nut ing… |  |
| T-3 Custom specialty fats and oils | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.42 | A is a tailored food-fat ingredient for manufacturers, while B comprises professional chocolate and cocoa ingredients. A’s potential animal- or palm-fat replac… |  |
| T-3 Custom specialty fats and oils | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.41 | A develops tailored food fats, including potential replacements for palm or animal fats; B supplies nut pastes, butters, and other nut preparations used as ing… |  |
| T-3 Custom specialty fats and oils | P2-7 Instant beverage mixes and mi… | candidate | different product |  | A could be an input for B (AI) | 0.39 | A comprises tailored food fats intended to provide particular fat functionality in manufactured foods. B comprises beverage mixes and milk-based drink ingredie… |  |
| T-2 Yeast-derived cocoa-butter al… | P2-6 Biscuit, cookie, cereal and m… | candidate | similar product, possibly substitutable | ●●○ |  | 0.38 | A is a food fat intended to replicate cocoa butter’s functionality in confectionery, while B consists of baked, cereal and meringue pieces used as inclusions i… |  |
| T-1 Cocoa-free chocolate alternat… | P2-8 Cocoa-fruit ingredients | unclear | different product |  |  | 0.55 | A is a cocoa-free chocolate alternative supplied for use in confectionery and other food products, while B consists of cocoa-fruit pulp, juice, concentrate and… |  |

<details><summary>6 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P2-10 Professional chocolate and pastry … (sim. 0.38): A is a cocoa-free chocolate ingredient used in manufacturing food products, while B provides practi…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P2-7 Instant beverage mixes and milk-ba… (sim. 0.40): The yeast-derived fat is intended to replicate cocoa butter for use in confectionery, while the mix…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P2-10 Professional chocolate and pastry … (sim. 0.37): A is a food fat intended as an ingredient in confectionery, while B is training that provides pract…
- T-3 Custom specialty fats and oils ↔ P2-6 Biscuit, cookie, cereal and mering… (sim. 0.33): A provides tailored fats and oils for fat functionality in food products, whereas B provides biscui…
- T-3 Custom specialty fats and oils ↔ P2-8 Cocoa-fruit ingredients (sim. 0.40): Custom specialty fats and oils provide fat functionality in food products, while cocoa-fruit ingred…
- T-3 Custom specialty fats and oils ↔ P2-10 Professional chocolate and pastry … (sim. 0.35): Activity A develops tailored food fats for use as ingredients in food products. Activity B provides…

</details>

### Bahlsen

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-free chocolate alternat… | P3-5 Private-label biscuits, wafer… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.45 | The cocoa-free ingredient is used in coatings, fillings and inclusions for confectionery, biscuits and wafers, while B supplies finished biscuits, wafers and c… |  |
| T-1 Cocoa-free chocolate alternat… | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be an input for B (AI) | 0.43 | A is a bulk cocoa-free chocolate ingredient for use in manufacturing, while B is retail sale of packaged finished foods to consumers. Consumers buying the pack… |  |
| T-2 Yeast-derived cocoa-butter al… | P3-5 Private-label biscuits, wafer… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.42 | A is a confectionery fat ingredient designed to replicate cocoa butter’s composition and functionality, while B consists of finished sweet products. A is not i… |  |
| T-3 Custom specialty fats and oils | P3-5 Private-label biscuits, wafer… | candidate | different product |  | A could be an input for B (AI) | 0.41 | A develops specialty fats and oils for use as ingredients in food products, while B supplies finished biscuits, wafers and confectionery for consumers to eat. … |  |
| T-1 Cocoa-free chocolate alternat… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.40 | The cocoa-free chocolate alternative is an ingredient used in coatings, fillings and inclusions, while Activity B is a finished biscuit-based snack bar. They a… |  |
| T-2 Yeast-derived cocoa-butter al… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.40 | A is an ingredient intended to perform the role of cocoa butter in confectionery, while B consists of finished baked snacks and treats. They are not the same p… |  |
| T-3 Custom specialty fats and oils | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be an input for B (AI) | 0.40 | A is a tailored fat ingredient intended for food manufacturers to use in making food products, whereas B is the retail sale of packaged foods for consumer cons… |  |
| T-1 Cocoa-free chocolate alternat… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.40 | The cocoa-free chocolate alternative is an ingredient used in coatings, fillings and inclusions for baked goods, while B is a ready-to-eat cake. They are not t… |  |
| T-1 Cocoa-free chocolate alternat… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.38 | A is a cocoa-free chocolate alternative ingredient used in baked goods and other confectionery, while B is finished biscuits, wafers and pastries. They are dif… |  |
| T-2 Yeast-derived cocoa-butter al… | P3-7 Retail sale of packaged foods | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.37 | A is a cocoa-butter alternative intended for use in confectionery, while B sells finished packaged foods, including chocolate and pralines. They are not the sa… |  |
| T-3 Custom specialty fats and oils | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A supplies or develops functional fats and oils for use as ingredients in food manufacturing. B consists of finished baked snacks eaten by consumers; the fact … |  |
| T-1 Cocoa-free chocolate alternat… | P3-4 Seasonal baked goods | candidate | different product |  | A could be an input for B (AI) | 0.37 | A is a bulk ingredient used by manufacturers in confectionery and other foods, while B consists of finished seasonal biscuits, cakes and related baked goods ea… |  |
| T-2 Yeast-derived cocoa-butter al… | P3-3 Packaged cakes | candidate | different product |  | A could be an input for B (AI) | 0.36 | A is an intermediate food fat intended to replicate cocoa butter for use in confectionery manufacturing; B is a ready-to-eat packaged cake eaten as a snack or … |  |
| T-2 Yeast-derived cocoa-butter al… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.36 | The yeast-derived fat is intended to replicate cocoa butter’s composition and function in confectionery, while the bars are finished snacks eaten by consumers.… |  |
| T-2 Yeast-derived cocoa-butter al… | P3-4 Seasonal baked goods | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.35 | The yeast-derived fat is intended to perform cocoa butter’s function in confectionery, while the seasonal baked goods are finished snacks and treats. They are … |  |
| T-3 Custom specialty fats and oils | P3-4 Seasonal baked goods | candidate | different product |  | A could be an input for B (AI) | 0.34 | A comprises fats and oils intended as functional ingredients for food manufacturers, whereas B comprises finished seasonal baked goods eaten as snacks or treat… |  |
| T-3 Custom specialty fats and oils | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.34 | The fats are ingredients intended to provide particular functionality in food products, while the cakes are finished snacks or desserts. They are not the same … |  |
| T-3 Custom specialty fats and oils | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.29 | A is a tailored food-fat ingredient intended for use by food manufacturers, while B is a packaged biscuit-and-chocolate snack eaten by consumers. The descripti… |  |

<details><summary>6 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.37): A is a bulk cocoa-free chocolate ingredient used by manufacturers in confectionery and other foods;…
- T-1 Cocoa-free chocolate alternative i… ↔ P3-8 Branded clothing and fabric bags (sim. 0.24): A is a bulk cocoa-free chocolate alternative ingredient used in food manufacturing, while B consist…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.34): A is an ingredient fat intended for confectionery manufacturing, while B consists of finished snack…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P3-8 Branded clothing and fabric bags (sim. 0.27): The yeast-derived fat is an ingredient for confectionery, intended to perform the function of cocoa…
- T-3 Custom specialty fats and oils ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.35): A is a food ingredient developed for manufacturers to use for fat functionality in food products, w…
- T-3 Custom specialty fats and oils ↔ P3-8 Branded clothing and fabric bags (sim. 0.28): Custom specialty fats and oils are food ingredients intended to provide fat functionality in food p…

</details>

### FRoSTA

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-3 Custom specialty fats and oils | P4-5 Frozen food production and su… | candidate | not enough information |  | A could be an input for B (AI) | 0.50 | A is a pipeline platform for specialty fats and oils intended to provide particular fat functionality in food products. B supplies frozen food products, but it… |  |
| T-3 Custom specialty fats and oils | P4-2 Customer-branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.46 | A supplies tailored food fats and oils for use as ingredients, while B manufactures finished frozen foods for sale to consumers. Customers would not use the fa… |  |
| T-3 Custom specialty fats and oils | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.42 | A is a tailored food-fat ingredient intended to provide specific fat functionality in food manufacturing, while B consists of finished frozen foods for prepara… |  |
| T-3 Custom specialty fats and oils | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.40 | A develops specialty fats and oils for use as functional ingredients in food manufacturing, while B supplies a range of finished frozen foods for household del… |  |
| T-3 Custom specialty fats and oils | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.38 | Activity A is a developing food-fat ingredient intended to provide fat functionality in food products, while Activity B consists of branded finished frozen foo… |  |
| T-3 Custom specialty fats and oils | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.34 | A develops specialty fats for use as ingredients in food products, including potential replacements for animal fats. B sells finished frozen meals and other fo… |  |
| T-2 Yeast-derived cocoa-butter al… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.34 | A is an ingredient fat intended to replace cocoa butter in confectionery, while B is a range of finished frozen foods for professional kitchens. Their stated f… |  |
| T-3 Custom specialty fats and oils | P4-1 Frozen ready meals, fish, veg… | candidate | different product |  | A could be an input for B (AI) | 0.32 | A develops specialty fats and oils for food manufacturers to use as ingredients for particular fat functionality. B comprises finished frozen meals and frozen … |  |
| T-1 Cocoa-free chocolate alternat… | P4-2 Customer-branded frozen foods | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.32 | A is a cocoa-free chocolate alternative ingredient used in confectionery and other foods, while B makes finished frozen foods, including meals and snacks. They… |  |
| T-2 Yeast-derived cocoa-butter al… | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.31 | A is a confectionery fat designed to replicate cocoa butter’s composition and function, while B is a varied range of frozen foods. They are not the same produc… |  |
| T-1 Cocoa-free chocolate alternat… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.30 | A is a bulk cocoa-free chocolate ingredient used by manufacturers in confectionery and other food products. B is a range of finished frozen foods for professio… |  |
| T-2 Yeast-derived cocoa-butter al… | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ |  | 0.28 | A is a food fat intended to replicate cocoa butter for use in confectionery, while B includes frozen meals and other frozen foods for household meals and prepa… |  |
| T-1 Cocoa-free chocolate alternat… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.28 | A is a cocoa-free chocolate ingredient used by manufacturers in confectionery and other food products, while B is a range of frozen foods supplied for resale a… |  |
| T-2 Yeast-derived cocoa-butter al… | P4-1 Frozen ready meals, fish, veg… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.25 | The yeast-derived fat is intended to replicate cocoa butter’s composition and functionality for use in confectionery, while B includes finished frozen foods an… |  |
| T-2 Yeast-derived cocoa-butter al… | P4-5 Frozen food production and su… | unclear | not enough information |  |  | 0.35 | A is a specific fat intended to replicate cocoa butter for confectionery, while B supplies frozen products for downstream food production but does not identify… |  |

<details><summary>15 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P4-1 Frozen ready meals, fish, vegetabl… (sim. 0.26): A is a cocoa-free chocolate ingredient used by manufacturers in confectionery, bakery and other pro…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-3 Branded frozen foods (sim. 0.27): A is a cocoa-free chocolate ingredient used by food manufacturers in confectionery and other foods,…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-5 Frozen food production and supply … (sim. 0.34): A is a cocoa-free chocolate ingredient for use in confectionery and other food applications. B supp…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.29): A is a bulk cocoa-free chocolate ingredient for use in manufacturing confectionery and other foods,…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-8 Frozen meals and team meal boxes (sim. 0.22): A is a cocoa-free chocolate ingredient used in manufacturing confectionery and other foods, while B…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-9 Food product development and assor… (sim. 0.33): A is a cocoa-free chocolate alternative ingredient used in food products, while B is a consulting s…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-10 Non-food merchandise (sim. 0.27): A is a bulk ingredient used by food manufacturers to make confectionery and other foods. B consists…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P4-2 Customer-branded frozen foods (sim. 0.38): A is an ingredient fat intended to replace cocoa butter in confectionery, while B consists of finis…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P4-3 Branded frozen foods (sim. 0.30): A is an intermediate food fat intended for confectionery manufacturers to use in confectionery prod…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P4-8 Frozen meals and team meal boxes (sim. 0.24): A is a food fat designed to function as cocoa butter in confectionery manufacturing, while B consis…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P4-9 Food product development and assor… (sim. 0.37): A is a food fat intended as an ingredient in confectionery, whereas B is a consulting service suppo…
- T-2 Yeast-derived cocoa-butter alterna… ↔ P4-10 Non-food merchandise (sim. 0.29): The yeast-derived fat is intended as an ingredient for confectionery, whereas the merchandise consi…
- T-3 Custom specialty fats and oils ↔ P4-8 Frozen meals and team meal boxes (sim. 0.28): A supplies tailored fats and oils intended as ingredients for food manufacturers, while B supplies …
- T-3 Custom specialty fats and oils ↔ P4-9 Food product development and assor… (sim. 0.50): A develops specialty fats and oils intended to provide fat functionality in food products. B provid…
- T-3 Custom specialty fats and oils ↔ P4-10 Non-food merchandise (sim. 0.32): A is a food ingredient under development for use in food products requiring particular fat function…

</details>

## Calibration: closest pairs that were screened out

If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.

- 0.50 · T-3 Custom specialty fats and oils ↔ P4-9 Food product development and assortment… (FRoSTA)
- 0.48 · T-2 Yeast-derived cocoa-butter alternative ↔ P1-6 Cocoa-fruit beverages (Ritter Sport)
- 0.47 · T-2 Yeast-derived cocoa-butter alternative ↔ P1-10 Cocoa cultivation and post-harvest oper… (Ritter Sport)
- 0.44 · T-1 Cocoa-free chocolate alternative ingred… ↔ P1-7 Chocolate-making workshops and visitor … (Ritter Sport)
- 0.42 · T-3 Custom specialty fats and oils ↔ P1-10 Cocoa cultivation and post-harvest oper… (Ritter Sport)
- 0.40 · T-3 Custom specialty fats and oils ↔ P2-8 Cocoa-fruit ingredients (Barry Callebaut)
- 0.40 · T-2 Yeast-derived cocoa-butter alternative ↔ P2-7 Instant beverage mixes and milk-based b… (Barry Callebaut)
- 0.39 · T-2 Yeast-derived cocoa-butter alternative ↔ P1-7 Chocolate-making workshops and visitor … (Ritter Sport)
- similarity of candidate pairs: min 0.18 · median 0.41 · max 0.78
- similarity of screened out pairs: min 0.20 · median 0.32 · max 0.50

## Example: exactly what the comparison call received

```
ACTIVITY A
Product: Cocoa-free chocolate alternative ingredient
Description: Commercially produced ingredient supplied as chips or liquid in tanks, in milk, vegan, semi-sweet dark, white and no-added-sugar formulations. The no-added-sugar formulation uses maltitol instead of added sugar. Published minimum orders for four recipes are 12 tonnes. Country-by-country availability of the bulk formulations is not stated.
Intended use: Used by food manufacturers in coatings, fillings, inclusions, bars, pralines, biscuits, cereals, wafers, hollow figures and ice cream.
Main inputs: not stated
Level of trade: intermediate products
Direct customers: manufacturers / processors (Food, confectionery and bakery manufacturers; the sources also identify artisan confectionery customers. Direct purchasers for some retail, bakery, travel-catering and promotional applications are not disclosed.)
End users: consumers
Sales channels: B2B ingredient supply and direct sales enquiries. The ingredient is used in products made and sold downstream by manufacturers and partners; the sources do not establish [name removed] as the direct seller of those finished consumer products.
Status: on the market

ACTIVITY B
Product: Packaged chocolate bars and chocolate confectionery
Description: Ready-to-eat chocolate products, including filled, nut, vegan and protein varieties, miniatures, cubes, seasonal products and gift assortments. Sold through retail and wholesale channels.
Intended use: Eating as confectionery or giving as a gift.
Main inputs: cocoa, sugar, milk ingredients, nuts, other filling ingredients
Level of trade: finished products
Direct customers: retailers, wholesalers / distributors (Food retailers and trade customers, including wholesale and distribution customers; the sources do not allocate all sales between the group company and local sales companies.)
End users: consumers
Sales channels: Food retail, wholesale and distribution, including travel retail.
Status: on the market
```

## Run summary

- names removed before any comparison: 57 name variants (list in the .json file)
- comparison calls blocked or failed: 0 (kept as 'unclear', never screened out)
- search: 5 calls (5 from cache) · tokens 0 in / 0 out · USD 0.0000
- extract: 5 calls (4 from cache) · tokens 4,216 in / 1,265 out · USD 0.0010
- embed: 5 calls (4 from cache) · tokens 235 in / 0 out · USD 0.0000
- compare: 120 calls (0 from cache) · tokens 152,661 in / 19,558 out · USD 0.0250
- total: USD 0.0261 (token costs only, without web search fees)
