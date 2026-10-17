"""
schemas.py - the data schemas and prompts of the generic overlap screen.

The legal concepts of the screen live in these schemas (field descriptions and fixed answer lists):
what counts as an activity, a level of trade, a direct customer, a vertical link. They are
sector-neutral; the answer lists themselves come from rules.py, so code and AI use the same terms.

Three AI tasks:
  1. SEARCH       one company per call, web search, prose with cited links
  2. EXTRACTION   one company per call, prose -> structured activity list (ActivityList)
  3. COMPARISON   one anonymised pair of activities per call, no names (Comparison)
"""
import json
from typing import Literal

from pydantic import BaseModel, Field

from rules import (CATEGORIES, DIRECT_CUSTOMER_TYPES, END_USERS, MAX_MAIN, PRODUCT_RELATIONS, STATUS,
                   VALUE_CHAIN_LEVELS, VERTICAL_LINKS)

Level = Literal[tuple(VALUE_CHAIN_LEVELS)]
CustomerType = Literal[tuple(DIRECT_CUSTOMER_TYPES)]
EndUsers = Literal[tuple(END_USERS)]
Status = Literal[tuple(STATUS)]
Category = Literal[tuple(CATEGORIES)]
ProductRelation = Literal[tuple(PRODUCT_RELATIONS)]
VerticalLink = Literal[tuple(VERTICAL_LINKS)]


# =============================================================== 1. search (one company per call)
SOURCE_RULES = """Use only publicly available sources: pages that anyone can open without logging in, paying or getting around an
access restriction. Do not try to reach password-protected, paywalled, internal, confidential or leaked material, and
do not use cached or mirrored copies of such material.
Prefer sources in this order: the company's own websites, annual and sustainability reports and press releases;
official registers and filings; established news and trade media. Use business directories and data aggregators only
for a fact that no better source gives, and say that the fact comes from such a site."""

GAP_RULE = """Only report what the sources say; write "not stated" where they say nothing. If the public sources say little or
nothing about the company, say so and stop: a gap is an acceptable answer, a guess is not."""


def _who_and_start(company, hint, website):
    who = f"{company} ({hint})" if hint else company
    if website:
        who += f", whose own website is {website}"
        start = (f"Start with the company's own website ({website}) and its most recent annual report. The website "
                 "identifies the company: ignore other companies with similar names.")
    else:
        start = ("Start with the company's own website and its most recent annual report. Ignore other companies with "
                 "similar names.")
    return who, start


def search_prompt(company, hint="", website=""):
    """Search 1 (main business). Since 17 Oct each company is searched twice, in parallel and in separate calls: this
    search covers the business as the company presents it, search 2 (search_prompt_beyond) what such a search easily
    misses. Both contain only this one company's name (the guard checks it)."""
    who, start = _who_and_start(company, hint, website)
    return f"""Research the business activities of {who}, including all subsidiaries and brands that the group controls.

{SOURCE_RULES}
{start}
Describe every activity, also those outside the company's main business, and for each:
- how the company itself presents and groups its activities (divisions, segments, business areas)
- the product or service, what it is used for and its main inputs or raw materials
- at which level of trade the company sells it (e.g. raw materials, ingredients for other producers,
  finished products, wholesale, own shops or online shop)
- who buys it directly from the company, and who finally uses it
- how it is sold (sales channels)
- in which countries it is sold, especially in the European Economic Area
- whether it is on the market or still in development
Also state where the group is headquartered (city and country) and who owns it, and give every figure (revenue,
employees) with its year or reporting period and its source.
Name the group companies and brands, and any partnership, supply or distribution agreement with other companies
that the sources mention.
{GAP_RULE}"""


def search_prompt_beyond(company, hint="", website=""):
    """Search 2 (added 17 Oct, Linda: Luna with a double search): the same company, a complementary focus. The live
    test of 17 Oct showed that one search finds the core reliably but misses side lines from run to run (e.g. a
    drinks brand, cafes, sales to businesses, private label). Sector-neutral: it names kinds of activity, not
    products."""
    who, start = _who_and_start(company, hint, website)
    return f"""Research {who}. A separate search already covers the company's main business as it presents it. This search
looks for the activities that such a search easily misses, including those of subsidiaries and brands that the group
controls.

{SOURCE_RULES}
{start} Then look specifically for:
- smaller brands and product lines, brands the group owns but presents separately, recent launches and acquisitions
- sales to other businesses: ingredients, components or products for other manufacturers; products for professional,
  foodservice, hospitality or industrial customers; private-label or contract manufacturing for retailers or others
- own retail and hospitality: own shops, outlets, cafes, restaurants, visitor centres, online shops
- side businesses offered to third parties, e.g. licensing, services, energy, property, logistics, training
- joint ventures, partnerships, supply or distribution agreements with other companies
- activities still in development
For each activity found, describe the product or service and what it is used for, the level of trade at which the
company sells it, who buys it directly and who finally uses it, how it is sold, in which countries (especially in the
European Economic Area), and whether it is on the market or still in development.
Also state where the group is headquartered (city and country), and give every figure with its year and source.
{GAP_RULE}"""


# =============================================================== 2. extraction (one company per call)
EXTRACTION_INSTRUCTIONS = f"""You turn research notes about ONE company group into (1) a short company profile and
(2) a structured list of its activities, for the first step of a competition-law overlap analysis.
Use only the research notes and the numbered sources given. The notes may come from two searches about the same
company (its main business, and what lies beyond it): combine them, and never list the same activity twice.

COMPANY PROFILE (company_profile): 2-3 factual sentences, the way the company would introduce itself: who it is,
where it is based (city and country), who owns it or which group it belongs to, and its main business areas; revenue
and number of employees only if the notes state them, always with their year or reporting period (e.g. "sales of
EUR 712 million in 2025"). If two sources give different figures, give the most recent one with its year. Names are allowed here. Do not repeat claims about its
market position or "its market" (e.g. "a leading player in the global snacks market"); say what it does.
profile_source_numbers: the sources used for the profile.

ACTIVITIES: work in two steps.

Step 1, form the lines. One line = one BUSINESS AREA of the company at one level of trade: what a lawyer would write
as one line of a first overview. Start from how the company presents and groups its business (divisions, segments,
the sections of its website); ignore purely geographic segments.
Split a business area ONLY when its level of trade differs, into these groups:
  (1) inputs for other producers (raw materials, ingredients, semi-finished or intermediate products);
  (2) goods made for resale or for business use (sold to retailers, wholesalers, foodservice or other businesses);
  (3) own retail and hospitality (own shops, outlets, own online shop, cafes, restaurants, catering);
  (4) other services;
and keep a product that is still in development as its own line. Wholesale of goods made by others is also its own
line.
Do NOT split by type of product: different products of one business area at one level of trade are ONE line, and
every product type goes into "includes" (e.g. one line "paints and coatings" at the level "finished products" with
includes "interior wall paint, exterior paint, varnishes, wood stains, trade packs"). Also merge brands, product lines, formats,
channels, customer groups (branded, private label, corporate gifts), countries and group companies doing the same
thing (name them all in "entity"). When unsure whether two lines belong together, MERGE them.
"includes" must list every product type, format and customer group covered, in generic words, so that nothing is
lost by merging.

Step 2, categorise each line on its own, after the lines are formed:
- "main": the company offers it to customers as a business in its own right.
- "other": (a) it is not offered on the market at all, i.e. production or services only for the group's own use
  (direct customer "internal use (captive)"); or (b) it is offered to third parties only as a side line that exists
  to support or promote the company's main business.
The size of an activity is never a reason for "other". A line never combines activities of different levels of
trade or of different categories. AT MOST {MAX_MAIN} "main" lines per company. List each "other" line separately;
code combines them into one line.
category_reason: one short sentence applying this definition.

Fields:
- business_area: how the company itself groups this activity (division, segment), else "not stated".
- sector: the broad sector in plain words (e.g. "food", "frozen food", "real estate"). Only for sorting the overview.
- entity: the group companies or brands that carry this activity (comma-separated).
- brands: brand names used for this activity. Brand names go ONLY here (and in the company profile).
- product: a short generic name of WHAT the business area offers, i.e. the product or service and, where helpful,
  its use (e.g. "paints and coatings", "frozen ready meals and vegetables", "cocoa powder and cocoa butter"). Do NOT
  put the buyers or the channel into the name (no "sold to businesses", "supplied to the trade", "for retailers"):
  the level of trade and the direct customers are separate fields and are shown next to the name. Only own retail
  and hospitality may say so in the name (e.g. "own shops and cafes for chocolate"). If the same products appear at
  two levels of trade, the two names may be alike; the level tells them apart.
- A brand, business or group company that the notes name without saying what it offers: do not guess a product.
  List it as its own line with product "not stated", includes [], its name in "brands" or "entity", and
  description "The sources name it but do not say what it offers." Code shows it as a question for the company.
- includes: every product type, format and customer group covered, in generic words (e.g. "interior wall paint",
  "varnishes", "trade packs", "private label", "corporate gifts"), else [].
- product, includes, description, intended_use, customer_details, sales_channels: generic words, NO company or brand
  names, including the names of customers, suppliers, partners or retailers (write "a biscuit manufacturer", not its
  name). Describe what the products are, their key characteristics and, if stated, their price positioning; and what
  the direct customers use them for.
- main_inputs: the main raw materials or inputs, if stated or obvious from the description, else ["not stated"].
- value_chain_level: the company's own level of trade for this activity (own retail and hospitality = "retail"):
  {"; ".join(f"{k} = {v}" for k, v in VALUE_CHAIN_LEVELS.items())}.
- direct_customers: who buys directly FROM THE COMPANY, at its own level of trade (not the end consumer of a
  product sold through shops): {"; ".join(f"{k} = {v}" for k, v in DIRECT_CUSTOMER_TYPES.items())}.
- customer_details: specifics the list cannot express (e.g. "bakeries and confectioners", "travel retail",
  "hotels and restaurants"), without naming individual customers, else "not stated".
- end_users, sales_channels, countries_of_sale ("not stated" if the sources give none), status.
- source_numbers: only numbers from the numbered source list; evidence: a short quote or paraphrase.
- group_companies: subsidiaries and brands of the group named in the notes.

Rules:
- Ignore information about other companies with similar names.
- Never adopt the company's own description of "its market" (e.g. "we compete in the global snacks market")
  as a market definition; describe the activity instead.
- Write "not stated" instead of guessing."""


class Activity(BaseModel):
    business_area: str = Field(description="How the company itself groups this activity, else 'not stated'")
    sector: str = Field(description="Broad sector in plain words, for sorting the overview only")
    entity: str = Field(description="Group companies or brands that carry this activity, comma-separated")
    brands: list[str] = Field(description="Brand names used for this activity (the only field with brand names)")
    category: Category = Field(description="main: offered as a business in its own right; other: own use only, or a "
                                           "side line that supports or promotes the main business")
    category_reason: str = Field(description="One short sentence why main or secondary")
    product: str = Field(description="Short generic name of what the business area offers (product or service); no "
                                     "buyers or channel in the name; no names; 'not stated' if the sources do not say")
    includes: list[str] = Field(description="Every product type, format and customer group covered; generic words")
    description: str = Field(description="What it is, key characteristics, price positioning if stated; no names")
    intended_use: str = Field(description="What the direct customers use it for; no names")
    main_inputs: list[str] = Field(description="Main raw materials or inputs, or ['not stated']")
    value_chain_level: Level
    direct_customers: list[CustomerType] = Field(description="Who buys directly from the company, at its own level of trade")
    customer_details: str = Field(description="Specifics the customer list cannot express, else 'not stated'")
    end_users: EndUsers
    sales_channels: str
    countries_of_sale: list[str] = Field(description="Countries named in the sources, or ['not stated']")
    status: Status
    source_numbers: list[int] = Field(description="Only numbers from the numbered source list")
    evidence: str = Field(description="Short quote or paraphrase from the sources")


class ActivityList(BaseModel):
    company_profile: str = Field(description="2-3 factual sentences introducing the company group; names allowed")
    profile_source_numbers: list[int] = Field(description="Only numbers from the numbered source list")
    group_companies: list[str] = Field(description="Subsidiaries and brands of the group named in the notes")
    activities: list[Activity]


class ActivityGroup(BaseModel):
    activities: list[Activity]


CONSOLIDATION_INSTRUCTIONS = f"""You receive the main activities of ONE company group, extracted for the first overview of a
competition-law overlap screen. There are more than {MAX_MAIN}. Merge them into AT MOST {MAX_MAIN} main activities.
One activity = one business area of the company at one level of trade. Its product name says what it offers, never
who buys it ("cocoa powder and cocoa butter", not "cocoa products sold to businesses"). Split ONLY by level of trade: (1) inputs for
other producers, (2) goods made for resale or business use, (3) own retail and hospitality, (4) other services;
keep a product in development separate. Merge everything else; when unsure, merge.
When you merge lines: give a product name that covers all of them; "includes" keeps every item of the merged lines,
including their former product names; combine description, intended_use, main_inputs, direct_customers,
customer_details, sales_channels and countries_of_sale; source_numbers is the union; evidence is a short combination.
Keep every field rule: no company, brand, customer or supplier names except in "brands" and "entity".
Return only the merged main activities, with category "main"."""


def consolidation_input(company, activities):
    keep = set(Activity.model_fields)
    return f"Company: {company}\n\nMAIN ACTIVITIES (JSON)\n" + json.dumps(
        [{k: v for k, v in a.items() if k in keep} for a in activities], ensure_ascii=False, indent=1)


def extraction_input(company, notes, sources):
    numbered = "\n".join(f"[{s['n']}] {s['title']} - {s['url']}" for s in sources) or "(no sources returned)"
    return f"Company: {company}\n\nRESEARCH NOTES\n{notes}\n\nNUMBERED SOURCES\n{numbered}"


# =============================================================== 3. factual comparison (one anonymised pair per call)
COMPARISON_INSTRUCTIONS = """You support a competition lawyer with the first, factual step of an overlap screen.
You receive two business activities, A and B, described without company names. Compare them on the facts only.
Do not define markets and do not cite decisions; that is done in a later step.
An activity whose status is "in development" (a pipeline product) is compared like a product on the market.
Each activity names its products in the line "Product" and in the list "Includes", whose items are separated by
semicolons. These are its ITEMS.

1. product_relation: compare WHAT the products are, from the point of view of the customers who buy them:
   characteristics, intended use (function) and price positioning. Ignore who the direct customers are and at
   which level of trade the products are sold; that is compared separately.
   - "same product": the same type of product or service, even if sold at a different level of trade,
     in a different form (e.g. in bulk v in consumer packs) or to different customers.
   - "similar product, possibly substitutable": a different product that customers could plausibly use for the
     same specific purpose or switch to, even if only partly or only in one direction.
   - "different product": customers would not use one instead of the other.
   - "not enough information": the descriptions do not allow a comparison.
   Belonging to the same broad category (e.g. both are food, both are consumer goods, both are services) is not
   enough for "similar product". If in doubt between two labels, choose the one closer to "same product".
2. vertical_links: two activities are vertically related when one is active in a market upstream or downstream of
   the market of the other: it supplies an input for the other's type of product, or it distributes or resells the
   other's type of product. Judge this at the level of the TYPE of product or service, not the actual relationship
   between the two businesses: a link exists even if B does not buy from A today. "Product" includes services and
   technologies. Return an empty list if no link is supported.
   - "A could be an input for B": A's good or service is used to make or supply products or services of B's type,
     e.g. a raw material, ingredient, component, semi-finished product, by-product or recycled material, packaging,
     manufacturing or processing carried out for others, logistics, software, data, or rights and technology needed
     to make B's product. Supported if A's product appears among B's main inputs, if products of B's type are made
     or supplied with it, or if A's product would do the same job as one of B's main inputs. Links over several
     levels of the value chain count too; call them "indirect" in vertical_reason.
     Rights (e.g. brand or technology licences) and general business services (e.g. consulting, advice,
     administration, financing, property) are inputs only if the descriptions show that products of B's type are
     made or sold with them (e.g. B makes products under licence); that any business could use them is not enough.
   - "B could be an input for A": the reverse.
   - "A could be resold by B": B is active in wholesale, distribution or retail of goods of A's type, including
     shops that sell only their own goods of that type.
   - "B could be resold by A": the reverse.
   Not vertical links: products used together or bought together by the same customers (complements, ranges);
   a shared broad category; selling one's own products to retailers or wholesalers, which is not itself wholesale
   or retail activity; a connection that is merely theoretical, i.e. supported neither by the descriptions nor by
   how products of that type are made, supplied or distributed.
3. product_reason and vertical_reason: one or two factual sentences each. In vertical_reason, name the part of
   the descriptions (main inputs, product, range) that supports each link, or say why there is none.
4. matching_items_a and matching_items_b: if product_relation is "same product" or "similar product, possibly
   substitutable", the items of A and the items of B that meet, i.e. that are the same or that customers could use
   instead of each other. Otherwise two empty lists.
5. vertical_items: one entry for each link in vertical_links, with the items of A and the items of B that the link
   concerns (what is supplied or resold, and the activity that uses or resells it).
   In 4 and 5, copy each item exactly as it is written: the text of the line "Product", or one entry of "Includes"
   (the text between two semicolons). Do not reword items and do not list items that do not meet.
Never mention a company or brand, even if you think you recognise the business."""


class VerticalItems(BaseModel):
    link: VerticalLink
    items_a: list[str] = Field(description="Items of A this link concerns, copied exactly from Product or Includes")
    items_b: list[str] = Field(description="Items of B this link concerns, copied exactly from Product or Includes")


class Comparison(BaseModel):
    product_relation: ProductRelation
    product_reason: str
    # added 16 Oct (option C): which items meet, so the assessment can say "with regard to ..." (checked in code)
    matching_items_a: list[str] = Field(description="Items of A that meet items of B (same or similar product), "
                                                    "copied exactly; else []")
    matching_items_b: list[str] = Field(description="Items of B that meet items of A, copied exactly; else []")
    vertical_links: list[VerticalLink]
    vertical_items: list[VerticalItems] = Field(description="One entry per link in vertical_links")
    vertical_reason: str


def comparison_input(abstract_a, abstract_b):
    return f"ACTIVITY A\n{abstract_a}\n\nACTIVITY B\n{abstract_b}"