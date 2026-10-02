---
name: |-
  case-file-builder
description: |-
  Build the Case File (.md) for one Augusta project from its linked GitHub repos, following the Case Studies Gold Standard: fourteen sections, every fact sourced and dated, empty fields left empty and turned into asks. Use when asked to build, refresh or check the case file of a row in the Project Tracker; not for writing slides, cards or any case-study format, which are generated from the file later.
notion_page_id: 3ed76b8e-5e31-81c7-a61e-ee738f9c8c1d
---

# case-file-builder

Takes one row of the Project Tracker and produces one Case File: a single markdown file that records everything the project's repos say about what happened, in the Gold Standard structure. The Quarter, Half, One-pager and Flagship case-study formats are later read from this file. None of them is written here.

The spec is the Notion page "Case Studies New Gold Standard Format" (Pedro's Corner / Deck OS). This skill is that page turned into a procedure. Where they disagree, the Notion page wins; say so in your return summary.

## Input

One Project Tracker row:

- the row's Notion page URL
- Client, Client label, Type, Sector, Business function, Value driver, Engagement owner, Project stage, Case study title, Attio deal
- `Brain repo` (the main repo) and `Other repos`
- an existing case file, when this is a refresh

If the row has no repo at all, stop and return "no sources".

## Output

1. One file, `<slug>.md`, built on `references/case-file-template.md`.
2. The status summary block defined in `references/routing-gates.md`.
3. A short return note: verdict, what filled well, what is empty, the top five asks, and anything that made you unsure.

You do not write to Notion, GitHub or Slack. The caller reviews the file and updates the tracker.

## The rules

These come from the Gold Standard and are not negotiable.

1. **No source, no fact.** Every fact carries its source id and its as-of date. A fact you cannot point at in the repos is not written. The only other source is the tracker row, for classification fields.
2. **Filled or empty.** A number is filled only with value, period, as-of date and source together. Anything less is empty. No inference, no derived figures, no conversions, no placeholders, no "approximately" to cover a guess.
3. **Empty stays silent.** An empty field is blank in the body. The prose never mentions what is missing and never hedges around it. Gaps appear only in section 12 (status) and section 14 (asks).
4. **Section 6 is the record of truth for every number.** Sections 2.4, 8 and the front matter point at section 6 and never restate or recompute it.
5. **Coverage is computed, never typed.** Section 12 is derived from which fields are filled. Section 14 is derived from section 12.
6. **Real names are stored.** Redaction happens at output, not here. If no permission is recorded in the sources, leave every `permissions` key blank: that means fully anonymised, no quote.
7. **Quotes are verbatim**, in the original language, with who said it, their role and where it came from.
8. **The fee is stored, never output.** Record it in 8.3 only when a source states it as the contracted fee (SOW, signed proposal, invoice). A CRM deal value is not a fee.
9. **A target is not a result.** Figures from proposals, business cases or plans never fill an `after` state. They can fill a modelled value only when the source is a named model with stated assumptions, graded `modelled`.
10. **Client framing stays the client's.** 8.9 EBITDA holds the client's own words and figure, verbatim, or it is empty.
11. <b>Every write bumps </b>**`last_updated`** on the file and on the section touched.

## Decisions already made

| Question | Answer |
| --- | --- |
| One file per what | Per tracker row, not per client. |
| Language | English prose. Verbatim excerpts and quotes stay in the original language. |
| 1.4 title | The tracker's `Case study title` when it holds a real title; otherwise empty. Ignore placeholder values such as "\[use case TBD\]" or "(none …)". |
| Sector, business function, value driver, owner | From the tracker row, cited as the tracker source. Use the tracker's option names exactly. "Unclassified" and "Not selected" count as empty. |
| Calls | The transcript is the source. A Fireflies summary is cited only when no transcript exists, typed `call-summary`. |
| Weeks | Only if a source states the number of weeks. Never computed from start and end dates. |
| id and slug | `<client>-<short-project>` in kebab-case, lower case, ASCII. Set once; never change it on a refresh. |
| Refresh | Update the existing file in place. Section 13 is append-only: add sources, never rewrite or delete an excerpt. |
| Asks | List all. Order by what they unlock. Mark the top five `send: true`. |

## Procedure

1. **Read the references.** `references/case-file-structure.md` (every key and its rule), `references/extraction-table.md` (what to look for, with examples), `references/routing-gates.md`, `references/source-guide.md`.
2. **Inventory the sources.** List the full file tree of every linked repo. Note what exists: calls, emails, plans, documents, imports, code, deal record. Work out which material is about this row's project and which is sales, another project, or noise.
3. **Read.** All call summaries first, to map the engagement over time. Then the transcripts, documents and emails that carry mandate, process, numbers, results, technical choices, quotes and permissions. Then code READMEs for section 9. Do not stop at summaries.
4. **Register sources.** Give every file you will cite an id and add it to the front matter with type, date, author and path.
5. **Extract.** Walk the extraction table row by row. For each row, either record the value with its source and date, or leave it empty. Copy the verbatim passage behind every number and quote into section 13 as you go.
6. **Decide the shape.** `transformation` only when the sources show workflows mapped across an estate and grouped into initiatives. Otherwise `single-workflow`, and section 7 is n/a.
7. **Write sections 1 to 11** on the template. Plain prose for narrative fields, the YAML blocks for structured ones. Each sentence and each value ends with `[S<n>, YYYY-MM-DD]`.
8. **Generate section 12** using the definitions in `routing-gates.md`: status per section, formats, verdict, next unlock, headline grades. Mirror coverage, verdict and headline grades into the front matter.
9. **Generate section 13.xref and section 14.** One ask per empty applicable field.
10. **Check the file** against the list below, then return the three outputs.

## Check before returning

- Every heading and key from the template is present, in order.
- No sentence or value in sections 1 to 11 lacks a source id and date.
- Every source id used in the body exists in the front matter and in section 13.
- No number appears in sections 2, 8 or the front matter that is not in section 6.
- Every `delta` has a filled `before` and `after` in the same unit and period.
- 8.2 equals the sum of 6.n.value.annual, or 8.2 is empty.
- No placeholder text, no gap markers, no mention of missing data in sections 1 to 11.
- Section 12 statuses match the body. The verdict is the highest gate actually passed.
- Section 14 has one entry per empty applicable field, and at most five marked `send: true`.
- The fee, if recorded, appears only in 8.3.

## When the sources are thin

Do the same thing. A project whose repos hold only sales emails produces a file with front matter, a source register, mostly blank sections, verdict `none` and a long list of asks. That file is correct. Do not pad it, and do not lower the bar to make it look fuller. Say "dump needed" in the return note.

## What not to do

- Do not use the tracker's `Card ·` columns, the web, or what you know about the client.
- Do not turn "saves around 70%" into a filled figure. Without a baseline, a period and a date it is empty; the verbatim line goes in section 13 and becomes an ask.
- Do not write to any repo, to Notion, or to Slack.
- Do not produce slides, cards or summaries of the case. Only the file.
