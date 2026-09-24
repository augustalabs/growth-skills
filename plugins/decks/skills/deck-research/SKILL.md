---
name: |-
  deck-research
description: |-
  How to research a company, a PE fund and its portfolio, or an industry for an Augusta deck. Latest information first, and only facts confirmed by a source, returned as a brief in a fixed format. Use when a deck skill asks for research; the deck skill decides what to research and how deep.
notion_page_id: 3e576b8e-5e31-8155-88a0-df7d19a15667
---

# deck-research

This skill is the how. The deck skill that calls it says what to research, meaning which sections of the brief below, and how deep. Research only what it asks for.

## The two rules

1. **Latest first.** Always look for the most recent information, and date everything.
   - The newest primary source wins over an older one.
   - Figures carry their period, e.g. "Revenue €412M (FY2025)". A figure without a period is not used.
   - Company pages, portfolio pages and annual reports go stale on exits, sales, mergers and leadership. Check recent news (last 12 months) before trusting them.
2. **Only what is certain.** Report a fact only when a source confirms it.
   - Every fact has its source (URL and date) right after it.
   - No estimates, no modelling, no "likely", no filling gaps with reasoning. A figure is reported only as the source states it.
   - Sources disagree? An organisation's own current page wins for its own basic facts (e.g. when a fund invested). For events and for facts that change over time (leadership, revenue, headcount), the newest dated statement wins over an older one. If that still doesn't settle it, leave the fact out.
   - Anything important you couldn't confirm goes under "Not confirmed" at the end, with what you found. It never goes into the brief itself.

## Where to look

Primary sources, which are the ones that count:

- the company's or fund's own site: about, investor relations, press, portfolio pages
- annual and interim reports, and results presentations
- company registries and filings: SEC EDGAR, Companies House (UK), CRO (Ireland), Portal da Justiça / Racius (Portugal), Registro Mercantil / Infoempresa (Spain), and the registry of the company's own country
- official press releases: the company's, the buyer's or seller's, and newswires (PR Newswire, GlobeNewswire, Business Wire)

What the company itself states also counts, when you open and read the article:

- figures and facts given by the company's CEO, CFO or spokesperson in an interview or official statement, as quoted by established press (e.g. Expansión, Jornal Económico, Jornal de Negócios, the FT, sector trade titles)
- government trade-agency profiles built with the company (e.g. AICEP Portugal Global, ICEX)

Mark these "(company statement, \<outlet>, \<date>)". Most of our clients are private and publish little, so this is often the only source for revenue, EBITDA, headcount and plans.

Established press can also confirm events (deals, exits, insolvencies, leadership changes), when you open and read the article.

Leads only, never a source: Crunchbase, PitchBook snippets, LinkedIn, Wikipedia, headcount and company-data sites, and any page you could not open. Confirm what they say elsewhere, or it goes to "Not confirmed".

Method:

- Web-search, then open the page: never report from a search snippet alone.
- If a site blocks you, try its press releases on a newswire or its filings in the registry.
- Never get past a login, a paywall or a CAPTCHA.
- Split large requests into parallel subagents, one per section, and give each these same rules.

## The brief

Write `<run>/research/<subject>.md`. Include only the sections the deck skill asked for, in this order, with these headings.

### Company profile

- Name: short brand name, and legal name
- Domain: the company's own website
- What it does: its products or services and segments, in plain words
- Business model: who it sells to (B2B, B2C, government), how it earns, and its channels
- Size: revenue, EBITDA, employees, sites or locations, each with its period
- Region: HQ and the countries where it operates
- Ownership: listed, family, PE-backed (which fund, since when) or public sector
- Recent events: M&A, new leadership, restructurings, big contracts, each dated, last 24 months

### Costs and operations

- Disclosed cost lines and headcount, with their periods
- How the business runs: sites, channels, operations, and any systems or technology it names publicly
- Named competitors and peers

### Fund profile

- Name, domain, HQ
- Strategy: buyout or growth, deal size, geographies
- Sector focus: the sectors it invests in, and its **dominant sector**, meaning where most current holdings sit
  - Group holdings into broad sectors before counting (Healthcare, Consumer, Industrials, Technology & Software, Financial Services, Business Services, Energy & Infrastructure, Media, Real Estate). State the grouping you used.

### Portfolio today

One row per company the fund **currently** owns:

| Company | Domain | Sector | What it does | Owned since | Confirmed current (source, date) |
| --- | --- | --- | --- | --- | --- |

- Start from the fund's current portfolio page, then search each company's news for the last 12 months.
- Current means both:
  - the fund lists it as a current holding
  - no exit, sale, insolvency or merger appears in that news
- The fund's page alone is not enough. Pages stay stale for months (e.g. a company shown "In portfolio" while it was insolvent and being sold).
- Minority stakes count as owned. Write the stake in "What it does", e.g. "(minority, 25%)".
- An open sale process (a mandate, advisers hired, bidders) still counts as owned. Add "sale process under way" with its source.
- A signed or announced sale that hasn't closed goes under "Not confirmed" as "being sold to X, closing expected \<date>".
- Sold, exited, insolvent or unclear: "Not confirmed", with what you found.

### Industry

- What defines the industry, its main segments and its main players, with sources
- Recent shifts in the last 24 months that the sources state, not your own view

### Not confirmed

- Everything important you looked for but couldn't confirm, and why (not found, sources disagree, possibly outdated)

### Sources

- Every source used: URL, title, date
