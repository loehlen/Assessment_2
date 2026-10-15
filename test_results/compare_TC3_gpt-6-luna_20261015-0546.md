# Factual comparison TC3: Koa (20261015-0546)

Models: search saved gpt-6.1-sol · extraction gpt-6-luna · comparison gpt-6-luna · text-embedding-3-large  
Thresholds: unclear ≥ 0.5 · input match ≥ 0.5 · resale ≥ 0.5

## Benchmark check (spec section 13)

6 ✔ as expected · 0 ◐ kept in another form · **0 ✖ missed by the comparison** · 0 ∅ activity not found · 1 ⚠ false positives in a control row

Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py need adjusting: compare with the activity overview below).

| Check | Portco | Pair | Expected | Result | Pairs | Detail |
|---|---|---|---|---|---|---|
| TC3-1 | Barry Callebaut | Cabosse Naturals ↔ Koa ingredients (central overlap) | horizontal | ✔ | T-1↔P2-8, T-2↔P2-8, T-3↔P2-8, T-4↔P2-8 (+2) | 6 of 6 matching pairs as expected |
| TC3-2 | Barry Callebaut | Koa ingredients → BC chocolate (vertical candidate) | vertical | ✔ | T-1↔P2-1, T-1↔P2-3, T-1↔P2-4, T-1↔P2-7 (+22) | 26 of 42 matching pairs as expected |
| TC3-3 | Barry Callebaut | Koa drinks ↔ BC beverages (unclear is fine) | kept | ✔ | T-6↔P2-3, T-6↔P2-5, T-6↔P2-7, T-6↔P2-8 (+3) | 7 of 8 matching pairs as expected |
| TC3-4 | Ritter Sport | CacaoVida ↔ Koa shots | horizontal | ✔ | T-6↔P1-5, T-6↔P1-7, T-7↔P1-5, T-7↔P1-7 | 4 of 6 matching pairs as expected |
| TC3-5 | Ritter Sport | Koa ingredients → Ritter (chocolate, CacaoVida) | vertical | ✔ | T-1↔P1-1, T-1↔P1-5, T-1↔P1-7, T-1↔P1-9 (+28) | 32 of 48 matching pairs as expected |
| TC3-6 | Bahlsen | Koa ingredients → bakery (vertical candidate) | vertical | ✔ | T-1↔P3-1, T-1↔P3-4, T-1↔P3-5, T-1↔P3-8 (+21) | 25 of 36 matching pairs as expected |
| TC3-7 | FRoSTA | control (possible false positive: fruit ingredient → frozen food) | screened out | ⚠ | T-1↔P4-1, T-1↔P4-2, T-1↔P4-3, T-1↔P4-5 (+29) | 33 of 80 pairs kept: check whether these are false positives |

## Activity overview (stages ①–②)

### Target: Koa (8 activities, 15 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| T-1 | not stated | Cocoa-fruit juice | intermediate products | manufacturers / processors, wholesalers / distributors, other businesses | Germany, Austria, France, Net… | on the market | [3, 8, 9] |
| T-2 | not stated | Cocoa-fruit juice concentrate | intermediate products | manufacturers / processors, wholesalers / distributors, other businesses | Germany, Austria, France, Net… | on the market | [3, 4, 8, 9] |
| T-3 | not stated | Dried cocoa-fruit pulp | intermediate products | manufacturers / processors, wholesalers / distributors | Germany, Austria, France, Net… | on the market | [3, 8, 9] |
| T-4 | not stated | Dried cocoa-fruit pulp flakes | wholesale / distribution | retailers | not stated | on the market | [3] |
| T-5 | not stated | Dried cocoa-fruit pulp mixed with cocoa powd… | intermediate products | manufacturers / processors, wholesalers / distributors | not stated | on the market | [5] |
| T-6 | not stated | Ready-to-drink cocoa-fruit juice | retail | consumers | Ghana | on the market | [6] |
| T-7 | not stated | Beverage shots | retail | consumers | Germany | on the market | [7] |
| T-8 | not stated | Cocoa-fruit pulp ingredient for balsamic vin… | intermediate products | manufacturers / processors | Germany | on the market | [11] |

### Portco 1: Ritter Sport (9 activities, 23 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P1-1 | not stated | Packaged chocolate bars and other chocolate … | finished products | retailers, wholesalers / distributors | Germany, Italy, United Kingdo… | on the market | [2, 3, 4, 5] |
| P1-2 | Company shops and webshop | Chocolate confectionery sold directly to con… | retail | consumers | Germany | on the market | [8, 9] |
| P1-3 | not stated | Chocolate-covered wafer rolls with cream fil… | finished products | not stated | not stated | on the market | [6, 7] |
| P1-4 | Business-customer sales | Corporate gifts and promotional chocolate | finished products | other businesses | not stated | on the market | [10] |
| P1-5 | not stated | Cocoa-fruit beverages | finished products | consumers, other businesses | Germany | on the market | [11, 12] |
| P1-6 | Visitor experiences | Chocolate-making workshops and educational v… | services | consumers, other businesses | Germany | on the market | [9] |
| P1-7 | Bunte Schokowelt | Prepared food and beverages for on-site cons… | services | consumers, other businesses | Germany | on the market | [8] |
| P1-8 | Company shops | Non-food branded merchandise and gift items | retail | consumers | Germany | on the market | [9] |
| P1-9 | Agriculture and cocoa su… | Cocoa and hazelnuts grown for the group's su… | raw materials | internal use (captive) | not stated | on the market | [13, 14] |

### Portco 2: Barry Callebaut (10 activities, 21 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P2-1 | Global Chocolate | Industrial chocolate and couverture | intermediate products | manufacturers / processors | not stated | on the market | [1, 2] |
| P2-2 | Global Chocolate | Professional and artisan chocolate and cocoa… | wholesale / distribution | wholesalers / distributors, other businesses | Belgium, Czechia, France, Ger… | on the market | [3, 19] |
| P2-3 | Global Cocoa | Processed cocoa ingredients | intermediate products | manufacturers / processors, other businesses, internal use (captive) | not stated | on the market | [1] |
| P2-4 | Global Chocolate | Chocolate fillings, inclusions and decoratio… | intermediate products | manufacturers / processors, other businesses, wholesalers / distributors | not stated | on the market | [4] |
| P2-5 | Global Chocolate | Nut and almond ingredients | intermediate products | manufacturers / processors, other businesses, wholesalers / distributors | not stated | on the market | [5, 6] |
| P2-6 | Global Chocolate | Bakery, confectionery and dessert inclusions… | intermediate products | manufacturers / processors, other businesses, wholesalers / distributors | not stated | on the market | [7, 8, 9, 10] |
| P2-7 | Global Chocolate | Professional beverage mixes and ingredients | intermediate products | retailers, wholesalers / distributors, other businesses | not stated | on the market | [11, 12, 13] |
| P2-8 | Global Chocolate | Cocoa-fruit ingredients | intermediate products | manufacturers / processors, other businesses | not stated | on the market | [14] |
| P2-9 | Global Chocolate | Cocoa-free chocolate alternative ingredients | intermediate products | manufacturers / processors | not stated | on the market | [15] |
| P2-10 | Corporate and other | Professional chocolate education and training | services | consumers, other businesses | Belgium, France, Italy, Polan… | on the market | [17] |

### Portco 3: Bahlsen (9 activities, 19 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P3-1 | not stated | Packaged biscuits, cookies, wafers and sweet… | finished products | retailers, wholesalers / distributors, consumers | Germany, United States, Unite… | on the market | [1, 2, 4, 5, 12, 17] |
| P3-2 | not stated | Biscuit-based snack bars | finished products | retailers, wholesalers / distributors, consumers | Germany, United States, Unite… | on the market | [1, 4, 5, 11] |
| P3-3 | not stated | Packaged cakes | finished products | retailers, wholesalers / distributors | Germany | on the market | [1, 6] |
| P3-4 | not stated | Seasonal biscuits and baked goods | finished products | retailers, wholesalers / distributors, consumers | Germany | on the market | [1, 5, 6] |
| P3-5 | not stated | Private-label biscuits, coffee pastries, waf… | finished products | retailers | not stated | on the market | [7, 8] |
| P3-6 | not stated | Private-label product development and custom… | services | retailers | not stated | on the market | [7, 8] |
| P3-7 | not stated | Organic fruit-and-nut bars and protein bars | finished products | consumers, retailers, not stated | Germany, Austria, not stated | on the market | [9, 10] |
| P3-8 | not stated | Biscuits, baked goods, snacks and selected t… | retail | consumers | Germany | on the market | [12, 13, 14] |
| P3-9 | not stated | Hoodies and fabric tote bags | retail | consumers | Germany, Austria | on the market | [10, 15, 16] |

### Portco 4: FRoSTA (10 activities, 14 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| P4-1 | not stated | Branded frozen meals, fish, vegetables, frui… | finished products | retailers | Germany, Austria, Italy, Pola… | on the market | [1, 3] |
| P4-2 | COPACK | Customer-brand frozen foods | finished products | retailers, wholesalers / distributors | not stated | on the market | [3, 4] |
| P4-3 | COPACK | Branded frozen foods | finished products | retailers, wholesalers / distributors | not stated | on the market | [5] |
| P4-4 | FRoSTA Foodservice | Frozen foods for professional kitchens | finished products | wholesalers / distributors, other businesses | Germany, Italy, Poland | on the market | [1, 6, 7, 8] |
| P4-5 | industrial business | Frozen food supplied to industrial customers | intermediate products | manufacturers / processors | not stated | on the market | [1] |
| P4-6 | not stated | Frozen foods supplied to home-delivery busin… | finished products | other businesses | not stated | on the market | [1, 4, 9] |
| P4-7 | not stated | Frozen meals, fish, vegetables and herbs sol… | retail | consumers | Germany, Austria | on the market | [10, 11] |
| P4-8 | not stated | Frozen meals and meal boxes for workplace te… | finished products | other businesses | Germany | on the market | [12] |
| P4-9 | COPACK and FRoSTA Foodse… | Product development and assortment consulting | services | retailers, wholesalers / distributors, other businesses | not stated | on the market | [7, 13] |
| P4-10 | not stated | Non-food merchandise | retail | consumers | Germany, Austria | on the market | [11, 14] |

## Factual comparison (stage ③)

304 pairs: 162 candidates · 9 unclear · 133 screened out

### Ritter Sport

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-6 Ready-to-drink cocoa-fruit ju… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.83 | Both are finished cocoa-fruit beverages intended to be consumed as drinks, and the cocoa-fruit juice in A could plausibly be switched with the juice-based lemo… | no EEA overlap |
| T-1 Cocoa-fruit juice | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.74 | A is an ingredient used in drinks and food, while B is a finished ready-to-drink beverage made from cocoa-fruit juice. For the specific purpose of drinking, A … |  |
| T-2 Cocoa-fruit juice concentrate | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.71 | A is a concentrated ingredient used by food manufacturers, while B consists of finished drinks for consumption. The products differ in form and intended use, b… |  |
| T-3 Dried cocoa-fruit pulp | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (rule) | 0.61 | A is a dried food ingredient used to sweeten, flavour or add texture to foods, while B consists of ready-to-drink beverages. They are different product types, … |  |
| T-4 Dried cocoa-fruit pulp flakes | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ |  | 0.59 | Both are cocoa-fruit products intended for consumption, but A is a dried culinary flake and B consists of ready-to-drink beverages. Consumers might use the fla… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P1-5 Cocoa-fruit beverages | candidate | different product |  | A could be an input for B (AI and rule) | 0.58 | A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B consists of ready-to-drink cocoa-fruit beverages. Their uses differ: the ingredient i… |  |
| T-4 Dried cocoa-fruit pulp flakes | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (rule) | 0.57 | A is a packaged dried cocoa-fruit pulp product for household culinary use, while B is cultivation of cocoa and hazelnuts to supply ingredients for chocolate an… | captive (not on the merchant market) |
| T-5 Dried cocoa-fruit pulp mixed … | P1-5 Cocoa-fruit beverages | candidate | different product |  | A could be an input for B (rule) | 0.57 | A is a dried ingredient for use in finished foods, while B consists of finished beverages for drinking. The descriptions do not indicate that customers would u… |  |
| T-7 Beverage shots | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.56 | Both are finished drinks intended to be consumed directly. The shots and the lemonade, iced tea, and sparkling alcoholic drink differ in format and, for some p… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI and rule) | 0.55 | A is cocoa-fruit pulp supplied as an ingredient for making balsamic vinegar, while B is cultivated cocoa and hazelnuts used as ingredients for chocolate and be… | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-9 Cocoa and hazelnuts grown for… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.54 | Dried cocoa-fruit pulp is a processed ingredient used in food products, while B grows cocoa and hazelnuts as raw ingredients for chocolate and beverages. Cocoa… | captive (not on the merchant market) |
| T-4 Dried cocoa-fruit pulp flakes | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be resold by B (rule) | 0.54 | Dried cocoa-fruit pulp flakes are used as a culinary ingredient, while the other activity sells finished chocolate confectionery for personal consumption or gi… |  |
| T-4 Dried cocoa-fruit pulp flakes | P1-1 Packaged chocolate bars and o… | candidate | different product |  | B could be resold by A (rule) | 0.54 | Dried cocoa-fruit pulp flakes are sold for household culinary use, while packaged chocolate products are finished confectionery for consumption or gifting. The… |  |
| T-1 Cocoa-fruit juice | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | A could be an input for B (rule); B could be an input for A (AI and rule) | 0.54 | A is processed cocoa-fruit juice used as a beverage ingredient and for culinary purposes. B is cultivated cocoa and hazelnut output used as agricultural ingred… | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.53 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to chocolate and confectionery, while B consists of finished chocolate confectio… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI and rule) | 0.53 | A is a finished drink for direct consumption or use in recipes, while B is the cultivation of cocoa and hazelnuts for ingredient supply. Customers would not us… | no EEA overlap; captive (not on the merchant market) |
| T-6 Ready-to-drink cocoa-fruit ju… | P1-1 Packaged chocolate bars and o… | candidate | different product |  | B could be resold by A (rule) | 0.52 | A is a ready-to-drink cocoa-fruit beverage used for drinking, mixing or cooking, while B is chocolate confectionery consumed as a sweet or bought as a gift. Sh… | no EEA overlap |
| T-5 Dried cocoa-fruit pulp mixed … | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI and rule) | 0.51 | A is a processed food ingredient made from dried cocoa-fruit pulp and cocoa powder, while B is cultivated cocoa and hazelnut output intended as raw ingredients… | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.48 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to chocolate and other foods, while Activity B sells finished chocolate confecti… |  |
| T-2 Cocoa-fruit juice concentrate | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | A could be an input for B (AI); B could be an input for A (rule) | 0.48 | A is concentrated cocoa-fruit juice used as a sweetener and food ingredient, while B is cultivation and post-harvest supply of cocoa and hazelnuts. The descrip… | captive (not on the merchant market) |
| T-2 Cocoa-fruit juice concentrate | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.47 | Cocoa-fruit juice concentrate is an ingredient and sweetener, whereas packaged chocolate is finished confectionery. The concentrate can be used in chocolate fi… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.47 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods, while B consists of finished chocolate confectionery for consumption or gi… |  |
| T-1 Cocoa-fruit juice | P1-1 Packaged chocolate bars and o… | candidate | different product |  | A could be an input for B (AI and rule) | 0.46 | Cocoa-fruit juice is an ingredient used in drinks and food or in culinary preparation, whereas packaged chocolate confectionery is a finished product eaten as … |  |
| T-3 Dried cocoa-fruit pulp | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.44 | Both are cocoa-derived food products that can be used in chocolate and confectionery, but dried cocoa-fruit pulp is an ingredient for sweetening, flavouring or… |  |
| T-3 Dried cocoa-fruit pulp | P1-3 Chocolate-covered wafer rolls… | candidate | different product |  | A could be an input for B (AI) | 0.43 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour, or add crunchy inclusions to foods, while chocolate-covered wafer rolls are finished confecti… |  |
| T-2 Cocoa-fruit juice concentrate | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.43 | Cocoa-fruit juice concentrate is an ingredient used by food manufacturers, while chocolate confectionery is a finished product for personal consumption or gift… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be an input for B (AI) | 0.42 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods, while B is finished chocolate confectionery for personal consumption or gi… |  |
| T-2 Cocoa-fruit juice concentrate | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.40 | A is a concentrated food ingredient used by manufacturers in foods and beverages. B is a workshop and educational visitor service; participants would not use t… |  |
| T-2 Cocoa-fruit juice concentrate | P1-4 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.39 | Cocoa-fruit juice concentrate is a fruit sweetener and food ingredient used in manufacturing, while the other activity supplies chocolate as a finished promoti… |  |
| T-7 Beverage shots | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●●● |  | 0.38 | Both are finished products for personal consumption, but beverage shots are drinks while chocolate confectionery is eaten as a sweet or given as a gift. The de… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.37 | The juice is a finished beverage consumed directly, while the bistro serves prepared drinks including hot chocolate. For some drink occasions, customers could … | no EEA overlap |
| T-2 Cocoa-fruit juice concentrate | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A is a concentrated ingredient used by food manufacturers and professional users, while B provides prepared food and drinks for immediate consumption and event… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.37 | A is a dried cocoa-pulp and cocoa-powder ingredient used in finished foods, while B is finished chocolate supplied as gifts or promotional items. They are diff… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.36 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for making finished foods. B is a workshop and educational visitor experience; customers participate … |  |
| T-2 Cocoa-fruit juice concentrate | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.36 | Cocoa-fruit juice concentrate is a sweetener and food ingredient, while the wafer rolls are finished confectionery, so they are not the same product. The conce… |  |
| T-1 Cocoa-fruit juice | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is a pasteurised cocoa-fruit juice sold as an ingredient for manufacturers and culinary professionals. B is a bistro service providing prepared food and drin… |  |
| T-7 Beverage shots | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.35 | A consists of finished, ready-to-drink beverage shots, while B consists of cultivated cocoa and hazelnuts supplied as ingredients for further production. Consu… | captive (not on the merchant market) |
| T-7 Beverage shots | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.35 | Both activities offer beverages for consumers to drink, and the bistro’s hot chocolate could serve a similar drinking occasion to the finished shots. The bistr… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be an input for B (AI) | 0.33 | Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas the bistro provides prepared food and beverages for consumption and event-space hire. … |  |
| T-7 Beverage shots | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ |  | 0.30 | Both are finished, directly consumable beverage or confectionery products, but shots are drinks while B is chocolate supplied as gifts or promotional items. Th… |  |
| T-3 Dried cocoa-fruit pulp | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be an input for B (AI) | 0.30 | Dried cocoa-fruit pulp is an ingredient used to make or flavour foods, while the bistro sells prepared food and drinks for consumption and event-space hire. Cu… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be an input for B (AI) | 0.27 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient used by food manufacturers and professional food users. B is prepared food and beverages for immediat… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P1-2 Chocolate confectionery sold … | unclear | different product |  |  | 0.52 | A is a ready-to-drink cocoa-fruit juice used as a beverage or ingredient in drinks and cooking, while B is finished chocolate confectionery for personal consum… | no EEA overlap |

<details><summary>29 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P1-2 Chocolate confectionery sold direc… (sim. 0.43): Cocoa-fruit juice is a beverage ingredient used in manufacturing and culinary preparation, while ch…
- T-1 Cocoa-fruit juice ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.38): Cocoa-fruit juice is a beverage ingredient for manufacturing and culinary use, while chocolate-cove…
- T-1 Cocoa-fruit juice ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.39): Cocoa-fruit juice is a beverage ingredient and culinary juice, while B supplies chocolate as promot…
- T-1 Cocoa-fruit juice ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.40): Cocoa-fruit juice is an ingredient used in beverages and food, while the other activity provides pa…
- T-1 Cocoa-fruit juice ↔ P1-8 Non-food branded merchandise and g… (sim. 0.27): Cocoa-fruit juice is a beverage ingredient used in food and drink production or culinary preparatio…
- T-2 Cocoa-fruit juice concentrate ↔ P1-8 Non-food branded merchandise and g… (sim. 0.26): Cocoa-fruit juice concentrate is a food ingredient used in manufacturing and professional food prep…
- T-3 Dried cocoa-fruit pulp ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.41): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food product…
- T-3 Dried cocoa-fruit pulp ↔ P1-8 Non-food branded merchandise and g… (sim. 0.27): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add crunchy inclusions to f…
- T-4 Dried cocoa-fruit pulp flakes ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.47): Dried cocoa-fruit pulp flakes are used as an ingredient or culinary food, while chocolate-covered w…
- T-4 Dried cocoa-fruit pulp flakes ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.46): Dried cocoa-fruit pulp flakes are sold for household culinary use, while B supplies chocolate as co…
- T-4 Dried cocoa-fruit pulp flakes ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.43): Dried cocoa-fruit pulp flakes are a food product used by households for culinary purposes. Workshop…
- T-4 Dried cocoa-fruit pulp flakes ↔ P1-7 Prepared food and beverages for on… (sim. 0.32): Dried cocoa-fruit pulp flakes are packaged goods for household culinary use, whereas the bistro pro…
- T-4 Dried cocoa-fruit pulp flakes ↔ P1-8 Non-food branded merchandise and g… (sim. 0.33): Dried cocoa-fruit pulp flakes are a food product for culinary use, while bags, keyrings and lanyard…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.42): A is a dried cocoa-fruit pulp and cocoa-powder ingredient used by food manufacturers and profession…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P1-8 Non-food branded merchandise and g… (sim. 0.22): Activity A is a food ingredient used by professional users to make finished foods; Activity B consi…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.43): A is a ready-to-drink cocoa-fruit beverage used for drinking, mixing or cooking; B is chocolate-cov…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.46): A is a ready-to-drink cocoa-fruit beverage used for drinking, cocktails, mocktails or cooking; B is…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.43): A is a ready-to-drink beverage used for drinking or cooking, while B consists of workshops and educ…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P1-8 Non-food branded merchandise and g… (sim. 0.33): A is a ready-to-drink cocoa-fruit beverage for drinking or use in recipes and cocktails. B consists…
- T-7 Beverage shots ↔ P1-1 Packaged chocolate bars and other … (sim. 0.37): Beverage shots are drinks consumed directly, while chocolate bars and other chocolate confectionery…
- T-7 Beverage shots ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.31): Beverage shots are drinks intended to be consumed directly, while chocolate-covered wafer rolls are…
- T-7 Beverage shots ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.29): Activity A supplies ready-to-drink beverage shots, while Activity B provides chocolate-making works…
- T-7 Beverage shots ↔ P1-8 Non-food branded merchandise and g… (sim. 0.29): Activity A consists of ready-to-drink beverage shots. Activity B consists of non-food items such as…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-1 Packaged chocolate bars and other … (sim. 0.43): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas packaged chocolate product…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-2 Chocolate confectionery sold direc… (sim. 0.44): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while Activity B offers finished c…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.37): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while chocolate-covered wafer roll…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.41): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B supplies finished chocolat…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.42): Activity A supplies cocoa-fruit pulp as an ingredient for making balsamic vinegar. Activity B provi…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.27): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas the merchandise consists o…

</details>

### Barry Callebaut

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-fruit juice | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (AI and rule) | 0.82 | Both activities include cocoa-fruit juice supplied as an ingredient for food and beverage uses. Activity B also offers other cocoa-fruit ingredients, but that … |  |
| T-3 Dried cocoa-fruit pulp | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.79 | Both activities supply cocoa-fruit pulp ingredients to food manufacturers, but A is specifically dried pulp in flakes or powder, while B also includes juice, c… |  |
| T-2 Cocoa-fruit juice concentrate | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.79 | Both activities include cocoa-fruit juice concentrate used as a sweetener and food ingredient by manufacturers. B also includes other cocoa-fruit ingredients, … |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.75 | Both activities include a powder blend of dried cocoa-fruit pulp and cocoa powder supplied as an ingredient for use in finished foods. Activity B also includes… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-8 Cocoa-fruit ingredients | candidate | same product | ●○○ | B could be an input for A (AI and rule) | 0.74 | Both activities include cocoa-fruit juice intended for use as a beverage; B also offers pulp, concentrate and a powder blend, but its juice overlaps with A’s r… | no EEA overlap |
| T-8 Cocoa-fruit pulp ingredient f… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); B could be an input for A (AI and rule) | 0.73 | Both activities supply cocoa-fruit pulp as an ingredient to food manufacturers, so their pulp offerings are the same type of ingredient. Activity B also includ… |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); B could be an input for A (rule) | 0.70 | Both activities involve cocoa-fruit pulp for food use, but A is dried flakes for household culinary use while B supplies pulp, juice, concentrate and a pulp-an… |  |
| T-3 Dried cocoa-fruit pulp | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.69 | Dried cocoa-fruit pulp is used to sweeten, flavour or add crunchy inclusions, while cocoa liquor, butter and powder serve broader cocoa-ingredient functions. T… |  |
| T-1 Cocoa-fruit juice | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.68 | Cocoa-fruit juice and processed cocoa ingredients are different products, but both are used by manufacturers and professional users in food and beverage applic… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); B could be an input for A (rule) | 0.66 | A is a dried cocoa-fruit pulp and cocoa-powder mixture, while B consists of processed cocoa ingredients such as liquor, butter and powder. Both are used as ing… |  |
| T-3 Dried cocoa-fruit pulp | P2-2 Professional and artisan choc… | candidate | different product |  | A could be an input for B (rule); A could be resold by B (rule) | 0.65 | Dried cocoa-fruit pulp is used as a sweetener, flavouring or crunchy inclusion, while professional chocolate and cocoa ingredients are chocolate products such … |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (rule) | 0.65 | Both are cocoa-derived food products used in culinary applications, but dried cocoa-fruit pulp flakes differ from cocoa liquor, butter and powder in compositio… |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (rule); B could be resold by A (rule) | 0.64 | Both are cocoa-derived food ingredients used in preparing culinary products, but dried cocoa-fruit pulp flakes and professional chocolate and cocoa ingredients… |  |
| T-2 Cocoa-fruit juice concentrate | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.62 | Cocoa-fruit juice concentrate is a fruit sweetener and ingredient, while cocoa liquor, butter and powder are processed cocoa ingredients with different charact… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (AI and rule) | 0.62 | A is cocoa-fruit pulp used specifically to make balsamic vinegar, while B comprises processed cocoa ingredients used mainly in chocolate, bakery, dessert and b… |  |
| T-1 Cocoa-fruit juice | P2-2 Professional and artisan choc… | candidate | different product |  | A could be an input for B (rule); A could be resold by B (rule) | 0.62 | Cocoa-fruit juice is a beverage and culinary ingredient, while the products in B are chocolate and cocoa ingredients such as couverture, callets and blocks. Al… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); B could be an input for A (rule) | 0.61 | A is a ready-to-drink beverage, while B consists of processed cocoa ingredients, so they are not the same product. Cocoa powder or liquor could plausibly be us… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.61 | Both are food ingredients used by manufacturers in chocolate, confectionery and other culinary products. Dried cocoa-fruit pulp provides sweetening, flavouring… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); A could be resold by B (rule) | 0.60 | Both are cocoa-based food ingredients supplied for professional food production, but A is a dried cocoa-fruit-pulp and cocoa-powder mixture while B comprises c… |  |
| T-3 Dried cocoa-fruit pulp | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.60 | Dried cocoa-fruit pulp is used to sweeten, flavour and add crunchy inclusions, while the sunflower-seed-based ingredients are chocolate-like alternatives used … |  |
| T-3 Dried cocoa-fruit pulp | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.60 | Both are food ingredients used by manufacturers and culinary professionals in confectionery and other foods, and dried cocoa-fruit pulp can provide flavour, sw… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●○○ | B could be resold by A (rule) | 0.60 | Both are cocoa-derived products used in food and drink, but A is a ready-to-drink juice while B consists of chocolate and cocoa ingredients intended for profes… | no EEA overlap |
| T-1 Cocoa-fruit juice | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.59 | Both are food and beverage ingredients used by manufacturers, but cocoa-fruit juice and industrial chocolate have different characteristics and typical uses. T… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.59 | A is primarily a dried cocoa-fruit pulp ingredient with a small proportion of cocoa powder, used in finished foods generally. B is a sunflower-seed-based choco… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-7 Professional beverage mixes a… | candidate | different product |  | B could be resold by A (rule) | 0.58 | A is a finished cocoa-fruit juice for direct drinking or culinary use, while B consists of mixes and ingredients used to prepare beverages, including fruit dri… | no EEA overlap |
| T-4 Dried cocoa-fruit pulp flakes | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ |  | 0.58 | Dried cocoa-fruit pulp flakes and industrial chocolate are different cocoa-derived food products with different characteristics and price positioning. Both can… |  |
| T-2 Cocoa-fruit juice concentrate | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); A could be resold by B (rule) | 0.58 | Both are professional food ingredients used in applications such as confectionery, bakery products and ice cream. Cocoa-fruit juice concentrate is a fruit swee… |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (rule) | 0.57 | Dried cocoa-fruit pulp flakes are used by households for culinary purposes, while the sunflower-seed-based ingredients are used by manufacturers in finished fo… |  |
| T-2 Cocoa-fruit juice concentrate | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.57 | Both are food ingredients used by manufacturers in products such as bakery goods and ice cream, and cocoa-fruit juice concentrate is used as a fruit sweetener.… |  |
| T-1 Cocoa-fruit juice | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.57 | Cocoa-fruit juice is a beverage ingredient used in drinks, while B includes fruit-drink mixes and cocoa or chocolate drink preparations. They are not the same … |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.56 | Both are cocoa-based ingredients used by food manufacturers, but dried cocoa-fruit pulp mixed with cocoa powder is distinct from industrial chocolate and couve… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●● | B could be an input for A (rule) | 0.55 | Both are food ingredients supplied to manufacturers, but the cocoa-fruit pulp is used to make balsamic vinegar, while the sunflower-seed-based ingredients are … |  |
| T-3 Dried cocoa-fruit pulp | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ |  | 0.55 | Dried cocoa-fruit pulp is used as a sweetening, flavouring or crunchy inclusion, while B supplies a range of inclusions, fillings, coatings and decorations for… |  |
| T-1 Cocoa-fruit juice | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.55 | Both are intermediate food ingredients used by manufacturers in finished foods and beverages. Cocoa-fruit juice is a juice ingredient for drinks and culinary u… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● |  | 0.55 | Cocoa-fruit pulp for vinegar and industrial chocolate or couverture are different ingredients with different characteristics and intended uses. Both are suppli… |  |
| T-2 Cocoa-fruit juice concentrate | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.53 | Both are food ingredients used in beverage preparation, and the cocoa-fruit juice concentrate can serve as a sweetener or ingredient in some drinks for which B… |  |
| T-3 Dried cocoa-fruit pulp | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.53 | Dried cocoa-fruit pulp and nut-based ingredients are different products, but both are used as sweetening, flavouring or inclusion ingredients in confectionery … |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | B could be resold by A (rule) | 0.53 | Dried cocoa-fruit pulp flakes are packaged for household culinary use, while B consists of chocolate components used as ingredients or decorations in food prod… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.53 | Both are cocoa-based food ingredients supplied for use in finished foods, but dried cocoa-fruit pulp mixed with cocoa powder is distinct from chocolate filling… |  |
| T-2 Cocoa-fruit juice concentrate | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.53 | Both are intermediate food ingredients used by manufacturers in confectionery and bakery products. Cocoa-fruit juice concentrate is a sweetener, while the sunf… |  |
| T-7 Beverage shots | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI); B could be resold by A (rule) | 0.52 | A consists of ready-to-drink beverage shots, while B consists mainly of mixes and ingredients that must be prepared into drinks. They differ in form and prepar… |  |
| T-4 Dried cocoa-fruit pulp flakes | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); B could be resold by A (AI and rule) | 0.52 | A is dried cocoa-fruit pulp flakes for household culinary use, while B is a range of prepared beverage mixes and ingredients. The descriptions do not establish… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.51 | A is a finished drink consumed directly or used in cocktails and cooking; B is a sunflower-seed-based ingredient used by manufacturers to make confectionery, b… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.50 | Dried cocoa-fruit pulp is a sweetening and flavouring ingredient with crunchy inclusions, while B comprises prepared beverage mixes and ingredients. The pulp c… |  |
| T-1 Cocoa-fruit juice | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●● |  | 0.50 | Cocoa-fruit juice is a beverage ingredient and culinary input, while the nut and almond products are varied ingredients such as pastes, flours, fillings and to… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.50 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient, while B includes prepared cocoa or chocolate drink mixes and other beverage ingredients. A could pla… |  |
| T-1 Cocoa-fruit juice | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | A could be an input for B (rule) | 0.49 | Cocoa-fruit juice is a beverage ingredient and culinary juice, while B consists of chocolate fillings, pieces and decorations used in food production. Although… |  |
| T-2 Cocoa-fruit juice concentrate | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI and rule) | 0.48 | Cocoa-fruit juice concentrate is a sweetening ingredient, while chocolate fillings, pieces and decorations are finished or semi-finished chocolate components. … |  |
| T-2 Cocoa-fruit juice concentrate | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●● |  | 0.48 | Cocoa-fruit juice concentrate is a fruit sweetener and ingredient, while B comprises inclusions, fillings, coatings and decorations. They are different product… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ |  | 0.47 | A is a dried food ingredient, while B comprises finished inclusions, fillings, coatings and decorations. A could plausibly serve as an inclusion in some of the… |  |
| T-2 Cocoa-fruit juice concentrate | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●● |  | 0.43 | Cocoa-fruit juice concentrate and the nut and almond ingredients are different products, but both are used by food manufacturers in some of the same applicatio… |  |
| T-7 Beverage shots | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.43 | A consists of finished, ready-to-drink shots, while B consists of cocoa-fruit ingredients used by manufacturers in beverages and other foods. The cocoa-fruit j… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.38 | A is a finished beverage, while B consists of nut-based ingredients and preparations, so they are not the same product. However, B includes ingredients intende… | no EEA overlap |
| T-7 Beverage shots | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.36 | A consists of finished drinks consumed directly as shots, while B consists of cocoa ingredients used by manufacturers and professional users to make other prod… |  |
| T-7 Beverage shots | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●○○ |  | 0.36 | A’s cocoa-fruit shots and B’s chocolate and cocoa ingredients are different products, but cocoa-based ingredients could plausibly serve some of the same specif… |  |
| T-7 Beverage shots | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.28 | Both are edible beverage or food products, but A consists of ready-to-drink shots while B consists of ingredients and decorations incorporated into or applied … |  |
| T-8 Cocoa-fruit pulp ingredient f… | P2-2 Professional and artisan choc… | unclear | different product |  |  | 0.60 | A is cocoa-fruit pulp used to make balsamic vinegar, while B is chocolate and cocoa ingredients used to make confectionery, baked goods, ice cream and desserts… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P2-1 Industrial chocolate and couv… | unclear | different product |  |  | 0.55 | A is a finished ready-to-drink cocoa-fruit beverage for direct consumption or use in drinks and cooking. B is industrial chocolate supplied as an ingredient fo… | no EEA overlap |
| T-8 Cocoa-fruit pulp ingredient f… | P2-7 Professional beverage mixes a… | unclear | different product |  |  | 0.51 | A is cocoa-fruit pulp supplied for making balsamic vinegar, while B consists of prepared beverage mixes and ingredients for making drinks. The descriptions do … |  |

<details><summary>21 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.47): Cocoa-fruit juice is a beverage ingredient and culinary juice, while B consists of inclusions, fill…
- T-1 Cocoa-fruit juice ↔ P2-10 Professional chocolate education a… (sim. 0.38): A is a pasteurised cocoa-fruit juice used as a beverage ingredient and in culinary applications. B …
- T-2 Cocoa-fruit juice concentrate ↔ P2-10 Professional chocolate education a… (sim. 0.37): Cocoa-fruit juice concentrate is a food ingredient used in products such as beverages, fillings, ic…
- T-3 Dried cocoa-fruit pulp ↔ P2-10 Professional chocolate education a… (sim. 0.43): A is a food ingredient used in chocolate, confectionery and other culinary products, while B is edu…
- T-4 Dried cocoa-fruit pulp flakes ↔ P2-5 Nut and almond ingredients (sim. 0.46): A is dried cocoa-fruit pulp flakes for household culinary use, while B consists of nut- and almond-…
- T-4 Dried cocoa-fruit pulp flakes ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.48): Dried cocoa-fruit pulp flakes are packaged for household culinary use, while B consists of ingredie…
- T-4 Dried cocoa-fruit pulp flakes ↔ P2-10 Professional chocolate education a… (sim. 0.41): Dried cocoa-fruit pulp flakes are a food product used for culinary purposes, while the other activi…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P2-5 Nut and almond ingredients (sim. 0.47): A is a dried cocoa-fruit pulp and cocoa-powder ingredient, while B comprises nut- and almond-based …
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P2-10 Professional chocolate education a… (sim. 0.36): A is a dried cocoa-pulp and cocoa-powder ingredient used in finished foods, whereas B is education …
- T-6 Ready-to-drink cocoa-fruit juice ↔ P2-4 Chocolate fillings, inclusions and… (sim. 0.45): A is a ready-to-drink cocoa-fruit beverage, while B consists of chocolate components used to make o…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.40): A is a finished beverage for direct consumption or use in drinks and cooking. B consists of ingredi…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P2-10 Professional chocolate education a… (sim. 0.37): A is a finished beverage for drinking or culinary use, while B is education and training to develop…
- T-7 Beverage shots ↔ P2-1 Industrial chocolate and couverture (sim. 0.32): A consists of ready-to-drink 60 ml beverage shots, while B is chocolate supplied as an ingredient f…
- T-7 Beverage shots ↔ P2-4 Chocolate fillings, inclusions and… (sim. 0.30): Activity A consists of finished drinks consumed directly as beverage shots. Activity B consists of …
- T-7 Beverage shots ↔ P2-5 Nut and almond ingredients (sim. 0.27): Beverage shots are finished drinks consumed directly, while the nut products are ingredients used t…
- T-7 Beverage shots ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.31): Activity A is a finished beverage intended to be consumed directly, while Activity B is an ingredie…
- T-7 Beverage shots ↔ P2-10 Professional chocolate education a… (sim. 0.28): A consists of ready-to-drink beverage shots, while B provides education and training in chocolate a…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P2-4 Chocolate fillings, inclusions and… (sim. 0.47): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B’s products are chocolate f…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P2-5 Nut and almond ingredients (sim. 0.43): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while the listed nut and almond in…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.46): A is cocoa-fruit pulp used specifically as an ingredient to make balsamic vinegar. B comprises incl…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P2-10 Professional chocolate education a… (sim. 0.35): Cocoa-fruit pulp is an ingredient used to produce balsamic vinegar, while Activity B provides educa…

</details>

### Bahlsen

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-4 Dried cocoa-fruit pulp flakes | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI) | 0.49 | Dried cocoa-fruit pulp flakes are a distinct food product intended for culinary use, while Activity B describes biscuits, baked goods, snacks and other selecte… |  |
| T-4 Dried cocoa-fruit pulp flakes | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI) | 0.47 | Cocoa-fruit pulp flakes are a dried fruit ingredient used for culinary purposes, while biscuits, wafers and pastries are finished baked snacks or treats. The d… |  |
| T-3 Dried cocoa-fruit pulp | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.46 | Dried cocoa-fruit pulp is an ingredient used to sweeten and flavour confectionery, while biscuits, wafers and pastries are finished baked snacks. The products … |  |
| T-3 Dried cocoa-fruit pulp | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.45 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to confectionery and other foods, whereas B consists of finished biscuits, pastr… |  |
| T-3 Dried cocoa-fruit pulp | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI) | 0.44 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add texture to food products. Biscuits, baked goods, snacks and other finished foods are pu… |  |
| T-2 Cocoa-fruit juice concentrate | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.43 | Cocoa-fruit juice concentrate is a food ingredient used by manufacturers in products such as beverages and baked goods, whereas Activity B consists of finished… |  |
| T-4 Dried cocoa-fruit pulp flakes | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.43 | Both are edible fruit-based products for consumers, and the flakes and bars could plausibly serve a snack or culinary eating occasion. However, the flakes are … |  |
| T-2 Cocoa-fruit juice concentrate | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.42 | Cocoa-fruit juice concentrate is an ingredient and sweetener used by food manufacturers, while B consists of finished snack and confectionery products for cons… |  |
| T-2 Cocoa-fruit juice concentrate | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.42 | Cocoa-fruit juice concentrate is an ingredient used by food manufacturers, while biscuit-based snack bars are finished portable snacks eaten by consumers. The … |  |
| T-1 Cocoa-fruit juice | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.41 | Cocoa-fruit juice is an ingredient for manufacturing drinks and foods and for culinary use, whereas B consists of finished packaged sweet baked goods eaten as … |  |
| T-8 Cocoa-fruit pulp ingredient f… | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.41 | A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, whereas B is retail resale of biscuits, baked goods, snacks and other finished foods. The des… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.41 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for professional food users, while B is finished packaged sweet baked goods eaten as snacks or treats… |  |
| T-3 Dried cocoa-fruit pulp | P3-3 Packaged cakes | candidate | different product |  | A could be an input for B (AI) | 0.41 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to food products, while packaged cakes are ready-to-eat baked goods. The descrip… |  |
| T-1 Cocoa-fruit juice | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.40 | Cocoa-fruit juice is an ingredient for manufacturing drinks and food or for culinary use, whereas B consists of finished biscuits, pastries, wafers, cakes and … |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.40 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient used by food manufacturers and professional users in finished foods. B consists of finished biscuits,… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.40 | Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B consists of finished sweet baked goods and peppermint tablets eaten as snacks or con… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI) | 0.40 | A is a ready-to-drink cocoa-fruit juice, while B consists of biscuits, baked goods, snacks and other selected food products. Although both are consumed by cons… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.40 | Dried cocoa-fruit pulp is an ingredient used for sweetening, flavouring or adding crunchy inclusions, while biscuit-based snack bars are finished portable snac… |  |
| T-3 Dried cocoa-fruit pulp | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.40 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to foods, while the bars are finished portable snacks. They are different produc… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in making finished foods; B is retail resale of finished biscuits, baked goods, snacks and ot… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.39 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient used by professional food users to make finished foods. B is a packaged biscuit-and-chocolate snack e… |  |
| T-2 Cocoa-fruit juice concentrate | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.39 | Cocoa-fruit juice concentrate is a sweetener and ingredient used in food production, whereas the listed goods are finished foods bought for consumption or as g… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.38 | A is cocoa-fruit pulp sold as an ingredient for making balsamic vinegar; B is finished packaged sweet baked goods eaten as snacks or treats. The descriptions d… |  |
| T-2 Cocoa-fruit juice concentrate | P3-3 Packaged cakes | candidate | different product |  | A could be an input for B (AI) | 0.38 | Cocoa-fruit juice concentrate is an ingredient used by professional food users in products such as fillings, ice cream and bakery goods. Packaged cakes are fin… |  |
| T-1 Cocoa-fruit juice | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.37 | Cocoa-fruit juice is an ingredient for manufacturing and culinary use, while B describes retail resale of finished biscuits, baked goods, snacks and other food… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-7 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A is a dried cocoa-fruit-pulp and cocoa-powder ingredient used by food manufacturers and professional food users in finished foods. B is a finished fruit-and-n… |  |
| T-2 Cocoa-fruit juice concentrate | P3-7 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.36 | Cocoa-fruit juice concentrate is a food ingredient used by manufacturers and professional food users in products such as beverages and fillings. Fruit-and-nut … |  |
| T-1 Cocoa-fruit juice | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.35 | Cocoa-fruit juice is used as a beverage ingredient and in culinary applications, while the bars are portable snacks. They are different products, but the juice… |  |
| T-7 Beverage shots | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ |  | 0.34 | Both are finished, portable food products consumed directly by consumers as snacks. The shots are beverages and the bars are solid snacks, so they are not the … |  |
| T-3 Dried cocoa-fruit pulp | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ |  | 0.33 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour and add texture to food, while the seasonal biscuits and baked goods are finished snacks, trea… |  |
| T-7 Beverage shots | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ |  | 0.31 | Both are finished sweet food products consumed by consumers as snacks or treats. Packaged baked goods and drinkable beverage shots are different products, but … |  |
| T-5 Dried cocoa-fruit pulp mixed … | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.31 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in finished foods, while B consists of finished seasonal biscuits and baked goods. The ingredient c… |  |
| T-7 Beverage shots | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI) | 0.30 | A consists of drinkable 60 ml beverage shots, while B is retail resale of biscuits, baked goods, snacks and other food products. The descriptions do not indica… |  |
| T-7 Beverage shots | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ |  | 0.28 | Both are finished foods consumed directly as snacks or treats, but beverage shots are drinks while the seasonal range consists of biscuits and baked goods. The… |  |
| T-1 Cocoa-fruit juice | P3-4 Seasonal biscuits and baked g… | candidate | different product |  | A could be an input for B (AI) | 0.28 | Cocoa-fruit juice is a beverage ingredient for manufacturing and culinary use, while the seasonal biscuits and baked goods are finished snacks, treats or desse… |  |
| T-2 Cocoa-fruit juice concentrate | P3-4 Seasonal biscuits and baked g… | candidate | different product |  | A could be an input for B (AI) | 0.28 | Cocoa-fruit juice concentrate is a sweetener and food ingredient used by professional food users in manufacturing, whereas the seasonal biscuits and baked good… |  |

<details><summary>36 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P3-2 Biscuit-based snack bars (sim. 0.35): Cocoa-fruit juice is a beverage ingredient and culinary input used by manufacturers and culinary pr…
- T-1 Cocoa-fruit juice ↔ P3-3 Packaged cakes (sim. 0.40): Cocoa-fruit juice is supplied as a beverage ingredient and culinary input, whereas packaged cakes a…
- T-1 Cocoa-fruit juice ↔ P3-6 Private-label product development … (sim. 0.37): A is a pasteurised cocoa-fruit juice used as a beverage ingredient and for culinary purposes. B is …
- T-1 Cocoa-fruit juice ↔ P3-9 Hoodies and fabric tote bags (sim. 0.31): Cocoa-fruit juice is a beverage ingredient for food and drink preparation, while hoodies and fabric…
- T-2 Cocoa-fruit juice concentrate ↔ P3-6 Private-label product development … (sim. 0.38): A is a cocoa-fruit juice concentrate used as a sweetener and food ingredient, while B is a product-…
- T-2 Cocoa-fruit juice concentrate ↔ P3-9 Hoodies and fabric tote bags (sim. 0.28): Cocoa-fruit juice concentrate is a food ingredient used in manufacturing food and beverages, wherea…
- T-3 Dried cocoa-fruit pulp ↔ P3-6 Private-label product development … (sim. 0.39): A is a food ingredient used for sweetening, flavouring and texture, while B is a product-developmen…
- T-3 Dried cocoa-fruit pulp ↔ P3-9 Hoodies and fabric tote bags (sim. 0.30): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food product…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-2 Biscuit-based snack bars (sim. 0.43): Dried cocoa-fruit pulp flakes are used as a culinary ingredient, while biscuit-and-chocolate bars a…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-3 Packaged cakes (sim. 0.43): Dried cocoa-fruit pulp flakes are used as a culinary ingredient, while packaged cakes are ready-to-…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.36): Dried cocoa-fruit pulp flakes are used as a culinary ingredient, while the seasonal biscuits and ba…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.48): Dried cocoa-fruit pulp flakes are sold for household culinary use, while B consists of finished bis…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-6 Private-label product development … (sim. 0.43): A is a packaged food ingredient/product for household culinary use; B is a business service that he…
- T-4 Dried cocoa-fruit pulp flakes ↔ P3-9 Hoodies and fabric tote bags (sim. 0.35): Dried cocoa-fruit pulp flakes are food for culinary use, while hoodies and fabric tote bags are app…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P3-3 Packaged cakes (sim. 0.37): The dried cocoa-pulp and cocoa-powder mixture is an ingredient for making finished foods, whereas p…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P3-6 Private-label product development … (sim. 0.35): A is a dried food ingredient for use in finished foods, while B is a development and customization …
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P3-9 Hoodies and fabric tote bags (sim. 0.27): Activity A is a dried food ingredient used in finished foods, whereas Activity B consists of appare…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.43): A is a ready-to-drink fruit juice used as a beverage or ingredient in drinks and cooking; B consist…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-2 Biscuit-based snack bars (sim. 0.42): A is a ready-to-drink cocoa-fruit beverage, while B is a packaged biscuit-and-chocolate snack bar. …
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-3 Packaged cakes (sim. 0.44): Cocoa-fruit juice is a drink used for direct consumption or in drinks and cooking, whereas packaged…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.32): A is a ready-to-drink cocoa-fruit beverage, while B consists of seasonal biscuits and baked goods. …
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.44): A is a ready-to-drink cocoa-fruit beverage, while B consists of biscuits, pastries, wafers, cakes a…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-6 Private-label product development … (sim. 0.38): A is a finished beverage for drinking or use in food and drinks. B is a development service used by…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.44): A is a ready-to-drink beverage used for drinking or as an ingredient in cocktails and cooking, whil…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P3-9 Hoodies and fabric tote bags (sim. 0.35): A is a ready-to-drink beverage used for drinking or in food and cocktails, while B consists of appa…
- T-7 Beverage shots ↔ P3-3 Packaged cakes (sim. 0.29): The shots are beverages intended to be drunk, while the packaged cakes are sweet baked goods intend…
- T-7 Beverage shots ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.34): The shots are beverages intended to be drunk, while the biscuits, pastries, wafers, cakes and peppe…
- T-7 Beverage shots ↔ P3-6 Private-label product development … (sim. 0.28): Activity A is a finished beverage consumed directly as a drink. Activity B is a development service…
- T-7 Beverage shots ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.36): A consists of ready-to-drink beverage shots, while B consists of solid snack bars eaten as portable…
- T-7 Beverage shots ↔ P3-9 Hoodies and fabric tote bags (sim. 0.26): The 60 ml beverage shots are consumed as drinks, whereas hoodies are worn and fabric tote bags are …
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-2 Biscuit-based snack bars (sim. 0.35): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while biscuit-based bars are packa…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-3 Packaged cakes (sim. 0.35): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas packaged cakes are ready-t…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.30): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B consists of finished seaso…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-6 Private-label product development … (sim. 0.41): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B is a service for developi…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.34): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas fruit-and-nut and protein …
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.33): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas hoodies and fabric tote ba…

</details>

### FRoSTA

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-4 Dried cocoa-fruit pulp flakes | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is packaged dried cocoa-fruit pulp flakes for household culinary use, while B is a broad range of frozen foods intended for professional kitchens. Although b… |  |
| T-3 Dried cocoa-fruit pulp | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.38 | Dried cocoa-fruit pulp is an ingredient used for sweetening, flavouring and crunchy inclusions, whereas Activity B consists of finished frozen foods for profes… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-5 Frozen food supplied to indus… | candidate | different product |  | A could be an input for B (AI) | 0.38 | A is a specific dried cocoa-pulp and cocoa-powder ingredient, while B is frozen food supplied to industrial customers. The descriptions do not indicate that th… |  |
| T-3 Dried cocoa-fruit pulp | P4-2 Customer-brand frozen foods | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.37 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour, or add crunch to food, while B supplies finished frozen foods such as ready meals, fruit, and… |  |
| T-3 Dried cocoa-fruit pulp | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.36 | Dried cocoa-fruit pulp is a sweetening, flavouring and crunchy ingredient, while B supplies a range of frozen foods, including fruit and other food products. T… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is a dried cocoa-fruit pulp and cocoa powder ingredient for use in finished foods, while B comprises finished frozen foods such as meals, fish, vegetables, f… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is an ingredient for incorporation into finished foods, while B consists of frozen finished foods that professional kitchens prepare and serve. Their shared … |  |
| T-8 Cocoa-fruit pulp ingredient f… | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.35 | Activity A supplies cocoa-fruit pulp as an ingredient used to make balsamic vinegar, while Activity B manufactures finished frozen foods such as ready meals, f… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.34 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods. B is a range of frozen foods, including fish, vegetables, meals, fruit, he… |  |
| T-1 Cocoa-fruit juice | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.34 | Cocoa-fruit juice is a beverage ingredient used in drinks and culinary preparations, while B makes finished frozen foods for resale. The descriptions do not in… |  |
| T-6 Ready-to-drink cocoa-fruit ju… | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●○○ |  | 0.34 | A is a ready-to-drink beverage, while B includes frozen fruit and other foods used to prepare meals in professional kitchens. A could plausibly be used in some… | no EEA overlap |
| T-2 Cocoa-fruit juice concentrate | P4-5 Frozen food supplied to indus… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.33 | A is a fruit-sweetening ingredient used in food and beverage production, while B supplies frozen food products for industrial customers’ food production or pro… |  |
| T-1 Cocoa-fruit juice | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.33 | Cocoa-fruit juice is a beverage ingredient and culinary product, while B supplies frozen foods including fruit and other food categories. Some products in B’s … |  |
| T-8 Cocoa-fruit pulp ingredient f… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.33 | Activity A is a cocoa-fruit pulp ingredient used to make balsamic vinegar. Activity B is a range of frozen foods for household delivery; the descriptions do no… |  |
| T-3 Dried cocoa-fruit pulp | P4-1 Branded frozen meals, fish, v… | candidate | different product |  | A could be an input for B (AI) | 0.32 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to manufactured or culinary products, while Activity B consists of finished froz… |  |
| T-2 Cocoa-fruit juice concentrate | P4-9 Product development and assor… | candidate | different product |  | A could be an input for B (AI) | 0.31 | A is a physical food ingredient used to sweeten or formulate foods and beverages. B is a consulting and product-development service used for assortment plannin… |  |
| T-1 Cocoa-fruit juice | P4-1 Branded frozen meals, fish, v… | candidate | different product |  | A could be an input for B (AI) | 0.31 | Cocoa-fruit juice is an ingredient for manufacturing or culinary use, whereas B consists of frozen foods and ready meals intended for household consumption. Th… |  |
| T-2 Cocoa-fruit juice concentrate | P4-2 Customer-brand frozen foods | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.31 | A is a concentrated fruit ingredient used to sweeten or formulate foods, while B consists of finished frozen foods. A could plausibly serve as a sweetening ing… |  |
| T-2 Cocoa-fruit juice concentrate | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.30 | Cocoa-fruit juice concentrate is a sweetening ingredient, while Activity B consists of frozen foods prepared for professional kitchens. The concentrate could p… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-1 Branded frozen meals, fish, v… | candidate | different product |  | A could be an input for B (AI) | 0.30 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in manufacturing finished foods. B comprises finished frozen meals and frozen fish, vegetable… |  |
| T-5 Dried cocoa-fruit pulp mixed … | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.29 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods, whereas B is a range of branded frozen foods sold to shoppers. The descrip… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.28 | A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B consists of finished frozen foods for professional kitchens. The described products s… |  |
| T-2 Cocoa-fruit juice concentrate | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●●○ |  | 0.28 | Cocoa-fruit juice concentrate is a sweetening food ingredient, while B comprises finished frozen foods across several categories. Some B products, such as froz… |  |
| T-7 Beverage shots | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.27 | A consists of finished 60 ml drinks intended to be consumed as shots. B consists of frozen food ranges for household delivery, including meals and other food c… |  |
| T-1 Cocoa-fruit juice | P4-7 Frozen meals, fish, vegetable… | candidate | different product |  | A could be an input for B (AI) | 0.27 | Cocoa-fruit juice is a beverage ingredient and culinary input, while B sells frozen meals and frozen fish, vegetables and herbs for consumers to prepare and ea… |  |
| T-2 Cocoa-fruit juice concentrate | P4-1 Branded frozen meals, fish, v… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.26 | Cocoa-fruit juice concentrate is a sweetener and ingredient, while B consists of finished frozen foods, so they are not the same product. The concentrate could… |  |
| T-7 Beverage shots | P4-4 Frozen foods for professional… | candidate | different product |  | B could be an input for A (AI) | 0.26 | Activity A consists of ready-to-drink beverage shots, while Activity B consists of frozen foods for professional kitchens. The described frozen foods are used … |  |
| T-7 Beverage shots | P4-9 Product development and assor… | candidate | different product |  | B could be an input for A (AI) | 0.26 | Activity A is a finished drink consumed directly, while Activity B is business-to-business advice and product-development work used to plan assortments or deve… |  |
| T-3 Dried cocoa-fruit pulp | P4-5 Frozen food supplied to indus… | unclear | not enough information |  |  | 0.39 | A is a specified dried cocoa-fruit ingredient used for sweetening, flavouring and crunchy inclusions. B is described only as frozen food supplied for industria… |  |
| T-1 Cocoa-fruit juice | P4-5 Frozen food supplied to indus… | unclear | not enough information |  |  | 0.39 | A is pasteurised cocoa-fruit juice used as a beverage ingredient and for culinary applications. B is described only as frozen food for industrial customers, wi… |  |
| T-8 Cocoa-fruit pulp ingredient f… | P4-5 Frozen food supplied to indus… | unclear | not enough information |  |  | 0.36 | A is cocoa-fruit pulp used specifically to make balsamic vinegar, while B supplies frozen products for industrial customers’ food production. B’s product catal… |  |
| T-3 Dried cocoa-fruit pulp | P4-3 Branded frozen foods | unclear | not enough information |  |  | 0.31 | A is a dried cocoa-fruit ingredient for use in food products, while B’s frozen-food product categories are not identified. The descriptions therefore do not sh… |  |
| T-1 Cocoa-fruit juice | P4-3 Branded frozen foods | unclear | not enough information |  | ✗ A could be resold by B (AI, disregarded: B is not active in wholesale or retail (level: finished products)) | 0.29 | Cocoa-fruit juice is a beverage ingredient and culinary product, while the categories within the branded frozen-food ranges are not identified. The description… |  |

<details><summary>47 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P4-4 Frozen foods for professional kitc… (sim. 0.35): Cocoa-fruit juice is a beverage ingredient and culinary input, while B consists of finished frozen …
- T-1 Cocoa-fruit juice ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.25): Cocoa-fruit juice is a beverage ingredient and culinary ingredient, while B consists of frozen meal…
- T-1 Cocoa-fruit juice ↔ P4-9 Product development and assortment… (sim. 0.33): A is a pasteurised cocoa-fruit juice used as a beverage ingredient and for culinary purposes. B is …
- T-1 Cocoa-fruit juice ↔ P4-10 Non-food merchandise (sim. 0.29): Cocoa-fruit juice is a beverage ingredient used in food and drink preparation, while the merchandis…
- T-2 Cocoa-fruit juice concentrate ↔ P4-3 Branded frozen foods (sim. 0.30): A is a concentrated fruit ingredient used by professional food users in manufacturing, while B is a…
- T-2 Cocoa-fruit juice concentrate ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.22): Cocoa-fruit juice concentrate is an ingredient used by professional food users in products such as …
- T-2 Cocoa-fruit juice concentrate ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.21): Cocoa-fruit juice concentrate is a sweetener and food ingredient used to make or formulate foods an…
- T-2 Cocoa-fruit juice concentrate ↔ P4-10 Non-food merchandise (sim. 0.28): Cocoa-fruit juice concentrate is a food ingredient used by professional users in food and beverage …
- T-3 Dried cocoa-fruit pulp ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.30): Dried cocoa-fruit pulp is an ingredient used by food manufacturers and culinary professionals to sw…
- T-3 Dried cocoa-fruit pulp ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.26): Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add texture to foods, while B s…
- T-3 Dried cocoa-fruit pulp ↔ P4-9 Product development and assortment… (sim. 0.34): A is a dried food ingredient used to sweeten, flavour or add crunchy inclusions to food products. B…
- T-3 Dried cocoa-fruit pulp ↔ P4-10 Non-food merchandise (sim. 0.30): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food product…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.37): Dried cocoa-fruit pulp flakes are a distinct culinary product, while B comprises frozen meals and f…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-2 Customer-brand frozen foods (sim. 0.43): A is a dried cocoa-fruit ingredient for household culinary use, while B consists of finished frozen…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-3 Branded frozen foods (sim. 0.37): Dried cocoa-fruit pulp flakes are a specific culinary ingredient, while the other activity covers b…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-5 Frozen food supplied to industrial… (sim. 0.45): Dried cocoa-fruit pulp flakes are packaged for household culinary use, while B supplies frozen prod…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.44): Dried cocoa-fruit pulp flakes are a specific packaged ingredient for culinary use, while Activity B…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.38): Dried cocoa-fruit pulp flakes are a packaged ingredient for culinary use, while Activity B offers r…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.33): Dried cocoa-fruit pulp flakes are a culinary ingredient sold for household use, while B consists of…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-9 Product development and assortment… (sim. 0.36): A is a packaged food ingredient for household culinary use, while B is a business-to-business consu…
- T-4 Dried cocoa-fruit pulp flakes ↔ P4-10 Non-food merchandise (sim. 0.35): Dried cocoa-fruit pulp flakes are a food product used for culinary purposes, while the merchandise …
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.29): A is a dried cocoa-pulp and cocoa-powder ingredient for use by food manufacturers and professional …
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.25): A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods. B is a finishe…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P4-9 Product development and assortment… (sim. 0.31): A is a dried food ingredient used in finished foods, while B is a business-to-business consulting a…
- T-5 Dried cocoa-fruit pulp mixed with … ↔ P4-10 Non-food merchandise (sim. 0.26): A is a dried food ingredient intended for use in finished foods, while B consists of non-food appar…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.34): Cocoa-fruit juice is a beverage consumed directly or used in drinks and cooking, while B consists o…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-2 Customer-brand frozen foods (sim. 0.36): A is a ready-to-drink cocoa-fruit beverage, while B makes a range of frozen foods such as meals, fi…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-3 Branded frozen foods (sim. 0.32): A is a ready-to-drink cocoa-fruit beverage, consumed directly or used in drinks and cooking. B is a…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-5 Frozen food supplied to industrial… (sim. 0.37): A is a finished beverage for direct consumption or use in drinks and cooking, while B supplies froz…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.34): A is a ready-to-drink cocoa-fruit beverage, while B comprises frozen foods such as fish, vegetables…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.33): A is a ready-to-drink cocoa-fruit beverage, while B consists of frozen meals and other frozen foods…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.29): A is a ready-to-drink cocoa-fruit beverage, while B consists of frozen meals and meal boxes. They s…
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-9 Product development and assortment… (sim. 0.32): A is a finished beverage for drinking or use in cooking and cocktails. B is a business-to-business …
- T-6 Ready-to-drink cocoa-fruit juice ↔ P4-10 Non-food merchandise (sim. 0.34): A is a ready-to-drink beverage for drinking or use in food preparation, while B consists of apparel…
- T-7 Beverage shots ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.30): The shots are finished drinks consumed directly, while B consists of frozen meals and individual fr…
- T-7 Beverage shots ↔ P4-2 Customer-brand frozen foods (sim. 0.25): Beverage shots are consumed directly as drinks, while Activity B makes frozen meals and other froze…
- T-7 Beverage shots ↔ P4-3 Branded frozen foods (sim. 0.26): A consists of ready-to-drink 60 ml beverage shots, while B consists of branded frozen foods. The de…
- T-7 Beverage shots ↔ P4-5 Frozen food supplied to industrial… (sim. 0.28): A consists of finished beverage shots for consumers to drink directly, while B consists of frozen p…
- T-7 Beverage shots ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.27): Activity A sells ready-to-drink 60 ml beverage shots, while Activity B sells frozen meals and other…
- T-7 Beverage shots ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.28): Activity A consists of ready-to-drink beverage shots, while Activity B consists of frozen meals and…
- T-7 Beverage shots ↔ P4-10 Non-food merchandise (sim. 0.31): Activity A consists of ready-to-drink beverage shots, while Activity B consists of apparel, accesso…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.26): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B consists of finished fro…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-3 Branded frozen foods (sim. 0.31): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B is a range of branded fro…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.24): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B sells prepared frozen me…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.19): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B supplies prepared frozen m…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-9 Product development and assortment… (sim. 0.37): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B is a business service for…
- T-8 Cocoa-fruit pulp ingredient for ba… ↔ P4-10 Non-food merchandise (sim. 0.33): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while the merchandise consists of …

</details>

## Calibration: closest pairs that were screened out

If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.

- 0.48 · T-4 Dried cocoa-fruit pulp flakes ↔ P3-5 Private-label biscuits, coffee pastries… (Bahlsen)
- 0.48 · T-4 Dried cocoa-fruit pulp flakes ↔ P2-6 Bakery, confectionery and dessert inclu… (Barry Callebaut)
- 0.47 · T-5 Dried cocoa-fruit pulp mixed with cocoa… ↔ P2-5 Nut and almond ingredients (Barry Callebaut)
- 0.47 · T-8 Cocoa-fruit pulp ingredient for balsami… ↔ P2-4 Chocolate fillings, inclusions and deco… (Barry Callebaut)
- 0.47 · T-1 Cocoa-fruit juice ↔ P2-6 Bakery, confectionery and dessert inclu… (Barry Callebaut)
- 0.47 · T-4 Dried cocoa-fruit pulp flakes ↔ P1-3 Chocolate-covered wafer rolls with crea… (Ritter Sport)
- 0.46 · T-4 Dried cocoa-fruit pulp flakes ↔ P2-5 Nut and almond ingredients (Barry Callebaut)
- 0.46 · T-4 Dried cocoa-fruit pulp flakes ↔ P1-4 Corporate gifts and promotional chocola… (Ritter Sport)
- similarity of candidate pairs: min 0.26 · median 0.43 · max 0.83
- similarity of screened out pairs: min 0.19 · median 0.35 · max 0.48

## Example: exactly what the comparison call received

```
ACTIVITY A
Product: Cocoa-fruit juice
Description: Pasteurised juice supplied as a beverage ingredient and for culinary use, including in industrial formats.
Intended use: Manufacturers use it in drinks and food products; culinary professionals use it in prepared dishes and beverages.
Main inputs: cocoa-fruit pulp
Level of trade: intermediate products
Direct customers: manufacturers / processors, wholesalers / distributors, other businesses (Food and beverage manufacturers, specialist ingredient distributors and professional gastronomy customers.)
End users: consumers and businesses
Sales channels: Direct large-volume projects and professional distributors; distributors supply artisan and foodservice customers.
Status: on the market

ACTIVITY B
Product: Packaged chocolate bars and other chocolate confectionery
Description: Finished chocolate products in bar, miniature, cube, filled, seasonal and gift formats, including milk, white, dark, nut, vegan and protein varieties. The sources do not state price positioning.
Intended use: Consumption as confectionery and purchase as gifts.
Main inputs: cocoa, sugar, milk, nuts
Level of trade: finished products
Direct customers: retailers, wholesalers / distributors (Food retailers and trade customers; local sales-company and distributor arrangements are not fully specified.)
End users: consumers
Sales channels: Food retail and supermarkets; wholesale distribution; airport and travel retail.
Status: on the market
```

## Run summary

- names removed before any comparison: 72 name variants (list in the .json file)
- comparison calls blocked or failed: 0 (kept as 'unclear', never screened out)
- search: 5 calls (5 from cache) · tokens 0 in / 0 out · USD 0.0000
- extract: 5 calls (4 from cache) · tokens 4,424 in / 2,823 out · USD 0.0019
- embed: 5 calls (4 from cache) · tokens 447 in / 0 out · USD 0.0001
- compare: 304 calls (0 from cache) · tokens 377,544 in / 52,978 out · USD 0.0643
- total: USD 0.0662 (token costs only, without web search fees)
