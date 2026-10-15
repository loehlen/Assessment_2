# Factual comparison TC2: Planet A Foods (20261015-0543)

Models: search saved gpt-6.1-sol · extraction gpt-6-luna · comparison gpt-6-luna · text-embedding-3-large  
Thresholds: unclear ≥ 0.5 · input match ≥ 0.5 · resale ≥ 0.5

## Benchmark check (spec section 13)

6 ✔ as expected · 0 ◐ kept in another form · **0 ✖ missed by the comparison** · 0 ∅ activity not found · 1 ⚠ false positives in a control row

Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py need adjusting: compare with the activity overview below).

| Check | Portco | Pair | Expected | Result | Pairs | Detail |
|---|---|---|---|---|---|---|
| TC2-1 | Barry Callebaut | ChoViva partnership (🔗 note must appear) | relationship | ✔ |  | 🔗 mention found in the public sources |
| TC2-2 | Barry Callebaut | compound / industrial chocolate ↔ ChoViva | horizontal | ✔ | T-1↔P2-1, T-1↔P2-4, T-1↔P2-6, T-1↔P2-9 | 4 of 4 matching pairs as expected |
| TC2-3 | Barry Callebaut | ChoViva Butter (pipeline) ↔ cocoa butter | kept | ✔ | T-2↔P2-3, T-2↔P2-5 | 2 of 2 matching pairs as expected |
| TC2-4 | Ritter Sport | ChoViva → Ritter chocolate (vertical candidate) | vertical | ✔ | T-1↔P1-1, T-1↔P1-3, T-1↔P1-4 | 3 of 3 matching pairs as expected |
| TC2-5 | Ritter Sport | Ritter consumer chocolate ↔ ChoViva (related, ●○○) | horizontal | ✔ | T-1↔P1-3, T-1↔P1-4 | 2 of 3 matching pairs as expected |
| TC2-6 | Bahlsen | ChoViva → biscuits (vertical candidate) | vertical | ✔ | T-1↔P3-1, T-1↔P3-2, T-1↔P3-3, T-1↔P3-4 (+1) | 5 of 5 matching pairs as expected |
| TC2-7 | FRoSTA | control: nothing in common | screened out | ⚠ | T-1↔P4-2, T-1↔P4-3, T-1↔P4-4, T-1↔P4-5 (+14) | 18 of 30 pairs kept: check whether these are false positives |

## Activity overview (stages ①–②)

### Target: Planet A Foods (3 activities, 12 sources)
🔗 The public sources for Planet A Foods mention: Barry Callebaut (check for an existing relationship)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| T-1 | not stated | Cocoa-free chocolate alternative ingredient | intermediate products | manufacturers / processors | not stated | on the market | [1, 3, 4, 5, 6, 8, 10, 11] |
| T-2 | not stated | Yeast-derived food fats and oils | intermediate products | manufacturers / processors | not stated | in development | [1, 9] |
| T-3 | not stated | Product-development and manufacturing-suppor… | services | manufacturers / processors, other businesses | not stated | on the market | [8] |

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
🔗 The public sources for Barry Callebaut mention: Planet A Foods (check for an existing relationship)

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

114 pairs: 74 candidates · 2 unclear · 38 screened out

### Ritter Sport

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-free chocolate alternat… | P1-1 Packaged chocolate bars and o… | candidate | different product |  | A could be an input for B (AI) | 0.57 | A is a bulk ingredient used by food manufacturers to make confectionery and other foods, while B consists of finished chocolate products for consumption or gif… |  |
| T-1 Cocoa-free chocolate alternat… | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be an input for B (AI and rule) | 0.52 | A is a bulk cocoa-free chocolate-alternative ingredient for food manufacturers, while B consists of finished chocolate confectionery for personal consumption a… |  |
| T-1 Cocoa-free chocolate alternat… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.47 | A is a cocoa-free chocolate-alternative ingredient for manufacturers, while B is finished chocolate supplied for gifts and promotion. The products differ in fo… |  |
| T-1 Cocoa-free chocolate alternat… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.47 | A is a bulk chocolate alternative ingredient used by manufacturers in confectionery, while B is a finished chocolate-covered wafer confectionery product. They … |  |
| T-1 Cocoa-free chocolate alternat… | P1-9 Cocoa and hazelnuts grown for… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.46 | The cocoa-free ingredient is formulated for use in chocolate-style applications, while cocoa is a raw material for chocolate production; manufacturers could pl… | captive (not on the merchant market) |
| T-1 Cocoa-free chocolate alternat… | P1-5 Cocoa-fruit beverages | candidate | different product |  | B could be an input for A (AI) | 0.45 | A is a bulk ingredient used by food manufacturers to make confectionery, bakery, cereal and ice-cream products. B consists of ready-to-drink refreshments and a… |  |
| T-3 Product-development and manuf… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.42 | Activity A provides recipe tailoring and production-process support services, while Activity B grows and processes cocoa and hazelnuts as ingredients. The farm… | captive (not on the merchant market) |
| T-1 Cocoa-free chocolate alternat… | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.41 | A is a bulk food ingredient used by manufacturers to make confectionery and other foods. B provides participatory chocolate-making workshops and educational vi… |  |
| T-2 Yeast-derived food fats and o… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.40 | A’s fats are ingredients intended for food manufacturers, while B’s products are finished chocolate confectionery, so they are not the same product. A’s cocoa-… |  |
| T-2 Yeast-derived food fats and o… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.40 | A’s fats are ingredients for food products, while B’s products are finished beverages. They are not the same product, but A’s cocoa-butter-like fat or other ta… |  |
| T-2 Yeast-derived food fats and o… | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.38 | Activity A’s fats are ingredients intended for food manufacturing, including cocoa-butter-like fats; Activity B is finished chocolate confectionery for consump… |  |
| T-2 Yeast-derived food fats and o… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.35 | Activity A’s fats are ingredients for food manufacturers, including fats designed to resemble cocoa butter, while Activity B supplies finished chocolate for gi… |  |
| T-2 Yeast-derived food fats and o… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? | A could be an input for B (AI) | 0.33 | A’s fats are intended as food ingredients, including alternatives to cocoa butter and animal fats, while B is a finished chocolate-covered wafer confectionery.… |  |
| T-1 Cocoa-free chocolate alternat… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.32 | The cocoa-free ingredient is used by manufacturers to make confectionery and ice cream, while the bistro sells prepared items including cake, ice cream, and ho… |  |
| T-3 Product-development and manuf… | P1-5 Cocoa-fruit beverages | candidate | different product |  | A could be an input for B (AI) | 0.30 | A provides recipe-development and production-support services, while B consists of finished beverages for drinking. Customers would not use the service instead… |  |
| T-2 Yeast-derived food fats and o… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.28 | A supplies food fats intended as ingredients for food products, while B serves prepared foods and drinks, including cake and ice cream. The fats could plausibl… |  |

<details><summary>11 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.28): A is a bulk food ingredient used by manufacturers to make confectionery, bakery, cereal, and ice-cr…
- T-2 Yeast-derived food fats and oils ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.30): A is a food ingredient intended for use in manufacturing food products. B provides chocolate-making…
- T-2 Yeast-derived food fats and oils ↔ P1-8 Non-food branded merchandise and g… (sim. 0.28): Activity A supplies food fats for use as ingredients in food products, while Activity B consists of…
- T-2 Yeast-derived food fats and oils ↔ P1-9 Cocoa and hazelnuts grown for the … (sim. 0.42): A produces tailored food fats, including a cocoa-butter-like fat, for use as ingredients. B grows c…
- T-3 Product-development and manufactur… ↔ P1-1 Packaged chocolate bars and other … (sim. 0.37): Activity A provides recipe, application, and production-process support to help businesses adapt an…
- T-3 Product-development and manufactur… ↔ P1-2 Chocolate confectionery sold direc… (sim. 0.38): Activity A provides recipe tailoring, application development, and production-process support for f…
- T-3 Product-development and manufactur… ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.28): A provides recipe tailoring, application development and production-process support for food manufa…
- T-3 Product-development and manufactur… ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.37): Activity A provides technical support to help food manufacturers adapt ingredients and use them in …
- T-3 Product-development and manufactur… ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.37): A provides recipe tailoring and production-process support to help food businesses adapt ingredient…
- T-3 Product-development and manufactur… ↔ P1-7 Prepared food and beverages for on… (sim. 0.34): Activity A provides technical support to food manufacturers for adapting ingredients and using them…
- T-3 Product-development and manufactur… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.35): Activity A provides technical support for adapting ingredients and incorporating them into food pro…

</details>

### Barry Callebaut

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-1 Cocoa-free chocolate alternat… | P2-9 Cocoa-free chocolate alternat… | candidate | same product | ●●● |  | 0.74 | Both are bulk cocoa-free chocolate-alternative ingredients supplied to food manufacturers for use in confectionery, bakery and other finished products. The des… |  |
| T-1 Cocoa-free chocolate alternat… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI) | 0.65 | Both are bulk chocolate ingredients used by manufacturers in confectionery, bakery, cereal, and ice-cream applications. A is cocoa-free while B is conventional… |  |
| T-1 Cocoa-free chocolate alternat… | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●○○ |  | 0.61 | Both are professional ingredients used to make confectionery, baked goods, ice cream and similar products. The cocoa-free ingredient could plausibly replace so… |  |
| T-1 Cocoa-free chocolate alternat… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ |  | 0.58 | Both are bulk or professional-use chocolate-type ingredients for confectionery, bakery, cereal or ice-cream applications. The cocoa-free ingredient can plausib… |  |
| T-1 Cocoa-free chocolate alternat… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.58 | Both are bulk intermediate ingredients used by food manufacturers in products such as chocolate and confectionery, bakery goods, and desserts. The cocoa-free a… |  |
| T-2 Yeast-derived food fats and o… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●●● |  | 0.55 | Both are intermediate food ingredients intended for manufacturers to use in finished foods. The yeast-derived fats are tailored fat ingredients, including a co… |  |
| T-1 Cocoa-free chocolate alternat… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.55 | A is a cocoa-free chocolate-style ingredient for coatings, fillings and other confectionery or bakery applications, while B consists of cocoa-fruit pulp, juice… |  |
| T-1 Cocoa-free chocolate alternat… | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ |  | 0.54 | Both are intermediate food ingredients used in confectionery, bakery and related products, including as coatings, fillings or inclusions. The cocoa-free chocol… |  |
| T-1 Cocoa-free chocolate alternat… | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.51 | A is a bulk chocolate-alternative ingredient, while B comprises nut-based ingredients and preparations. They are different products, but could plausibly serve … |  |
| T-3 Product-development and manuf… | P2-6 Bakery, confectionery and des… | candidate | different product |  | A could be an input for B (AI) | 0.51 | Activity A provides development and production-support services that help customers adapt ingredients and run production processes. Activity B supplies physica… |  |
| T-3 Product-development and manuf… | P2-7 Professional beverage mixes a… | candidate | different product |  | A could be an input for B (AI) | 0.50 | Activity A provides development and production-support services, while Activity B supplies beverage mixes and ingredients. The services may help customers use … |  |
| T-2 Yeast-derived food fats and o… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.49 | Both are intermediate food fats used as ingredients by food manufacturers. The yeast-derived fats are tailored alternatives, including a cocoa-butter-like fat … |  |
| T-2 Yeast-derived food fats and o… | P2-2 Professional and artisan choc… | candidate | different product |  | A could be an input for B (AI) | 0.48 | A consists of yeast-derived fats intended as ingredients in food products, including potential cocoa-butter-like fats. B consists of professional chocolate and… |  |
| T-2 Yeast-derived food fats and o… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.48 | A supplies food fats intended as ingredients for food products, while B consists of chocolate components and preparations. They are different products, but A’s… |  |
| T-2 Yeast-derived food fats and o… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI) | 0.48 | Both are intermediate food ingredients intended for manufacturers, and the in-development fats include cocoa-butter-like alternatives that could plausibly serv… |  |
| T-3 Product-development and manuf… | P2-1 Industrial chocolate and couv… | candidate | different product |  | A could be an input for B (AI) | 0.47 | Activity A provides recipe tailoring, application development, and production-process support; Activity B supplies chocolate ingredients. The services help man… |  |
| T-2 Yeast-derived food fats and o… | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.46 | A’s tailored food fats are ingredients for food manufacturers, while B’s inclusions and decorations are ingredients applied to or incorporated into foods. They… |  |
| T-3 Product-development and manuf… | P2-3 Processed cocoa ingredients | candidate | different product |  | A could be an input for B (AI) | 0.46 | Activity A provides recipe tailoring, application development and production-process support, while Activity B supplies processed cocoa ingredients. The servic… |  |
| T-2 Yeast-derived food fats and o… | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.43 | Both are food ingredients supplied for use in manufactured foods, but yeast-derived fats are fat ingredients while B’s products are nut-based ingredients and p… |  |
| T-3 Product-development and manuf… | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | A could be an input for B (AI) | 0.43 | A provides recipe tailoring, application development and production-process support, while B consists of chocolate components used in food products. The servic… |  |
| T-3 Product-development and manuf… | P2-8 Cocoa-fruit ingredients | candidate | different product |  | A could be an input for B (AI) | 0.41 | Activity A provides recipe tailoring, application development and production-process support; Activity B supplies cocoa-fruit ingredients for use in foods and … |  |
| T-3 Product-development and manuf… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | A could be an input for B (AI) | 0.40 | Activity A provides development and manufacturing-support services to help customers adapt and use ingredients; Activity B supplies sunflower-seed-based chocol… |  |
| T-2 Yeast-derived food fats and o… | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.40 | A’s food fats are ingredients for food manufacturers, while B’s cocoa and chocolate drink preparations are beverage products. A’s cocoa-butter-like fat could p… |  |

<details><summary>7 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P2-7 Professional beverage mixes and in… (sim. 0.43): A is a bulk cocoa-free chocolate alternative ingredient for use in confectionery, bakery, cereal an…
- T-1 Cocoa-free chocolate alternative i… ↔ P2-10 Professional chocolate education a… (sim. 0.42): A is a bulk food ingredient used to make confectionery, bakery, cereal and ice-cream products. B is…
- T-2 Yeast-derived food fats and oils ↔ P2-8 Cocoa-fruit ingredients (sim. 0.48): A consists of yeast-derived fats intended to function as fat ingredients, including alternatives to…
- T-2 Yeast-derived food fats and oils ↔ P2-10 Professional chocolate education a… (sim. 0.33): A supplies food fats and oils intended as ingredients for food products. B provides education and t…
- T-3 Product-development and manufactur… ↔ P2-2 Professional and artisan chocolate… (sim. 0.48): A is a service that helps manufacturers adapt ingredients and use them in production, while B consi…
- T-3 Product-development and manufactur… ↔ P2-5 Nut and almond ingredients (sim. 0.40): Activity A provides recipe and production-support services, while Activity B supplies physical nut-…
- T-3 Product-development and manufactur… ↔ P2-10 Professional chocolate education a… (sim. 0.40): A provides tailored recipe and production-process support to help manufacturers incorporate ingredi…

</details>

### Bahlsen

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-3 Product-development and manuf… | P3-6 Private-label product develop… | candidate | similar product, possibly substitutable | ●○○ |  | 0.62 | Both provide tailored product-development support to business customers, but A focuses on adapting ingredients and supporting incorporation into production pro… |  |
| T-2 Yeast-derived food fats and o… | P3-6 Private-label product develop… | candidate | different product |  | A could be an input for B (AI) | 0.46 | A supplies yeast-derived food fats and oils as ingredients for food products. B provides product-development and customization services to retailers; customers… |  |
| T-1 Cocoa-free chocolate alternat… | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.45 | A is a bulk ingredient used by food manufacturers in products such as coatings, fillings and biscuits; B consists of finished snacks and confectionery eaten by… |  |
| T-3 Product-development and manuf… | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.45 | Activity A provides recipe tailoring, application development and production-process support to food manufacturers; Activity B retails finished foods for consu… |  |
| T-1 Cocoa-free chocolate alternat… | P3-6 Private-label product develop… | candidate | different product |  | A could be an input for B (AI) | 0.43 | A is a bulk cocoa-free chocolate ingredient used in food products, while B is a service for developing and customizing products for retailers’ private labels. … |  |
| T-2 Yeast-derived food fats and o… | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI); A could be resold by B (AI) | 0.42 | A develops intermediate food fats intended as ingredients for food manufacturers, while B retails finished biscuits, baked goods, snacks and other foods for co… |  |
| T-1 Cocoa-free chocolate alternat… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.41 | The cocoa-free ingredient is used by manufacturers to make sweet baked goods and confectionery, while packaged cakes are ready-to-eat sweet baked goods. They a… |  |
| T-1 Cocoa-free chocolate alternat… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI and rule) | 0.41 | A is a bulk ingredient used by manufacturers to make a range of foods, while B consists of finished packaged baked goods eaten by consumers. The ingredient may… |  |
| T-1 Cocoa-free chocolate alternat… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.41 | A is a bulk ingredient used to make confectionery and other foods, while B resells finished biscuits, snacks and other foods. Finished chocolate or confectione… |  |
| T-1 Cocoa-free chocolate alternat… | P3-2 Biscuit-based snack bars | candidate | different product |  | A could be an input for B (AI) | 0.39 | Activity A is a bulk ingredient for manufacturers to use in producing foods, while Activity B is a packaged bar eaten by consumers as a portable snack. The ing… |  |
| T-1 Cocoa-free chocolate alternat… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.38 | A is a bulk ingredient for manufacturing confectionery and other foods, while B is a ready-to-eat snack bar. They are different products, but A can be used to … |  |
| T-2 Yeast-derived food fats and o… | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.38 | A supplies yeast-derived food fats as ingredients for food manufacturers, while B consists of finished biscuits, pastries, wafers, cakes and peppermint tablets… |  |
| T-2 Yeast-derived food fats and o… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.38 | The yeast-derived fats are ingredients for food manufacturers, while the packaged cakes are ready-to-eat desserts, so they are different products. The fats are… |  |
| T-2 Yeast-derived food fats and o… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A supplies yeast-derived fats as intermediate ingredients for food manufacturers, while B consists of finished packaged baked goods eaten as snacks or treats. … |  |
| T-1 Cocoa-free chocolate alternat… | P3-4 Seasonal biscuits and baked g… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A is a bulk ingredient used by food manufacturers to make confectionery, bakery, cereal and ice-cream products. B is finished seasonal biscuits and baked goods… |  |
| T-2 Yeast-derived food fats and o… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.36 | A is a food-fat ingredient intended for use in manufactured foods, while B is a finished snack bar. They are not the same product, but A’s cocoa-butter-like or… |  |
| T-2 Yeast-derived food fats and o… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.34 | Activity A's fats are ingredients for food manufacturers, while Activity B consists of finished seasonal baked goods consumed as snacks or desserts. A's cocoa-… |  |
| T-2 Yeast-derived food fats and o… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.33 | The fats are food ingredients intended for manufacturers, while the bars are finished portable snacks for consumers, so they are not the same product. The fats… |  |
| T-3 Product-development and manuf… | P3-7 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.32 | Activity A is product-development and manufacturing-support services for food businesses, while Activity B is finished snack bars for consumers to eat. The ser… |  |

<details><summary>8 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.28): A is a bulk food ingredient used by manufacturers to make confectionery, bakery, cereal, and ice-cr…
- T-2 Yeast-derived food fats and oils ↔ P3-9 Hoodies and fabric tote bags (sim. 0.31): Yeast-derived fats are food ingredients intended for use in manufacturing food products. Hoodies an…
- T-3 Product-development and manufactur… ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.37): Activity A provides recipe-development and production-process support to food businesses; Activity …
- T-3 Product-development and manufactur… ↔ P3-2 Biscuit-based snack bars (sim. 0.33): Activity A is a service helping food manufacturers adapt ingredients and incorporate them into prod…
- T-3 Product-development and manufactur… ↔ P3-3 Packaged cakes (sim. 0.32): Activity A provides recipe tailoring and production-process support to food manufacturers, while Ac…
- T-3 Product-development and manufactur… ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.35): A provides recipe-tailoring and production-support services to food manufacturers and brands; B con…
- T-3 Product-development and manufactur… ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.41): Activity A provides recipe tailoring, application development and production-process support to bus…
- T-3 Product-development and manufactur… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.33): Activity A provides recipe, application, and production-process support to food manufacturers; Acti…

</details>

### FRoSTA

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | Flags |
|---|---|---|---|---|---|---|---|---|
| T-3 Product-development and manuf… | P4-9 Product development and assor… | candidate | similar product, possibly substitutable | ●●○ |  | 0.67 | Both are business-to-business product-development and advisory services for food businesses, and both include recipe or product-concept work. A focuses on adap… |  |
| T-3 Product-development and manuf… | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.51 | A provides recipe-tailoring and production-support services, while B supplies finished frozen foods for resale. The services help customers develop and make fo… |  |
| T-2 Yeast-derived food fats and o… | P4-5 Frozen food supplied to indus… | candidate | similar product, possibly substitutable | ●●● |  | 0.49 | A supplies fats intended as food ingredients, while B supplies frozen food products for use in customers’ food production or processing. The descriptions do no… |  |
| T-3 Product-development and manuf… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.45 | A provides recipe tailoring, application development and production-process support, while B supplies frozen foods for household consumption. The services help… |  |
| T-2 Yeast-derived food fats and o… | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.44 | A supplies yeast-derived fats intended as ingredients for food manufacturers, while B supplies finished frozen foods for resale. Their functions and forms diff… |  |
| T-3 Product-development and manuf… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.44 | A provides recipe tailoring, application development and production-process support, while B consists of frozen foods prepared and served in professional kitch… |  |
| T-2 Yeast-derived food fats and o… | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.42 | A’s pipeline fats are food ingredients intended for manufacturers, while B’s frozen foods are finished products for professional kitchens. A’s fats could plaus… |  |
| T-2 Yeast-derived food fats and o… | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.42 | A supplies food fats and oils as ingredients for food manufacturers, while B supplies finished frozen foods for household consumption. The products are not the… |  |
| T-2 Yeast-derived food fats and o… | P4-3 Branded frozen foods | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.37 | A’s fats are food ingredients intended for use by food manufacturers, while B’s frozen foods are finished products offered to shoppers. The descriptions identi… |  |
| T-2 Yeast-derived food fats and o… | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.34 | Activity A’s fats are ingredients for food products, while Activity B sells prepared frozen meals and other foods for consumers to eat at home. The description… |  |
| T-2 Yeast-derived food fats and o… | P4-1 Branded frozen meals, fish, v… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.33 | The yeast-derived fats are ingredients for food manufacturers, while Activity B consists of finished frozen foods for households. The fats could plausibly repl… |  |
| T-1 Cocoa-free chocolate alternat… | P4-2 Customer-brand frozen foods | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.29 | A is a cocoa-free chocolate alternative ingredient used in confectionery, bakery and other foods, while B is a range of finished frozen foods. They are not the… |  |
| T-1 Cocoa-free chocolate alternat… | P4-6 Frozen foods supplied to home… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); ✗ A could be resold by B (AI, disregarded: B is not active in wholesale or retail (level: finished products)) | 0.28 | A is a bulk chocolate-alternative ingredient used in foods such as confectionery, bakery products, cereals and ice cream; B includes finished frozen meals and … |  |
| T-1 Cocoa-free chocolate alternat… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.27 | A is a bulk cocoa-free chocolate ingredient used by manufacturers to make foods such as confectionery and bakery products. B consists of finished frozen foods … |  |
| T-1 Cocoa-free chocolate alternat… | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.25 | A is a bulk cocoa-free chocolate ingredient for manufacturers to use in foods, while B is a range of finished frozen foods offered to shoppers. The description… |  |
| T-1 Cocoa-free chocolate alternat… | P4-7 Frozen meals, fish, vegetable… | candidate | different product |  | A could be an input for B (AI); ✗ B could be resold by A (AI, disregarded: A is not active in wholesale or retail (level: intermediate products)) | 0.25 | A is a bulk cocoa-free chocolate ingredient used by food manufacturers in products such as confectionery, bakery goods and ice cream. B is a range of finished … |  |
| T-3 Product-development and manuf… | P4-5 Frozen food supplied to indus… | unclear | different product |  |  | 0.55 | A provides recipe, application, and production-process support services, while B supplies frozen food products for use in customers’ food production. The servi… |  |
| T-1 Cocoa-free chocolate alternat… | P4-5 Frozen food supplied to indus… | unclear | not enough information |  |  | 0.34 | A is a specified cocoa-free chocolate alternative ingredient, while B is described only as frozen food supplied to industrial customers. The descriptions do no… |  |

<details><summary>12 pairs screened out</summary>

- T-1 Cocoa-free chocolate alternative i… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.24): A is a bulk cocoa-free chocolate ingredient used by food manufacturers to make other foods. B consi…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.22): A is a bulk ingredient used by food manufacturers to make confectionery, bakery, cereal, and ice-cr…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-9 Product development and assortment… (sim. 0.29): A is a bulk cocoa-free chocolate-alternative ingredient used in food products, while B is a consult…
- T-1 Cocoa-free chocolate alternative i… ↔ P4-10 Non-food merchandise (sim. 0.28): A is a bulk food ingredient used by manufacturers in confectionery, bakery, cereal and ice-cream pr…
- T-2 Yeast-derived food fats and oils ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.30): Activity A is developing food fats and oils for use as ingredients by food manufacturers. Activity …
- T-2 Yeast-derived food fats and oils ↔ P4-9 Product development and assortment… (sim. 0.44): A supplies yeast-derived fats as food ingredients, while B supplies advice and product-development …
- T-2 Yeast-derived food fats and oils ↔ P4-10 Non-food merchandise (sim. 0.34): A supplies food fats and oils intended as ingredients for food products, while B sells apparel, acc…
- T-3 Product-development and manufactur… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.37): A provides recipe-tailoring and production-process support to food manufacturers, while B consists …
- T-3 Product-development and manufactur… ↔ P4-3 Branded frozen foods (sim. 0.44): Activity A provides recipe adaptation, application development, and production-process support for …
- T-3 Product-development and manufactur… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.34): Activity A provides recipe and production-process support services to food manufacturers, while Act…
- T-3 Product-development and manufactur… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.33): Activity A provides recipe and production-process support to help manufacturers incorporate ingredi…
- T-3 Product-development and manufactur… ↔ P4-10 Non-food merchandise (sim. 0.40): Activity A provides recipe and production-process support for food manufacturers, while Activity B …

</details>

## Calibration: closest pairs that were screened out

If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.

- 0.48 · T-3 Product-development and manufacturing-s… ↔ P2-2 Professional and artisan chocolate and … (Barry Callebaut)
- 0.48 · T-2 Yeast-derived food fats and oils ↔ P2-8 Cocoa-fruit ingredients (Barry Callebaut)
- 0.44 · T-3 Product-development and manufacturing-s… ↔ P4-3 Branded frozen foods (FRoSTA)
- 0.44 · T-2 Yeast-derived food fats and oils ↔ P4-9 Product development and assortment cons… (FRoSTA)
- 0.43 · T-1 Cocoa-free chocolate alternative ingred… ↔ P2-7 Professional beverage mixes and ingredi… (Barry Callebaut)
- 0.42 · T-1 Cocoa-free chocolate alternative ingred… ↔ P2-10 Professional chocolate education and tr… (Barry Callebaut)
- 0.42 · T-2 Yeast-derived food fats and oils ↔ P1-9 Cocoa and hazelnuts grown for the group… (Ritter Sport)
- 0.41 · T-3 Product-development and manufacturing-s… ↔ P3-5 Private-label biscuits, coffee pastries… (Bahlsen)
- similarity of candidate pairs: min 0.25 · median 0.42 · max 0.74
- similarity of screened out pairs: min 0.22 · median 0.35 · max 0.48

## Example: exactly what the comparison call received

```
ACTIVITY A
Product: Cocoa-free chocolate alternative ingredient
Description: Commercially produced ingredient supplied in bulk as chips or liquid, in milk, vegan, dark, and white formulations. A no-added-sugar formulation using maltitol was also announced. Applications include coatings, fillings, inclusions, bars, pralines, biscuits, cereals, wafers, hollow figures, and ice cream. A published minimum order for four recipes is 12 tonnes.
Intended use: Food manufacturers use the ingredient in confectionery, bakery, cereal, and ice-cream products.
Main inputs: not stated
Level of trade: intermediate products
Direct customers: manufacturers / processors (Food manufacturers, including confectionery and bakery manufacturers; named supplied companies include Griesson–de Beukelaer and Peter Kölln, and an artisan confectioner is also acknowledged. Other retailer and partner arrangements do not establish that those parties buy directly from the company.)
End users: consumers
Sales channels: Direct B2B sales and enquiries; supplied in bulk. Finished products are sold downstream by partner manufacturers and retailers, not established as direct sales by the company.
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

- names removed before any comparison: 56 name variants (list in the .json file)
- comparison calls blocked or failed: 0 (kept as 'unclear', never screened out)
- search: 5 calls (5 from cache) · tokens 0 in / 0 out · USD 0.0000
- extract: 5 calls (4 from cache) · tokens 4,180 in / 1,098 out · USD 0.0010
- embed: 5 calls (4 from cache) · tokens 247 in / 0 out · USD 0.0000
- compare: 114 calls (0 from cache) · tokens 147,127 in / 19,466 out · USD 0.0244
- total: USD 0.0254 (token costs only, without web search fees)
