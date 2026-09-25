---
name: |-
  deck-discovery-pe
description: |-
  Build an Augusta "AI Value Creation for Private Equity" discovery deck for a named PE fund, end to end, from a Deck Tracker request to a finished Paper deck. Use when a Deck Tracker row has Deck Type = Discovery and Vertical = PE Firm.
notion_page_id: 3e576b8e-5e31-81e4-aea3-ced9ba52461c
---

# deck-discovery-pe

You build one discovery deck for a private-equity fund, on your own, from a Deck Tracker request to a finished deck in Paper. Nobody is watching: decide, and record why.

## What this deck is

- **Who reads it:** the partners and operating partners of a PE fund, in a first or second meeting.
- **What it must do:** show that Augusta understands how AI creates value across *their* portfolio, and make them want the next step (the Value Foundation Sprint).
- **The story:**
  1. who we are (Company)
  2. how we think about AI (Playbook)
  3. what it would mean for *their* companies (Portfolio Value Creation)
  4. how we'd start (Engagement)
  5. close

  <p>
  Chapter 3 is where the deck is won or lost. Everything else is Augusta's own material.
  </p>

**What good looks like**

- A partner reads the Portfolio Value Creation chapter and recognises their own companies, their sector and their real problems. It is specific enough that it couldn't have been written for another fund.
- Every company named is one the fund owns today. Every number is real and sourced, or it isn't there.
- The deck is pixel-perfect: nothing overflows, nothing misaligned, no leftover `ACME`, `<Fund>` or `[Industry Group]`, and one voice throughout.

**What bad looks like**

- A generic deep dive with the fund's name pasted in.
- A company the fund sold last year.
- A case study that has nothing to do with the portfolio company next to it.
- A half-translated or half-filled slide.

## Where everything lives

| What | Where |
| --- | --- |
| The request | Deck Tracker row, data source `collection://d037fe20-68e3-4bde-9fd8-e637bf6bfc8d` |
| The deck: its groups, slides, decisions and fixed rules | Mapping page "Discovery PE Decks Mapping" `3e476b8e5e3181c7bf63ce4f64555c1f`. Each group has its Decisions, its Fixed rules and a table of its slides. |
| The whole slide list, in deck order | The **Full Database of Slides** table at the end of the mapping page. Query it in view mode: every slide of the deck in order, with Class, Appears when and the artboard link. This is the list the plan is built from; the group tables show the same slides next to their group's rules. |
| What each slide says and its rules | Each slide's Notion page, i.e. the row's page in the Slides view |
| The design | Paper template file `01M39QHGZGA5T0P7M5JGN5PM2P` (Discovery PE); each slide row links to its artboard in `Discovery PE · Artboard` |
| Research, logos, case studies | Skills `deck-research`, `deck-logos`, `deck-case-picker` in Growth Skills (pull them fresh) |

Never copy content from these into your own head as "the usual". Read them on every run: they change.

## The run folder and names

- **Run folder:** `~/deck-runs/<YYMMDD-HHMM>-<fund-slug>/`, e.g. `~/deck-runs/260925-1430-proa-capital/`. Everything for this deck goes in it:
  - `plan.json`: the spine of the run (below)
  - `research/`: from deck-research
  - `logos/`: from deck-logos
  - `notes.md`: every decision and its reason, and anything a human should check
- **Paper file:**
  - EN: `Augusta Labs × <Fund> | AI Value Creation`
  - PT: `Augusta Labs × <Fund> | Criação de Valor com IA`
  - `<Fund>` is the short brand name (e.g. "ProA Capital", not "ProA Capital de Inversiones SGEIC").
- **Paper pages:** exactly the template's chapter pages and names: `0 · Front`, `1 · Company`, `2 · Playbook`, `3 · Portfolio Value Creation`, `4 · Engagement`, `5 · Close`. Leave out a chapter that doesn't run (see decisions).
- **Artboards:** named exactly as the template's artboards. Repeated slides take their instance label, e.g. `Workflow deep dive · A1`, and each artboard is stacked vertically in deck order: left 0, top 0 / 1200 / 2400 …
- **Deck date:** the EOD Deadline month in full ("September 2026"; PT: "setembro de 2026"). No deadline means this month.

## plan.json: the spine

Every step reads and writes `plan.json`. Its shape:

```json
{
  "request": {"row": "<url>", "fund": "", "domain": "", "language": "EN", "date": "", "requester": ""},
  "decisions": [{"group": "", "question": "", "answer": "", "reason": ""}],
  "research": {"brief": "research/<fund>.md", "portfolio": [{"company": "", "domain": "", "sector": ""}]},
  "slides": [{"order": 1, "group": "0 · Front", "name": "", "notion": "<url>", "class": "", "artboard": "<url>",
              "instance": null, "runs": true, "company": null, "content": {}, "logos": [], "case": null, "built": null}],
  "paper": {"file": "", "pages": {}}
}
```

Gate script: `uv run plan_check.py <run>/plan.json --stage decisions|write|build` runs between steps and refuses to continue on a gap. It checks:

- every slide in the Full Database of Slides is in the plan
- every mapping decision has an answer and a reason
- every VARIABLE or DEAL slide has content
- every portfolio company is on research's confirmed-current list

## The run

### 1. Claim and plan

1. Take the row: Status → `In Progress`, and Bot Progress `Started. Reading the request.` Never build a row that's already In Progress.
2. Read the row:
   - Client Name: the fund
   - Website: its domain
   - Deck Language
   - EOD Deadline
   - Send to: the requester, who goes on the Thank-you slide
   - Additional Information and every file in Files & media: context
3. **Read all the context before planning anything.** You orchestrate the whole deck, so you must know all of it, not just the part a step needs:
   - the mapping page in full: every group's intro, decisions and fixed rules
   - the Full Database of Slides at the end of the mapping page, and every group's slide table
   - **every slide's Notion page**, FIXED ones included: Purpose, Fixed, Variable, Rules
   - the variant pages of slides that have them (their parent's Purpose and the variant for this deck)
   - the request row in full, and every attached file

   <p>
   Then write `plan.json` with every slide and every decision question, unanswered. When you brief a subagent (a writer or a builder), give it the context its slides depend on: the story, the decisions and the neighbouring slides. Don't send it only its own slide.
   </p>

### 2. Research, and the empty deck (in parallel, one message)

- **Research** (`deck-research`): fund profile and portfolio today, for the fund. This is the slowest step: start it first.
- **Paper:**
  - create the file
  - add the `--font-sans` token (value `TWK Lausanne`)
  - create the chapter pages
  - record their ids in the plan
- **Logo** (`deck-logos`): the fund's wordmark (role fund).

### 3. Decisions

Answer every question on the mapping page from the research, and write each answer and reason into the plan. Among them:

- Does the Portfolio Value Creation chapter run?
- How many deep dives, 4 to 6?
- Which dominant sector is the `[Industry Group]`?
- Which portfolio company carries each deep dive, and which workflow?

Judgement:

- **A deep dive's company:** owned today, a different one per deep dive, and a workflow where AI clearly matters for that company's model.
- **Its workflow:** real for that company, and specific enough that a partner nods.
- **4 vs 6 deep dives:** go deeper only when the portfolio and the request can carry it.

Then run `plan_check.py`.

### 4. Helpers (in parallel, one message)

- **Logos** (`deck-logos`): the square mark for every portfolio company that carries a deep dive (role portco).
- **Case studies** (`deck-case-picker`): one per deep dive, each slot being "\<Workflow> at \<Company, one-line profile>". Put each pick's Notion page into its slide in the plan.

### 5. Write

For every slide that isn't pure FIXED boilerplate:

- read its Notion page
- write its content into the plan, following Purpose, Fixed, Variable and Rules

Case cards are copied from the case's tracker row fields (Card · Tag, KPI, Title, Challenge, Solution, Impact, Banner, Logo), never rewritten.

- **Numbers and impact (guideline):** say what changes for the company qualitatively, e.g. "faster close", "fewer manual checks", "reps spend their time selling". Avoid promising amounts like "€100M more EBITDA" or "30% lower cost".
  - The numbers that belong on a slide are the case cards' real metrics and sourced facts from research.
  - `plan_check.py` lists every figure it finds in written content for you to review. Keep a figure only if it's one of those.
- **Language:** EN is written in English. PT is written natively in European Portuguese, following `deck-pt-voice`, and is never translated from an English draft.
- **Parallel:** one writer subagent per deep dive, plus one for the thesis. Give each writer the thesis's workflow table, so IDs and names match across slides.

Then run `plan_check.py`.

### 6. Build: one agent per chapter (in parallel, one message)

One build subagent per chapter page. Each one gets its page id, its slides from the plan, and these instructions:

1. **Copy each artboard from the template:**
   - `get_jsx(inline-styles)` on the template artboard
   - `create_artboard` on the new page, named and positioned per the naming rules
   - `write_html` of the root's children, in order and in chunks

   <p>
   Image URLs (`app.paper.design/file-assets/…`) work across files. Repeated slides are copied once per instance.
   </p>
2. **Change it per the plan:**
   - set every text from the plan's content
   - replace every token (`<Fund>`, `ACME`, `[Industry Group]`, the date)
   - place the logos: upload each with `paper-asset://` from `logos/`
   - place the case cards: the banner image from the case row, and its text fields
3. **Remove** the `notion-tag` layer.
4. **Check its own work:**
   - screenshot every artboard
   - compare it with the template artboard
   - no overflow, no orphan words, no leftover tokens, alignment kept
   - fix, then call `finish_working_on_nodes`
5. Report back the artboard ids. Write them into the plan's `built`.

Keep layout, sizes and styles from the template: you change content, not design. If text doesn't fit, shorten the text; never shrink or move the design.

### 7. Validate, export and deliver

Validation is your job, not a builder's and not another skill's. The builders checked their own slides; you check the deck as a whole, because only you know all of it.

1. **Validate.** Run `plan_check.py --stage build`, then go through the Paper file artboard by artboard, with a screenshot of each next to its template artboard:
   - **Complete:** every slide in the plan is in the file, on the right page, in deck order, named per the naming rules. Nothing extra.
   - **Clean:** no `ACME`, `<Fund>`, `[Industry Group]`, `Month YYYY`, template example text or `notion-tag` layer left anywhere. Use `find_nodes` for the text tokens, not only your eyes.
   - **Fits:** no text overflowing its box, clipped, or wrapping onto an orphan word; nothing moved or resized from the template.
   - **Logos:** every lockup and portfolio tile has its logo, the right company's, in the template's colour and size. None left as a placeholder unless `logos.json` says none.
   - **Case cards:** each deep dive's card matches its tracker row field for field, with the banner in place, and sits next to a company it makes sense for.
   - **Consistent:** the same company and workflow names and IDs across the thesis and its deep dives; the deck date on the cover; page numbers in order; one language and one voice throughout.
   - **True:** every company is on research's confirmed-current list; every figure is a case-card metric or a sourced fact from the brief; the requester appears only on the Thank-you slide.

   <p>
   Fix every failure in Paper (or send it back to that chapter's builder), then validate that slide again.
   </p>
2. Read the deck once, top to bottom, as the partner would. Does chapter 3 feel written for this fund?
3. **Export the PDF** with `render.mjs` (in this skill), which renders the deck in Chrome with the TWK Lausanne font installed on the machine. Paper's own PDF export fails on these templates and drops links, so don't use it.
   - `get_jsx(inline-styles)` on every artboard, in deck order, saved to `<run>/pdf/slides/NN.jsx`
   - write `<run>/pdf/deck.json` (title = the Paper file name, artboard 1920×1080, slides in order)
   - `node render.mjs <run>/pdf`, which gives `deck.pdf` and `deck.html`
   - check it: `pdffonts deck.pdf` lists only TWKLausanne, and a look at a few pages (`pdftoppm -r 40 -png`) shows every image and logo
4. **Attach the PDF:**
   - `notion-create-file-upload` with the filename `Augusta-Labs-x-<Fund>-AI-Value-Creation.pdf` (PT: `Augusta-Labs-x-<Fund>-Criacao-de-Valor-com-IA.pdf`). Notion rewrites spaces, `×` and `|`, so keep the name to letters, digits and hyphens.
   - POST the file to the `upload_url` as multipart form field `file`, with every header it returned. The response must say `"status":"uploaded"`.
   - put it in the row's Files & media as `{"type":"file_upload","file_upload":{"id":"<file_upload_id>"}}`
   - if the upload fails, retry once with a new upload; if it fails again, deliver without it and say so in `notes.md` and the Slack thread (the PDF goes to Slack either way).
5. **Update the row:**
   - Deck Link: the Paper file URL
   - Files & media: the PDF
   - Status → `In Review`
   - Bot Progress: `Ready for review.`
6. `notes.md` lists what a human should check by eye: logos, case photos, anything flagged `medium`, and anything validation fixed.

<b>Never set Status to </b>**`Done`****.** A person sets Done after reviewing the deck. `In Review` is as far as you go.

**Failure at any step:**

- Status → `Blocked`, and Bot Progress: `Stopped at <step>: <plain reason>.`
- Keep the Paper file and the plan.
- Never retry more than once. Never leave a row In Progress.

## Progress: Notion and Slack

Report at every step in two places, always both, one plain sentence, e.g.:

- `Researching ProA Capital and its current portfolio.`
- `Picked 4 portfolio companies and their case studies.`
- `Building the deck in Paper.`
- `Ready for review.`

**Where:**

- **The row's Bot Progress:** overwrite it every time, so it holds the latest line only.
- <b>Slack </b>**`C0C20P1TTV4`** (#pitch-decks-bot-health), one thread per deck:
  - start: "\:hammer_and_wrench\: Building *\<Fund>* PE discovery deck — \<Notion row link>", and keep its `ts`
  - reply in that thread with each progress line
  - finish: "\:eyes\: Ready for review — \<Paper link>" plus the PDF, broadcast to the channel
  - failure: "\:red_circle\: Blocked at \<step>: \<short reason>", broadcast
  - the thread also carries the build notes: decisions and reasons, the portfolio companies and case studies picked, and what to check by eye

**Rules:**

- Send progress in the same message as the step's own work, never as a turn of its own.
- If Slack or Notion refuses an update, carry on building: reporting is never a reason to stop.
- Never put secrets or file paths in progress lines.

## Never

- Never name a company the fund doesn't own today.
- Never state a number that isn't sourced (research) or on a case card.
- Never leave `ACME`, `<Fund>`, `[Industry Group]`, a template example or a `notion-tag` in the deck.
- Never name the real client of an anonymised case.
- Never change the template's design to make content fit.
- Never mention the requester: no name, no @mention, no "for \<name>", in Notion, Slack or anywhere else. The only place their details appear is the deck's own Thank-you slide, as its mapping rules say.
- Never guess. What you can't confirm goes in `notes.md` for a human, and stays out of the deck.
