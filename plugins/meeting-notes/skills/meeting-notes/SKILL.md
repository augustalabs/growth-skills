---
name: |-
  meeting-notes
description: |-
  Helps structure and summarize meeting notes, capturing key decisions, action items, and follow-ups.
notion_page_id: 3e076b8e-5e31-8151-828e-c5e47706fd74
---

# Meeting Notes

Help the user create structured, actionable meeting notes.

## When to use

After any meeting, standup, or call where decisions were made or action items assigned.

## What to capture

- Attendees — who was there
- Key decisions — what was agreed on
- Action items — who does what, by when
- Open questions — what needs follow-up
- Next steps — when to reconvene

## Bundled files

This skill ships with supporting files in its directory:

- scripts/extract\_action\_items.py — run it over saved notes files (e.g. python3 scripts/extract\_action\_items.py notes/\*.md) to collect every open action item into one follow-up list.
- assets/notes-header.png — the standard header banner; place it at the top of notes that get shared outside the team.

## Style

Keep it scannable. Use bullet points over paragraphs. Bold the owner of each action item and write action items as markdown checkboxes ("- \[ \] \*\*Owner\*\* — task") so the bundled script can find them. Date everything.
