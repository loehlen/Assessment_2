# Factual comparison TC1: Lindt & Sprüngli (20261015-0359)

Models: search saved gpt-6.1-sol · extraction gpt-6-luna · comparison gpt-6-luna · text-embedding-3-large  
Thresholds: unclear ≥ 0.5 · input match ≥ 0.5 · resale ≥ 0.4

## Benchmark check (spec section 13)

11 ✔ as expected · 0 ◐ kept in another form · **0 ✖ missed by the comparison** · 0 ∅ activity not found · 1 ⚠ false positives in a control row

Checkpoint Wed 21 Oct: no ✖. A ∅ is a search or extraction gap (or the keywords in benchmark.py need adjusting: compare with the activity overview below).

| Check | Portco | Pair | Expected | Result | Pairs | Detail |
|---|---|---|---|---|---|---|
| TC1-1 | Ritter Sport | consumer chocolate ↔ consumer chocolate | horizontal | ✔ | T-1↔P1-1, T-1↔P1-3, T-1↔P1-4, T-5↔P1-1 (+7) | 11 of 12 matching pairs as expected |
| TC1-2 | Ritter Sport | own shops ↔ own shops (both in Berlin) | horizontal | ✔ | T-2↔P1-2 | 1 of 2 matching pairs as expected |
| TC1-3 | Ritter Sport | Lindt chocolate → Ritter shops (false positive by design) | vertical | ✔ | T-1↔P1-2, T-1↔P1-8, T-5↔P1-2, T-6↔P1-2 (+2) | 6 of 8 matching pairs as expected |
| TC1-4 | Ritter Sport | Amicelli wafer rolls ↔ Lindt chocolate | kept | ✔ | T-1↔P1-3, T-5↔P1-3, T-6↔P1-3, T-9↔P1-3 | 4 of 4 matching pairs as expected |
| TC1-5 | Barry Callebaut | semi-finished / industrial chocolate → Lindt | vertical | ✔ | T-1↔P2-1, T-1↔P2-2, T-1↔P2-3, T-1↔P2-8 (+12) | 16 of 16 matching pairs as expected |
| TC1-6 | Barry Callebaut | industrial chocolate ↔ Lindt consumer chocolate (●○○) | horizontal | ✔ | T-1↔P2-4, T-1↔P2-6, T-5↔P2-1, T-5↔P2-4 (+4) | 8 of 12 matching pairs as expected |
| TC1-7 | Barry Callebaut | beverages ↔ Lindt hot chocolate (◐) | kept | ✔ | T-6↔P2-3, T-6↔P2-5, T-6↔P2-7, T-6↔P2-8 (+4) | 8 of 8 matching pairs as expected |
| TC1-8 | Bahlsen | chocolate ↔ biscuits (must never be screened out) | kept | ✔ | T-1↔P3-1, T-1↔P3-2, T-1↔P3-3, T-1↔P3-4 (+12) | 16 of 20 matching pairs as expected |
| TC1-9 | Bahlsen | Bahlsen outlets ↔ Lindt shops | horizontal | ✔ | T-2↔P3-8 | 1 of 1 matching pairs as expected |
| TC1-10 | Bahlsen | Lindt chocolate → Bahlsen outlets (distribution, M.5644 (47)) | vertical | ✔ | T-1↔P3-8, T-5↔P3-8, T-6↔P3-8, T-9↔P3-8 | 4 of 4 matching pairs as expected |
| TC1-11 | Bahlsen | Caffarel candies ↔ Bisquiva peppermint tablets (◐) | kept | ✔ | T-3↔P3-5 | 1 of 1 matching pairs as expected |
| TC1-12 | FRoSTA | control: nothing in common | screened out | ⚠ | T-1↔P4-1, T-1↔P4-4, T-1↔P4-5, T-1↔P4-10 (+37) | 41 of 120 pairs kept: check whether these are false positives |

## Activity overview (stages ①–②)

### Target: Lindt & Sprüngli (12 activities, 15 sources)

| # | Business area | Product | Level | Direct customers | Countries | Status | Src |
|---|---|---|---|---|---|---|---|
| T-1 | not stated | Finished chocolate and chocolate confectione… | finished products | retailers, wholesalers / distributors, consumers | Austria, Belgium, Bulgaria, C… | on the market | [1, 2, 12, 13] |
| T-2 | not stated | Retail sale of chocolate and confectionery | retail | consumers | Australia, Italy, United Stat… | on the market | [4, 5, 9, 12] |
| T-3 | not stated | Non-chocolate sugar confectionery | finished products | consumers, wholesalers / distributors, retailers | Italy, United States | on the market | [3, 4] |
| T-4 | not stated | Candied chestnuts | finished products | retailers, wholesalers / distributors, not stated | Italy | on the market | [5] |
| T-5 | not stated | Chocolate and cocoa ingredients and professi… | finished products | wholesalers / distributors, other businesses | United States | on the market | [6, 8] |
| T-6 | not stated | Dessert and beverage sauces and beverage mix… | finished products | wholesalers / distributors, other businesses, consumers | United States | on the market | [6, 7] |
| T-7 | not stated | Café, beverage and dessert service | services | consumers | Australia, Italy, United Stat… | on the market | [9] |
| T-8 | not stated | Catering and café food service for private e… | services | other businesses, consumers | Switzerland | on the market | [10] |
| T-9 | not stated | Liqueur | finished products | retailers, not stated | Italy | on the market | [5] |
| T-10 | not stated | Foodservice accessories | finished products | wholesalers / distributors, other businesses | not stated | on the market | [7] |
| T-11 | not stated | Licensing of product brands | services | other businesses | United States | on the market | [1] |
| T-12 | not stated | Property-related income and contracted admin… | services | other businesses | Switzerland | on the market | [1] |

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
🔗 The public sources for Bahlsen mention: Lindt & Sprüngli (check for an existing relationship)

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

456 pairs: 264 candidates · 4 unclear · 188 screened out

### Ritter Sport

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | EEA |
|---|---|---|---|---|---|---|---|---|
| T-1 Finished chocolate and chocol… | P1-1 Packaged chocolate bars and o… | candidate | same product | ●●○ |  | 0.83 | Both activities concern finished chocolate and chocolate confectionery for consumption or gifting, with overlapping for… |  |
| T-1 Finished chocolate and chocol… | P1-2 Chocolate confectionery sold … | candidate | same product | ●●○ | A could be resold by B (AI and rule) | 0.82 | Both activities concern finished chocolate confectionery for consumers to eat or give as gifts. Activity A includes a b… |  |
| T-2 Retail sale of chocolate and … | P1-2 Chocolate confectionery sold … | candidate | same product | ●●● |  | 0.77 | Both activities are retail sales of finished chocolate and confectionery to consumers through own shops and e-commerce,… |  |
| T-1 Finished chocolate and chocol… | P1-4 Corporate gifts and promotion… | candidate | same product | ●○○ | A could be an input for B (AI) | 0.69 | Both activities supply finished chocolate for consumers to eat or give as gifts. B’s bulk or customised packaging and b… |  |
| T-2 Retail sale of chocolate and … | P1-1 Packaged chocolate bars and o… | candidate | same product | ●○○ | B could be resold by A (AI and rule) | 0.67 | Both activities concern finished chocolate and confectionery for consumers to eat or give as gifts. The difference is t… |  |
| T-3 Non-chocolate sugar confectio… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ |  | 0.65 | Both are finished confectionery products eaten by consumers and bought as gifts, so they share a broad purpose. Sugar c… |  |
| T-5 Chocolate and cocoa ingredien… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.64 | A comprises professional chocolate and cocoa ingredients or coatings used to prepare and coat foods, while B comprises … | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); A could be resold by B (rule) | 0.62 | Both activities involve chocolate products that can be consumed as food, but A consists of professional ingredients and… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? |  | 0.62 | Both are finished chocolate confectionery for consumers to eat or give as gifts. Chocolate-covered wafer rolls are a di… |  |
| T-8 Catering and café food servic… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●● |  | 0.61 | Both activities provide prepared food and refreshments for consumption and include service connected with events. Their… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.60 | Both activities supply chocolate or confectionery intended ultimately to be eaten or given as a gift. Activity B adds c… |  |
| T-5 Chocolate and cocoa ingredien… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.59 | Both activities supply chocolate-based products that can be consumed as chocolate. Activity A’s professional chips, waf… | no EEA overlap |
| T-9 Liqueur | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ |  | 0.59 | Liqueur is an alcoholic drink, while chocolate products are confectionery, so their characteristics and ordinary consum… |  |
| T-7 Café, beverage and dessert se… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.59 | Both activities offer prepared drinks and desserts for consumption at an outlet or takeaway, including ice cream and ho… |  |
| T-1 Finished chocolate and chocol… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI and rule) | 0.58 | A consists of finished chocolate and confectionery for consumers to eat or give as gifts. B consists of raw cocoa and h… |  |
| T-9 Liqueur | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be resold by B (rule) | 0.57 | Liqueur is an alcoholic drink for consumption, while chocolate confectionery is eaten. Both may be given as gifts, but … |  |
| T-3 Non-chocolate sugar confectio… | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (rule) | 0.57 | Both are finished confectionery products for personal consumption or gifting, and consumers may choose between them for… |  |
| T-9 Liqueur | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? |  | 0.56 | Both are packaged, branded foods intended for consumer enjoyment and gifting, but one is an alcoholic drink and the oth… |  |
| T-5 Chocolate and cocoa ingredien… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI and rule) | 0.55 | Activity A consists of finished professional ingredients and coatings for preparing or coating foods, while Activity B … | no EEA overlap |
| T-2 Retail sale of chocolate and … | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.55 | A sells chocolate and confectionery for consumers to eat or give as gifts. B provides participatory workshops and educa… |  |
| T-9 Liqueur | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ |  | 0.55 | Both are confectionery products that can be bought as gifts, and chocolate products could plausibly be chosen instead o… |  |
| T-2 Retail sale of chocolate and … | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.54 | A is a retail activity selling finished chocolate and confectionery for eating or gifting. B is cultivation and post-ha… |  |
| T-7 Café, beverage and dessert se… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI); B could be resold by A (AI) | 0.54 | Activity A provides prepared drinks and desserts for immediate consumption or takeaway, while Activity B consists of pa… |  |
| T-5 Chocolate and cocoa ingredien… | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.54 | A supplies professional chocolate, cocoa and confectionery coating ingredients for preparing or coating foods. B provid… | no EEA overlap |
| T-4 Candied chestnuts | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●● |  | 0.54 | Both are finished confectionery intended for consumers to eat or give as gifts, and may overlap in gift-oriented or sea… |  |
| T-7 Café, beverage and dessert se… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.53 | Both activities offer beverages for consumers, and the cocoa-fruit lemonade or iced tea could serve as a refreshment in… |  |
| T-7 Café, beverage and dessert se… | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●●● | B could be resold by A (AI) | 0.53 | Both offer chocolate-based products for consumers to eat, although A primarily provides prepared drinks, desserts and c… |  |
| T-5 Chocolate and cocoa ingredien… | P1-3 Chocolate-covered wafer rolls… | candidate | different product |  | A could be an input for B (AI) | 0.53 | A consists of professional-format ingredients and coatings used to prepare or coat foods, whereas B is a packaged, read… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.52 | Activity A consists of chocolate foods intended for eating or gifting, while Activity B provides participatory workshop… |  |
| T-12 Property-related income and c… | P1-6 Chocolate-making workshops an… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.52 | Most of A—property arrangements and administrative services—is unlike B’s workshops and educational visitor experiences… | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ |  | 0.52 | Both are confectionery eaten by consumers and can be given as gifts. A is non-chocolate sugar confectionery, while B is… |  |
| T-9 Liqueur | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●○○ |  | 0.52 | The cocoa-fruit products are mainly non-alcoholic refreshments, unlike liqueur, but the documented alcoholic sparkling … |  |
| T-5 Chocolate and cocoa ingredien… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.51 | A comprises professional chocolate, cocoa powders and confectionery coatings used to prepare or coat foods and drinks; … | no EEA overlap |
| T-9 Liqueur | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.50 | Liqueur is a finished alcoholic drink for consumers, while cocoa and hazelnuts are agricultural raw materials intended … |  |
| T-6 Dessert and beverage sauces a… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●●○ |  | 0.50 | Both are finished, sweet food products that consumers may choose for indulgence or gifting, but sauces and beverage mix… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be resold by B (rule) | 0.50 | A consists of sauces and mixes used to prepare or top drinks and desserts, while B consists of finished chocolate confe… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P1-3 Chocolate-covered wafer rolls… | candidate | same product | ? | B could be resold by A (AI) | 0.49 | Both activities concern chocolate and confectionery intended for consumers to eat or give as gifts. B describes a parti… |  |
| T-6 Dessert and beverage sauces a… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.49 | Both include finished beverage products that consumers may drink for refreshment, so the beverage mixes and cocoa-fruit… | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? |  | 0.49 | Both are finished confectionery products eaten by consumers and may be bought for gifting. Sugar candies and chocolate-… |  |
| T-7 Café, beverage and dessert se… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.49 | Activity A provides prepared café beverages and desserts for immediate consumption, while Activity B produces raw cocoa… |  |
| T-12 Property-related income and c… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.48 | A provides property, administrative support and chocolate-making demonstrations, while B cultivates cocoa and hazelnuts… | no EEA overlap |
| T-4 Candied chestnuts | P1-2 Chocolate confectionery sold … | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (AI and rule) | 0.48 | Both are finished confectionery intended for personal consumption or gifting. Candied chestnuts and chocolate confectio… |  |
| T-6 Dessert and beverage sauces a… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.47 | A consists of finished sauces and beverage mixes used to prepare or top drinks and foods. B consists of raw agricultura… | no EEA overlap |
| T-12 Property-related income and c… | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be an input for B (AI) | 0.46 | Activity A comprises property income, administrative support, and contracted chocolate-making demonstrations; Activity … | no EEA overlap |
| T-1 Finished chocolate and chocol… | P1-8 Non-food branded merchandise … | candidate | different product |  | A could be resold by B (rule) | 0.46 | Finished chocolate is edible confectionery for consumption or gifting, whereas the merchandise consists of non-food ite… |  |
| T-4 Candied chestnuts | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? |  | 0.45 | Both are finished confectionery products for consumers to eat or give as gifts. Candied chestnuts and chocolate-covered… |  |
| T-1 Finished chocolate and chocol… | P1-5 Cocoa-fruit beverages | candidate | similar product, possibly substitutable | ●●○ |  | 0.45 | A comprises chocolate foods eaten as snacks or given as gifts, while B comprises cocoa-fruit juice-based refreshments a… |  |
| T-4 Candied chestnuts | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ |  | 0.45 | Both are finished confectionery products that consumers may eat or receive as gifts, though one is candied chestnuts an… |  |
| T-7 Café, beverage and dessert se… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.45 | Both activities involve chocolate products for consumers, but A provides prepared café drinks and desserts for immediat… |  |
| T-6 Dessert and beverage sauces a… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●●○ |  | 0.44 | Both activities supply finished food products containing or based on chocolate or other flavours, which consumers may u… | no EEA overlap |
| T-9 Liqueur | P1-8 Non-food branded merchandise … | candidate | different product |  | A could be resold by B (rule) | 0.43 | Liqueur is an alcoholic drink for consumption, while the merchandise consists of non-food items such as bags, keyrings … |  |
| T-12 Property-related income and c… | P1-4 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.42 | A consists of property income and administrative and demonstration services, while B supplies chocolate products for us… | no EEA overlap |
| T-9 Liqueur | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.42 | Bottled liqueur is an alcoholic drink bought for consumption or gifting, whereas B provides hands-on chocolate-making a… |  |
| T-6 Dessert and beverage sauces a… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? |  | 0.42 | Both are finished food products consumed by end users, and chocolate-based drink or dessert preparations could overlap … | no EEA overlap |
| T-7 Café, beverage and dessert se… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? | B could be an input for A (AI) | 0.42 | Both are consumer foods for sweet eating or drinking, and a packaged wafer roll could partly serve as an alternative to… |  |
| T-2 Retail sale of chocolate and … | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.41 | Chocolate and confectionery sold for eating or as gifts differ from prepared meals, desserts and drinks consumed at a b… |  |
| T-3 Non-chocolate sugar confectio… | P1-8 Non-food branded merchandise … | candidate | different product |  | A could be resold by B (AI and rule) | 0.41 | Non-chocolate sugar confectionery is edible and intended for consumption, while the merchandise consists of non-food it… |  |
| T-6 Dessert and beverage sauces a… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.41 | The sauces and beverage mixes are preparation or topping products, while the bistro sells prepared items such as cake, … | no EEA overlap |
| T-1 Finished chocolate and chocol… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.40 | Finished chocolate confectionery and the bistro’s cake, ice cream, and hot chocolate are different products and are not… |  |
| T-11 Licensing of product brands | P1-2 Chocolate confectionery sold … | candidate | different product |  | A could be an input for B (AI) | 0.39 | Activity A is a licensing service that enables businesses to produce or market branded products; Activity B is finished… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.36 | A consists of finished sauces and beverage mixes used to prepare or top food and drinks. B consists of participatory wo… | no EEA overlap |
| T-10 Foodservice accessories | P1-7 Prepared food and beverages f… | candidate | different product |  | A could be resold by B (AI) | 0.36 | Foodservice accessories are equipment for dispensing and organising sauces, whereas the bistro supplies prepared food a… |  |
| T-11 Licensing of product brands | P1-1 Packaged chocolate bars and o… | candidate | different product |  | A could be an input for B (AI) | 0.36 | A is a licensing service that grants businesses rights to use product brands; B consists of finished chocolate confecti… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.35 | Professional chocolate, cocoa and confectionery-coating products are ingredients or toppings used to prepare foods and … | no EEA overlap |
| T-8 Catering and café food servic… | P1-4 Corporate gifts and promotion… | candidate | similar product, possibly substitutable | ●●○ |  | 0.34 | Both provide food products for events or business occasions, but catering and café service supplies prepared meals and … | no EEA overlap |
| T-8 Catering and café food servic… | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.33 | Catering and café services provide prepared food and refreshments for consumption, while the workshops and exhibitions … | no EEA overlap |
| T-11 Licensing of product brands | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.33 | Product-brand licensing provides businesses rights to use brands on products, while workshops and visitor experiences p… | no EEA overlap |
| T-4 Candied chestnuts | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.32 | Candied chestnuts are finished confectionery eaten or given as gifts. Chocolate-making workshops and educational visito… |  |
| T-11 Licensing of product brands | P1-4 Corporate gifts and promotion… | candidate | different product |  | A could be an input for B (AI) | 0.31 | A sells brand-use rights and related licensing services to businesses, while B supplies finished chocolate products for… | no EEA overlap |
| T-11 Licensing of product brands | P1-3 Chocolate-covered wafer rolls… | candidate | different product |  | A could be an input for B (AI) | 0.31 | A is a brand-licensing service for businesses, while B is packaged chocolate-covered wafer confectionery for consumptio… | no EEA overlap |
| T-8 Catering and café food servic… | P1-5 Cocoa-fruit beverages | candidate | different product |  | B could be resold by A (AI) | 0.28 | A provides prepared food and a catering/café service, while B consists of finished beverages. Although B’s drinks could… | no EEA overlap |
| T-8 Catering and café food servic… | P1-1 Packaged chocolate bars and o… | candidate | similar product, possibly substitutable | ●○○ |  | 0.27 | Both provide food for consumption, but A is prepared catering and café food for event attendees, while B is packaged ch… | no EEA overlap |
| T-8 Catering and café food servic… | P1-9 Cocoa and hazelnuts grown for… | candidate | different product |  | B could be an input for A (AI) | 0.26 | A provides prepared food and refreshments for event attendees, while B produces raw cocoa and hazelnuts for use as ingr… | no EEA overlap |
| T-4 Candied chestnuts | P1-7 Prepared food and beverages f… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.25 | Candied chestnuts and the cake or ice cream offered by the bistro are different products, but could both serve as sweet… |  |
| T-8 Catering and café food servic… | P1-3 Chocolate-covered wafer rolls… | candidate | similar product, possibly substitutable | ? | B could be resold by A (AI) | 0.23 | Both are food products for consumption, but prepared event and café food is generally meal or refreshment service, whil… | no EEA overlap |
| T-10 Foodservice accessories | P1-6 Chocolate-making workshops an… | candidate | different product |  | A could be an input for B (AI) | 0.22 | Foodservice accessories dispense and organise sauces in professional settings, whereas the other activity provides choc… |  |

<details><summary>32 pairs screened out</summary>

- T-2 Retail sale of chocolate and confe… ↔ P1-5 Cocoa-fruit beverages (sim. 0.38): Chocolate and confectionery are eaten or given as gifts, while cocoa-fruit beverages are consumed a…
- T-2 Retail sale of chocolate and confe… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.48): Chocolate and confectionery are edible products for consumption or gifting. Bags, keyrings and lany…
- T-3 Non-chocolate sugar confectionery ↔ P1-5 Cocoa-fruit beverages (sim. 0.43): A consists of sweets eaten as confectionery, while B consists of drinks consumed as refreshments or…
- T-3 Non-chocolate sugar confectionery ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.42): Activity A consists of edible sugar confectionery bought to eat or give as gifts. Activity B consis…
- T-3 Non-chocolate sugar confectionery ↔ P1-7 Prepared food and beverages for on… (sim. 0.31): Activity A consists of packaged non-chocolate sugar confectionery for consumers to eat or give as g…
- T-3 Non-chocolate sugar confectionery ↔ P1-9 Cocoa and hazelnuts grown for the … (sim. 0.40): A consists of finished sweets for consumers to eat or give as gifts. B consists of agricultural raw…
- T-4 Candied chestnuts ↔ P1-5 Cocoa-fruit beverages (sim. 0.40): Candied chestnuts are confectionery eaten as a sweet or given as a gift, while cocoa-fruit products…
- T-4 Candied chestnuts ↔ P1-8 Non-food branded merchandise and g… (sim. 0.36): Candied chestnuts are edible confectionery for consumption or gifting, while the described merchand…
- T-4 Candied chestnuts ↔ P1-9 Cocoa and hazelnuts grown for the … (sim. 0.40): Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Cocoa and hazel…
- T-5 Chocolate and cocoa ingredients an… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.30): Professional chocolate and cocoa ingredients and confectionery coatings are used to prepare or coat…
- T-6 Dessert and beverage sauces and be… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.38): Activity A consists of sauces and beverage mixes used to prepare or top drinks, desserts, ice cream…
- T-7 Café, beverage and dessert service ↔ P1-6 Chocolate-making workshops and edu… (sim. 0.49): A provides prepared drinks and desserts for consumption, while B provides hands-on chocolate-making…
- T-7 Café, beverage and dessert service ↔ P1-8 Non-food branded merchandise and g… (sim. 0.37): Activity A provides prepared drinks, ice cream and desserts for consumption, while Activity B sells…
- T-8 Catering and café food service for… ↔ P1-2 Chocolate confectionery sold direc… (sim. 0.28): Activity A provides prepared meals and refreshments for events and café visits, while Activity B se…
- T-8 Catering and café food service for… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.32): Activity A provides prepared food and refreshments for consumption at events or cafés. Activity B c…
- T-9 Liqueur ↔ P1-7 Prepared food and beverages for on… (sim. 0.37): B sells prepared food and drinks for immediate consumption, plus event-space hire; A is bottled liq…
- T-10 Foodservice accessories ↔ P1-1 Packaged chocolate bars and other … (sim. 0.28): Foodservice accessories are equipment for dispensing and organising sauces, whereas packaged chocol…
- T-10 Foodservice accessories ↔ P1-2 Chocolate confectionery sold direc… (sim. 0.26): Sauce-bottle pumps and racks are professional tools for dispensing and organising sauces, whereas t…
- T-10 Foodservice accessories ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.22): Foodservice accessories dispense and organise sauces in professional settings, whereas chocolate-co…
- T-10 Foodservice accessories ↔ P1-4 Corporate gifts and promotional ch… (sim. 0.32): Sauce-bottle pumps and racks dispense and organise sauces in foodservice settings. Chocolate produc…
- T-10 Foodservice accessories ↔ P1-5 Cocoa-fruit beverages (sim. 0.22): Foodservice accessories dispense and organise sauces, while cocoa-fruit beverages are drinks for re…
- T-10 Foodservice accessories ↔ P1-8 Non-food branded merchandise and g… (sim. 0.40): Foodservice accessories dispense and organise sauces in professional settings, while bags, keyrings…
- T-10 Foodservice accessories ↔ P1-9 Cocoa and hazelnuts grown for the … (sim. 0.25): Foodservice accessories dispense and organise sauces, while cocoa and hazelnuts are agricultural in…
- T-11 Licensing of product brands ↔ P1-5 Cocoa-fruit beverages (sim. 0.31): Activity A is a licensing service that grants rights to use product brands, while Activity B consis…
- T-11 Licensing of product brands ↔ P1-7 Prepared food and beverages for on… (sim. 0.32): A is a brand-licensing service for businesses, while B provides prepared food and drinks for consum…
- T-11 Licensing of product brands ↔ P1-8 Non-food branded merchandise and g… (sim. 0.45): A is a licensing service that grants businesses rights to use product brands, while B consists of p…
- T-11 Licensing of product brands ↔ P1-9 Cocoa and hazelnuts grown for the … (sim. 0.37): Activity A is a service granting brand rights for others to produce or market branded goods, while …
- T-12 Property-related income and contra… ↔ P1-1 Packaged chocolate bars and other … (sim. 0.42): Activity A consists of property-related income, administrative services and chocolate-making demons…
- T-12 Property-related income and contra… ↔ P1-3 Chocolate-covered wafer rolls with… (sim. 0.28): A comprises property income, administrative services and chocolate-making demonstrations; B is pack…
- T-12 Property-related income and contra… ↔ P1-5 Cocoa-fruit beverages (sim. 0.31): A comprises property arrangements, administrative services, and chocolate-making demonstrations, wh…
- T-12 Property-related income and contra… ↔ P1-7 Prepared food and beverages for on… (sim. 0.34): A provides property-related income, administrative support and contracted chocolate-making demonstr…
- T-12 Property-related income and contra… ↔ P1-8 Non-food branded merchandise and g… (sim. 0.28): Property rental, administrative support, and chocolate-making demonstrations serve property, organi…

</details>

### Barry Callebaut

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | EEA |
|---|---|---|---|---|---|---|---|---|
| T-5 Chocolate and cocoa ingredien… | P2-2 Professional and artisan choc… | candidate | same product | ●●● | A could be resold by B (rule) | 0.85 | Both activities supply chocolate and cocoa ingredients in professional formats for use in preparing confectionery, dess… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.77 | Both are chocolate or cocoa-based ingredients used to make or finish confectionery, desserts and other foods. Activity … | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.72 | Both activities include cocoa powder for professional food and beverage uses. Activity B also supplies cocoa liquor or … | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.69 | Both are professional chocolate or cocoa-based products used to prepare, coat, fill, decorate, or incorporate into food… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.68 | Both activities involve chocolate products with overlapping forms, including filled pieces and other confectionery comp… |  |
| T-1 Finished chocolate and chocol… | P2-1 Industrial chocolate and couv… | candidate | different product |  | B could be an input for A (AI) | 0.67 | Activity A covers finished chocolate products eaten directly or given as gifts, while Activity B covers chocolate suppl… |  |
| T-6 Dessert and beverage sauces a… | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.67 | Both activities include beverage preparations used to make drinks for consumers, with overlap in chocolate-based and ot… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.67 | The café activity provides prepared drinks for immediate consumption, while the mixes are ingredients used to prepare d… |  |
| T-5 Chocolate and cocoa ingredien… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.65 | Both are chocolate-like ingredients used to make or coat confectionery, bakery products and other foods. The sunflower-… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P2-2 Professional and artisan choc… | candidate | different product |  | B could be an input for A (AI); A could be resold by B (rule) | 0.65 | A consists of finished chocolate products for consumers to eat or give as gifts. B consists of professional-format choc… |  |
| T-5 Chocolate and cocoa ingredien… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); B could be an input for A (rule) | 0.62 | Most products differ in composition and form: A consists mainly of chocolate, cocoa and confectionery coatings, while B… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.62 | Both offer professional ingredients or coatings used to prepare or decorate desserts and confectionery. Chocolate or co… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); A could be resold by B (AI) | 0.59 | Sauces and beverage mixes differ in form and function from inclusions and decorations, but caramel sauces could partly … | no EEA overlap |
| T-2 Retail sale of chocolate and … | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.58 | Both are chocolate or confectionery products intended ultimately for consumers to eat, but Activity A offers finished p… |  |
| T-3 Non-chocolate sugar confectio… | P2-6 Bakery, confectionery and des… | candidate | different product |  | A could be an input for B (AI) | 0.58 | A consists of finished sweets for consumers to eat or give as gifts. B consists of ingredients and decorations that pro… |  |
| T-2 Retail sale of chocolate and … | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (AI); B could be resold by A (rule) | 0.56 | Both are chocolate or confectionery products intended ultimately for consumption, and some finished products sold at re… |  |
| T-3 Non-chocolate sugar confectio… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.56 | Both are chocolate or sugar confectionery products ultimately consumed as sweets, so they may overlap in some consumer … |  |
| T-5 Chocolate and cocoa ingredien… | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.56 | Most confectionery coatings and chocolate pieces serve different purposes from beverage mixes. However, cocoa and sweet… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P2-10 Professional chocolate educat… | candidate | different product |  | A could be an input for B (AI) | 0.56 | A consists of edible chocolate products for consumption or gifting. B is educational and training services that develop… |  |
| T-3 Non-chocolate sugar confectio… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.56 | Both are sweet confectionery products intended ultimately for consumption, but A is finished non-chocolate candy for co… |  |
| T-1 Finished chocolate and chocol… | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI) | 0.56 | Both activities include confectionery-related products, and some chocolate products could plausibly serve overlapping d… |  |
| T-7 Café, beverage and dessert se… | P2-2 Professional and artisan choc… | candidate | different product |  | B could be an input for A (AI) | 0.55 | Activity A provides prepared drinks and desserts for immediate consumption, while Activity B supplies ingredients for p… |  |
| T-7 Café, beverage and dessert se… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.55 | The café serves finished chocolate drinks and desserts, while industrial chocolate is an ingredient for making finished… |  |
| T-9 Liqueur | P2-1 Industrial chocolate and couv… | candidate | different product |  | B could be an input for A (AI) | 0.55 | Liqueur is a finished alcoholic drink for consumers, whereas industrial chocolate and couverture are ingredients used t… |  |
| T-5 Chocolate and cocoa ingredien… | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.54 | Both are professional food ingredients used in confectionery, pastry, bakery and related applications, and some product… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P2-1 Industrial chocolate and couv… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.54 | Both include chocolate-based products used in desserts and bakery applications, so some overlap in intended use is plau… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.54 | A comprises finished chocolate and confectionery for consumers to eat or give as gifts. B comprises processed cocoa ing… |  |
| T-4 Candied chestnuts | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.54 | Candied chestnuts are finished confectionery eaten as a treat or given as a gift, while most listed nut and almond prod… |  |
| T-9 Liqueur | P2-2 Professional and artisan choc… | candidate | different product |  | B could be an input for A (AI); A could be resold by B (rule) | 0.53 | Liqueur is a finished alcoholic drink for consumers to drink or give as a gift, while the chocolate and cocoa products … |  |
| T-6 Dessert and beverage sauces a… | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.53 | The products differ in form and composition: A consists of sauces and beverage mixes, while B consists of chocolate fil… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P2-2 Professional and artisan choc… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI); A could be resold by B (AI and rule) | 0.53 | A consists mainly of ready-to-use sauces and beverage mixes for preparing or topping drinks and desserts, while B consi… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule); B could be resold by A (rule) | 0.53 | Both are chocolate or confectionery products intended ultimately for consumption, but A consists of finished goods sold… |  |
| T-9 Liqueur | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | A could be an input for B (AI) | 0.52 | Liqueur is a bottled alcoholic drink intended for consumption or gifting, while the chocolate products are components u… |  |
| T-1 Finished chocolate and chocol… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (AI) | 0.52 | A consists of finished products for consumers to eat or give as gifts, while B is an ingredient that food manufacturers… |  |
| T-3 Non-chocolate sugar confectio… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.51 | Both are sweet food products associated with confectionery, but A is finished sugar candy while B is an ingredient used… |  |
| T-7 Café, beverage and dessert se… | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | B could be an input for A (AI) | 0.51 | Activity A provides prepared drinks and desserts for consumers to eat or drink at or take away from outlets. Activity B… |  |
| T-9 Liqueur | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.51 | Activity A is a finished alcoholic drink intended for consumers to drink or give as a gift. Activity B consists of coco… |  |
| T-3 Non-chocolate sugar confectio… | P2-2 Professional and artisan choc… | candidate | different product |  | A could be resold by B (rule) | 0.50 | A is finished, ready-to-eat non-chocolate candy for consumers, while B is professional chocolate and cocoa material int… |  |
| T-7 Café, beverage and dessert se… | P2-6 Bakery, confectionery and des… | candidate | different product |  | B could be an input for A (AI) | 0.50 | A provides prepared café drinks and desserts for immediate consumption, while B supplies ingredients and decorations fo… |  |
| T-2 Retail sale of chocolate and … | P2-10 Professional chocolate educat… | candidate | different product |  | A could be an input for B (AI) | 0.50 | Activity A sells finished chocolate and confectionery for eating or gifting. Activity B provides instruction to develop… |  |
| T-2 Retail sale of chocolate and … | P2-6 Bakery, confectionery and des… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule); B could be resold by A (rule) | 0.50 | Both activities concern confectionery-related edible products, but A sells finished chocolate and confectionery for con… |  |
| T-7 Café, beverage and dessert se… | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.49 | Activity A provides ready-to-consume café drinks and desserts, while Activity B supplies processed cocoa ingredients fo… |  |
| T-6 Dessert and beverage sauces a… | P2-5 Nut and almond ingredients | candidate | similar product, possibly substitutable | ●●○ |  | 0.49 | Both are used to flavour or top desserts, baked goods, ice cream and beverages, so some customers could choose a nut-ba… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P2-7 Professional beverage mixes a… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.49 | Most products are different: finished confectionery is eaten or given as a gift, while beverage mixes and ingredients a… |  |
| T-1 Finished chocolate and chocol… | P2-5 Nut and almond ingredients | candidate | different product |  | B could be an input for A (AI) | 0.49 | Finished chocolate products are ready-to-eat treats or gifts, while the listed nut and almond products are primarily in… |  |
| T-6 Dessert and beverage sauces a… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.48 | Activity A supplies finished sauces and beverage mixes for preparing or topping drinks and foods; Activity B supplies c… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P2-8 Cocoa-fruit ingredients | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.48 | A provides prepared drinks and desserts for consumers, while B supplies ingredients used to make foods and beverages. S… |  |
| T-2 Retail sale of chocolate and … | P2-7 Professional beverage mixes a… | candidate | different product |  | B could be resold by A (rule) | 0.47 | Chocolate and confectionery are eaten or given as gifts, whereas beverage mixes and ingredients are used to prepare dri… |  |
| T-11 Licensing of product brands | P2-7 Professional beverage mixes a… | candidate | different product |  | A could be an input for B (AI) | 0.47 | Activity A is a brand-licensing service, while Activity B consists of beverage mixes and ingredients. Customers would n… | no EEA overlap |
| T-4 Candied chestnuts | P2-4 Chocolate fillings, inclusion… | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI) | 0.47 | Both are sweet confectionery products intended ultimately for consumers, but candied chestnuts are finished products ea… |  |
| T-6 Dessert and beverage sauces a… | P2-3 Processed cocoa ingredients | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.46 | A’s chocolate-based beverage mixes and dessert sauces and B’s cocoa ingredients can both contribute chocolate or cocoa … | no EEA overlap |
| T-4 Candied chestnuts | P2-6 Bakery, confectionery and des… | candidate | different product |  | A could be an input for B (AI) | 0.46 | Candied chestnuts are finished confectionery for consumers to eat or give as gifts. The products in B are ingredients o… |  |
| T-3 Non-chocolate sugar confectio… | P2-5 Nut and almond ingredients | candidate | different product |  | A could be resold by B (AI) | 0.46 | A consists of finished sugar candies eaten or given as gifts, while B consists mainly of nut-based ingredients and prep… |  |
| T-9 Liqueur | P2-5 Nut and almond ingredients | candidate | different product |  | A could be an input for B (AI) | 0.45 | Activity A is a finished alcoholic drink intended for consumers to drink or give as a gift. Activity B comprises nut-ba… |  |
| T-9 Liqueur | P2-8 Cocoa-fruit ingredients | candidate | different product |  | B could be an input for A (AI) | 0.45 | Liqueur is a finished alcoholic drink for consumption or gifting, whereas cocoa-fruit pulp, juice and powder blends are… |  |
| T-1 Finished chocolate and chocol… | P2-8 Cocoa-fruit ingredients | candidate | different product |  | B could be an input for A (AI and rule) | 0.45 | Finished chocolate products are eaten or given as gifts, while cocoa-fruit ingredients are inputs used by manufacturers… |  |
| T-2 Retail sale of chocolate and … | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.45 | A consists of finished chocolate and confectionery sold for consumers to eat or give as gifts. B consists of processed … |  |
| T-4 Candied chestnuts | P2-2 Professional and artisan choc… | candidate | different product |  | A could be an input for B (AI); A could be resold by B (rule) | 0.44 | Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Professional chocolate and cocoa pr… |  |
| T-12 Property-related income and c… | P2-2 Professional and artisan choc… | candidate | different product |  | B could be an input for A (AI) | 0.43 | Activity A consists of property, administrative and chocolate-making demonstration services, while Activity B supplies … | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.43 | Activity A’s chocolate-based beverage mixes and Activity B’s sunflower-seed-based chocolate-like ingredients are differ… | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.43 | Non-chocolate sugar confectionery is a finished sweet eaten or given as a gift, whereas cocoa liquor, cocoa butter and … |  |
| T-4 Candied chestnuts | P2-1 Industrial chocolate and couv… | candidate | different product |  | B could be an input for A (AI) | 0.43 | Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Industrial chocolate and couverture… |  |
| T-2 Retail sale of chocolate and … | P2-9 Cocoa-free chocolate alternat… | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI and rule) | 0.42 | Activity A sells finished chocolate and confectionery for eating or gifting, while Activity B supplies sunflower-based … |  |
| T-8 Catering and café food servic… | P2-7 Professional beverage mixes a… | candidate | different product |  | B could be an input for A (AI) | 0.42 | A provides prepared food and café service for event attendees, while B supplies mixes and ingredients used to prepare b… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (AI) | 0.42 | A is a consumer-facing café service providing prepared drinks and desserts for consumption at or away from outlets. B i… |  |
| T-4 Candied chestnuts | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (AI) | 0.41 | Candied chestnuts are finished confectionery eaten or given as gifts, while the sunflower-seed-based products are inter… |  |
| T-11 Licensing of product brands | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.39 | Activity A is a service that grants rights to use product brands, while Activity B consists of physical cocoa ingredien… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P2-5 Nut and almond ingredients | candidate | different product |  | B could be an input for A (AI) | 0.39 | Activity A provides prepared café drinks and desserts for consumers to consume, while Activity B supplies ingredients u… |  |
| T-12 Property-related income and c… | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.38 | Activity A provides property-related income, administrative services, and chocolate-making demonstrations; Activity B s… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P2-8 Cocoa-fruit ingredients | candidate | different product |  | B could be an input for A (AI) | 0.38 | Activity A sells finished chocolate and confectionery for consumers to eat or give as gifts. Activity B supplies cocoa-… |  |
| T-2 Retail sale of chocolate and … | P2-5 Nut and almond ingredients | candidate | different product |  | B could be an input for A (AI) | 0.37 | Chocolate and confectionery sold for eating or gifting are finished consumer products, whereas the listed nuts and almo… |  |
| T-8 Catering and café food servic… | P2-6 Bakery, confectionery and des… | candidate | different product |  | B could be an input for A (AI) | 0.36 | Activity A provides prepared meals and refreshments for consumption at events or a café. Activity B supplies ingredient… | no EEA overlap |
| T-11 Licensing of product brands | P2-1 Industrial chocolate and couv… | candidate | different product |  | A could be an input for B (AI) | 0.36 | Activity A is a brand-licensing service that gives licensees rights to produce or market branded products. Activity B i… | no EEA overlap |
| T-8 Catering and café food servic… | P2-2 Professional and artisan choc… | candidate | different product |  | B could be an input for A (AI) | 0.36 | A provides prepared food and refreshments for event attendees, while B supplies chocolate and cocoa ingredients for pro… | no EEA overlap |
| T-11 Licensing of product brands | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | A could be an input for B (AI) | 0.35 | Activity A licenses brand rights so others can produce or market branded products; Activity B supplies physical chocola… | no EEA overlap |
| T-8 Catering and café food servic… | P2-1 Industrial chocolate and couv… | candidate | different product |  | B could be an input for A (AI) | 0.33 | Activity A provides prepared food and refreshments as a catering or café service for event attendees. Activity B suppli… | no EEA overlap |
| T-8 Catering and café food servic… | P2-4 Chocolate fillings, inclusion… | candidate | different product |  | B could be an input for A (AI) | 0.33 | Activity A provides prepared meals, refreshments and café service for event attendees. Activity B supplies chocolate co… | no EEA overlap |
| T-11 Licensing of product brands | P2-8 Cocoa-fruit ingredients | candidate | different product |  | A could be an input for B (AI) | 0.31 | Activity A supplies rights and services that let licensees produce or market branded products. Activity B supplies phys… | no EEA overlap |
| T-11 Licensing of product brands | P2-9 Cocoa-free chocolate alternat… | candidate | different product |  | B could be an input for A (AI) | 0.29 | Activity A is a brand-licensing service that lets licensees produce or market branded products; Activity B is a sunflow… | no EEA overlap |
| T-8 Catering and café food servic… | P2-3 Processed cocoa ingredients | candidate | different product |  | B could be an input for A (AI) | 0.29 | Activity A provides prepared meals, refreshments and café service for event attendees. Activity B supplies processed co… | no EEA overlap |
| T-8 Catering and café food servic… | P2-5 Nut and almond ingredients | candidate | different product |  | B could be an input for A (AI) | 0.28 | Activity A provides prepared meals and refreshments for event attendees, while Activity B supplies ingredients and prep… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P2-10 Professional chocolate educat… | unclear | different product |  |  | 0.60 | Activity A supplies edible chocolate and cocoa ingredients and coatings for preparing or finishing foods. Activity B pr… | no EEA overlap |

<details><summary>38 pairs screened out</summary>

- T-3 Non-chocolate sugar confectionery ↔ P2-7 Professional beverage mixes and in… (sim. 0.43): A consists of finished sweets eaten directly or given as gifts, while B consists of preparations an…
- T-3 Non-chocolate sugar confectionery ↔ P2-8 Cocoa-fruit ingredients (sim. 0.45): Activity A comprises finished sugar confectionery eaten as sweets or given as gifts. Activity B com…
- T-3 Non-chocolate sugar confectionery ↔ P2-10 Professional chocolate education a… (sim. 0.39): Activity A is finished sugar confectionery for eating or gifting, while Activity B is education and…
- T-4 Candied chestnuts ↔ P2-3 Processed cocoa ingredients (sim. 0.39): Candied chestnuts are finished confectionery eaten by consumers or given as gifts. Cocoa liquor, co…
- T-4 Candied chestnuts ↔ P2-7 Professional beverage mixes and in… (sim. 0.36): Candied chestnuts are finished confectionery eaten as a sweet or given as a gift. Beverage mixes an…
- T-4 Candied chestnuts ↔ P2-8 Cocoa-fruit ingredients (sim. 0.40): Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Cocoa-fruit pul…
- T-4 Candied chestnuts ↔ P2-10 Professional chocolate education a… (sim. 0.33): Candied chestnuts are finished confectionery eaten or given as gifts, whereas the other activity pr…
- T-6 Dessert and beverage sauces and be… ↔ P2-10 Professional chocolate education a… (sim. 0.42): Sauces and beverage mixes are consumable food products used to prepare or top drinks and desserts. …
- T-7 Café, beverage and dessert service ↔ P2-10 Professional chocolate education a… (sim. 0.48): Activity A provides prepared drinks and desserts for consumption, while Activity B provides instruc…
- T-8 Catering and café food service for… ↔ P2-8 Cocoa-fruit ingredients (sim. 0.27): A provides prepared food and refreshments for event attendees, while B supplies cocoa-fruit ingredi…
- T-8 Catering and café food service for… ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.25): Activity A provides prepared meals and refreshments for immediate consumption at events or a café. …
- T-8 Catering and café food service for… ↔ P2-10 Professional chocolate education a… (sim. 0.33): A provides prepared food and refreshments for event attendees, while B provides education and train…
- T-9 Liqueur ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.44): Liqueur is a finished alcoholic drink for consumers to drink or give as a gift. The other activity …
- T-9 Liqueur ↔ P2-7 Professional beverage mixes and in… (sim. 0.49): Liqueur is a finished alcoholic drink intended for direct consumption or gifting. The mixes and ing…
- T-9 Liqueur ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.42): Branded bottled liqueur is an alcoholic drink for consumers, while the cocoa-free chocolate-like in…
- T-9 Liqueur ↔ P2-10 Professional chocolate education a… (sim. 0.42): A is a finished alcoholic drink intended for consumption or gifting, while B is education and train…
- T-10 Foodservice accessories ↔ P2-1 Industrial chocolate and couverture (sim. 0.31): Foodservice accessories dispense and organise sauces, while industrial chocolate and couverture are…
- T-10 Foodservice accessories ↔ P2-2 Professional and artisan chocolate… (sim. 0.36): Sauce-bottle pumps and racks dispense or organise sauces, while professional chocolate and cocoa in…
- T-10 Foodservice accessories ↔ P2-3 Processed cocoa ingredients (sim. 0.29): Sauce-bottle pumps and racks dispense and organise sauces, while cocoa liquor, butter and powder ar…
- T-10 Foodservice accessories ↔ P2-4 Chocolate fillings, inclusions and… (sim. 0.36): Foodservice accessories dispense or organise sauces, while chocolate fillings, pieces and decoratio…
- T-10 Foodservice accessories ↔ P2-5 Nut and almond ingredients (sim. 0.29): Foodservice accessories dispense and organise sauces, while nut and almond ingredients are food pro…
- T-10 Foodservice accessories ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.36): Sauce-bottle pumps and racks are equipment for dispensing and organising sauces, while the other pr…
- T-10 Foodservice accessories ↔ P2-7 Professional beverage mixes and in… (sim. 0.42): Foodservice accessories dispense and organise sauces, while beverage mixes and ingredients are used…
- T-10 Foodservice accessories ↔ P2-8 Cocoa-fruit ingredients (sim. 0.27): Sauce-bottle pumps and racks are foodservice equipment for dispensing and organising sauces, while …
- T-10 Foodservice accessories ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.22): Foodservice accessories dispense and organise sauces, whereas the cocoa-free ingredients are used t…
- T-10 Foodservice accessories ↔ P2-10 Professional chocolate education a… (sim. 0.26): Activity A supplies physical accessories used to dispense and organise sauces in foodservice settin…
- T-11 Licensing of product brands ↔ P2-2 Professional and artisan chocolate… (sim. 0.37): Activity A is a service granting rights to use product brands, while Activity B consists of chocola…
- T-11 Licensing of product brands ↔ P2-5 Nut and almond ingredients (sim. 0.35): A is a brand-licensing service, while B consists of nut and almond ingredients used in food product…
- T-11 Licensing of product brands ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.45): A is a brand-licensing service, while B consists of physical food ingredients and decorations used …
- T-11 Licensing of product brands ↔ P2-10 Professional chocolate education a… (sim. 0.29): Activity A provides brand rights and licensing services that enable other businesses to produce or …
- T-12 Property-related income and contra… ↔ P2-1 Industrial chocolate and couverture (sim. 0.43): Property income, administrative support, and chocolate-making demonstrations serve property, organi…
- T-12 Property-related income and contra… ↔ P2-4 Chocolate fillings, inclusions and… (sim. 0.40): A comprises property income, administrative services and contracted chocolate-making demonstrations…
- T-12 Property-related income and contra… ↔ P2-5 Nut and almond ingredients (sim. 0.30): Activity A comprises property income, administrative support and chocolate-making demonstrations; A…
- T-12 Property-related income and contra… ↔ P2-6 Bakery, confectionery and dessert … (sim. 0.34): Activity A comprises property income, administrative support, and chocolate-making demonstrations; …
- T-12 Property-related income and contra… ↔ P2-7 Professional beverage mixes and in… (sim. 0.36): Activity A concerns property arrangements, administrative support and contracted chocolate-making d…
- T-12 Property-related income and contra… ↔ P2-8 Cocoa-fruit ingredients (sim. 0.32): Activity A comprises property income, administrative services and chocolate-making demonstrations, …
- T-12 Property-related income and contra… ↔ P2-9 Cocoa-free chocolate alternative i… (sim. 0.37): A comprises property income, administrative support and chocolate-making demonstrations; B is a sun…
- T-12 Property-related income and contra… ↔ P2-10 Professional chocolate education a… (sim. 0.40): Activity A combines property income, administrative support for foundations and funds, and contract…

</details>

### Bahlsen

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | EEA |
|---|---|---|---|---|---|---|---|---|
| T-2 Retail sale of chocolate and … | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●●● | A could be resold by B (AI) | 0.69 | Both activities retail chocolate and confectionery for consumers to eat or give as gifts, so those items overlap direct… |  |
| T-1 Finished chocolate and chocol… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI and rule) | 0.68 | Both activities include chocolate and chocolate confectionery sold for consumers to eat or give as gifts. Activity B al… |  |
| T-1 Finished chocolate and chocol… | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●●○ |  | 0.61 | Both are finished sweet products consumed as snacks or confectionery, so some biscuits, wafers, or peppermint tablets c… |  |
| T-1 Finished chocolate and chocol… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI) | 0.58 | Both are finished sweet products eaten by consumers as snacks or treats, and some chocolate products and chocolate-cont… |  |
| T-1 Finished chocolate and chocol… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●● |  | 0.57 | Both are finished chocolate-containing products for consumers to eat, and chocolate snacks may overlap with portable bi… |  |
| T-3 Non-chocolate sugar confectio… | P3-8 Biscuits, baked goods, snacks… | candidate | same product | ●●○ | A could be resold by B (AI and rule) | 0.56 | B’s assortment expressly includes fruit gums, which fall within non-chocolate sugar confectionery; the remaining items … |  |
| T-1 Finished chocolate and chocol… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●○ |  | 0.56 | Both are finished, packaged sweet foods intended for consumers to eat, and some chocolate confectionery and cakes may s… |  |
| T-2 Retail sale of chocolate and … | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●○○ | B could be resold by A (AI and rule) | 0.55 | Both are finished sweet products for consumers to eat as snacks or confectionery, and some products in B could plausibl… |  |
| T-3 Non-chocolate sugar confectio… | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●●○ |  | 0.54 | Both activities include finished sweet products for consumers, and peppermint tablets in B may overlap with A’s sugar c… |  |
| T-5 Chocolate and cocoa ingredien… | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.54 | A consists of professional ingredients and coatings used to prepare or finish foods, while B consists of finished snack… | no EEA overlap |
| T-11 Licensing of product brands | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI) | 0.52 | Activity A provides brand-licensing services to businesses; Activity B sells finished food products to consumers. The p… | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●● |  | 0.52 | Both are finished sweet treats eaten by consumers, including as snacks or gifts, so they may serve overlapping consumpt… |  |
| T-5 Chocolate and cocoa ingredien… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.52 | A consists of professional ingredients and coatings used to prepare or finish foods, while B consists of finished packa… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●● |  | 0.50 | Both are finished seasonal or treat products eaten by consumers as snacks or desserts, and some chocolate confectionery… |  |
| T-7 Café, beverage and dessert se… | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●○○ | B could be resold by A (AI) | 0.50 | Café beverages and ice cream are distinct from packaged biscuits, wafers, cakes and peppermint tablets. However, some o… |  |
| T-2 Retail sale of chocolate and … | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); B could be resold by A (rule) | 0.50 | Both are sweet foods eaten as snacks or treats, and some biscuits, wafers and pastries contain chocolate or cocoa. They… |  |
| T-1 Finished chocolate and chocol… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.50 | Both are finished sweet snack products intended for consumers to eat, and some chocolate snacks and fruit-and-nut bars … |  |
| T-6 Dessert and beverage sauces a… | P3-5 Private-label biscuits, coffe… | candidate | different product |  | A could be an input for B (AI) | 0.50 | Sauces and beverage mixes are used to prepare or top drinks and desserts, while biscuits, pastries, wafers and peppermi… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●○ |  | 0.49 | Both are sweet food products that consumers may use for dessert occasions, although sauces and beverage mixes are used … | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (rule) | 0.49 | A includes chocolate products, while B’s resale assortment can include chocolate and pralines, creating some overlap in… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI); B could be resold by A (rule) | 0.48 | Chocolate and confectionery sold in shops includes products for eating, while biscuit-based snack bars are portable, pa… |  |
| T-2 Retail sale of chocolate and … | P3-6 Private-label product develop… | candidate | different product |  | A could be resold by B (AI); B could be resold by A (rule) | 0.48 | A is the retail sale of finished chocolate and confectionery for consumers to eat or give as gifts. B is a business-to-… |  |
| T-9 Liqueur | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be resold by B (AI and rule) | 0.48 | Liqueur is an alcoholic drink, while Activity B describes retail sales of biscuits, baked goods, snacks and other food … |  |
| T-7 Café, beverage and dessert se… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ | B could be resold by A (AI) | 0.48 | Packaged biscuits, cookies, wafers and pastries are sweet snacks or treats, while the café activity offers drinks and d… |  |
| T-6 Dessert and beverage sauces a… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI and rule) | 0.48 | Both activities involve finished food products bought for consumption, and some products in B’s assortment (such as cho… | no EEA overlap |
| T-4 Candied chestnuts | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●● |  | 0.48 | Candied chestnuts and packaged cakes are different types of sweet confectionery or baked goods, but both are ready-to-e… |  |
| T-3 Non-chocolate sugar confectio… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●○ |  | 0.48 | Both are finished, sweet products for consumers to eat as treats or desserts, so some customers could choose between th… |  |
| T-9 Liqueur | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI) | 0.47 | Liqueurs and biscuits, pastries, wafers, cakes and peppermint tablets are different products, but some are consumed as … |  |
| T-7 Café, beverage and dessert se… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●●● | A could be an input for B (AI) | 0.47 | A sells prepared drinks, ice cream and desserts for immediate consumption, while B resells packaged snacks and other fo… |  |
| T-7 Café, beverage and dessert se… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ |  | 0.46 | Packaged cakes are distinct from café-prepared drinks and desserts, but both can serve as sweet treats or desserts for … |  |
| T-4 Candied chestnuts | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (AI and rule) | 0.46 | Candied chestnuts are a confectionery product for eating or gifting, while B sells a broader range of food products tha… |  |
| T-5 Chocolate and cocoa ingredien… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●●○ |  | 0.46 | Professional chocolate and cocoa ingredients are used to prepare or coat desserts, while packaged cakes are ready-to-ea… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | A could be resold by B (AI); B could be resold by A (rule) | 0.46 | Both are sweet products eaten by consumers as snacks, desserts, or gifts, though chocolate and confectionery differ fro… |  |
| T-3 Non-chocolate sugar confectio… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●● |  | 0.45 | Both are finished, packaged sweet foods for consumers, and both may be eaten as snacks. Biscuit-based chocolate bars di… |  |
| T-5 Chocolate and cocoa ingredien… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.45 | Professional chocolate and cocoa ingredients or coatings are used to prepare or coat foods, while biscuit-based chocola… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | A could be an input for B (AI) | 0.45 | A consists of sauces and mixes used to prepare or top drinks, desserts and baked goods; B consists of finished baked go… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ | B could be resold by A (AI) | 0.45 | Café drinks and desserts are prepared for consumption at or near the point of purchase, while the bars are packaged for… |  |
| T-3 Non-chocolate sugar confectio… | P3-6 Private-label product develop… | candidate | different product |  | B could be an input for A (AI) | 0.44 | A consists of finished sugar confectionery for consumers to eat or give as gifts. B is a business service for developin… |  |
| T-4 Candied chestnuts | P3-5 Private-label biscuits, coffe… | candidate | similar product, possibly substitutable | ●●○ |  | 0.43 | Both are finished sweet products for consumers to eat, and some biscuit, wafer or peppermint products could serve as an… |  |
| T-4 Candied chestnuts | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ |  | 0.42 | Both are finished sweet foods eaten by consumers as treats, and may compete for some snack or confectionery occasions. … |  |
| T-6 Dessert and beverage sauces a… | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ |  | 0.41 | Sauces and beverage mixes are used to prepare or top drinks and desserts, while biscuit-based bars are eaten as portabl… | no EEA overlap |
| T-11 Licensing of product brands | P3-1 Packaged biscuits, cookies, w… | candidate | different product |  | B could be resold by A (AI) | 0.41 | A is a licensing service involving rights to use product brands; B is finished packaged sweet baked goods eaten as snac… | no EEA overlap |
| T-4 Candied chestnuts | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ |  | 0.41 | Both are finished sweet confectionery or baked goods consumed by consumers as treats and may also be bought as gifts. C… |  |
| T-11 Licensing of product brands | P3-3 Packaged cakes | candidate | different product |  | A could be an input for B (AI) | 0.41 | A is a licensing service that grants rights to use product brands; B is a finished, ready-to-eat packaged cake. Custome… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI); B could be resold by A (rule) | 0.41 | Chocolate and confectionery and seasonal biscuits and baked goods are different product types, but both are consumer tr… |  |
| T-6 Dessert and beverage sauces a… | P3-4 Seasonal biscuits and baked g… | candidate | different product |  | A could be an input for B (AI) | 0.41 | Sauces and beverage mixes are used to prepare or top drinks, desserts and other foods, while seasonal biscuits and bake… | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●● |  | 0.40 | Both are finished sweet treats eaten by consumers, including as snacks or gifts, so some customers may choose between t… |  |
| T-4 Candied chestnuts | P3-6 Private-label product develop… | candidate | different product |  | A could be resold by B (AI) | 0.40 | Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Private-label product development a… |  |
| T-11 Licensing of product brands | P3-2 Biscuit-based snack bars | candidate | different product |  | B could be resold by A (AI) | 0.39 | Activity A is a licensing service that grants businesses rights to use product brands; Activity B is a packaged biscuit… | no EEA overlap |
| T-12 Property-related income and c… | P3-8 Biscuits, baked goods, snacks… | candidate | different product |  | A could be an input for B (AI) | 0.38 | A comprises property income, administrative services and contracted chocolate-making demonstrations, while B comprises … | no EEA overlap |
| T-11 Licensing of product brands | P3-9 Hoodies and fabric tote bags | candidate | different product |  | A could be an input for B (AI) | 0.38 | A is a business-to-business service granting rights to use product brands, while B consists of physical apparel and fab… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.38 | A's sauces and beverage mixes are used to prepare or top drinks and foods, while B's bars are eaten as portable snacks.… | no EEA overlap |
| T-2 Retail sale of chocolate and … | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ | A could be resold by B (AI) | 0.38 | Both are sweet foods intended for consumers to eat, and chocolate or confectionery could plausibly substitute for a sna… |  |
| T-4 Candied chestnuts | P3-2 Biscuit-based snack bars | candidate | similar product, possibly substitutable | ●●○ |  | 0.37 | Candied chestnuts and biscuit-based snack bars are different confectionery products, but both are finished sweet foods … |  |
| T-3 Non-chocolate sugar confectio… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.37 | Both are finished confectionery or snack products intended for consumers to eat, and some consumers could choose a frui… |  |
| T-5 Chocolate and cocoa ingredien… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ | A could be an input for B (AI) | 0.37 | A supplies professional chocolate and cocoa ingredients used to prepare or coat foods, while B consists of finished sea… | no EEA overlap |
| T-8 Catering and café food servic… | P3-8 Biscuits, baked goods, snacks… | candidate | similar product, possibly substitutable | ●●○ | B could be resold by A (AI) | 0.37 | Both activities provide food for consumption, and some retail snacks or baked goods could serve as refreshments in plac… | no EEA overlap |
| T-11 Licensing of product brands | P3-4 Seasonal biscuits and baked g… | candidate | different product |  | A could be an input for B (AI) | 0.37 | A is a service granting rights to use product brands, while B consists of finished seasonal biscuits and baked goods ea… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●○○ |  | 0.36 | Both are finished food products that can be eaten by consumers, but A consists of chocolate and cocoa ingredients and c… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ |  | 0.35 | Both are consumer-facing treats or desserts that may be consumed as snacks, and a customer could sometimes choose a sea… |  |
| T-7 Café, beverage and dessert se… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.34 | The café drinks and desserts and the packaged bars are different products, but both can serve as a snack or treat for c… |  |
| T-8 Catering and café food servic… | P3-1 Packaged biscuits, cookies, w… | candidate | similar product, possibly substitutable | ●●○ |  | 0.33 | Both activities provide food for consumption, but A serves prepared meals and refreshments in an event or café setting,… | no EEA overlap |
| T-11 Licensing of product brands | P3-7 Organic fruit-and-nut bars an… | candidate | different product |  | A could be an input for B (AI) | 0.33 | A is a brand-licensing service that enables other businesses to produce or market branded goods; B consists of finished… | no EEA overlap |
| T-4 Candied chestnuts | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.33 | Both are finished confectionery or snack products for consumers to eat, and either could serve as a sweet snack or edib… |  |
| T-8 Catering and café food servic… | P3-3 Packaged cakes | candidate | similar product, possibly substitutable | ●○○ | B could be resold by A (AI) | 0.33 | Both provide food for consumption, and packaged cakes could serve as a dessert or sweet food option at an event where c… | no EEA overlap |
| T-8 Catering and café food servic… | P3-4 Seasonal biscuits and baked g… | candidate | similar product, possibly substitutable | ●●○ | B could be resold by A (AI) | 0.30 | Both activities provide food for consumption, but A supplies prepared meals and refreshments as an event or café servic… | no EEA overlap |
| T-8 Catering and café food servic… | P3-7 Organic fruit-and-nut bars an… | candidate | similar product, possibly substitutable | ●●○ |  | 0.26 | Both provide food for consumption, but A is prepared event and café food while B consists of packaged portable snack ba… | no EEA overlap |
| T-11 Licensing of product brands | P3-6 Private-label product develop… | unclear | different product |  |  | 0.52 | A provides rights to use product brands, while B provides expertise and development support to create tailored sweet pr… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P3-6 Private-label product develop… | unclear | different product |  |  | 0.52 | A consists of finished sauces and beverage mixes used to prepare or top foods and drinks. B is a development service fo… | no EEA overlap |

<details><summary>39 pairs screened out</summary>

- T-1 Finished chocolate and chocolate c… ↔ P3-6 Private-label product development … (sim. 0.48): A consists of edible chocolate products for consumers to eat or give as gifts. B is a business serv…
- T-1 Finished chocolate and chocolate c… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.36): Chocolate and chocolate confectionery are eaten or given as gifts, while hoodies are worn and fabri…
- T-2 Retail sale of chocolate and confe… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.38): Chocolate and confectionery are eaten or given as gifts, while hoodies and fabric tote bags are wor…
- T-3 Non-chocolate sugar confectionery ↔ P3-9 Hoodies and fabric tote bags (sim. 0.30): Non-chocolate sugar confectionery is eaten, while hoodies are worn and fabric tote bags are used to…
- T-4 Candied chestnuts ↔ P3-9 Hoodies and fabric tote bags (sim. 0.29): Candied chestnuts are edible confectionery intended for consumption or gifting, whereas hoodies and…
- T-5 Chocolate and cocoa ingredients an… ↔ P3-6 Private-label product development … (sim. 0.46): A consists of finished chocolate and cocoa ingredients and coatings used to prepare or coat foods. …
- T-5 Chocolate and cocoa ingredients an… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.29): Professional chocolate, cocoa and confectionery coating ingredients are used to prepare or coat foo…
- T-6 Dessert and beverage sauces and be… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.32): Dessert and beverage sauces and mixes are used to prepare or top food and drinks. Hoodies and fabri…
- T-7 Café, beverage and dessert service ↔ P3-6 Private-label product development … (sim. 0.45): Activity A provides ready-to-consume café beverages and desserts for consumers. Activity B provides…
- T-7 Café, beverage and dessert service ↔ P3-9 Hoodies and fabric tote bags (sim. 0.33): Activity A provides prepared drinks and desserts for consumption, while Activity B sells apparel an…
- T-8 Catering and café food service for… ↔ P3-2 Biscuit-based snack bars (sim. 0.28): Activity A provides prepared food and refreshments as catering and café services for events and sit…
- T-8 Catering and café food service for… ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.35): Activity A provides prepared food and refreshments as an event and café service, while Activity B s…
- T-8 Catering and café food service for… ↔ P3-6 Private-label product development … (sim. 0.36): A provides prepared food and refreshments for event attendees, while B provides development support…
- T-8 Catering and café food service for… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.29): A provides prepared food and refreshments for consumption at events or in a café. B consists of app…
- T-9 Liqueur ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.45): Liqueur is an alcoholic drink intended for drinking or gifting, while the packaged biscuits and pas…
- T-9 Liqueur ↔ P3-2 Biscuit-based snack bars (sim. 0.44): Liqueur is an alcoholic drink intended for drinking or gifting, while biscuit-based snack bars are …
- T-9 Liqueur ↔ P3-3 Packaged cakes (sim. 0.48): Liqueur is an alcoholic drink intended for drinking or gifting, while packaged cakes are ready-to-e…
- T-9 Liqueur ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.38): Liqueur is an alcoholic drink, while the seasonal products are biscuits and baked goods eaten as sn…
- T-9 Liqueur ↔ P3-6 Private-label product development … (sim. 0.43): A is a finished alcoholic drink for consumers, while B is a business service used to develop tailor…
- T-9 Liqueur ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.36): Liqueur is an alcoholic drink intended for drinking or gifting, whereas the bars are solid portable…
- T-9 Liqueur ↔ P3-9 Hoodies and fabric tote bags (sim. 0.35): Liqueur is an alcoholic beverage for drinking, while hoodies and fabric tote bags are apparel and c…
- T-10 Foodservice accessories ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.26): Foodservice pumps and racks are equipment for dispensing and organising sauces, while packaged bisc…
- T-10 Foodservice accessories ↔ P3-2 Biscuit-based snack bars (sim. 0.27): Foodservice accessories dispense and organise sauces, whereas biscuit-based bars are packaged foods…
- T-10 Foodservice accessories ↔ P3-3 Packaged cakes (sim. 0.24): Foodservice accessories are equipment for dispensing or organising sauces, while packaged cakes are…
- T-10 Foodservice accessories ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.26): Sauce pumps and racks are professional equipment for dispensing and organising sauces, while the ot…
- T-10 Foodservice accessories ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.30): Foodservice accessories are equipment for dispensing and organising sauces, whereas biscuits, pastr…
- T-10 Foodservice accessories ↔ P3-6 Private-label product development … (sim. 0.34): Activity A supplies physical accessories used to dispense and organise sauces in foodservice operat…
- T-10 Foodservice accessories ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.27): Foodservice accessories dispense and organise sauces, whereas fruit-and-nut and protein bars are po…
- T-10 Foodservice accessories ↔ P3-8 Biscuits, baked goods, snacks and … (sim. 0.32): Activity A supplies professional sauce-dispensing and organisation accessories for foodservice use.…
- T-10 Foodservice accessories ↔ P3-9 Hoodies and fabric tote bags (sim. 0.32): Sauce-bottle pumps and sauce racks are professional accessories for dispensing and organising sauce…
- T-11 Licensing of product brands ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.47): Activity A provides brand-licensing services to businesses, while Activity B supplies finished swee…
- T-12 Property-related income and contra… ↔ P3-1 Packaged biscuits, cookies, wafers… (sim. 0.27): A consists of property arrangements and administrative and demonstration services, while B consists…
- T-12 Property-related income and contra… ↔ P3-2 Biscuit-based snack bars (sim. 0.24): Activity A comprises property income, administrative services, and chocolate-making demonstrations,…
- T-12 Property-related income and contra… ↔ P3-3 Packaged cakes (sim. 0.29): Property income, administrative support, and chocolate-making demonstrations serve purposes distinc…
- T-12 Property-related income and contra… ↔ P3-4 Seasonal biscuits and baked goods (sim. 0.23): A comprises property income, administrative services and chocolate-making demonstrations, while B c…
- T-12 Property-related income and contra… ↔ P3-5 Private-label biscuits, coffee pas… (sim. 0.33): Activity A consists of property arrangements and administrative and demonstration services, whereas…
- T-12 Property-related income and contra… ↔ P3-6 Private-label product development … (sim. 0.34): Activity A comprises property arrangements, administrative support, and chocolate-making demonstrat…
- T-12 Property-related income and contra… ↔ P3-7 Organic fruit-and-nut bars and pro… (sim. 0.23): Activity A consists of property arrangements, administrative services and chocolate-making demonstr…
- T-12 Property-related income and contra… ↔ P3-9 Hoodies and fabric tote bags (sim. 0.24): Activity A comprises property-related income, administrative services and chocolate-making demonstr…

</details>

### FRoSTA

| Target | Portco | Result | Product (AI) | Cust. | Vertical (found by) | Sim. | Reason (AI) | EEA |
|---|---|---|---|---|---|---|---|---|
| T-11 Licensing of product brands | P4-3 Branded frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.50 | A is a service granting brand rights for other businesses to produce or market branded goods; B is a range of finished … | no EEA overlap |
| T-8 Catering and café food servic… | P4-8 Frozen meals and meal boxes f… | candidate | similar product, possibly substitutable | ●●○ |  | 0.49 | Both provide food for people to eat, but A is prepared catering and café service at an event site, while B is frozen me… | no EEA overlap |
| T-8 Catering and café food servic… | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●○ | B could be an input for A (AI) | 0.49 | A provides prepared food and refreshments for event attendees, while B supplies frozen foods that professional kitchens… | no EEA overlap |
| T-8 Catering and café food servic… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be an input for B (AI) | 0.44 | Activity A provides prepared food and refreshments for consumption at events or in a café. Activity B supplies frozen f… | no EEA overlap |
| T-8 Catering and café food servic… | P4-5 Frozen food supplied to indus… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.44 | Both activities concern food intended ultimately for consumption, but A provides prepared meals and refreshments for ev… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P4-5 Frozen food supplied to indus… | candidate | different product |  | A could be an input for B (AI) | 0.44 | Activity A consists of finished chocolate products for consumers to eat or give as gifts. Activity B supplies frozen pr… |  |
| T-8 Catering and café food servic… | P4-1 Branded frozen meals, fish, v… | candidate | similar product, possibly substitutable | ●○○ | A could be an input for B (AI) | 0.44 | Both provide prepared food for people to eat, but one is served as catering or café food at events, while the other con… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P4-5 Frozen food supplied to indus… | candidate | different product |  | B could be an input for A (AI) | 0.43 | Activity A provides prepared drinks and desserts for immediate consumer consumption, while Activity B supplies frozen p… |  |
| T-1 Finished chocolate and chocol… | P4-10 Non-food merchandise | candidate | different product |  | A could be resold by B (rule) | 0.43 | Activity A consists of chocolate foods for eating or gifting, while Activity B consists of non-food apparel, accessorie… |  |
| T-6 Dessert and beverage sauces a… | P4-5 Frozen food supplied to indus… | candidate | not enough information |  | A could be an input for B (AI) | 0.43 | A consists of sauces and beverage mixes for preparing or topping drinks, desserts, ice cream and baked goods. B’s froze… | no EEA overlap |
| T-7 Café, beverage and dessert se… | P4-6 Frozen foods supplied to home… | candidate | different product |  | B could be resold by A (AI) | 0.42 | A provides prepared café drinks and desserts for immediate consumption, whereas B supplies assorted frozen foods for ho… |  |
| T-7 Café, beverage and dessert se… | P4-4 Frozen foods for professional… | candidate | different product |  | B could be an input for A (AI) | 0.42 | A provides prepared café drinks and desserts for consumers, while B supplies frozen foods intended for professional kit… |  |
| T-8 Catering and café food servic… | P4-2 Customer-brand frozen foods | candidate | similar product, possibly substitutable | ●○○ | B could be resold by A (AI) | 0.42 | Both activities provide food for consumption, and some prepared dishes or café foods could serve the same immediate pur… | no EEA overlap |
| T-8 Catering and café food servic… | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●●○ |  | 0.42 | Both provide prepared food for people to eat, but A serves food at events or a café while B sells frozen products for p… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be resold by B (AI) | 0.42 | Activity A supplies sauces and mixes used to prepare or top drinks and desserts, whereas Activity B supplies a broad ra… | no EEA overlap |
| T-11 Licensing of product brands | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be resold by B (AI) | 0.42 | A is a brand-licensing service, while B consists of finished frozen foods supplied for resale. The licensed products ma… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P4-3 Branded frozen foods | candidate | different product |  | A could be resold by B (AI) | 0.42 | Activity A comprises sauces and powdered or other beverage mixes used to prepare or top drinks and foods. Activity B co… | no EEA overlap |
| T-10 Foodservice accessories | P4-10 Non-food merchandise | candidate | different product |  | A could be resold by B (rule) | 0.41 | Foodservice sauce pumps and racks are professional equipment for dispensing and organising sauces, while the apparel, a… |  |
| T-2 Retail sale of chocolate and … | P4-3 Branded frozen foods | candidate | different product |  | B could be resold by A (rule) | 0.41 | Chocolate and confectionery are products for eating or gifting, while the identified products are frozen foods offered … |  |
| T-6 Dessert and beverage sauces a… | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be resold by B (AI) | 0.41 | Activity A comprises sauces and beverage mixes used to prepare or top drinks, desserts and baked goods. Activity B comp… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P4-10 Non-food merchandise | candidate | different product |  | A could be resold by B (rule) | 0.41 | Activity A comprises sauces and beverage mixes used to prepare or top drinks and foods. Activity B comprises apparel, a… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P4-4 Frozen foods for professional… | candidate | similar product, possibly substitutable | ●●● |  | 0.41 | Both are finished food products sold in professional formats for use in preparing or serving food in professional kitch… | no EEA overlap |
| T-6 Dessert and beverage sauces a… | P4-9 Product development and assor… | candidate | different product |  | B could be an input for A (AI) | 0.39 | A consists of finished sauces and beverage mixes used to prepare or top drinks and foods. B is a business advisory and … | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P4-5 Frozen food supplied to indus… | candidate | not enough information |  | A could be an input for B (AI) | 0.39 | A comprises professional chocolate and cocoa ingredients and coatings for preparing or coating foods. B comprises froze… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P4-1 Branded frozen meals, fish, v… | candidate | similar product, possibly substitutable | ●●○ |  | 0.38 | Both are finished foods bought for consumers to eat, so some customers could switch between them for a snack or eating … |  |
| T-11 Licensing of product brands | P4-1 Branded frozen meals, fish, v… | candidate | different product |  | A could be an input for B (AI) | 0.37 | Activity A is a brand-licensing service supplied to businesses, while Activity B consists of finished frozen foods inte… | no EEA overlap |
| T-8 Catering and café food servic… | P4-3 Branded frozen foods | candidate | similar product, possibly substitutable | ●○○ | B could be an input for A (AI) | 0.36 | Both provide food for consumption, but A is prepared food and café service for event attendees, while B is branded froz… | no EEA overlap |
| T-5 Chocolate and cocoa ingredien… | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.36 | A consists of professional chocolate and cocoa ingredients and coatings used to prepare or coat foods. B manufactures a… | no EEA overlap |
| T-1 Finished chocolate and chocol… | P4-4 Frozen foods for professional… | candidate | different product |  | A could be an input for B (AI) | 0.36 | Finished chocolate confectionery is eaten as a snack or given as a gift, while the frozen products are ingredients or p… |  |
| T-7 Café, beverage and dessert se… | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●●● |  | 0.35 | Both offer food and drink for consumers, and some café desserts or beverages could plausibly be replaced by frozen prod… |  |
| T-2 Retail sale of chocolate and … | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●●● |  | 0.34 | Both are consumer food products bought for consumption at home, and chocolate or confectionery could plausibly serve as… |  |
| T-3 Non-chocolate sugar confectio… | P4-5 Frozen food supplied to indus… | candidate | different product |  | A could be an input for B (AI) | 0.34 | Non-chocolate sugar confectionery is eaten as a sweet or given as a gift, while the frozen products are supplied for us… |  |
| T-5 Chocolate and cocoa ingredien… | P4-3 Branded frozen foods | candidate | different product |  | A could be resold by B (AI) | 0.33 | A consists of professional chocolate and cocoa ingredients and coatings used to prepare or coat foods. B is a range of … | no EEA overlap |
| T-3 Non-chocolate sugar confectio… | P4-3 Branded frozen foods | candidate | not enough information |  | A could be resold by B (AI) | 0.31 | Activity A is specifically sugar confectionery, while Activity B covers branded frozen foods without identifying their … |  |
| T-4 Candied chestnuts | P4-2 Customer-brand frozen foods | candidate | different product |  | A could be an input for B (AI) | 0.31 | Candied chestnuts are confectionery for eating or gifting, while B makes a varied range of frozen foods, including meal… |  |
| T-11 Licensing of product brands | P4-7 Frozen meals, fish, vegetable… | candidate | different product |  | A could be an input for B (AI) | 0.30 | Activity A supplies brand-licensing services to businesses, while Activity B sells frozen food for consumers to prepare… | no EEA overlap |
| T-4 Candied chestnuts | P4-3 Branded frozen foods | candidate | different product |  | A could be resold by B (AI) | 0.30 | Candied chestnuts are a specific sweet confectionery product, whereas the frozen-food ranges are described only as a br… |  |
| T-5 Chocolate and cocoa ingredien… | P4-7 Frozen meals, fish, vegetable… | candidate | similar product, possibly substitutable | ●○○ |  | 0.28 | Both are food products that can be used in preparing or eating food, but professional chocolate and cocoa ingredients a… | no EEA overlap |
| T-4 Candied chestnuts | P4-6 Frozen foods supplied to home… | candidate | different product |  | A could be resold by B (AI) | 0.26 | Candied chestnuts are confectionery for eating or gifting, while the disclosed frozen-food range includes products such… |  |
| T-4 Candied chestnuts | P4-4 Frozen foods for professional… | candidate | different product |  | A could be resold by B (AI) | 0.26 | Candied chestnuts are a finished confectionery product eaten as a sweet or given as a gift. The frozen-food range consi… |  |
| T-4 Candied chestnuts | P4-5 Frozen food supplied to indus… | unclear | not enough information |  |  | 0.30 | Candied chestnuts are finished confectionery for consumers, while B covers unspecified frozen products supplied for ind… |  |

<details><summary>79 pairs screened out</summary>

- T-1 Finished chocolate and chocolate c… ↔ P4-2 Customer-brand frozen foods (sim. 0.41): Chocolate confectionery is eaten as a sweet or given as a gift, while the frozen foods described in…
- T-1 Finished chocolate and chocolate c… ↔ P4-3 Branded frozen foods (sim. 0.45): Activity A is finished chocolate and chocolate confectionery for eating or gifting. Activity B is a…
- T-1 Finished chocolate and chocolate c… ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.43): Activity A consists of chocolate confectionery for eating or gifting. Activity B consists of assort…
- T-1 Finished chocolate and chocolate c… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.35): Chocolate confectionery is eaten as a sweet or used as a gift, while the frozen products are foods …
- T-1 Finished chocolate and chocolate c… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.31): Finished chocolate and chocolate confectionery are for consumers to eat or give as gifts, whereas f…
- T-1 Finished chocolate and chocolate c… ↔ P4-9 Product development and assortment… (sim. 0.42): A consists of finished chocolate products for consumers to eat or give as gifts. B is business-to-b…
- T-2 Retail sale of chocolate and confe… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.32): Chocolate and confectionery are bought to eat or give as gifts, while the frozen products are bough…
- T-2 Retail sale of chocolate and confe… ↔ P4-2 Customer-brand frozen foods (sim. 0.38): A sells chocolate and confectionery for consumers to eat or give as gifts, while B manufactures a r…
- T-2 Retail sale of chocolate and confe… ↔ P4-4 Frozen foods for professional kitc… (sim. 0.28): Chocolate and confectionery are sold for consumers to eat or give as gifts, while the frozen produc…
- T-2 Retail sale of chocolate and confe… ↔ P4-5 Frozen food supplied to industrial… (sim. 0.42): Activity A sells chocolate and confectionery for consumers to eat or give as gifts. Activity B supp…
- T-2 Retail sale of chocolate and confe… ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.43): Chocolate and confectionery are sold for eating or gifting, while the described frozen-food range c…
- T-2 Retail sale of chocolate and confe… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.28): Chocolate and confectionery are intended for consumers to eat or give as gifts, while frozen meals …
- T-2 Retail sale of chocolate and confe… ↔ P4-9 Product development and assortment… (sim. 0.37): Activity A sells chocolate and confectionery for consumers to eat or give as gifts. Activity B prov…
- T-2 Retail sale of chocolate and confe… ↔ P4-10 Non-food merchandise (sim. 0.43): A consists of chocolate and confectionery for eating or gifting. B consists of apparel, accessories…
- T-3 Non-chocolate sugar confectionery ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.30): Non-chocolate sugar confectionery consists of sweets eaten as treats or gifts, while frozen meals a…
- T-3 Non-chocolate sugar confectionery ↔ P4-2 Customer-brand frozen foods (sim. 0.29): A is finished non-chocolate sugar confectionery for eating or gifting. B comprises frozen meals and…
- T-3 Non-chocolate sugar confectionery ↔ P4-4 Frozen foods for professional kitc… (sim. 0.27): A consists of sweets intended to be eaten as confectionery or given as gifts, while B consists of f…
- T-3 Non-chocolate sugar confectionery ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.31): Non-chocolate sugar confectionery is eaten as candy or given as a gift, while the described product…
- T-3 Non-chocolate sugar confectionery ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.27): Non-chocolate sugar confectionery is eaten as sweets or given as gifts, while frozen meals and othe…
- T-3 Non-chocolate sugar confectionery ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.21): Non-chocolate sugar confectionery consists of sweets eaten as treats or gifts, while frozen meals a…
- T-3 Non-chocolate sugar confectionery ↔ P4-9 Product development and assortment… (sim. 0.30): A consists of finished sugar confectionery for consumers to eat or give as gifts. B is a business-t…
- T-3 Non-chocolate sugar confectionery ↔ P4-10 Non-food merchandise (sim. 0.38): Sugar confectionery is food eaten by consumers, whereas the merchandise consists of apparel, access…
- T-4 Candied chestnuts ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.31): Candied chestnuts are confectionery eaten as a sweet or given as a gift, while the other products a…
- T-4 Candied chestnuts ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.27): Candied chestnuts are confectionery intended to be eaten as a sweet or given as a gift. Frozen meal…
- T-4 Candied chestnuts ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.21): Candied chestnuts are confectionery eaten as a sweet or given as a gift, while frozen meals and mea…
- T-4 Candied chestnuts ↔ P4-9 Product development and assortment… (sim. 0.30): Candied chestnuts are finished confectionery for consumers to eat or give as gifts. Product develop…
- T-4 Candied chestnuts ↔ P4-10 Non-food merchandise (sim. 0.34): Candied chestnuts are confectionery eaten or given as food gifts. Apparel, accessories and househol…
- T-5 Chocolate and cocoa ingredients an… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.29): Professional chocolate and cocoa ingredients and confectionery coatings are used to prepare or coat…
- T-5 Chocolate and cocoa ingredients an… ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.33): A consists of chocolate and cocoa ingredients and confectionery coatings for preparing or coating f…
- T-5 Chocolate and cocoa ingredients an… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.27): A consists of chocolate and cocoa ingredients and confectionery coatings used to prepare or coat fo…
- T-5 Chocolate and cocoa ingredients an… ↔ P4-9 Product development and assortment… (sim. 0.38): A consists of finished chocolate and cocoa ingredients and coatings used to prepare or coat foods. …
- T-5 Chocolate and cocoa ingredients an… ↔ P4-10 Non-food merchandise (sim. 0.32): A consists of professional chocolate, cocoa and confectionery coating products used to prepare or c…
- T-6 Dessert and beverage sauces and be… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.38): A comprises sauces and beverage mixes used to prepare or top drinks and desserts, while B comprises…
- T-6 Dessert and beverage sauces and be… ↔ P4-4 Frozen foods for professional kitc… (sim. 0.40): A consists of sauces and beverage mixes used to flavour, top or prepare drinks and desserts. B cons…
- T-6 Dessert and beverage sauces and be… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.34): A comprises sauces and beverage mixes used to prepare or top drinks and desserts. B comprises froze…
- T-6 Dessert and beverage sauces and be… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.31): Activity A comprises sauces and mixes used to prepare or top drinks and desserts. Activity B compri…
- T-7 Café, beverage and dessert service ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.38): Activity A provides prepared drinks and desserts for immediate consumption at or away from café out…
- T-7 Café, beverage and dessert service ↔ P4-2 Customer-brand frozen foods (sim. 0.39): Activity A provides prepared café drinks and desserts for immediate consumption or takeaway, while …
- T-7 Café, beverage and dessert service ↔ P4-3 Branded frozen foods (sim. 0.38): Activity A provides prepared drinks and desserts for immediate consumption at or from café outlets.…
- T-7 Café, beverage and dessert service ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.37): A provides café drinks and desserts for consumption at or near the outlet, while B supplies frozen …
- T-7 Café, beverage and dessert service ↔ P4-9 Product development and assortment… (sim. 0.39): A provides prepared drinks and desserts for consumers to eat or drink, while B provides businesses …
- T-7 Café, beverage and dessert service ↔ P4-10 Non-food merchandise (sim. 0.37): Activity A provides prepared beverages and desserts for immediate consumption, while Activity B sel…
- T-8 Catering and café food service for… ↔ P4-9 Product development and assortment… (sim. 0.40): A provides prepared food and refreshments for consumption at events or a café. B provides business …
- T-8 Catering and café food service for… ↔ P4-10 Non-food merchandise (sim. 0.36): Activity A provides prepared food and refreshments for consumption at events or a café. Activity B …
- T-9 Liqueur ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.28): Bottled liqueur is an alcoholic drink intended for consumption or gifting, while B comprises frozen…
- T-9 Liqueur ↔ P4-2 Customer-brand frozen foods (sim. 0.31): Liqueur is an alcoholic drink intended for consumption or gifting, whereas B makes a range of froze…
- T-9 Liqueur ↔ P4-3 Branded frozen foods (sim. 0.36): Liqueur is an alcoholic drink intended for consumption or gifting, while the other activity covers …
- T-9 Liqueur ↔ P4-4 Frozen foods for professional kitc… (sim. 0.23): Liqueur is a bottled alcoholic drink intended for consumers to drink or give as a gift. The frozen …
- T-9 Liqueur ↔ P4-5 Frozen food supplied to industrial… (sim. 0.32): Branded bottled liqueurs are alcoholic drinks for consumers to drink or give as gifts. The frozen p…
- T-9 Liqueur ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.27): Liqueur is an alcoholic drink intended for consumption or gifting, while the listed frozen foods ar…
- T-9 Liqueur ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.22): Liqueur is an alcoholic drink for consumption or gifting, whereas the frozen products are foods pre…
- T-9 Liqueur ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.19): Bottled liqueur is an alcoholic drink intended for adult consumption or gifting, while B consists o…
- T-9 Liqueur ↔ P4-9 Product development and assortment… (sim. 0.32): A is a finished alcoholic beverage for adult consumers, while B is a business service providing pro…
- T-9 Liqueur ↔ P4-10 Non-food merchandise (sim. 0.39): Liqueur is an alcoholic drink intended for consumption, whereas the merchandise consists of wearabl…
- T-10 Foodservice accessories ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.30): Foodservice accessories are equipment used to dispense or organise sauces, while the other products…
- T-10 Foodservice accessories ↔ P4-2 Customer-brand frozen foods (sim. 0.31): Foodservice accessories dispense and organise sauces, while the other activity makes frozen foods f…
- T-10 Foodservice accessories ↔ P4-3 Branded frozen foods (sim. 0.33): Foodservice accessories are equipment for dispensing and organising sauces, while branded frozen fo…
- T-10 Foodservice accessories ↔ P4-4 Frozen foods for professional kitc… (sim. 0.42): Sauce-bottle pumps and racks dispense or organise sauces, while frozen foods are ingredients or pre…
- T-10 Foodservice accessories ↔ P4-5 Frozen food supplied to industrial… (sim. 0.38): Foodservice accessories are equipment for dispensing or organising sauces, whereas the frozen produ…
- T-10 Foodservice accessories ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.36): Sauce pumps and racks are foodservice equipment used to dispense and organise sauces, whereas the o…
- T-10 Foodservice accessories ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.28): Foodservice accessories dispense and organise sauces, while frozen meals and ingredients are food f…
- T-10 Foodservice accessories ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.30): Sauce pumps and racks are foodservice equipment used to dispense and organise sauces, while frozen …
- T-10 Foodservice accessories ↔ P4-9 Product development and assortment… (sim. 0.40): A consists of physical equipment for dispensing and organising sauces in professional foodservice s…
- T-11 Licensing of product brands ↔ P4-2 Customer-brand frozen foods (sim. 0.45): A is a brand-licensing service for businesses, while B is the development and manufacture of finish…
- T-11 Licensing of product brands ↔ P4-4 Frozen foods for professional kitc… (sim. 0.34): Activity A is a brand-licensing service for businesses, while Activity B consists of finished froze…
- T-11 Licensing of product brands ↔ P4-5 Frozen food supplied to industrial… (sim. 0.42): A is a licensing service that grants rights to produce or market branded goods, while B is a physic…
- T-11 Licensing of product brands ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.28): Activity A is a service granting rights to use product brands so licensees can produce or market br…
- T-11 Licensing of product brands ↔ P4-9 Product development and assortment… (sim. 0.43): Activity A grants brand rights so licensees can produce or market branded products. Activity B prov…
- T-11 Licensing of product brands ↔ P4-10 Non-food merchandise (sim. 0.47): Activity A is a business-to-business service granting rights to use product brands, while Activity …
- T-12 Property-related income and contra… ↔ P4-1 Branded frozen meals, fish, vegeta… (sim. 0.19): A comprises property-related income, administrative support and chocolate-making demonstrations; B …
- T-12 Property-related income and contra… ↔ P4-2 Customer-brand frozen foods (sim. 0.25): A consists of property-related income, administrative services, and chocolate-making demonstrations…
- T-12 Property-related income and contra… ↔ P4-3 Branded frozen foods (sim. 0.27): A covers property income, administrative services and chocolate-making demonstrations, while B cons…
- T-12 Property-related income and contra… ↔ P4-4 Frozen foods for professional kitc… (sim. 0.24): Activity A provides property-related income, administrative support and chocolate-making demonstrat…
- T-12 Property-related income and contra… ↔ P4-5 Frozen food supplied to industrial… (sim. 0.31): A consists of property-related income, administrative services and chocolate-making demonstrations.…
- T-12 Property-related income and contra… ↔ P4-6 Frozen foods supplied to home-deli… (sim. 0.26): A consists mainly of property income and administrative services, with contracted chocolate-making …
- T-12 Property-related income and contra… ↔ P4-7 Frozen meals, fish, vegetables and… (sim. 0.15): Activity A provides property, administrative and chocolate-demonstration services, while Activity B…
- T-12 Property-related income and contra… ↔ P4-8 Frozen meals and meal boxes for wo… (sim. 0.20): Activity A includes property income, administrative support and chocolate-making demonstrations; Ac…
- T-12 Property-related income and contra… ↔ P4-9 Product development and assortment… (sim. 0.29): A provides property-related arrangements, administrative support and contracted chocolate-making de…
- T-12 Property-related income and contra… ↔ P4-10 Non-food merchandise (sim. 0.30): Activity A comprises property income, administrative services and chocolate-making demonstrations; …

</details>

## Calibration: closest pairs that were screened out

If a benchmark overlap appears here, lower SIMILARITY_UNCLEAR in rules.py below its similarity.

- 0.49 · T-7 Café, beverage and dessert service ↔ P1-6 Chocolate-making workshops and educatio… (Ritter Sport)
- 0.49 · T-9 Liqueur ↔ P2-7 Professional beverage mixes and ingredi… (Barry Callebaut)
- 0.48 · T-2 Retail sale of chocolate and confection… ↔ P1-8 Non-food branded merchandise and gift i… (Ritter Sport)
- 0.48 · T-7 Café, beverage and dessert service ↔ P2-10 Professional chocolate education and tr… (Barry Callebaut)
- 0.48 · T-9 Liqueur ↔ P3-3 Packaged cakes (Bahlsen)
- 0.48 · T-1 Finished chocolate and chocolate confec… ↔ P3-6 Private-label product development and c… (Bahlsen)
- 0.47 · T-11 Licensing of product brands ↔ P3-5 Private-label biscuits, coffee pastries… (Bahlsen)
- 0.47 · T-11 Licensing of product brands ↔ P4-10 Non-food merchandise (FRoSTA)
- similarity of candidate pairs: min 0.22 · median 0.46 · max 0.85
- similarity of screened out pairs: min 0.15 · median 0.34 · max 0.49

## Example: exactly what the comparison call received

```
ACTIVITY A
Product: Finished chocolate and chocolate confectionery
Description: Bars, truffles, pralines, filled chocolates, boxed assortments, seasonal figures and gifts, spreads, and chocolate snacks. Products are sold through business channels and through the group's own shops and e-shops.
Intended use: For consumers to eat or give as gifts.
Main inputs: cocoa, sugar, milk, hazelnuts
Level of trade: finished products
Direct customers: retailers, wholesalers / distributors, consumers (Retail and wholesale customers, independent distributors, and consumers purchasing through group shops and e-shops.)
End users: consumers
Sales channels: Supermarkets, grocery retailers, club and discount retailers, third-party online retailers, wholesalers and distributors, group shops and e-shops, and airport/travel retail.
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

- names removed before any comparison: 85 name variants (list in the .json file)
- comparison calls blocked or failed: 0 (kept as 'unclear', never screened out)
- search: 5 calls (5 from cache) · tokens 0 in / 0 out · USD 0.0000
- extract: 5 calls (0 from cache) · tokens 31,153 in / 14,744 out · USD 0.0105
- embed: 5 calls (0 from cache) · tokens 3,015 in / 0 out · USD 0.0004
- compare: 456 calls (0 from cache) · tokens 355,074 in / 91,087 out · USD 0.0811
- total: USD 0.0920 (token costs only, without web search fees)
