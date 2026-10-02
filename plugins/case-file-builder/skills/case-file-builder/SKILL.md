---
name: |-
  case-file-builder
description: |-
  Build the Case File (.md) for one Augusta project from its linked GitHub repos and Fireflies calls, in the Case Studies Gold Standard structure: fourteen sections, every fact sourced and dated, every stated figure recorded and graded, empty fields left empty and turned into asks. Use when asked to build, refresh or check the case file of a row in the Project Tracker; not for writing slides, cards or any case-study format, which are generated from the file later.
notion_page_id: 3ed76b8e-5e31-81c7-a61e-ee738f9c8c1d
---

# case-file-builder

Takes one row of the Project Tracker and produces one Case File: a single markdown file that records everything the project's repos and call recordings say about what happened, in the Gold Standard structure. The Quarter, Half, One-pager and Flagship case-study formats are later read from this file. None of them is written here.

The spec is the Notion page "Case Studies New Gold Standard Format" (Pedro's Corner / Deck OS). This skill is that page turned into a procedure, with adjustments agreed after piloting it on real projects. Where the two differ, this skill wins. The deliberate differences are: a figure the project's own sources state counts as filled and is graded `estimated` when it was not formally measured; stated ratios and model-versus-baseline comparisons count as impact figures; other sourced figures are kept in 8.12 supporting metrics; classification values and titles may be proposed from the sources; `delivery_status` is recorded; Fireflies is a source.

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

You do not write to Notion, GitHub, Slack or Fireflies. The caller reviews the file and updates the tracker.

## The rules

These come from the Gold Standard, adjusted after the pilot. Follow them as written.

1. **No source, no fact.** Every fact carries its source id and its as-of date. A fact you cannot point at in the linked repos or in a Fireflies call about this project is not written. The only other source is the tracker row, for classification fields.
2. **Filled or empty.** A number is filled when the sources state it: value, source and as-of date together. Record the period and volume whenever the source gives them. A number the project's own material states (a steerco deck, a status email, a call) counts even without a formal measurement window; it is filled and graded `estimated`. What you may never do is supply a number the sources do not state: no inference, no unit conversions, no assumed rates or volumes, no placeholders, no "approximately" to cover a guess. Simple arithmetic on two sourced numbers is allowed (see Decisions).
3. **Empty stays silent.** An empty field is blank in the body. The prose never mentions what is missing and never hedges around it. Gaps appear only in section 12 (status) and section 14 (asks).
4. **Section 6 is the record of truth for every number.** Sections 2.4, 8 and the front matter point at section 6 and never restate or recompute it.
5. **Coverage is computed, never typed.** Section 12 is derived from which fields are filled. Section 14 is derived from section 12.
6. **Real names are stored.** Redaction happens at output, not here. If no permission is recorded in the sources, leave every `permissions` key blank: that means fully anonymised, no quote.
7. **Quotes are verbatim**, in the original language, with who said it, their role and where it came from. 10.1 takes a client statement about the delivered work or its results; a pre-sale statement about a proposal does not fill it.
8. **The fee is stored, never output.** Record it in 8.3 only when a source states it as the contracted fee (signed SOW, signed proposal, invoice). A CRM deal value is not a fee. Price lines never go in section 13: cut them from an excerpt and mark the cut with `[…]` (the one exception to append-only). Note in the return note where they were seen. A project with several phases records one fee line per phase.
9. **A target is not a result.** Figures from proposals, business cases or plans never fill an `after` state. They can fill a modelled value only when the source is a named model with stated assumptions, graded `modelled`. Planned engagement values (weeks, modules, gates from a proposal) may fill `engagement.*` only with `(planned)` after the value.
10. **Use every sourced number.** A sourced figure that is not a before/after pair (an accuracy score, minutes saved per day, share of cases handled) goes in 8.12 supporting metrics, in the body, not only in the evidence appendix.
11. **Drafts are drafts.** An unsigned or draft contract or SOW can supply mandate wording (4.1), labelled as a draft. It never fills the fee or permissions.
12. **Never copy secrets.** Passwords, access codes and tokens found in sources are never written into the file. Mention in the return note that they exist and where.
13. **Client framing stays the client's.** 8.9 EBITDA holds the client's own words and figure, verbatim, or it is empty.
14. <b>Every write bumps </b>**`last_updated`** on the file and on the section touched.

## Decisions already made

| Question | Answer |
| --- | --- |
| One file per what | Per tracker row, not per client. |
| Language | English prose. Verbatim excerpts and quotes stay in the original language. |
| 1.4 title | The tracker's `Case study title` when it holds a real title. When it is empty or a placeholder ("\[use case TBD\]", "(none …)"), write a title from the sources (the SOW or steerco title, or a plain description of what was built) followed by `(proposed)`, with its source. |
| Sector, business function, value driver, owner | From the tracker row, cited as the tracker source. When the tracker value is "Unclassified", "Not selected" or blank, choose the option the sources support, from the lists below, followed by `(proposed)` and the source it rests on. A proposed value counts as filled. List every proposed value in the return note so the tracker can be updated. Owner is never proposed. |
| Sector options | Healthcare, Financial, SaaS, Consumer, Services, Media, Industrials, Technology, Energy & Utilities, Infrastructure, Retail, Other |
| Business function options | Sales & Marketing, IT & Engineering, Customer Service, HR & Talent, Finance, Product & R&D, Procurement & Supply Chain, Legal & Compliance, Operations, Strategy & Planning. The function is the organisational unit the work sat in, not the use case. |
| Value driver options | Decision Quality, Productivity Uplift, Topline Expansion, Customer Experience & Retention, Operational Efficiency, Speed-to-Market |
| Before/after pairs | Every pair the sources state becomes a section 6 entry with its 8.1 figure: same thing measured by hand and with the solution, in the same unit (e.g. "6 h 39 by hand against 1 h 09 with the agent"). A pair the team extrapolated is graded estimated and labelled as such. Do not leave a stated pair in 8.12. A pair counts only when it describes the effect of what Augusta delivered; a pair about something else (the overhead of a tool, a vendor benchmark, a comparison between two options that were not built) stays in 8.12. |
| Model and target comparisons | For a project whose result is a model or a system (forecasting, classification, optimisation), a comparison the sources state in the same unit counts as a pair: the solution against a baseline method (e.g. forecast error 13.4% against 18.9% for a flat forecast), or against the tolerance or target agreed with the client (16.7% against a tolerance of 20%). Record it as a section 6 entry with `before` = the baseline or agreed tolerance and `after` = the achieved value, and say in `changed` and in the 8.1 label what it is compared against ("against a flat-forecast baseline", "against the agreed tolerance"). Grade measured when it comes from a recorded evaluation with a stated period, otherwise estimated. Never present it as time or money saved. |
| Stated ratios | A ratio or multiple the sources state as a result of a real test or measurement ("2.83x faster on average in the test week") is an 8.1 figure even when the two underlying values are not given. Record it in 8.1 with `before` and `after` blank, the basis in the label (who reported it, what test, which dates), and raise an ask for the underlying values. Grade it estimated until they are supplied. |
| Remarks versus results | A pair or ratio counts when someone is reporting what they observed or measured. An illustration ("say it took 15 minutes and now takes 5"), an aspiration, a hypothetical or a sales claim does not; it stays in 8.12 or out of the file. When one figure rests on a single offhand remark and a better-based figure exists, lead 8.1 with the better-based one. |
| One contract, several rows | When a signed contract covers several tracker rows, leave the fee blank on each row and say so in the return note. |
| Ranges | A value the source gives as a range ("5 to 6 minutes") is kept as a range, quoted; a delta from it is given as a range. Never pick a midpoint. |
| Arithmetic | You may compute from sourced numbers: a difference, a percentage, a multiple, a sum (delta, 8.2, 8.4 to 8.7). Show the inputs by pointing at their fields. You may not supply an input the sources do not state (a rate, a volume, a working-days assumption). |
| Calls | The transcript is the source. A Fireflies summary is cited only when no transcript exists, typed `call-summary`. |
| Weeks | Only if a source states the number of weeks. Never computed from start and end dates. |
| id and slug | `<client>-<short-project>` in kebab-case, lower case, ASCII. Set once; never change it on a refresh. |
| Refresh | Update the existing file in place. Section 13 is append-only: add sources, never rewrite or delete an excerpt. |
| Asks | One ask per thing a person can answer, not per key: group related empties (all permissions in one ask; before, after and volume of a workflow in one ask). No asks for computed fields (delta, grade, 8.2, 8.4 to 8.7, 12.x). Order by what they unlock. Mark the top five `send: true`. |
| Delivery status | Record what the sources show in front-matter `delivery_status` (ongoing, delivered, accepted, no delivery evidence) with its source. If it disagrees with the tracker's Project stage, say so first in the return note. |
| Section 6 on a transformation | One entry per workflow that has its own content in the sources (a number, an owner, a described change). Workflows that were only mapped stay in section 7. |
| 4.3 and section 7 on a single-workflow project | Section 7 keeps its heading with `n/a` on the line below and no blocks. 4.3 holds any sourced scope that was considered and cut, with the reason if a source gives one. |
| Empty sections | An empty section gets no `updated` date. An unknown workflow is not given a 6.n heading. |

## Procedure

1. **Read the references.** `references/case-file-structure.md` (every key and its rule), `references/extraction-table.md` (what to look for, with examples), `references/routing-gates.md`, `references/source-guide.md`.
2. **Inventory the sources.** List the full file tree of every linked repo, then search Fireflies for calls about this client that are not in a repo (see the source guide). Note what exists: calls, emails, plans, documents, imports, code, deal record. Work out which material is about this row's project and which is sales, another project, or noise.
3. **Read.** All call summaries first, to map the engagement over time. Then the transcripts, documents and emails that carry mandate, process, numbers, results, technical choices, quotes and permissions. Then code READMEs for section 9. Do not stop at summaries.
4. **Register sources.** Give every file you will cite an id and add it to the front matter with type, date, author and path.
5. **Extract.** Walk the extraction table row by row. For each row, either record the value with its source and date, or leave it empty. Copy the verbatim passage behind every number and quote into section 13 as you go. Search the sources specifically for numbers (seconds, minutes, hours, %, x, EUR, cases, accuracy) so that no stated figure is missed.
6. **Decide the shape.** `transformation` only when the sources show workflows mapped across an estate and grouped into initiatives. Otherwise `single-workflow`, and section 7 is n/a.
7. **Write sections 1 to 11** on the template. Plain prose for narrative fields, the YAML blocks for structured ones. Each sentence and each value ends with `[S<n>, YYYY-MM-DD]`.
8. **Generate section 12** using the definitions in `routing-gates.md`: status per section, formats, verdict, next unlock, headline grades. Mirror coverage, verdict and headline grades into the front matter.
9. **Generate section 13.xref and section 14.** Asks follow the grouping rule in the decisions table.
10. **Check the file** against the list below, then return the three outputs.

## Check before returning

- Every section heading and key from the template is present, in order (6.n and 7.n headings only for workflows and initiatives the sources name).
- No sentence or value in sections 1 to 11 lacks a source id and date.
- Every source id used in the body exists in the front matter and in section 13.
- No baseline or result number appears in 2.4, 8.1 to 8.8 or the front matter that is not in section 6. Scale figures in section 2 (headcount, volumes, sites) and 8.12 supporting metrics are sourced where they stand.
- Every `delta` has a filled `before` and `after` in the same unit.
- 8.2 equals the sum of 6.n.value.annual, or 8.2 is empty.
- No placeholder text, no gap markers, no mention of missing data in sections 1 to 11.
- Section 12 statuses match the body. The verdict is the highest gate actually passed.
- Section 14 follows the grouping rule, with at most five marked `send: true`.
- The fee, if recorded, appears only in 8.3, and no price line appears in section 13.
- No password, access code or token appears anywhere in the file.

## When the sources are thin

Do the same thing. A project whose repos hold only sales emails produces a file with front matter, a source register, mostly blank sections, verdict `none` and a long list of asks. That file is correct. Do not pad it, and do not lower the bar to make it look fuller. Say "dump needed" in the return note.

## What not to do

- Do not use the tracker's `Card ·` columns, the web, Slack, Drive, or what you know about the client.
- Do not compute a figure the sources do not state. If a deck says "54 s against a 180 s benchmark", record 180 s as the before (graded estimated) and 54 s as the after, and the delta they imply. If a source reports a ratio as the result of a real test or measurement with no before or after ("2.83x faster in the test week"), it is an 8.1 figure under the Stated ratios rule, and the underlying values become an ask. A loose claim with no test behind it ("saves around 70%") goes in 8.12 as stated.
- Do not write to any repo, to Notion, to Slack or to Fireflies.
- Do not produce slides, cards or summaries of the case. Only the file.
