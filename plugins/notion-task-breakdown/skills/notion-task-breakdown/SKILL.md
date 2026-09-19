---
name: |-
  notion-task-breakdown
description: |-
  Break an existing Augusta Labs Growth task into actionable subtasks and write the approved breakdown to the Growth tasks database in Notion. Use while Guilherme Brandão is planning or decomposing Growth work; do not use for generic status reports or unrelated Notion pages.
notion_page_id: 3e076b8e-5e31-811b-9b87-fec70db74c28
---

# Notion Task Breakdown

Work in the `tasks` database on the [Growth page](https://app.notion.com/p/34d76b8e5e31811dbbc7c415aae6bfcb), data source `collection://d6d76b8e-5e31-823e-bf98-87bee12a382a`.

1. Find and fetch the exact existing parent task. Use a supplied link or exact title; ask only when multiple plausible parents remain. Never create a new parent unless requested.
2. Turn the discussion into concise, outcome-based steps that are distinct enough to track. Avoid vague items such as “work on” and avoid tiny administrative steps. Preserve Guilherme's informal, direct English/Portuguese wording and the database's short task-title style.
3. Show the proposed breakdown before writing, unless Guilherme explicitly asks to write immediately. Apply requested edits, then create each approved item as a row in the same database.
4. Set `Parent item` to the parent task URL. Do not write `Sub-item`; Notion maintains the reciprocal relation. Default `status` to `unstarted` unless the conversation establishes another valid state: `backlog`, `unstarted`, `in-progress`, `paused`, `canceled`, or `finished`.
5. Set `Owner` to Guilherme Brandão's Augusta Labs identity (`user://3d4d872b-594c-813f-9a10-0002bbe37b48`) unless another owner is explicit. Add collaborators to `Involved`. Carry over parent context such as `type`, ` type  `, `prio (brand)`, `thread`, or dates only when it clearly applies; prefer a subtask's own stated dates. Set `For review`, `output`, or `link` only from explicit context.

Keep the selected task's page content intact. Never edit formulas (`%`, `% bar`, `sprint`, `deadline key`, `effort · deadline`), archived material, other tasks, or database structure. After writing, fetch the created subtasks and briefly confirm their titles and parent.
