---
name: |-
  deck-case-picker
description: |-
  Pick the Augusta case studies that make sense for a specific company, from the Case Study Tracker in Notion, and return them as a list of Notion pages with a one-line reason each. Use when a deck skill asks for N case studies for an angle (a deep-dive workflow, a company, an industry or a function); not for writing or placing the cards.
notion_page_id: 3e576b8e-5e31-819f-a1ba-ca2938a30da3
---

# deck-case-picker

Called by a deck skill. It gets how many case studies are needed and the angle. It researches the target, selects the cases and returns a list of Notion pages. No human step.

## Input

- count: how many case studies (e.g. 1 per deep dive, 4, 10)
- angle: what each pick has to prove, e.g.:
  - a company, such as "Acme, a PE-backed UK dental group, 40 clinics"
  - a deep-dive workflow at a company, such as "A1. Lead qualification at Acme"
  - an industry or a function, such as "Insurance brokerage" or "Finance function"
- exclude (optional): Notion pages already used in this deck

When the angle has one slot per pick (e.g. four deep dives), treat each slot as its own angle and pick one case per slot.

## Where the cases live

The Case Study Tracker in Notion. Read the `Case picker` view with notion-query-data-sources in view mode:

- view URL: `view://3e576b8e-5e31-81af-a656-000c92df6e02`
- page\_size 20, and follow `next_cursor` until `has_more` is false (about 80 rows, 4 calls). Larger pages overflow the tool's output limit.

Only rows with a case card appear in that view.

What each row gives you:

- Who the client is: Client, Client label, Type (Enterprise / PortCo / PE / Gov), Sector, PE-Owner
- What the work was: Business function, Value driver, Card · Title, Card · Challenge, Card · Solution, Card · Impact
- The result: Card · KPI
- The row's Notion page: `url`

## Steps

1. Understand the target. When the angle names a company, research it briefly (web search) until you know its industry, business model (who it sells to and what), size, region, and whether it is PE-backed. Use what the deck skill already passed on first.
2. Read every row in the view. Keep a short note per row: the client in a few words, the work, and the result.
3. Select, for each slot, the case that best passes the rules below.
4. Return the list.

## Rules for selecting

- Makes sense for this specific company. The client should read the case and think "that's us". In order of weight:
  1. closest industry
  2. similar business model and size
  3. work close to the angle's workflow or function

  <p>
  A case in the same sector doing unrelated work is weaker than a neighbouring sector doing the same work.
  </p>
- Judge by the card, not the tags. Card · Title, Challenge, Solution and Impact say what the work really was. Sector, Business function and Value driver are sometimes wrong or "Unclassified".
- Real results only. Pick only cases whose Project stage is done and whose KPI is a result.
  - Skip aborted, on pause and planned projects.
  - Skip KPIs marked "(Target)" or "Project Ongoing", unless nothing else fits; then say so in the reason.
- Each case once. Duplicate rows that share a `Card · Slot` are one case: return either URL.
- Different clients. Prefer a different client for every pick.
  - The same real company can appear under different names (e.g. "Decskill" and "Decskill (Astek Group)", "Bene" and "Bene (via 2Logical)"): treat them as one client.
  - Rows whose Client is `UNATTRIBUTABLE` are different clients unless their Client label and work show otherwise.
  - Two cases telling the same story for different clients count as a repeat: pick one.
  - Across slots, give a strong client to the slot where it fits best, then fill the others. Repeat a client only when the next best option for a slot is clearly weaker, and say so.
- Nothing from exclude.
- Prefer cases with a Card · Banner when two are close.
- Type fit, as a tie-breaker only:
  - for a PE fund's deck, prefer PortCo and PE cases
  - for a government body, prefer Gov cases
  - otherwise the company's own profile decides
- Anonymity. When `Anon?` is checked, the reason never names the real Client. Use the Client label.
- Never invent or change a case's numbers or text. You pick cases; you don't write them.
- If fewer good cases exist than asked, return the good ones and say how many are missing and why. A weak pick is worse than a missing one.

## Output

A numbered list, one line per pick, in slot order:

```txt
1. <Notion page url> — <Client label> · <Card · KPI> — <why it fits, one line>
```

For slot-based requests, start each line with the slot, e.g. `A1 · <url> — …`.

Then the runners-up, so the deck skill can swap one if needed:

```javascript
Runners-up: A1 — <url> (<Client label> · <KPI>); <url> (…) | A2 — …
```

For requests without slots, list up to 3 runners-up for the whole list.

If fewer good cases exist than asked, end with: `Missing: <n> — <why>`.
