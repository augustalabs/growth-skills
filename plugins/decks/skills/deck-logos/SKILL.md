---
name: |-
  deck-logos
description: |-
  Find, clean and choose company logos for Augusta decks, fully automatically — the horizontal wordmark for the lockups next to Augusta's logo and the square mark for portfolio-company tiles. Use when a deck skill needs logos for a client, fund or portfolio companies; not for placing or colouring them on slides.
notion_page_id: 3e576b8e-5e31-8112-bacd-fad7eba0f90b
---

# deck-logos

Called by a deck skill with a list of logos to find. Returns one clean file per entry, or an explicit `none` with the reason. No human step.

## Input

One entry per logo, from the deck skill:

- **company**: the short brand name (`Rolls-Royce`, not `Rolls-Royce Holdings plc`)
- **domain**: the company's own website
- **kind**: `wordmark` for the lockups (cover, company divider, thank-you), or `mark` for the square portfolio-company tiles
- **role**: `client`, `fund` or `portco`, used in the report only

## Setup

Files: `logos.py`, self-contained. Run it with `uv run logos.py ...`: uv installs its dependencies (Pillow, Playwright) on first use, and the script fetches Chromium once if the machine doesn't have it. Needs only `uv` on the machine.

## Steps, for each entry

1. **Collect.** Run `uv run logos.py collect --kind <kind> --company "<company>" --domain <domain> --out <run>/logos/<company>-<kind>`. It scans the company's own site in a real browser for:
   - the header logo
   - the [schema.org](http://schema.org) logo
   - the apple-touch icon, icons and favicon

   <p>
   It then cleans every candidate, checks it, and writes `candidates.json` and `sheet.png`.
   </p>
2. <b>Look at </b>**`sheet.png`****.** For a `wordmark`, each row shows the candidate in white next to Augusta's logo on the dark cover. For a `mark`, it shows the candidate in ink in the tile. The original colours are on the right.
3. **Pick** the best candidate that passes the rules below:
   <p>
   `uv run logos.py pick <dir> <n> --reason "<one line>"`
   </p>
4. **Nothing good yet?** Add sources and collect again with `--extra <url> ...`; numbering continues. Try them in this order:
   1. the company's brand or press page (SVG, or a brand-kit .zip)
   2. Wikimedia Commons (`File:` pages work)
   3. logo sites

   <p>
   Never use Google Images, and never get past a CAPTCHA or a login.
   </p>
5. **Still nothing:** return `none` with the reason. The deck keeps its placeholder.

## Rules for picking

- **Right company.** The file comes from the company's own domain, its official brand page, or a Wikimedia file named for it. Reject look-alikes, e.g. H&M for HM Hospitales.
- **Current.** When the site header and an older file disagree, the logo in the live site header wins. [Schema.org](http://Schema.org) logos and old uploads are often outdated.
- **Primary logo only.** No sub-brand, product, campaign, tagline or country version.
- **Clean.** Blocking flags (`busy_background`, `solid_block`, `boxed_logo`, `knockout_detail`, `empty`) are never accepted. They mean the logo breaks when made one colour.
- **Low resolution.** Accept `--accept low_resolution` only when the sheet shows the logo reading cleanly at slot size.
- **Wordmark: one unit with Augusta.** Take the horizontal, one-line version whose proportions sit best next to Augusta's logo in the dark preview. A `stacked` version (symbol over name) is used only when no horizontal one exists.
- **Mark, in this order:**
  1. the company's real square symbol
  2. its site icon (apple-touch icon, favicon)
  3. its standard logo, picked with the `not_square` note, which goes in the tile as it is

  <p>
  Never crop letters or set type to make a symbol.
  </p>
- **Page noise.** Photos, social icons and cookie-banner copies of the logo are ignored unless they are the only clean copy of the current logo.

## Output

Write `<run>/logos/logos.json`, one object per entry:

```json
{"company": "Apax", "role": "fund", "kind": "wordmark",
 "file": ".../logo.svg", "png": ".../logo.png", "aspect": 2.72,
 "source": "https://www.apax.com/assets/images/logo-main-new.svg",
 "confidence": "high", "reason": "current site header logo, vector"}
```

- <b>confidence </b>**`high`****:** an official source with no accepted flags.
- <b>confidence </b>**`medium`****:** an accepted `low_resolution`, the `not_square` fallback, or a third-party source. Say which in `reason`.
- **no logo:** `{"company": ..., "kind": ..., "none": "<reason>"}`.

`file` is the vector when there is one; `png` is always there. Files keep their own colours. White, ink and grey are applied on the slide.

## Out of scope

- Which companies need logos: research and the deck skill decide.
- Where logos go, their colour and their size: the deck skill and the template decide.
