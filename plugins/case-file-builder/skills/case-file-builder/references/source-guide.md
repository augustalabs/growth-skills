# Source guide

Where a project's material lives and how to read and cite it.

## What counts as a source

| Allowed | Not allowed |
|---|---|
| Files in the repos named in the tracker row's `Brain repo` and `Other repos` | The tracker's `Card ·` columns (old case-study copy) |
| The tracker row itself, for classification only: Client, Client label, Sector, Business function, Value driver, Engagement owner, Type, Case study title | Web search, the client's website, press |
| | Your own knowledge of the client or the sector |
| | Other clients' repos |

The repos are the entirety of what exists. If it is not there, the field is empty.

## Reading the repos

All repos are in the `augustalabs` GitHub organisation. Read only; never write, commit, open issues or comment.

```bash
# list every file
gh api "repos/augustalabs/<repo>/git/trees/HEAD?recursive=1" -q '.tree[]|select(.type=="blob")|.path'
# read one file
gh api "repos/augustalabs/<repo>/contents/<path>" -H "Accept: application/vnd.github.raw"
```

List the tree first, then decide what to read. Large repos have hundreds of calls; read all summaries, then open transcripts for the calls that matter.

## Repo layouts

**Engagement (brain) repos**, the usual `Brain repo`:

| Path | Holds | Good for |
|---|---|---|
| `calls/<date>-<slug>/summary.md` | Fireflies summary of a call | Finding which calls matter |
| `calls/<date>-<slug>/transcript.md` | Full transcript | Quotes, numbers, decisions: the citable source |
| `calls/<date>-<slug>/attendees.json` | Who was on the call | Speaker roles |
| `emails/<date>-<slug>/` | Email threads | Sign-offs, status updates, scope changes |
| `plans/`, `briefings/`, `status/` | Project plans, briefs, status notes | Engagement shape, modules, gates |
| `documents/`, `imports/`, `slides/` | Proposals, SOWs, decks, reports, deliverables | Mandate, business case, results |
| `decisions.md`, `timeline.md`, `people.md`, `project.md` | Brain-written running notes | Orientation; cite the underlying call or document where one exists |
| `.brain/deal.md` | Attio deal record: stage, value, owner, dates | Deal dates and owner. `value_eur` is a CRM deal value, not a confirmed fee |

**Older project repos** vary. Common shapes: `client-management/calls|emails|documents|slides/`, `imports/local-pc-<date>/` (a bulk upload of someone's project folder), `plans/<project>/`, `documents/ours|from-client/`.

**Code repos** (usually in `Other repos`): read `README.md`, any `docs/` or architecture files, and configuration that names integrations or hosting. Good for section 9 only.

## Citing

- Register every file you use in the front-matter `sources` list with an id (`S1`, `S2`, …), type, date, author and `repo/path`.
- **Date** is the date of the call, email or document. For undated files use the last-commit date of the file and say so in the type (`document, commit-dated`).
- **Transcript over summary.** Fireflies summaries are AI-written. Use the summary to find the passage, then cite the transcript. Cite a summary only when no transcript exists, with type `call-summary`.
- A summary that reads "No Fireflies-provided summary" is empty. Open the transcript or skip the call.
- **Quotes** are word for word from a transcript, email or document, in the original language, with speaker, role, and location (file and timestamp where the transcript has one).
- Put the verbatim passage behind every number and every quote into section 13 under its source id.

## Sales material versus delivery material

Most brain repos start as sales pipeline. Calls and emails before the deal closed describe what was proposed, not what was done.

- Proposal and SOW content fills section 4 (mandate) and planned engagement shape.
- A target or forecast from a proposal is not a result. It never fills `6.n.after` or section 8.
- Section 5, 6 `after`, 8, 9, 10 and 11 need material from delivery: kick-off onward, status updates, demos, handover, results.

## Several projects in one repo

One case file per tracker row. When a repo covers several projects for the same client, use only the material about the row's project (match on the row's `Case study title`, `Attio deal` and dates). When two rows share a repo and the material cannot be separated, say so in your return summary and fill only what is clearly attributable.
