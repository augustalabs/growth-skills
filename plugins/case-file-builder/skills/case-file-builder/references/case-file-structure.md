# Case file structure

The fourteen sections and every key, what it holds, and the rule that governs it. Use the exact keys in `case-file-template.md`.

| Section | Key | Holds | Rule |
|---|---|---|---|
| 0 Front matter | id, slug | Stable identifier; the slug is the filename. | Set once, never changed. |
| 0 Front matter | client.real, client.label | Real name and the anonymised label used when the client cannot be named. | Both stored. Redaction happens at output, never in storage. |
| 0 Front matter | sector, business_function, value_driver | The three chips, in the order every format prints them. | Controlled vocabulary. Function is the organisational unit, not the use case. |
| 0 Front matter | shape | single-workflow or transformation. | Decides whether section 7 applies. |
| 0 Front matter | dates.created, dates.last_updated, dates.last_dump_received | When the file was made, last changed, and when delivery last sent material. | Every write bumps last_updated. Each section carries its own updated date. |
| 0 Front matter | engagement.weeks, modules, gates, start, end | The engagement line: 14 weeks, 3 modules, 2 gates. | Each field only if stated. Weeks are never computed from dates. |
| 0 Front matter | permissions.nameable, logo, metric_quotable, metric_precision, quote_attribution, embargo | What may be shown, and at what precision. | Absent means fully anonymised, no quote. Never assumed. |
| 0 Front matter | owner | The delivery owner who stands behind the numbers. | One person, named. Matches the tracker's Engagement owner. |
| 0 Front matter | delivery_status | What the sources show: ongoing, delivered, accepted, or no delivery evidence. | Sourced. Flag any disagreement with the tracker's Project stage. |
| 0 Front matter | sources[] (id, type, date, author) | Register of every dump item: Slack thread, SOW, voice note, document, demo link. | Every fact in the body points at one source id. |
| 0 Front matter | coverage, verdict, headline_grades | Mirror of section 12 for scripts. | Generated. Never hand-edited. |
| 1 Identity | 1.1 client | Who they are, in one line, and the anonymised form. | Real and label both present. |
| 1 Identity | 1.2 chips | Sector, business function, value driver. | Quarter prints the first two only. |
| 1 Identity | 1.3 engagement | Duration and shape in one line. | From front matter. |
| 1 Identity | 1.4 title | Project title as it will appear on a slide. | Written by Growth, not by delivery. |
| 2 Situation | 2.1 who | Enough for a reader to picture the business: size, footprint, margin shape. | Figures sourced, or the field stays empty. |
| 2 Situation | 2.2 where | The part of the organisation the work sat in. |  |
| 2 Situation | 2.3 process_before | The process as it ran on day one, described plainly. | Prose, sourced. |
| 2 Situation | 2.4 baseline | Pointer to the per-workflow baselines in section 6, plus the one-line summary a slide carries. | Never duplicated here. Section 6 is the record. |
| 3 Problem | 3.1 context | What was happening at the company. |  |
| 3 Problem | 3.2 challenge | Why it cost something: efficiency, productivity, cost, risk, quality. | One primary type named. |
| 3 Problem | 3.3 unit | The atomic unit the problem is measured in, and why that unit. | Human at the centre means time; otherwise a physical unit. |
| 4 Mandate | 4.1 commissioned | What Augusta was asked to solve, in the client's terms. | SOW wording preferred, sourced. |
| 4 Mandate | 4.2 placement | Where it sits in the organisation's order of priorities. |  |
| 4 Mandate | 4.3 declined | Pointer to any initiative considered and not built, with the reason. | The record lives in section 7. |
| 5 Solution | 5.1 plain | What was built, at a level a non-technical reader follows. One paragraph. | Quarter takes one sentence of this. |
| 5 Solution | 5.2 components[] | The named systems or agents, one line each. | Names only. Detail is section 9. |
| 5 Solution | 5.3 how_it_ran | Modules, gates, intermediate deliverables. Two or three lines. | A brief, not a plan. |
| 6 Workflows[] | 6.n.name, owner, systems[], updated | The workflow, who ran it, what it touched, when this entry last changed. One entry per workflow. | The record of truth for every number in the file. |
| 6 Workflows[] | 6.n.before (unit, value, volume, period, as_of, source) | Baseline in its atomic unit, the volume that makes it priceable, the period the measurement covers, the date it was true. | Filled when value, source and as-of date are stated; period and volume recorded when the source gives them. No stated measurement window, or not captured before build: graded estimated. |
| 6 Workflows[] | 6.n.after (unit, value, volume, period, as_of, source) | Same unit and same period basis as before. | Same unit as before. A different unit means no delta. Never converted. |
| 6 Workflows[] | 6.n.delta (absolute, pct, direction) | Before minus after in the unit; the ratio; and productivity (more output, same input) or efficiency (less input, same output). | Written only when both before and after are filled. Direction decides the claim and the price. |
| 6 Workflows[] | 6.n.changed | What changed in the work: where agentic reasoning replaced human steps, what was combined. |  |
| 6 Workflows[] | 6.n.rate (value, type, source, as_of) | Price per unit; whether fully-loaded labour, client tariff or other; who supplied it and when. | The rate source is a named person or document. |
| 6 Workflows[] | 6.n.value (annual, route, cash, capacity, margin) | Annual figure and its split across the three routes: cost out of the base, capacity redeployed, margin recovered. | The three parts sum to annual. Cash and capacity never blended. |
| 6 Workflows[] | 6.n.validated_by | Who on the client side accepted these numbers, if anyone. | Empty is normal. Filled raises the grade. |
| 6 Workflows[] | 6.n.grade | measured, modelled or estimated. | Internal. Not printed on outputs. |
| 7 Initiatives[] | 7.n.name, workflows[] | The initiative and which section 6 entries sit inside it. | n/a when shape is single-workflow. |
| 7 Initiatives[] | 7.n.value_score, feasibility_score | The two scores behind the ranking, as delivery recorded them. | Their scale, kept verbatim. |
| 7 Initiatives[] | 7.n.sequence | The order agreed. |  |
| 7 Initiatives[] | 7.n.status, reason | built, declined or deferred, and why. | Declined ones stay in. They are the credibility. |
| 8 Impact | 8.1 L1[] (figure, before, after, label, workflow, as_of, grade) | Two or three operational results, each as a ratio or multiple with its before-state, pointing at the section 6 entry it came from. | Ratio or multiple, never a level. Quarter takes the first. |
| 8 Impact | 8.2 gross.annual, basis, reconciles | Sum of every 6.n.value.annual, the price basis in one line, and an automatic check that the sum matches. | Must reconcile to section 6 or the file fails. |
| 8 Impact | 8.3 costs (fee, run, adoption, licence, displaced; each with amount, recurring, source, as_of) | The fee is one-off; run, adoption and licence recur; displaced is what the new stack retired, entered negative. | Every line optional. Only what delivery gave. The fee is stored, never output. |
| 8 Impact | 8.4 net.annual | Gross minus recurring costs. | Written only when 8.2 and at least one recurring cost are filled. |
| 8 Impact | 8.5 net.year_one | Gross minus all costs including the fee. | Same condition, plus the fee. |
| 8 Impact | 8.6 payback (months, banded) | Fee divided by monthly net, and the banded form for external use. | Precise internal, banded external. Precise leaks the fee. |
| 8 Impact | 8.7 routes (cash, capacity, margin) | Totals across section 6 for each route. | Sum to 8.2. Cash and capacity never blended. |
| 8 Impact | 8.8 capacity (hours, destination) | Hours released and where they went. | Stated separately. Not a saving. |
| 8 Impact | 8.9 ebitda (figure, framing, source, usable) | The client's own L3 framing where one exists, and whether it may be shown. | Theirs, verbatim. Never Augusta's. |
| 8 Impact | 8.10 sponsor (ev, moic, irr) | L4 and L5 slots. | Held as direction. Normally empty. |
| 8 Impact | 8.12 supporting[] (metric, value, context, source, as_of) | Sourced figures that are not a before/after pair: accuracy scores, minutes saved per day, share of cases handled. | Optional. Never feeds a gate. Printed with its context. |
| 8 Impact | 8.11 measurement (before_window, after_window, run_rate_start, validated_by) | The periods each state was measured over, when the after-state began, and who on the client side accepted the numbers. | Run-rate start places the result in the hold period. |
| 9 Technical | 9.1 architecture | Summary, at layer level. |  |
| 9 Technical | 9.2 integrations[] | Systems connected, and how: API, staging table, file. |  |
| 9 Technical | 9.3 decomposition | The workflow broken into nodes, with the recipe per node. | Named, not explained. |
| 9 Technical | 9.4 agentic | Where reasoning replaced rules; memory; control gates. |  |
| 9 Technical | 9.5 constraints | What shaped the build: precision bar, volume, data quality. |  |
| 9 Technical | 9.6 hosting | Where it runs and why: client tenancy, region, data residency. |  |
| 10 Proof | 10.1 quote (text, who, title, permission) | The client's words, verbatim, and who said them. | Attribution follows the front-matter permission. |
| 10 Proof | 10.2 demo (done, link, deliverable_link, data_status, access) | Whether a demo exists; its link, otherwise the link to the final deliverable; whether it runs on anonymised or demo data; access details. | Expected on every flagship. Never on live client records. Mirrored in the tracker. |
| 11 Forward | 11.1 assets | What the client keeps: the core, the memory, trained owners. |  |
| 11 Forward | 11.2 next | The next step agreed, if one was. | Absent is fine. |
| 11 Forward | 11.3 compounds | What the next workflow inherits and why it costs less. |  |
| 12 Coverage and routing | 12.1 status[] | One line per section: present, partial, absent, n/a. | Generated from the body, never typed. |
| 12 Coverage and routing | 12.2 formats[] | Every format the file supports right now, from the gates below. | Mirrored in the tracker's Formats column. |
| 12 Coverage and routing | 12.3 next_unlock | The single smallest thing that would move the file up one rung. | This is the delivery ask. |
| 12 Coverage and routing | 12.4 headline_grades | The grade of each L1 and of the L2. | Estimated cannot headline. |
| 13 Evidence appendix | 13.n.source_id | Matches an entry in sources[]. | Append-only. Nothing here is rewritten. |
| 13 Evidence appendix | 13.n.type, date, author | Slack thread, SOW, scoping document, voice-note transcript, demo link, screenshot description. | Voice transcripts flagged as such. |
| 13 Evidence appendix | 13.n.excerpt | The relevant passage, verbatim. | Never paraphrased. A challenged figure is answered with a pointer here. |
| 13 Evidence appendix | 13.xref[] | Fact to source cross-reference, so the trail runs both ways. | Generated. |
| 14 Gaps and asks | 14.n.field | The empty field, by key. | Derived from section 12. Nothing is written in the body. |
| 14 Gaps and asks | 14.n.ask | Who to ask, and the exact question. | At most five sent at once. |
| 14 Gaps and asks | 14.n.unlocks | What answering it moves, for example quarter to one-pager. | Ordered by unlock, highest first. |
