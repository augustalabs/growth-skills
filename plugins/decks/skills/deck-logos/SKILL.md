---
name: |-
  deck-logos
description: |-
  Find, clean and choose company logos for Augusta decks, fully automatically — the horizontal wordmark for the lockups next to Augusta's logo and the square mark for portfolio-company tiles. Use when a deck skill needs logos for a client, fund or portfolio companies; not for placing or colouring them on slides.
notion_page_id: 3e576b8e-5e31-8112-bacd-fad7eba0f90b
---

# deck-logos

Called by a deck skill with a list of logos to find. Returns one clean file per entry, or an explicit none with the reason. No human step.

## Input

One entry per logo, from the deck skill:

- company: the short brand name (Rolls-Royce, not Rolls-Royce Holdings plc)
- domain: the company's own website
- kind: wordmark for the lockups (cover, company divider, thank-you), or mark for the square portfolio-company tiles
- role: client, fund or portco

## Setup

The only file is `logos.py`, and it is self-contained. Run it with `uv run logos.py ...`. On first use, uv installs its dependencies and the script fetches Chromium once. The machine only needs `uv`.

Run the entries one at a time, never in parallel. Parallel runs get rate-limited by Wikimedia and some sites.

## Steps, for each entry

1. Collect:
   <p>
   `uv run logos.py collect --run <run> --company "<company>" --domain <domain> --kind <kind> --role <role>`
   </p>

   - It scans the company's own site in a real browser for the header logo, the [schema.org](http://schema.org) logo, the apple-touch icon, icons and favicon.
   - It cleans and checks every candidate, and prints the entry's folder (`dir:`) and its contact sheet (`sheet:`).
2. Open the contact sheet.
   - For a wordmark, each row shows the candidate in white next to Augusta's logo on the dark cover.
   - For a mark, each row shows the candidate in ink in the tile.
   - The original colours are on the right.
3. Pick the best candidate that passes the rules below:
   <p>
   `uv run logos.py pick <dir> <n> --reason "<one line>"`
   </p>

   <p>
   It records the file and works out the confidence itself.
   </p>
4. No good candidate yet, or a WARNING that the scan found nothing? The site probably blocks automated browsers. Add sources and collect again:
   <p>
   `uv run logos.py collect ... --no-site --extra <file-url> <file-url>`
   </p>

   - This adds to the same sheet: the earlier candidates keep their numbers and the new ones follow.
   - To find sources, web-search `<company> logo svg`, `<company> brand assets` or `<company> press kit`. When the company's own pages are blocked, go straight to Wikimedia Commons.
   - `--extra` takes direct file URLs (.svg, .png, .jpg, .webp, .zip), not web pages and not PDFs. Open the page yourself and copy the file links.
   - Wikimedia and Wikipedia `File:` page URLs are the one exception: they work as they are.
   - Look in this order:
     1. the company's brand, press or media page (an SVG or a brand-kit .zip)
     2. Wikimedia Commons
     3. logo sites
   - Never use Google Images, and never get past a CAPTCHA or a login.
   - A failed download is retried when you pass it again.
5. Still nothing acceptable: `uv run logos.py none <dir> --reason "<why>"`. The deck keeps its placeholder.

When every entry is done, run `uv run logos.py report --run <run>`. It writes `<run>/logos/logos.json` and warns about any entry left without a pick or a none.

## Rules for picking

- Right company.
  - The file comes from the company's own domain, its official brand page, or a Wikimedia file named for the company.
  - A logo site is a last resort. Use it only when its file is identical to the logo the company itself uses today.
  - Reject look-alikes, e.g. H&M for HM Hospitales.
- Current version.
  - When the live site header and an older file disagree, the header wins.
  - [Schema.org](http://Schema.org) logos, old uploads and anniversary or campaign versions (e.g. "KKR \| 50", "80 anos") are often outdated or temporary.
  - Among Wikimedia files, take the one dated most recently (the year is usually in the name, e.g. "(2023)"). Check it against how the company presents itself today.
  - The same applies to site icons: an icon that differs from the logo in the live header is outdated.
  - The current version beats an older one, even when the older one is unboxed or has no campaign line.
- Primary logo only. No sub-brand, product, campaign, tagline or country version.
- Clean.
  - The blocking flags (busy\_background, solid\_block, boxed\_logo, knockout\_detail, empty) mean the logo breaks when made one colour.
  - Those candidates stay numbered on the sheet, but `pick` refuses them.
- Knockouts are handled for you. When a logo has white letters or shapes over colour (a badge, a circle with bars), the script cuts the white out, the way the brand prints itself in one colour. It notes this as `knockout_cut`. Check on the sheet that it reads right. This does not lower confidence.
- Detail lost. The `detail_lost` note means colours that touch each other merge in one colour, e.g. a pin on a disc becomes a dot, or a tri-colour symbol becomes a block.
  - Pick it only if the one-colour preview still reads as the company's logo.
  - Otherwise look for the company's own one-colour version (brand page, Wikimedia), or take the next candidate.
- Boxed logos. The `boxed` note means the logo is a filled box with the name cut out. Prefer an unboxed version of the same logo when the company has one.
- Low resolution. Accept it with `--accept low_resolution` only when the sheet shows the logo reading cleanly at slot size.
- Wordmark: one unit with Augusta. Take the horizontal version whose proportions sit best next to Augusta's logo in the dark preview.
  - Use the logo as the company shows it in its header, symbol included. Take a text-only version only when the company itself uses one.
  - A name set on two lines is still a wordmark.
  - When the only horizontal version is a campaign or anniversary one, use the current primary logo instead, even if it is `stacked`.
  - The `stacked` note marks a tall, symbol-style logo (narrower than 1.5:1), such as a monogram or badge. Use it only when no horizontal version exists anywhere, including step 4.
- Mark, in this order:
  1. the company's real symbol
  2. its site icon (apple-touch icon, favicon), including a letter icon such as a single "c"
  3. its standard logo, picked despite the `not_square` note, which then goes in the tile as it is

  <p>
  Never crop letters or set type to make a symbol.
  </p>
- Page noise. Ignore photos, arrows, social icons and cookie-banner copies, unless one is the only clean copy of the current logo.

## Output

`logos.json` is one object per entry:

```json
{"company": "Apax", "role": "fund", "kind": "wordmark",
 "file": ".../logo.svg", "png": ".../logo.png", "aspect": 2.72,
 "source": "https://www.apax.com/assets/images/logo-main-new.svg",
 "confidence": "high", "reason": "current site header logo, vector"}
```

- The script sets confidence:
  - high: the company's own site, with no accepted flag and no note.
  - medium: anything else, such as a third-party source like Wikimedia, an accepted low\_resolution, `stacked` or `not_square`.
- A none entry is `{"company": ..., "kind": ..., "none": "<reason>"}`.
- `file` is the vector when there is one; `png` is always there.
  - After a knockout cut, `file` is the PNG, because the cut exists only in pixels. It is rendered large, so it stays sharp.
- Files keep their own colours. White, ink and grey are applied on the slide.

## Out of scope

- Which companies need logos: research and the deck skill decide.
- Where logos go, their colour and their size: the deck skill and the template decide.
