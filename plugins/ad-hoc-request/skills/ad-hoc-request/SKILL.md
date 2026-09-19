---
name: |-
  ad-hoc-request
description: |-
  Complete an ad hoc Growth request end-to-end in one pass, produce the requested output, and log the finished work in the Augusta Labs Growth ad hoc requests database. Use when someone invokes this skill with a request to execute; do not use for ordinary task planning or status updates.
notion_page_id: 3e076b8e-5e31-816d-bb0f-dc68f819c81a
---

# Ad Hoc Request

Complete the request first, then log it in the `ad hoc requests` database on the [Growth page](https://app.notion.com/p/34d76b8e5e31811dbbc7c415aae6bfcb), data source `collection://8356588f-8d86-4164-bbb6-86f61c85a309`.

## Execute

- Treat the invocation as the complete brief. Work end-to-end in one pass and make reasonable assumptions instead of asking follow-up questions.
- Use the relevant connected tools and artifact skills for the requested output. Do not turn a draft into a sent message or take another consequential external action unless the request explicitly asks for it.
- Ask only when an indispensable input is missing or a required approval cannot be bypassed safely.
- Measure active elapsed time from the start of the request through completion, in whole minutes, rounded up with a minimum of 1.

## Log

Fetch the data source immediately before writing, then create one row after the work is complete. Fill every property:

- `Name`: a short, outcome-based title.
- `Type`: one to three concise, reusable request categories. Reuse an existing option when it is equivalent; otherwise add the smallest useful new option.
- `Asker`: the person who originally requested the work. Resolve an explicitly named person to their Notion user. If nobody else is named, fetch `self` and use the authenticated Notion user's ID.
- `Time it took (min)`: the measured whole minutes.
- `Form of output`: one or more exact values from `Notion page`, `Google Sheet`, `Pitch Deck`, `Gmail`, or `Action`. Choose the closest actual output, not the tool used internally.
- `Resolution process`: a compact plain-text account of what was done, the main decisions or assumptions, and links or identifiers needed to find the result.

If the request produces several outputs, keep one row and select every applicable output form. Fetch the created row to verify the stored values, then return the result and a link to the log entry. Do not show a plan or ask for confirmation before executing unless a genuine blocker requires it.
