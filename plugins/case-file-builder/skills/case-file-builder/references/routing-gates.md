# Coverage, routing gates and status

Everything on this page is computed from the file body after sections 1 to 11 are written. None of it is typed by judgement.

## When a field is filled

Two states only: filled or empty.

- **A number** (anything in section 6, 8.1 to 8.12, engagement weeks, scale figures in section 2) is filled when value, source and as-of date are present. Period and volume are recorded whenever the source states them; a number with no stated measurement window is still filled, and is graded `estimated`.
- **A prose field** is filled when it holds at least one sentence that ends with a source id and date.
- **A classification field** (sector, business function, value driver, owner) is filled when it holds a value from the Project Tracker row, cited as the tracker source with the date the row was read. `shape` is decided from the sources (SKILL.md step 6).

A `delta` is written only when `before` and `after` are both filled, in the same unit. A different unit means no delta; never convert. The delta takes the lower of the two grades.

## Section status (12.1)

For each of sections 1 to 11, over the fields that apply to this project:

| Status | Meaning |
|---|---|
| present | Every applicable field is filled. |
| partial | At least one applicable field is filled and at least one is empty. |
| absent | No applicable field is filled. |
| n/a | The section does not apply. Only section 7, when `shape` is single-workflow. |

Fields that are optional by the structure table ("Absent is fine", "Normally empty", "Every line optional", "Empty is normal") do not count against `present`: 6.n.validated_by, 8.3 lines, 8.9, 8.10, 8.12, 11.2.

Section 1 counts the front-matter fields it prints: client, label, the three chips, owner, engagement, permissions, plus 1.4 title. Empty permissions make section 1 partial.

## Routing gates (12.2)

Each rung requires the one below it. A gate reads flags only.

| Format | Requires |
|---|---|
| Quarter | One 8.1 figure present, as a ratio or multiple. Sector and business function present. One sentence from 5.1. |
| Half | Everything in Quarter. Section 3 present. 5.1 present. A second 8.1 figure, or 8.2 present. |
| One-pager | Everything in Half. 8.2 gross value present. Permissions recorded in front matter. Section 4 present. |
| Flagship | Everything in One-pager. Two or more section 6 entries with before and after in the same unit. Every section 6 entry carries a value. Section 9 present, or a 10.2 demo recorded. Every headline grade measured or modelled. |

- `formats` = every rung passed, lowest to highest.
- `verdict` = the highest rung passed, or `none` when Quarter fails.
- `next_unlock` (12.3) = the first failed check of the rung above the verdict. It stays in the file; it has no tracker column.

## Headline grades (12.4)

The grade of each 8.1 figure and of 8.2, taken from the section 6 entries they point at.

| Grade | When |
|---|---|
| measured | Before and after both come from a recorded measurement (logs, timing sheets, system counts) with a stated period. |
| modelled | The figure comes from a stated model or business-case document with named assumptions. |
| estimated | Anything else the sources state: a benchmark given by the client or the team, a figure said in a call or shown on a deck without a measurement window, a before-state not captured before the build. |

An estimated figure counts as "an 8.1 figure present" for Quarter, Half and One-pager. It cannot headline a Flagship: that gate requires every headline grade to be measured or modelled. The grade travels with the figure so the output can label it.

## Reconciliation (8.2)

`8.2 gross.annual` must equal the sum of every `6.n.value.annual`. Set `reconciles: true` only when it does. If the sources state a gross figure that does not match the per-workflow values, leave 8.2 empty and raise an ask.

## Asks (section 14)

One ask per thing a person can answer, not per key. Group related empties: all permissions in one ask; the before, after and volume of one workflow in one ask; rate and value together. No asks for computed fields (delta, grade, 8.2, 8.4 to 8.7, section 12). An estimated figure that could be upgraded gets an ask for its measurement. Each ask names the field keys it covers, the person to ask (the tracker's Engagement owner unless a source names someone better), the exact question, and what answering it unlocks. Order by unlock, highest first. Mark the first five `send: true`.

## Status summary returned to the caller

After writing the file, return this block. The caller writes it to the tracker's `CF ·` columns.

```yaml
tracker_page: <Notion URL of the row>
file: <path to the .md file>
CF · 1 Identity: present | partial | absent
CF · 2 Situation:
CF · 3 Problem:
CF · 4 Mandate:
CF · 5 Solution:
CF · 6 Workflows:
CF · 7 Initiatives:        # may be n/a
CF · 8 Impact:
CF · 9 Technical:
CF · 10 Proof:
CF · 11 Forward:
CF · Verdict: none | quarter | half | one-pager | flagship
CF · Formats: []
CF · Open asks: <count of section 14 entries>
CF · Updated: <file last_updated, YYYY-MM-DD>
```
