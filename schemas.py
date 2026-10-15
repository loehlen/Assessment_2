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
from typing import Literal

from pydantic import BaseModel, Field

from rules import (DIRECT_CUSTOMER_TYPES, END_USERS, PRODUCT_RELATIONS, STATUS,
                   VALUE_CHAIN_LEVELS, VERTICAL_LINKS)

Level = Literal[tuple(VALUE_CHAIN_LEVELS)]
CustomerType = Literal[tuple(DIRECT_CUSTOMER_TYPES)]
EndUsers = Literal[tuple(END_USERS)]
Status = Literal[tuple(STATUS)]
ProductRelation = Literal[tuple(PRODUCT_RELATIONS)]
VerticalLink = Literal[tuple(VERTICAL_LINKS)]


# =============================================================== 1. search (one company per call)
def search_prompt(company, hint=""):
    who = f"{company} ({hint})" if hint else company
    return f"""Research the business activities of {who}, including all subsidiaries and brands that the group controls.

Start with the company's own website and its most recent annual report; then use other reliable sources.
Describe every activity, also those outside the company's main business, and for each:
- how the company itself presents and groups its activities (divisions, segments, business areas)
- the product or service, what it is used for and its main inputs or raw materials
- at which level of trade the company sells it (e.g. raw materials, ingredients for other producers,
  finished products, wholesale, own shops or online shop)
- who buys it directly from the company, and who finally uses it
- how it is sold (sales channels)
- in which countries it is sold, especially in the European Economic Area
- whether it is on the market or still in development
Also name the group companies and brands, and any partnership, supply or distribution agreement
with other companies that the sources mention.
Only report what the sources say; write "not stated" where they say nothing."""


# =============================================================== 2. extraction (one company per call)
EXTRACTION_INSTRUCTIONS = f"""You turn research notes about ONE company group into a structured list of its activities,
for the first step of a competition-law overlap analysis. Use only the research notes and the numbered sources given.

Granularity: one activity per plausible product market, at most about 10 per company. Split only by type of product
or service and by level of trade (e.g. the same product sold to retailers and in own shops = two activities).
Do not split by brand, flavour, pack size or individual product.

Fields:
- business_area: how the company itself groups this activity (division, segment), else "not stated".
- sector: the broad sector in plain words (e.g. "food", "frozen food", "real estate"). Only for sorting the overview.
- entity: the group company or brand the activity belongs to.
- brands: brand names used for this activity. Brand names go ONLY here.
- product, description, intended_use, customer_details, sales_channels: generic words, NO company or brand names,
  including the names of customers, suppliers, partners or retailers (write "a biscuit manufacturer", not its name).
  Describe what the product is, its key characteristics and, if stated, its price positioning; and what the direct
  customers use it for.
- main_inputs: the main raw materials or inputs, if stated or obvious from the description, else ["not stated"].
- value_chain_level: the company's own level of trade for this activity:
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
- Production for the group's own use is "internal use (captive)".
- Never adopt the company's own description of "its market" (e.g. "we compete in the global snacks market")
  as a market definition; describe the activity instead.
- Write "not stated" instead of guessing."""


class Activity(BaseModel):
    business_area: str = Field(description="How the company itself groups this activity, else 'not stated'")
    sector: str = Field(description="Broad sector in plain words, for sorting the overview only")
    entity: str = Field(description="Group company or brand the activity belongs to")
    brands: list[str] = Field(description="Brand names used for this activity (the only field with brand names)")
    product: str = Field(description="The product or service in generic words, no company or brand names")
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
    group_companies: list[str] = Field(description="Subsidiaries and brands of the group named in the notes")
    activities: list[Activity]


def extraction_input(company, notes, sources):
    numbered = "\n".join(f"[{s['n']}] {s['title']} - {s['url']}" for s in sources) or "(no sources returned)"
    return f"Company: {company}\n\nRESEARCH NOTES\n{notes}\n\nNUMBERED SOURCES\n{numbered}"


# =============================================================== 3. factual comparison (one anonymised pair per call)
COMPARISON_INSTRUCTIONS = """You support a competition lawyer with the first, factual step of an overlap screen.
You receive two business activities, A and B, described without company names. Compare them on the facts only.
Do not define markets and do not cite decisions; that is done in a later step.
An activity whose status is "in development" (a pipeline product) is compared like a product on the market.

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
Never mention a company or brand, even if you think you recognise the business."""


class Comparison(BaseModel):
    product_relation: ProductRelation
    product_reason: str
    vertical_links: list[VerticalLink]
    vertical_reason: str


def comparison_input(abstract_a, abstract_b):
    return f"ACTIVITY A\n{abstract_a}\n\nACTIVITY B\n{abstract_b}"