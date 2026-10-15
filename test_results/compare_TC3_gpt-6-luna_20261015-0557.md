# Factual comparison TC3: Koa (20261015-0557)

Models: search saved gpt-6.1-sol · extraction gpt-6-luna · comparison gpt-6-luna · text-embedding-3-large  
Thresholds: unclear ≥ 0.5 · input match ≥ 0.5 · resale ≥ 0.5

## Benchmark check (spec section 13)

6 ✔ as expected · 0 ◐ kept in another form · **0 ✖ missed by the comparison** · 0 ∅ activity not found · 1 ⚠ false positives in a control row

Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py need adjusting: compare with the activity overview below).

| Check | Portco | Pair | Expected | Result | Pairs | Detail |
|---|---|---|---|---|---|---|
| TC3-1 | Barry Callebaut | Cabosse Naturals ↔ Koa ingredients (central overlap) | horizontal | ✔ | T-1↔P2-8, T-2↔P2-8, T-3↔P2-8, T-4↔P2-8 (+1) | 5 of 5 matching pairs as expected |
| TC3-2 | Barry Callebaut | Koa ingredients → BC chocolate (vertical candidate) | vertical | ✔ | T-1↔P2-1, T-1↔P2-2, T-1↔P2-3, T-1↔P2-7 (+19) | 23 of 35 matching pairs as expected |
| TC3-3 | Barry Callebaut | Koa drinks ↔ BC beverages (unclear is fine) | kept | ✔ | T-5↔P2-3, T-5↔P2-7, T-5↔P2-8, T-6↔P2-7 (+1) | 5 of 8 matching pairs as expected |
| TC3-4 | Ritter Sport | CacaoVida ↔ Koa shots | horizontal | ✔ | T-5↔P1-6, T-5↔P1-8, T-6↔P1-6, T-6↔P1-8 | 4 of 4 matching pairs as expected |
| TC3-5 | Ritter Sport | Koa ingredients → Ritter (chocolate, CacaoVida) | vertical | ✔ | T-1↔P1-1, T-1↔P1-2, T-1↔P1-6, T-1↔P1-8 (+25) | 29 of 45 matching pairs as expected |
| TC3-6 | Bahlsen | Koa ingredients → bakery (vertical candidate) | vertical | ✔ | T-1↔P3-1, T-2↔P3-1, T-2↔P3-2, T-2↔P3-3 (+12) | 16 of 25 matching pairs as expected |
| TC3-7 | FRoSTA | control (possible false positive: fruit ingredient → frozen food) | screened out | ⚠ | T-1↔P4-1, T-1↔P4-2, T-1↔P4-3, T-1↔P4-4 (+25) | 29 of 70 pairs kept: check whether these are false positives |

## Activity overview (stages ①–②)

### Target: Koa (7 activities, 15 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| T-1 | not stated | Cocoa-fruit juice | intermediate products | manufacturers / processors, wholesalers / distributors | Germany, Austria, France, Net… | on the market | [3, 8, 9, 13] |
| T-2 | not stated | Cocoa-fruit juice concentrate | intermediate products | manufacturers / processors, wholesalers / distributors | Luxembourg, Switzerland, Turk… | on the market | [3, 4, 8, 9, 10] |
| T-3 | not stated | Dried cocoa-fruit pulp | intermediate products | manufacturers / processors, wholesalers / distributors | Germany, Austria, France, Net… | on the market | [3, 8, 9] |
| T-4 | not stated | Dried cocoa-fruit pulp mixed with cocoa powd… | intermediate products | manufacturers / processors, wholesalers / distributors | not stated | on the market | [3, 5] |
| T-5 | not stated | Ready-to-drink cocoa-fruit juice | finished products | consumers | Ghana | on the market | [6] |
| T-6 | not stated | Cocoa-fruit beverage shots | finished products | consumers | Germany | on the market | [7] |
| T-7 | not stated | Cocoa-fruit pulp ingredient for balsamic vin… | intermediate products | manufacturers / processors | Germany | on the market | [11] |

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

280 pairs: 139 candidates · 8 unclear · 133 screened out

### Ritter Sport

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-5 Ready-to-drink cocoa-fruit ju… | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.79 | Both are finished cocoa-fruit beverages intended for drinking, and the juice in A is a main input for B’s juice beverages. B also includes lemonade, iced tea a… | no EEA overlap |
| T-6 Cocoa-fruit beverage shots | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.72 | Both are ready-to-drink beverages made with cocoa-fruit juice and intended for direct consumption. Activity B includes lemonade and iced tea, which could plaus… |  |
| T-1 Cocoa-fruit juice | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.71 | A is pasteurised cocoa-fruit juice sold as an ingredient for beverages and food preparations, while B consists of finished cocoa-fruit drinks for refreshment o… |  |
| T-2 Cocoa-fruit juice concentrate | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.68 | A is a concentrated ingredient and sweetener used in food and beverage manufacturing, while B consists of finished drinks for consumption. Some consumers could… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P1-10 Cocoa cultivation and post-ha… | candidate | different product |  | B could be an input for A (rule) | 0.58 | A is cocoa-fruit pulp used as an ingredient to make balsamic vinegar, whereas B is cocoa cultivation and post-harvest operations supplying cocoa for chocolate … | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.57 | Dried cocoa-fruit pulp is used as a sweetening, flavouring or crunchy food ingredient, whereas B consists of ready-to-drink beverages. They are different produ… |  |
| T-1 Cocoa-fruit juice | P1-10 Cocoa cultivation and post-ha… | candidate | different product |  | A could be an input for B (AI and rule); B could be an input for A (rule) | 0.57 | Cocoa-fruit juice is a pasteurised liquid ingredient used in beverages and food preparations, whereas Activity B produces cocoa for chocolate-making. The descr… | captive (not on the merchant market) |
| T-7 Cocoa-fruit pulp ingredient f… | P1-6 Cocoa-fruit beverages | candidate | different product |  | A could be an input for B (AI and rule) | 0.57 | A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B comprises finished beverages made with cocoa-fruit juice. The beverages are intended … |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-6 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI and rule) | 0.55 | A is a dried pulp-and-cocoa-powder ingredient for use in foods, while B consists of ready-to-drink cocoa-fruit beverages. They differ in form and intended use,… |  |
| T-3 Dried cocoa-fruit pulp | P1-10 Cocoa cultivation and post-ha… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.55 | Dried cocoa-fruit pulp is a sweetening, flavouring and crunchy ingredient for food preparations, while B supplies cocoa from cultivation for chocolate producti… | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-1 Packaged chocolate bars and c… | candidate | different product |  | A could be an input for B (AI and rule) | 0.52 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add crunch to food preparations, while packaged chocolate bars and confectionery are ready-… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-10 Cocoa cultivation and post-ha… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.52 | A is a processed cocoa-fruit ingredient blended with cocoa powder, while B supplies cultivated and post-harvest cocoa. Both relate to cocoa inputs for food pro… | captive (not on the merchant market) |
| T-3 Dried cocoa-fruit pulp | P1-4 Custom chocolate products and… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.51 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring, or adding texture, while Activity B sells finished chocolate for eating or gifting. The pro… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P1-10 Cocoa cultivation and post-ha… | candidate | different product |  | B could be an input for A (AI and rule) | 0.51 | A is a finished, ready-to-drink cocoa-fruit beverage, while B is cocoa cultivation and post-harvest supply for chocolate production. Customers would not use co… | no EEA overlap; captive (not on the merchant market) |
| T-2 Cocoa-fruit juice concentrate | P1-10 Cocoa cultivation and post-ha… | candidate | different product |  | B could be an input for A (AI and rule) | 0.50 | Cocoa-fruit juice concentrate is an ingredient and sweetener used in beverages and food products. Cocoa cultivation and post-harvest operations supply cocoa fo… | captive (not on the merchant market) |
| T-5 Ready-to-drink cocoa-fruit ju… | P1-1 Packaged chocolate bars and c… | candidate | similar product, possibly substitutable | ●○○ |  | 0.50 | Both are cocoa-based products consumed by people, but A is a drink and B is solid chocolate confectionery, with different intended uses. They could plausibly s… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P1-2 Packaged chocolate and chocol… | candidate | different product |  | A could be an input for B (AI and rule) | 0.49 | Dried cocoa-fruit pulp is an ingredient used to sweeten, flavour or add texture to food preparations, while packaged chocolate and confectionery are ready-to-e… |  |
| T-6 Cocoa-fruit beverage shots | P1-1 Packaged chocolate bars and c… | candidate | similar product, possibly substitutable | ●○○ |  | 0.47 | Both are finished, ready-to-consume cocoa-based products for consumers, but one is a small-format drink and the other is solid chocolate confectionery. They ma… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-1 Packaged chocolate bars and c… | candidate | different product |  | A could be an input for B (AI) | 0.46 | A is a dried ingredient blend for use in finished foods and culinary preparations, while B is ready-to-eat chocolate confectionery for eating or gifting. Their… |  |
| T-2 Cocoa-fruit juice concentrate | P1-1 Packaged chocolate bars and c… | candidate | different product |  | A could be an input for B (AI and rule) | 0.46 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener used in manufacturing, while packaged chocolate bars and confectionery are finished p… |  |
| T-3 Dried cocoa-fruit pulp | P1-3 Cream-filled, chocolate-cover… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.45 | Dried cocoa-fruit pulp is a sweetening, flavouring and crunchy ingredient used in food preparations, while B is finished cream-filled chocolate wafer confectio… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-4 Custom chocolate products and… | candidate | different product |  | A could be an input for B (AI) | 0.45 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in food production, while B is finished chocolate confectionery for eating or gifting. They d… |  |
| T-2 Cocoa-fruit juice concentrate | P1-2 Packaged chocolate and chocol… | candidate | different product |  | A could be an input for B (AI and rule) | 0.45 | A is a concentrated fruit ingredient and sweetener for use in manufactured foods and beverages. B is ready-to-eat chocolate confectionery for eating or gifting… |  |
| T-1 Cocoa-fruit juice | P1-1 Packaged chocolate bars and c… | candidate | different product |  | A could be an input for B (rule) | 0.44 | Cocoa-fruit juice is an ingredient for beverage manufacturing and food preparation, while packaged chocolate bars and confectionery are ready-to-eat products f… |  |
| T-6 Cocoa-fruit beverage shots | P1-10 Cocoa cultivation and post-ha… | candidate | different product |  | B could be an input for A (AI) | 0.44 | Activity A is a ready-to-drink beverage consumed directly, while Activity B grows cocoa and performs post-harvest operations to supply cocoa for chocolate prod… | captive (not on the merchant market) |
| T-1 Cocoa-fruit juice | P1-2 Packaged chocolate and chocol… | candidate | different product |  | A could be an input for B (AI and rule) | 0.44 | Cocoa-fruit juice is supplied as an ingredient for beverages and food preparations, whereas the packaged chocolate and confectionery is ready to eat or give as… |  |
| T-2 Cocoa-fruit juice concentrate | P1-4 Custom chocolate products and… | candidate | different product |  | A could be an input for B (AI) | 0.43 | Cocoa-fruit juice concentrate is an intermediate fruit ingredient and sweetener for use in a range of manufactured foods and drinks. Custom and small-batch cho… |  |
| T-3 Dried cocoa-fruit pulp | P1-5 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.42 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring or adding texture, while Activity B supplies finished chocolate for gifts and promotions. Th… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-2 Packaged chocolate and chocol… | candidate | different product |  | A could be an input for B (AI) | 0.42 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient used in food production, while B is ready-to-eat chocolate confectionery for eating or gifting. Custo… |  |
| T-2 Cocoa-fruit juice concentrate | P1-5 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.39 | Cocoa-fruit juice concentrate is an ingredient and sweetener used in food and beverages, while corporate gifts and promotional chocolate are finished chocolate… |  |
| T-6 Cocoa-fruit beverage shots | P1-11 Hazelnut cultivation | candidate | different product |  | B could be an input for A (AI) | 0.37 | Cocoa-fruit beverage shots are ready-to-drink beverages consumed directly, whereas hazelnut cultivation produces raw hazelnuts for use as food ingredients. The… | captive (not on the merchant market) |
| T-4 Dried cocoa-fruit pulp mixed … | P1-5 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for incorporation into foods and culinary preparations. B is finished chocolate supplied as corporate… |  |
| T-6 Cocoa-fruit beverage shots | P1-8 Bistro food and beverages and… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.34 | Both include beverages intended for direct consumption, so a customer could plausibly choose a ready-to-drink shot instead of a drink served by the bistro for … |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P1-8 Bistro food and beverages and… | candidate | similar product, possibly substitutable | ●●○ |  | 0.31 | Both activities include beverages for consumption, and the ready-to-drink cocoa-fruit juice could plausibly be chosen instead of some drinks offered by the bis… | no EEA overlap |
| T-2 Cocoa-fruit juice concentrate | P1-8 Bistro food and beverages and… | candidate | different product |  | A could be an input for B (AI) | 0.30 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener used in manufacturing food and beverages. Bistro food and drinks are prepared for con… |  |
| T-1 Cocoa-fruit juice | P1-8 Bistro food and beverages and… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.28 | Cocoa-fruit juice is an ingredient used in beverages and food preparations, while B offers prepared food and drinks for immediate consumption. The juice is not… |  |
| T-3 Dried cocoa-fruit pulp | P1-8 Bistro food and beverages and… | candidate | different product |  | A could be an input for B (AI) | 0.22 | Dried cocoa-fruit pulp is an ingredient used in food preparation, while B provides prepared food and drinks for consumption and hires event space. The descript… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P1-8 Bistro food and beverages and… | candidate | different product |  | A could be an input for B (AI) | 0.20 | Activity A is a dried cocoa-pulp and cocoa-powder ingredient for use in food production and culinary preparations. Activity B provides prepared food and drinks… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P1-2 Packaged chocolate and chocol… | unclear | different product |  |  | 0.51 | Cocoa-fruit juice is a ready-to-drink beverage, whereas B consists of ready-to-eat chocolate and confectionery for eating or gifting. Their uses and product ch… | no EEA overlap |

<details><summary>45 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.39): Cocoa-fruit juice is an ingredient for beverages and food preparations, whereas cream-filled, choco…
- T-1 Cocoa-fruit juice ↔ P1-4 Custom chocolate products and smal… (sim. 0.44): Cocoa-fruit juice is an ingredient used in beverage and food preparation, whereas the chocolate pro…
- T-1 Cocoa-fruit juice ↔ P1-5 Corporate gifts and promotional ch… (sim. 0.41): Cocoa-fruit juice is an ingredient used in beverages and food preparations, whereas the chocolate p…
- T-1 Cocoa-fruit juice ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.41): Activity A is pasteurised cocoa-fruit juice sold as an ingredient for beverages and food preparatio…
- T-1 Cocoa-fruit juice ↔ P1-9 Non-food gifts and merchandise (sim. 0.26): Cocoa-fruit juice is a pasteurised food ingredient used in beverages and food preparations, whereas…
- T-1 Cocoa-fruit juice ↔ P1-11 Hazelnut cultivation (sim. 0.45): Cocoa-fruit juice is a pasteurised liquid ingredient used in beverages and food preparations, while…
- T-1 Cocoa-fruit juice ↔ P1-12 Electricity and heat generation fo… (sim. 0.24): Cocoa-fruit juice is a food ingredient used in beverages and food preparations, while Activity B ge…
- T-2 Cocoa-fruit juice concentrate ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.39): Cocoa-fruit juice concentrate is an intermediate fruit ingredient and sweetener for use in manufact…
- T-2 Cocoa-fruit juice concentrate ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.39): A is a concentrated fruit ingredient and sweetener used in food and beverage manufacturing, while B…
- T-2 Cocoa-fruit juice concentrate ↔ P1-9 Non-food gifts and merchandise (sim. 0.24): Cocoa-fruit juice concentrate is a concentrated food ingredient and sweetener used in manufacturing…
- T-2 Cocoa-fruit juice concentrate ↔ P1-11 Hazelnut cultivation (sim. 0.42): Cocoa-fruit juice concentrate is a concentrated fruit ingredient and sweetener, while hazelnut cult…
- T-2 Cocoa-fruit juice concentrate ↔ P1-12 Electricity and heat generation fo… (sim. 0.21): Cocoa-fruit juice concentrate is a food ingredient and sweetener used in food and beverage products…
- T-3 Dried cocoa-fruit pulp ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.42): A is dried cocoa-fruit pulp used as a food ingredient for sweetening, flavouring or texture; B is a…
- T-3 Dried cocoa-fruit pulp ↔ P1-9 Non-food gifts and merchandise (sim. 0.27): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food prepara…
- T-3 Dried cocoa-fruit pulp ↔ P1-11 Hazelnut cultivation (sim. 0.47): Dried cocoa-fruit pulp is a processed ingredient used to sweeten, flavour or add texture to foods, …
- T-3 Dried cocoa-fruit pulp ↔ P1-12 Electricity and heat generation fo… (sim. 0.23): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food prepara…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.44): A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in finished foods and culinary pr…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.36): A is a dried cocoa-pulp and cocoa-powder ingredient used in finished foods and culinary preparation…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P1-9 Non-food gifts and merchandise (sim. 0.21): A is a dried cocoa-fruit pulp and cocoa-powder blend used as an ingredient in foods and culinary pr…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P1-11 Hazelnut cultivation (sim. 0.41): A is a dried cocoa-fruit pulp and cocoa-powder blend used as a food ingredient, while B is the cult…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P1-12 Electricity and heat generation fo… (sim. 0.22): A is a dried food ingredient for use in finished foods and culinary preparations, whereas B is elec…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.43): A is a ready-to-drink cocoa-fruit beverage, while B is packaged wafer-roll confectionery eaten as a…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-4 Custom chocolate products and smal… (sim. 0.48): A is a ready-to-drink cocoa-fruit beverage, while B consists of chocolate confectionery intended fo…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-5 Corporate gifts and promotional ch… (sim. 0.44): A is a ready-to-drink cocoa-fruit beverage, while B is chocolate supplied as gifts or promotional i…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.43): A is a ready-to-drink beverage for consumption, including in drinks and cooking. B is an educationa…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-9 Non-food gifts and merchandise (sim. 0.30): A is a ready-to-drink beverage used for consumption and in food preparation; B consists of non-food…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-11 Hazelnut cultivation (sim. 0.39): A is a ready-to-drink cocoa-fruit beverage, while B is the cultivation of hazelnuts for use as a fo…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P1-12 Electricity and heat generation fo… (sim. 0.19): A is a ready-to-drink cocoa-fruit beverage for consumption and culinary use. B is electricity and h…
- T-6 Cocoa-fruit beverage shots ↔ P1-2 Packaged chocolate and chocolate c… (sim. 0.46): Activity A consists of small-format drinks consumed as beverages, while Activity B consists of read…
- T-6 Cocoa-fruit beverage shots ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.40): Activity A consists of small ready-to-drink beverages consumed as drinks, while Activity B consists…
- T-6 Cocoa-fruit beverage shots ↔ P1-4 Custom chocolate products and smal… (sim. 0.45): A consists of ready-to-drink beverage shots for direct consumption, while B consists of chocolate c…
- T-6 Cocoa-fruit beverage shots ↔ P1-5 Corporate gifts and promotional ch… (sim. 0.41): A consists of small ready-to-drink beverages consumed directly. B consists of chocolate products bo…
- T-6 Cocoa-fruit beverage shots ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.39): A is a ready-to-drink beverage consumed directly, while B is a workshop and educational visitor exp…
- T-6 Cocoa-fruit beverage shots ↔ P1-9 Non-food gifts and merchandise (sim. 0.29): Activity A consists of ready-to-drink beverages consumed directly. Activity B consists of non-food …
- T-6 Cocoa-fruit beverage shots ↔ P1-12 Electricity and heat generation fo… (sim. 0.19): Activity A is a ready-to-drink beverage for direct consumption, while Activity B generates electric…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-1 Packaged chocolate bars and chocol… (sim. 0.43): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B is ready-to-eat chocolate…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-2 Packaged chocolate and chocolate c… (sim. 0.43): A is a pulp ingredient used to make balsamic vinegar, while B consists of ready-to-eat chocolate an…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-3 Cream-filled, chocolate-covered wa… (sim. 0.38): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas chocolate-covered wafer ro…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-4 Custom chocolate products and smal… (sim. 0.45): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B offers finished chocolat…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-5 Corporate gifts and promotional ch… (sim. 0.39): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B is finished chocolate sol…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-7 Chocolate-making workshops and vis… (sim. 0.41): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, whereas B provides educational an…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-8 Bistro food and beverages and even… (sim. 0.28): Cocoa-fruit pulp is an ingredient used to make finished balsamic vinegar, whereas B offers prepared…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-9 Non-food gifts and merchandise (sim. 0.28): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas the gifts and merchandise …
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-11 Hazelnut cultivation (sim. 0.48): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while hazelnut cultivation produce…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P1-12 Electricity and heat generation fo… (sim. 0.26): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas Activity B generates elect…

</details>

### Barry Callebaut

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-3 Dried cocoa-fruit pulp | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.81 | Both activities include cocoa-fruit pulp supplied as an ingredient for food preparations, including in powder form. B also offers juice and concentrate, but th… |  |
| T-2 Cocoa-fruit juice concentrate | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.80 | Both activities include cocoa-fruit juice concentrate supplied as an intermediate ingredient for manufacturers, with uses including beverages and ice cream. Ac… |  |
| T-1 Cocoa-fruit juice | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.79 | Both activities include cocoa-fruit juice supplied as an ingredient for manufacturers and food professionals. Activity B also includes pulp, concentrate and so… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.76 | A is a finished ready-to-drink beverage, while B consists of ingredients supplied for use in manufacturing foods and beverages. B’s juice or concentrate could … | no EEA overlap |
| T-7 Cocoa-fruit pulp ingredient f… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.76 | Both activities include cocoa-fruit pulp supplied as an intermediate ingredient. B also includes juice, concentrate and powder products, and its stated uses ar… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-8 Cocoa-fruit ingredients | candidate | same product | ●●○ | A could be an input for B (rule); B could be an input for A (rule) | 0.73 | Both activities include dried cocoa-fruit pulp blended with cocoa powder for use as a food ingredient; Activity A specifies a 90% pulp and 10% cocoa-powder ble… |  |
| T-3 Dried cocoa-fruit pulp | P2-3 Cocoa liquor, cocoa butter an… | candidate | different product |  | A could be an input for B (rule); B could be an input for A (rule) | 0.69 | Dried cocoa-fruit pulp is used for sweetening, flavouring and crunchy inclusions, while cocoa liquor, cocoa butter and cocoa powder are processed cocoa-bean in… |  |
| T-1 Cocoa-fruit juice | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); B could be an input for A (rule) | 0.66 | Cocoa-fruit juice and cocoa liquor, butter and powder are distinct cocoa-derived ingredients, but both are used in beverages and food preparations. The descrip… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P2-3 Cocoa liquor, cocoa butter an… | candidate | different product |  | A could be an input for B (rule); B could be an input for A (rule) | 0.65 | A is cocoa-fruit pulp used specifically to make balsamic vinegar. B consists of processed cocoa ingredients used to make chocolate, bakery, dessert and beverag… |  |
| T-2 Cocoa-fruit juice concentrate | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); B could be an input for A (rule) | 0.64 | Cocoa-fruit juice concentrate is a fruit ingredient and sweetener, while cocoa liquor, butter and powder are processed cocoa ingredients with different charact… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-3 Cocoa liquor, cocoa butter an… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule); B could be an input for A (AI and rule) | 0.64 | A is a dried cocoa-pulp blend used as a food ingredient, while B comprises processed cocoa ingredients, including cocoa powder. The cocoa-powder component of A… |  |
| T-3 Dried cocoa-fruit pulp | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.63 | Both are professional food ingredients used in chocolate and other preparations, but dried cocoa-fruit pulp is a sweetening, flavouring or crunchy inclusion, w… |  |
| T-3 Dried cocoa-fruit pulp | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.63 | Dried cocoa-fruit pulp is used to sweeten, flavour and add crunchy inclusions, while industrial chocolate is used as an ingredient in confectionery and other f… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-3 Cocoa liquor, cocoa butter an… | candidate | different product |  | B could be an input for A (rule) | 0.62 | A is a ready-to-drink cocoa-fruit beverage, while B consists of processed cocoa ingredients used mainly to manufacture other food products. Their stated uses d… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.60 | Dried cocoa-fruit pulp is used for sweetening, flavouring and crunchy inclusions, while the sunflower-seed-based ingredients are chocolate-like ingredients and… |  |
| T-6 Cocoa-fruit beverage shots | P2-8 Cocoa-fruit ingredients | candidate | different product |  | B could be an input for A (AI and rule) | 0.60 | A consists of finished, ready-to-drink beverage shots consumed directly, while B consists of intermediate cocoa-fruit ingredients supplied for use in manufactu… |  |
| T-1 Cocoa-fruit juice | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.60 | Cocoa-fruit juice is a pasteurised liquid ingredient, while B consists mainly of chocolate and cocoa ingredients in professional formats. They can plausibly se… |  |
| T-3 Dried cocoa-fruit pulp | P2-4 Confectionery coatings, filli… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (rule) | 0.60 | Dried cocoa-fruit pulp is a sweetening, flavouring and crunchy inclusion ingredient, while B supplies a broader range of coatings, fillings, inclusions and dec… |  |
| T-2 Cocoa-fruit juice concentrate | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.59 | Cocoa-fruit juice concentrate is a fruit ingredient and sweetener, while industrial chocolate and couverture are chocolate ingredients with distinct characteri… |  |
| T-1 Cocoa-fruit juice | P2-1 Industrial chocolate and couv… | candidate | different product |  | A could be an input for B (rule) | 0.59 | Cocoa-fruit juice is a pasteurised fruit juice ingredient, while industrial chocolate and couverture are chocolate ingredients with different characteristics a… |  |
| T-2 Cocoa-fruit juice concentrate | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.57 | Both are professional-format ingredients used in preparing foods such as chocolate fillings, bakery products and ice cream, but cocoa-fruit juice concentrate i… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.57 | Both are cocoa-based ingredients used in preparing finished foods, but A is a dried pulp-and-cocoa blend while B comprises chocolate and cocoa ingredients such… |  |
| T-2 Cocoa-fruit juice concentrate | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.57 | A is a cocoa-fruit-derived concentrate used as a fruit ingredient and sweetener, while B is a sunflower-seed-based chocolate-like ingredient or coating. Althou… |  |
| T-6 Cocoa-fruit beverage shots | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.56 | Both are beverage products intended for direct consumption as drinks, but A is a ready-to-drink shot while B consists mainly of mixes and ingredients prepared … |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (rule) | 0.56 | Both are intermediate food ingredients used by manufacturers in finished foods, including confectionery or bakery applications. The cocoa-pulp and cocoa-powder… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.56 | Both are cocoa-based ingredients supplied for use in finished foods and culinary preparations. The dried pulp-and-cocoa blend is not chocolate or couverture, b… |  |
| T-3 Dried cocoa-fruit pulp | P2-6 Biscuit, cookie, cereal and m… | candidate | similar product, possibly substitutable | ●●○ |  | 0.55 | Both are intermediate food ingredients used to sweeten, flavour or add crunchy inclusions to prepared foods and desserts. Dried cocoa-fruit pulp differs from t… |  |
| T-2 Cocoa-fruit juice concentrate | P2-4 Confectionery coatings, filli… | candidate | different product |  | A could be an input for B (AI and rule) | 0.55 | A is a concentrated fruit ingredient and sweetener used in manufacturing, while B comprises confectionery coatings, fillings, inclusions and decorations used t… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●○○ |  | 0.55 | A is a ready-to-drink cocoa-fruit beverage, while B includes mixes used to prepare fruit and cocoa drinks. They differ in form and preparation, but may serve t… | no EEA overlap |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-2 Professional chocolate and co… | candidate | similar product, possibly substitutable | ●○○ |  | 0.54 | Both are cocoa-derived products used in food and drink, but A is a ready-to-drink juice while B consists of chocolate and cocoa ingredients for professional pr… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.54 | Dried cocoa-fruit pulp is a sweetening and flavouring ingredient, while B consists of mixes and ingredients for preparing beverages. They are not the same prod… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.54 | A is cocoa-fruit pulp used to make balsamic vinegar, while B is a sunflower-seed-based chocolate-like ingredient or coating used in confectionery, bakery and o… |  |
| T-2 Cocoa-fruit juice concentrate | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.54 | A is a concentrated cocoa-fruit ingredient and sweetener for use in beverages and other foods, while B consists of prepared beverage mixes and milk-based bever… |  |
| T-3 Dried cocoa-fruit pulp | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.53 | Dried cocoa-fruit pulp is used to sweeten, flavour and add crunchy inclusions to food preparations, while some nut ingredients and preparations—such as praliné… |  |
| T-1 Cocoa-fruit juice | P2-7 Instant beverage mixes and mi… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.53 | Cocoa-fruit juice is an ingredient used in beverages, while B includes mixes and ingredients for prepared drinks. They are not the same product, but cocoa-frui… |  |
| T-1 Cocoa-fruit juice | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.53 | Cocoa-fruit juice is a pasteurised juice ingredient used in beverages and food preparations, whereas B consists of sunflower-seed-based chocolate-like ingredie… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-4 Confectionery coatings, filli… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.52 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient, while B comprises coatings, fillings, inclusions and decorations made from ingredients including coc… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-7 Instant beverage mixes and mi… | candidate | different product |  | A could be an input for B (AI) | 0.51 | A is a dried cocoa-fruit-pulp and cocoa-powder ingredient for finished foods and culinary preparations. B comprises beverage mixes and milk-based ingredients i… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (rule) | 0.50 | A is a ready-to-drink beverage, while B is a chocolate-like ingredient or coating used by manufacturers in finished foods. Their characteristics and intended u… | no EEA overlap |
| T-1 Cocoa-fruit juice | P2-4 Confectionery coatings, filli… | candidate | different product |  | A could be an input for B (rule) | 0.50 | Cocoa-fruit juice is a beverage ingredient used in beverages and food preparations, whereas B comprises coatings, fillings and decorative ingredients used to c… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P2-7 Instant beverage mixes and mi… | candidate | different product |  | A could be an input for B (AI) | 0.49 | A is cocoa-fruit pulp used to make balsamic vinegar, while B comprises mixes and ingredients for preparing beverages. Their intended uses differ, and the descr… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-6 Biscuit, cookie, cereal and m… | candidate | similar product, possibly substitutable | ●●○ |  | 0.47 | Both are intermediate food ingredients used in finished foods and culinary preparations, including desserts. Their compositions differ substantially, but the d… |  |
| T-2 Cocoa-fruit juice concentrate | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.47 | Both are intermediate food ingredients used in overlapping applications such as beverages, bakery, confectionery and ice cream. Cocoa-fruit juice concentrate i… |  |
| T-1 Cocoa-fruit juice | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.46 | Cocoa-fruit juice and nut ingredients are different products with different characteristics, but both can be used as ingredients in beverages and some food pre… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P2-5 Nut ingredients and almond pr… | candidate | similar product, possibly substitutable | ●●○ |  | 0.46 | A is a dried cocoa-pulp and cocoa-powder ingredient, while B comprises nut-based ingredients and preparations. Both are used as ingredients in some of the same… |  |
| T-2 Cocoa-fruit juice concentrate | P2-6 Biscuit, cookie, cereal and m… | candidate | similar product, possibly substitutable | ●●○ |  | 0.45 | Both are intermediate food ingredients used by manufacturers in products such as bakery items and desserts, but they differ in form and function: A is a liquid… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P2-2 Professional chocolate and co… | unclear | different product |  |  | 0.58 | Cocoa-fruit pulp is used to make balsamic vinegar, while professional chocolate and cocoa ingredients are used to prepare chocolate, pastry, bakery and ice-cre… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P2-1 Industrial chocolate and couv… | unclear | different product |  |  | 0.57 | Cocoa-fruit pulp is used to make balsamic vinegar, while industrial chocolate and couverture are used to make confectionery, bakery products, ice cream and des… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P2-1 Industrial chocolate and couv… | unclear | different product |  |  | 0.53 | A is a ready-to-drink fruit beverage for consumption or use in drinks and cooking. B is an industrial chocolate ingredient used by manufacturers to make confec… | no EEA overlap |
| T-7 Cocoa-fruit pulp ingredient f… | P2-4 Confectionery coatings, filli… | unclear | different product |  |  | 0.52 | A is cocoa-fruit pulp used to make balsamic vinegar, while B comprises coatings, fillings and decorations used in confectionery, bakery products, ice cream and… |  |

<details><summary>20 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P2-6 Biscuit, cookie, cereal and mering… (sim. 0.36): Cocoa-fruit juice is a liquid ingredient used in beverages and food preparations, while B supplies …
- T-1 Cocoa-fruit juice ↔ P2-10 Professional chocolate and pastry … (sim. 0.36): Cocoa-fruit juice is a food ingredient used in beverages and food preparations, while the other act…
- T-2 Cocoa-fruit juice concentrate ↔ P2-10 Professional chocolate and pastry … (sim. 0.33): Cocoa-fruit juice concentrate is a food ingredient and sweetener used in manufacturing food and bev…
- T-3 Dried cocoa-fruit pulp ↔ P2-10 Professional chocolate and pastry … (sim. 0.41): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to preparations…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P2-10 Professional chocolate and pastry … (sim. 0.35): Activity A is a dried food ingredient used in finished foods and culinary preparations. Activity B …
- T-5 Ready-to-drink cocoa-fruit juice ↔ P2-4 Confectionery coatings, fillings, … (sim. 0.47): A is a ready-to-drink cocoa-fruit beverage, while B comprises ingredients and decorations used in c…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P2-5 Nut ingredients and almond prepara… (sim. 0.39): A is a ready-to-drink cocoa-fruit beverage, while B consists of nut ingredients and preparations us…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P2-6 Biscuit, cookie, cereal and mering… (sim. 0.34): A is a ready-to-drink cocoa-fruit beverage, while B consists of crunchy biscuit, cereal and meringu…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P2-10 Professional chocolate and pastry … (sim. 0.32): A is a ready-to-drink beverage used for consumption and in food preparation, while B is a training …
- T-6 Cocoa-fruit beverage shots ↔ P2-1 Industrial chocolate and couverture (sim. 0.45): A is a ready-to-drink beverage consumed directly, while B is industrial chocolate supplied as an in…
- T-6 Cocoa-fruit beverage shots ↔ P2-2 Professional chocolate and cocoa i… (sim. 0.47): Activity A consists of ready-to-drink shots consumed directly as beverages. Activity B consists of …
- T-6 Cocoa-fruit beverage shots ↔ P2-3 Cocoa liquor, cocoa butter and coc… (sim. 0.49): Activity A consists of ready-to-drink beverages consumed directly, while Activity B consists of pro…
- T-6 Cocoa-fruit beverage shots ↔ P2-4 Confectionery coatings, fillings, … (sim. 0.40): A consists of ready-to-drink beverage shots consumed directly, while B consists of ingredients and …
- T-6 Cocoa-fruit beverage shots ↔ P2-5 Nut ingredients and almond prepara… (sim. 0.35): A consists of ready-to-drink beverage shots consumed directly, whereas B consists of nut ingredient…
- T-6 Cocoa-fruit beverage shots ↔ P2-6 Biscuit, cookie, cereal and mering… (sim. 0.34): A consists of ready-to-drink beverage shots for direct consumption, while B consists of biscuit, ce…
- T-6 Cocoa-fruit beverage shots ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.45): A consists of ready-to-drink small-format beverages consumed directly, while B consists of sunflowe…
- T-6 Cocoa-fruit beverage shots ↔ P2-10 Professional chocolate and pastry … (sim. 0.32): A is a ready-to-drink beverage consumed directly, while B is training that provides practical skill…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P2-5 Nut ingredients and almond prepara… (sim. 0.43): A is cocoa-fruit pulp used specifically to make balsamic vinegar, while B comprises nut-based ingre…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P2-6 Biscuit, cookie, cereal and mering… (sim. 0.42): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B consists of biscuit, cerea…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P2-10 Professional chocolate and pastry … (sim. 0.33): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, while B provides training and tut…

</details>

### Bahlsen

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-6 Cocoa-fruit beverage shots | P3-6 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.46 | A is a small, ready-to-drink beverage and B is a solid snack bar, so they are different product types. Both are portable consumer refreshments, and a customer … |  |
| T-3 Dried cocoa-fruit pulp | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI and rule) | 0.45 | Dried cocoa-fruit pulp is an ingredient used to sweeten or flavour food and provide crunchy inclusions, while B consists of finished biscuits, wafers and pastr… |  |
| T-3 Dried cocoa-fruit pulp | P3-5 Private-label biscuits, wafer… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.44 | Dried cocoa-fruit pulp is an ingredient used to sweeten or flavour foods and add crunchy inclusions, while B supplies finished sweet snacks and confectionery. … |  |
| T-3 Dried cocoa-fruit pulp | P3-6 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.44 | Dried cocoa-fruit pulp is a food ingredient used in preparations, while the fruit-and-nut and protein bars are finished portable snacks. The descriptions do no… |  |
| T-3 Dried cocoa-fruit pulp | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be resold by B (AI) | 0.43 | A is a dried ingredient used in food preparations, while B is the retail sale of packaged foods for consumers. Although some foods sold by B may contain cocoa … |  |
| T-2 Cocoa-fruit juice concentrate | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.43 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener used in manufacturing, while biscuits, wafers and pastries are finished baked goods e… |  |
| T-2 Cocoa-fruit juice concentrate | P3-5 Private-label biscuits, wafer… | candidate | different product |  | A could be an input for B (AI) | 0.43 | A is a concentrated cocoa-fruit ingredient used in manufacturing foods and beverages, while B consists of finished sweet snacks and confectionery sold for cons… |  |
| T-3 Dried cocoa-fruit pulp | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.42 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring and adding crunchy inclusions, while packaged cakes are ready-to-eat snacks or desserts. The… |  |
| T-6 Cocoa-fruit beverage shots | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●○○ |  | 0.42 | Both are finished, individually portioned consumer products intended for direct consumption as snacks or refreshments. A beverage shot and a biscuit-and-chocol… |  |
| T-2 Cocoa-fruit juice concentrate | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.42 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener used in manufacturing, while biscuit-based snack bars are packaged, ready-to-eat cons… |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be resold by B (AI) | 0.41 | A is a ready-to-drink cocoa-fruit beverage, while B is the retail sale of a range of packaged foods such as snacks, chocolate, cereal bars and jam. The descrip… | no EEA overlap |
| T-3 Dried cocoa-fruit pulp | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.41 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring and adding texture to food preparations, while biscuit-based bars are finished snacks. They … |  |
| T-5 Ready-to-drink cocoa-fruit ju… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI) | 0.41 | A is a ready-to-drink cocoa-fruit beverage, while B consists of baked biscuits, cookies, wafers and pastries. They are different product types, despite both be… | no EEA overlap |
| T-4 Dried cocoa-fruit pulp mixed … | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.41 | A is an ingredient for finished foods and culinary preparations, whereas B consists of finished baked goods eaten as snacks or treats. Consumers would not use … |  |
| T-4 Dried cocoa-fruit pulp mixed … | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.41 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in finished foods and culinary preparations, whereas B is a packaged biscuit-and-chocolate snack ea… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P3-5 Private-label biscuits, wafer… | candidate | different product |  | A could be an input for B (AI) | 0.40 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in food manufacturing and culinary preparations. B consists of finished biscuits, wafers and confec… |  |
| T-2 Cocoa-fruit juice concentrate | P3-6 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.40 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener for manufacturers, while fruit-and-nut and protein bars are finished portable snacks.… |  |
| T-2 Cocoa-fruit juice concentrate | P3-3 Packaged cakes | candidate | different product |  | A could be an input for B (AI) | 0.39 | Cocoa-fruit juice concentrate is an intermediate ingredient and sweetener, while packaged cakes are ready-to-eat snacks or desserts. Consumers would not use th… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P3-6 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is a dried cocoa-fruit pulp and cocoa-powder ingredient for use in food manufacturing and culinary preparations. B consists of finished snack bars eaten dire… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (rule) | 0.39 | Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B consists of finished baked goods eaten as snacks or treats. They have different charac… |  |
| T-6 Cocoa-fruit beverage shots | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be resold by B (AI) | 0.39 | Activity A is a ready-to-drink beverage sold in small-format shots, while Activity B is the retail sale of a varied assortment of packaged foods. The foods des… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is a dried pulp-and-cocoa ingredient for use in finished foods and culinary preparations, whereas B is the retail sale of a varied assortment of packaged fin… |  |
| T-1 Cocoa-fruit juice | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be resold by B (AI) | 0.39 | Cocoa-fruit juice is a pasteurised ingredient for use in beverage manufacturing and professional food preparation. Activity B is the retail sale of assorted pa… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be an input for B (AI) | 0.39 | A is cocoa-fruit pulp used as an ingredient to make balsamic vinegar, while B is the retail sale of packaged foods such as snacks, confectionery, cereal bars a… |  |
| T-1 Cocoa-fruit juice | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.38 | Cocoa-fruit juice is an ingredient for beverages and food preparations, whereas the other activity supplies finished baked goods eaten as snacks or treats. The… |  |
| T-2 Cocoa-fruit juice concentrate | P3-7 Retail sale of packaged foods | candidate | different product |  | A could be resold by B (AI) | 0.37 | A is a concentrated cocoa-fruit ingredient used by manufacturers in making foods and beverages. B is the retail sale of packaged finished foods for consumers; … |  |
| T-3 Dried cocoa-fruit pulp | P3-4 Seasonal baked goods | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.35 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring and adding crunch, while the seasonal baked goods are finished snacks or treats. They are di… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P3-4 Seasonal baked goods | candidate | different product |  | A could be an input for B (AI) | 0.33 | Activity A is an ingredient blend for use in finished foods and culinary preparations, while Activity B consists of ready-to-eat seasonal biscuits and baked go… |  |
| T-2 Cocoa-fruit juice concentrate | P3-4 Seasonal baked goods | candidate | different product |  | A could be an input for B (AI) | 0.32 | Cocoa-fruit juice concentrate is an ingredient and sweetener used in manufacturing, while seasonal baked goods are finished snacks or treats for consumers. The… |  |

<details><summary>27 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P3-2 Biscuit-based snack bars (sim. 0.34): Cocoa-fruit juice is an ingredient used in beverage manufacturing and food preparation, whereas bis…
- T-1 Cocoa-fruit juice ↔ P3-3 Packaged cakes (sim. 0.41): Cocoa-fruit juice is an ingredient for beverages and food preparations, whereas packaged cakes are …
- T-1 Cocoa-fruit juice ↔ P3-4 Seasonal baked goods (sim. 0.29): Cocoa-fruit juice is an ingredient used in beverage manufacturing and food preparation, while seaso…
- T-1 Cocoa-fruit juice ↔ P3-5 Private-label biscuits, wafers and… (sim. 0.39): Cocoa-fruit juice is an ingredient used in beverages and food preparations, whereas the biscuits, w…
- T-1 Cocoa-fruit juice ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.38): Cocoa-fruit juice is an ingredient used in beverage manufacturing and food preparation, while the b…
- T-1 Cocoa-fruit juice ↔ P3-8 Branded clothing and fabric bags (sim. 0.29): Cocoa-fruit juice is an ingredient used in beverages and food preparations, while clothing and fabr…
- T-2 Cocoa-fruit juice concentrate ↔ P3-8 Branded clothing and fabric bags (sim. 0.26): Cocoa-fruit juice concentrate is a food ingredient and sweetener used in food and beverage manufact…
- T-3 Dried cocoa-fruit pulp ↔ P3-8 Branded clothing and fabric bags (sim. 0.28): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food prepara…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P3-3 Packaged cakes (sim. 0.39): A is a dried ingredient for use in finished foods and culinary preparations, while B is a ready-to-…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P3-8 Branded clothing and fabric bags (sim. 0.24): A is a dried cocoa-pulp and cocoa-powder ingredient for finished foods and culinary preparations, w…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-2 Biscuit-based snack bars (sim. 0.41): A is a ready-to-drink cocoa-fruit beverage, while B is a packaged biscuit-and-chocolate snack bar. …
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-3 Packaged cakes (sim. 0.45): A is a ready-to-drink cocoa-fruit beverage, while B is a packaged cake eaten as a snack or dessert.…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-4 Seasonal baked goods (sim. 0.33): A is a ready-to-drink cocoa-fruit beverage, while B consists of seasonal biscuits and baked goods. …
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-5 Private-label biscuits, wafers and… (sim. 0.40): A is a ready-to-drink cocoa-fruit beverage, while B consists of biscuits, wafers and confectionery …
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.45): A is a ready-to-drink beverage, while B consists of solid snack bars. Although both are consumed by…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P3-8 Branded clothing and fabric bags (sim. 0.32): Ready-to-drink cocoa-fruit juice is a beverage for drinking or use in cooking, while hoodies and fa…
- T-6 Cocoa-fruit beverage shots ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.38): A consists of small-format ready-to-drink beverages, while B consists of baked goods eaten as snack…
- T-6 Cocoa-fruit beverage shots ↔ P3-3 Packaged cakes (sim. 0.40): Activity A supplies small-format ready-to-drink beverages for direct consumption, while Activity B …
- T-6 Cocoa-fruit beverage shots ↔ P3-4 Seasonal baked goods (sim. 0.36): A consists of ready-to-drink beverage shots consumed as drinks, while B consists of seasonal biscui…
- T-6 Cocoa-fruit beverage shots ↔ P3-5 Private-label biscuits, wafers and… (sim. 0.37): Activity A consists of ready-to-drink beverage shots consumed as drinks, while Activity B consists …
- T-6 Cocoa-fruit beverage shots ↔ P3-8 Branded clothing and fabric bags (sim. 0.30): Activity A offers small ready-to-drink beverages for consumption, while Activity B offers clothing …
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-2 Biscuit-based snack bars (sim. 0.37): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while biscuit-based bars are finis…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-3 Packaged cakes (sim. 0.36): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas packaged cakes are ready-t…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-4 Seasonal baked goods (sim. 0.32): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while the seasonal baked goods are…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-5 Private-label biscuits, wafers and… (sim. 0.40): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B supplies finished sweet sn…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-6 Organic fruit-and-nut bars and pro… (sim. 0.36): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B consists of finished snack…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P3-8 Branded clothing and fabric bags (sim. 0.31): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while hoodies and tote bags are wo…

</details>

### FRoSTA

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-3 Dried cocoa-fruit pulp | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.39 | Dried cocoa-fruit pulp is a sweetening, flavouring and inclusion ingredient, while B is a range of frozen foods for professional kitchens. For some food prepar… |  |
| T-3 Dried cocoa-fruit pulp | P4-2 Customer-branded frozen foods | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.38 | Dried cocoa-fruit pulp is an ingredient used for sweetening, flavouring and crunchy inclusions, while B consists of finished frozen foods. They are different p… |  |
| T-3 Dried cocoa-fruit pulp | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.37 | Dried cocoa-fruit pulp is a sweetening, flavouring and crunchy inclusion ingredient, while B consists of ready-to-eat or meal-preparation frozen foods. They ar… |  |
| T-1 Cocoa-fruit juice | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.36 | Cocoa-fruit juice is a pasteurised fruit ingredient, while the frozen-food range includes frozen fruit and other foods for professional meal preparation. They … |  |
| T-3 Dried cocoa-fruit pulp | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.36 | Dried cocoa-fruit pulp is an ingredient for sweetening, flavouring and adding texture to food preparations. Activity B supplies assorted finished frozen foods … |  |
| T-1 Cocoa-fruit juice | P4-2 Customer-branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.35 | Cocoa-fruit juice is a pasteurised ingredient used in beverages and food preparations, while B makes finished frozen foods for resale. Their uses and product f… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P4-5 Frozen food production and su… | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is a specific cocoa-fruit pulp ingredient used to make balsamic vinegar, while B produces and supplies frozen products for use in downstream food production.… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-2 Customer-branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.35 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in foods and culinary preparations, while B consists of finished frozen foods such as meals, vegeta… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-5 Frozen food production and su… | candidate | not enough information |  | A could be an input for B (AI) | 0.35 | A is a dried cocoa-based ingredient, while B supplies frozen products, but B’s catalogue is not disclosed. Although both are intended for downstream food produ… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.34 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in finished foods and culinary preparations, while B is a range of frozen finished foods for prepar… |  |
| T-1 Cocoa-fruit juice | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI); ✗ A could be resold by B (AI, disregarded: B is not active in wholesale or retail (level: finished products)) | 0.34 | Cocoa-fruit juice is an ingredient for making beverages or food preparations, while Activity B supplies a range of frozen foods for resale to household custome… |  |
| T-3 Dried cocoa-fruit pulp | P4-1 Frozen ready meals, fish, veg… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.34 | Dried cocoa-fruit pulp is a sweetening, flavouring, or crunchy ingredient, while B consists of frozen meals and individual frozen foods. The pulp could plausib… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.32 | Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B comprises a range of frozen foods for household consumption. The descriptions do not i… |  |
| T-1 Cocoa-fruit juice | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ |  | 0.32 | Cocoa-fruit juice is an ingredient for beverages and food preparations, while Activity B offers ready-to-eat frozen meals and ingredients for household food pr… |  |
| T-7 Cocoa-fruit pulp ingredient f… | P4-2 Customer-branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.32 | A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, whereas B manufactures a range of frozen foods such as ready meals, fish, vegetables and snac… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.32 | A is a dried cocoa-based ingredient for use in food preparations, while B is a range of finished frozen foods intended for resale and delivery to households. T… |  |
| T-2 Cocoa-fruit juice concentrate | P4-2 Customer-branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.32 | Cocoa-fruit juice concentrate is an intermediate fruit ingredient and sweetener, while B supplies finished frozen foods such as meals, fish, vegetables and sna… |  |
| T-3 Dried cocoa-fruit pulp | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.32 | Dried cocoa-fruit pulp is a sweetening, flavouring and inclusion ingredient for food preparations, while the described activity is a range of branded frozen fo… |  |
| T-2 Cocoa-fruit juice concentrate | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.30 | Cocoa-fruit juice concentrate is an intermediate fruit ingredient and sweetener used in food and beverage manufacturing, whereas the other activity is a range … |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.30 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in finished foods and culinary preparations. B is a range of branded frozen foods, and the descript… |  |
| T-2 Cocoa-fruit juice concentrate | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.30 | Cocoa-fruit juice concentrate is an ingredient and sweetener, while the frozen-food range consists of finished products for professional kitchens. The concentr… |  |
| T-1 Cocoa-fruit juice | P4-3 Branded frozen foods | candidate | not enough information |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.30 | Cocoa-fruit juice is an ingredient used in beverages and food preparations, while the frozen-food description does not identify the products’ categories or cha… |  |
| T-4 Dried cocoa-fruit pulp mixed … | P4-1 Frozen ready meals, fish, veg… | candidate | different product |  | A could be an input for B (AI) | 0.30 | A is a dried cocoa-pulp and cocoa-powder ingredient for use in food manufacturing and culinary preparations. B comprises frozen ready meals and frozen foods fo… |  |
| T-1 Cocoa-fruit juice | P4-1 Frozen ready meals, fish, veg… | candidate | different product |  | A could be an input for B (AI) | 0.30 | Cocoa-fruit juice is an ingredient used in beverages and professional food preparations, whereas B consists of frozen ready meals and frozen food products for … |  |
| T-2 Cocoa-fruit juice concentrate | P4-7 Frozen meals, fish, vegetable… | candidate | different product |  | A could be an input for B (AI) | 0.27 | Cocoa-fruit juice concentrate is an intermediate fruit ingredient and sweetener used in manufacturing, while Activity B consists of branded frozen meals and ot… |  |
| T-2 Cocoa-fruit juice concentrate | P4-1 Frozen ready meals, fish, veg… | candidate | different product |  | A could be an input for B (AI) | 0.25 | A is a concentrated cocoa-fruit ingredient and sweetener used in manufacturing, while B consists of frozen meals and frozen food items intended for household m… |  |
| T-3 Dried cocoa-fruit pulp | P4-5 Frozen food production and su… | unclear | not enough information |  |  | 0.39 | A is a specified cocoa-fruit ingredient used for sweetening, flavouring and crunchy inclusions, while B supplies frozen products whose types are not disclosed.… |  |
| T-1 Cocoa-fruit juice | P4-5 Frozen food production and su… | unclear | not enough information |  |  | 0.39 | A is a specified cocoa-fruit juice ingredient for beverages and food preparations. B supplies frozen products for downstream food production, but its catalogue… |  |
| T-2 Cocoa-fruit juice concentrate | P4-5 Frozen food production and su… | unclear | not enough information |  |  | 0.34 | A is a specified cocoa-fruit concentrate used as an ingredient and sweetener, while B's frozen products are not identified in an exhaustive catalogue. The desc… |  |

<details><summary>41 pairs screened out</summary>

- T-1 Cocoa-fruit juice ↔ P4-8 Frozen meals and team meal boxes (sim. 0.29): Cocoa-fruit juice is an ingredient for beverages and food preparations, while frozen meals and meal…
- T-1 Cocoa-fruit juice ↔ P4-9 Food product development and assor… (sim. 0.36): A is a pasteurised cocoa-fruit juice used as a food and beverage ingredient, while B is a business …
- T-1 Cocoa-fruit juice ↔ P4-10 Non-food merchandise (sim. 0.28): Cocoa-fruit juice is an ingredient for beverage and food preparation, while the merchandise consist…
- T-2 Cocoa-fruit juice concentrate ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.27): A is a concentrated ingredient and sweetener for manufacturing products such as beverages, fillings…
- T-2 Cocoa-fruit juice concentrate ↔ P4-8 Frozen meals and team meal boxes (sim. 0.22): Cocoa-fruit juice concentrate is an ingredient and sweetener used in food manufacturing, while froz…
- T-2 Cocoa-fruit juice concentrate ↔ P4-9 Food product development and assor… (sim. 0.36): A is a concentrated cocoa-fruit ingredient and sweetener used in food and beverage production. B is…
- T-2 Cocoa-fruit juice concentrate ↔ P4-10 Non-food merchandise (sim. 0.26): Cocoa-fruit juice concentrate is a food ingredient and sweetener used in manufacturing food and bev…
- T-3 Dried cocoa-fruit pulp ↔ P4-8 Frozen meals and team meal boxes (sim. 0.26): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to preparations…
- T-3 Dried cocoa-fruit pulp ↔ P4-9 Food product development and assor… (sim. 0.37): A is a dried food ingredient used to sweeten, flavour and add texture to food preparations. B is a …
- T-3 Dried cocoa-fruit pulp ↔ P4-10 Non-food merchandise (sim. 0.29): Dried cocoa-fruit pulp is a food ingredient used to sweeten, flavour or add texture to food prepara…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.34): A is a dried cocoa-pulp and cocoa-powder ingredient for use in finished foods and culinary preparat…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P4-8 Frozen meals and team meal boxes (sim. 0.26): Activity A is a dried cocoa-pulp and cocoa-powder ingredient used in food manufacturing and culinar…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P4-9 Food product development and assor… (sim. 0.32): A is a dried food ingredient for use in finished foods and culinary preparations. B is a business c…
- T-4 Dried cocoa-fruit pulp mixed with … ↔ P4-10 Non-food merchandise (sim. 0.25): Activity A is a food ingredient for use in finished foods and culinary preparations. Activity B con…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-1 Frozen ready meals, fish, vegetabl… (sim. 0.32): A is a ready-to-drink beverage, while B comprises frozen meals and frozen food ingredients for hous…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-2 Customer-branded frozen foods (sim. 0.35): A is a ready-to-drink cocoa-fruit beverage, while B makes a range of frozen foods such as meals, ve…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-3 Branded frozen foods (sim. 0.32): Ready-to-drink cocoa-fruit juice is a beverage, while branded frozen foods are frozen-food products…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-4 Frozen foods for professional kitc… (sim. 0.34): A is a ready-to-drink cocoa-fruit beverage, while B consists of frozen foods prepared and served as…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-5 Frozen food production and supply … (sim. 0.33): A is a ready-to-drink cocoa-fruit beverage for consumption and culinary use. B supplies frozen prod…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.33): A is a ready-to-drink cocoa-fruit beverage, while B is a range of frozen foods such as fish, vegeta…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.35): Ready-to-drink cocoa-fruit juice is a beverage, while frozen meals, fish, vegetables and herbs are …
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-8 Frozen meals and team meal boxes (sim. 0.30): A is a ready-to-drink cocoa-fruit beverage, while B consists of frozen meals and meal boxes prepare…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-9 Food product development and assor… (sim. 0.34): A is a ready-to-drink beverage for consumption and use in cooking or cocktails. B is a business con…
- T-5 Ready-to-drink cocoa-fruit juice ↔ P4-10 Non-food merchandise (sim. 0.34): A is a ready-to-drink beverage used for drinking, mixing or cooking. B comprises non-food clothing,…
- T-6 Cocoa-fruit beverage shots ↔ P4-1 Frozen ready meals, fish, vegetabl… (sim. 0.30): A comprises small, ready-to-drink beverage shots consumed as drinks. B comprises frozen meals and f…
- T-6 Cocoa-fruit beverage shots ↔ P4-2 Customer-branded frozen foods (sim. 0.33): A consists of small-format ready-to-drink beverages consumed directly. B consists of frozen meals a…
- T-6 Cocoa-fruit beverage shots ↔ P4-3 Branded frozen foods (sim. 0.30): A consists of small ready-to-drink beverage shots consumed directly. B is a range of frozen foods f…
- T-6 Cocoa-fruit beverage shots ↔ P4-4 Frozen foods for professional kitc… (sim. 0.32): A consists of small, ready-to-drink beverage shots consumed directly. B consists of frozen food pro…
- T-6 Cocoa-fruit beverage shots ↔ P4-5 Frozen food production and supply … (sim. 0.29): A consists of ready-to-drink shots consumed directly, while B supplies frozen products for use as i…
- T-6 Cocoa-fruit beverage shots ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.29): A consists of ready-to-drink beverage shots, while B consists of frozen foods such as fish, vegetab…
- T-6 Cocoa-fruit beverage shots ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.32): A consists of ready-to-drink beverage shots consumed directly, while B consists of frozen foods int…
- T-6 Cocoa-fruit beverage shots ↔ P4-8 Frozen meals and team meal boxes (sim. 0.31): A consists of small, ready-to-drink beverage shots, while B consists of frozen meals and meal boxes…
- T-6 Cocoa-fruit beverage shots ↔ P4-9 Food product development and assor… (sim. 0.33): A is a ready-to-drink beverage for direct consumption, while B is a business advisory service for f…
- T-6 Cocoa-fruit beverage shots ↔ P4-10 Non-food merchandise (sim. 0.34): A consists of ready-to-drink beverages consumed directly, while B consists of clothing, accessories…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-1 Frozen ready meals, fish, vegetabl… (sim. 0.25): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, whereas B consists of finished fr…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-3 Branded frozen foods (sim. 0.30): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while Activity B comprises branded…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-4 Frozen foods for professional kitc… (sim. 0.30): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B comprises a varied range…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.29): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, whereas B offers finished frozen m…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-8 Frozen meals and team meal boxes (sim. 0.21): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B supplies frozen meals and …
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-9 Food product development and assor… (sim. 0.39): A is a cocoa-fruit pulp ingredient used to make balsamic vinegar, whereas B is consulting that supp…
- T-7 Cocoa-fruit pulp ingredient for ba… ↔ P4-10 Non-food merchandise (sim. 0.32): Cocoa-fruit pulp is an ingredient used to make balsamic vinegar, while B consists of finished non-f…

</details>

## Calibration: closest pairs that were screened out

If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.

- 0.49 · T-6 Cocoa-fruit beverage shots ↔ P2-3 Cocoa liquor, cocoa butter and cocoa po… (Barry Callebaut)
- 0.48 · T-7 Cocoa-fruit pulp ingredient for balsami… ↔ P1-11 Hazelnut cultivation (Ritter Sport)
- 0.48 · T-5 Ready-to-drink cocoa-fruit juice ↔ P1-4 Custom chocolate products and small-bat… (Ritter Sport)
- 0.47 · T-5 Ready-to-drink cocoa-fruit juice ↔ P2-4 Confectionery coatings, fillings, inclu… (Barry Callebaut)
- 0.47 · T-6 Cocoa-fruit beverage shots ↔ P2-2 Professional chocolate and cocoa ingred… (Barry Callebaut)
- 0.47 · T-3 Dried cocoa-fruit pulp ↔ P1-11 Hazelnut cultivation (Ritter Sport)
- 0.46 · T-6 Cocoa-fruit beverage shots ↔ P1-2 Packaged chocolate and chocolate confec… (Ritter Sport)
- 0.45 · T-5 Ready-to-drink cocoa-fruit juice ↔ P3-3 Packaged cakes (Bahlsen)
- similarity of candidate pairs: min 0.20 · median 0.45 · max 0.81
- similarity of screened out pairs: min 0.19 · median 0.34 · max 0.49

## Example: exactly what the comparison call received

```
ACTIVITY A
Product: Cocoa-fruit juice
Description: Pasteurised juice supplied as an ingredient in industrial formats, including 10- and 200-litre units.
Intended use: Used by manufacturers in beverages and by culinary professionals in food preparations.
Main inputs: cocoa-fruit pulp
Level of trade: intermediate products
Direct customers: manufacturers / processors, wholesalers / distributors (Food and beverage manufacturers and specialist distributors supplying food professionals.)
End users: consumers and businesses
Sales channels: Direct large-volume business enquiries and professional ingredient distributors.
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

- names removed before any comparison: 73 name variants (list in the .json file)
- comparison calls blocked or failed: 0 (kept as 'unclear', never screened out)
- search: 5 calls (5 from cache) · tokens 0 in / 0 out · USD 0.0000
- extract: 5 calls (4 from cache) · tokens 4,460 in / 1,760 out · USD 0.0013
- embed: 5 calls (4 from cache) · tokens 385 in / 0 out · USD 0.0001
- compare: 280 calls (0 from cache) · tokens 345,689 in / 46,853 out · USD 0.0580
- total: USD 0.0593 (token costs only, without web search fees)
