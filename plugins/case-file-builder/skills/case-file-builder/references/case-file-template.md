# Case file template

Copy this skeleton exactly. Keep every heading and key, in this order, in every file. Fill a key only when the rules in `SKILL.md` allow it; otherwise leave the value blank (nothing after the colon). Never write "TBD", "n/a", "unknown" or "not provided" in sections 1 to 11.

A sourced value is written as: `value [S3, 2026-05-12]` (source id, then the as-of date). Prose sentences end with their source the same way. Inside YAML blocks, quote any string that carries a citation, and keep numbers bare with the source id in the `source` key. A date known only to the month is written `2025-10`.

````markdown
---
id:
slug:
client:
  real:
  label:
sector:
business_function:
value_driver:
shape:                      # single-workflow | transformation
dates:
  created:
  last_updated:
  last_dump_received:
engagement:                 # a value taken from a proposal or plan is followed by (planned)
  weeks:
  modules:
  gates:
  start:
  end:
permissions:                # every key blank = fully anonymised, no quote
  nameable:
  logo:
  metric_quotable:
  metric_precision:
  quote_attribution:
  embargo:
owner:
delivery_status:            # ongoing | delivered | accepted | no delivery evidence, with [S, date]
tracker_page:               # Notion URL of the Project Tracker row
sources:
  - id: S1
    type:                   # call-transcript | call-summary | email | sow | proposal | plan | document | deck | code | deal-record | tracker | demo-link | slack | voice-note
    date:
    author:
    path:                   # repo/path/to/file
coverage:                   # generated, mirrors section 12
verdict:                    # generated: none | quarter | half | one-pager | flagship
headline_grades:            # generated
---

## 1 Identity
updated:
### 1.1 client
### 1.2 chips
### 1.3 engagement
### 1.4 title

## 2 Situation
updated:
### 2.1 who
### 2.2 where
### 2.3 process_before
### 2.4 baseline

## 3 Problem
updated:
### 3.1 context
### 3.2 challenge
### 3.3 unit

## 4 Mandate
updated:
### 4.1 commissioned
### 4.2 placement
### 4.3 declined

## 5 Solution
updated:
### 5.1 plain
### 5.2 components
### 5.3 how_it_ran

## 6 Workflows
updated:
### 6.1 <workflow name>
```yaml
name:
owner:
systems: []
updated:
before: {unit: , value: , volume: , period: , as_of: , source: }
after:  {unit: , value: , volume: , period: , as_of: , source: }
delta:  {absolute: , pct: , direction: }      # productivity | efficiency
changed:
rate:   {value: , type: , source: , as_of: }
value:  {annual: , route: , cash: , capacity: , margin: }
validated_by:
grade:                                          # measured | modelled | estimated
```

## 7 Initiatives
<!-- single-workflow: write n/a on the next line and no blocks -->
updated:
### 7.1 <initiative name>
```yaml
name:
workflows: []
value_score:
feasibility_score:
sequence:
status:                                         # built | declined | deferred
reason:
```

## 8 Impact
updated:
### 8.1 L1
```yaml
- {figure: , before: , after: , label: , workflow: , as_of: , grade: }
```
### 8.2 gross
```yaml
annual:
basis:
reconciles:
```
### 8.3 costs
```yaml
fee:       {amount: , recurring: false, source: , as_of: }   # one line per phase when there are several
run:       {amount: , recurring: true,  source: , as_of: }
adoption:  {amount: , recurring: true,  source: , as_of: }
licence:   {amount: , recurring: true,  source: , as_of: }
displaced: {amount: , recurring: true,  source: , as_of: }
```
### 8.4 net.annual
### 8.5 net.year_one
### 8.6 payback
```yaml
months:
banded:
```
### 8.7 routes
```yaml
cash:
capacity:
margin:
```
### 8.8 capacity
```yaml
hours:
destination:
```
### 8.9 ebitda
```yaml
figure:
framing:
source:
usable:
```
### 8.10 sponsor
```yaml
ev:
moic:
irr:
```
### 8.11 measurement
```yaml
before_window:
after_window:
run_rate_start:
validated_by:
```

### 8.12 supporting
<!-- sourced figures that are not a before/after pair; never feed a gate -->
```yaml
- {metric: , value: , context: , source: , as_of: }
```

## 9 Technical
updated:
### 9.1 architecture
### 9.2 integrations
### 9.3 decomposition
### 9.4 agentic
### 9.5 constraints
### 9.6 hosting

## 10 Proof
updated:
### 10.1 quote
```yaml
text:
who:
title:
permission:
source:
```
### 10.2 demo
```yaml
done:
link:
deliverable_link:
data_status:
access:
```

## 11 Forward
updated:
### 11.1 assets
### 11.2 next
### 11.3 compounds

## 12 Coverage and routing
<!-- generated from sections 1-11; never typed -->
### 12.1 status
```yaml
1 Identity:
2 Situation:
3 Problem:
4 Mandate:
5 Solution:
6 Workflows:
7 Initiatives:
8 Impact:
9 Technical:
10 Proof:
11 Forward:
```
### 12.2 formats
### 12.3 next_unlock
### 12.4 headline_grades

## 13 Evidence appendix
<!-- append-only; excerpts verbatim, in the original language -->
### S1
```yaml
type:
date:
author:
path:
```
> verbatim excerpt

### 13.xref
<!-- generated: field key -> source ids -->

## 14 Gaps and asks
<!-- derived from section 12; ordered by unlock, highest first; top five marked send: true -->
```yaml
- field:
  ask:
  who:
  unlocks:
  send:
```
````
