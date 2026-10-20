---
name: with-receipts
description: "Deliver a number from data with its receipt: the question as resolved (entity, grain, window, timezone, filters, denominator), the source and its freshness taken from the data, the query as it ran, a second route to the same number with the delta, and a reviewer who did not write the query. Use when answering a data question with a number, producing a metrics report, or when a number is about to go to a stakeholder, a board pack or a dashboard. Not for exploratory profiling with no number leaving the session."
metadata:
  author: Steve Solun
  version: "1.0"
---

# With Receipts

A number without its receipt is an opinion with digits. The **receipt** is what makes it checkable by someone who was not there: the question as actually resolved, the source and how fresh it is, the query that ran, a second route that lands on the same number, and the name of the person or agent who tried to break it. The receipt travels with the number, in the same message, every time.

## 1. Resolve the question

Write the question as one line that names the entity (which "users", which "orders"), the grain (one row is one what), the window (the last complete calendar period unless the asker said otherwise), the timezone, every filter and exclusion, and the denominator of any rate. Terms you do not recognise are looked up in the data dictionary or the metric definitions, then confirmed with the asker, so every term in the line has a source. Use the asker's exact words for the headline so the answer lands on what they asked.

**Done when** the resolved question is one line with every item above filled in, and every ambiguous term has a source or an answer from the asker.

## 2. Pick the source and read its freshness

Prefer a governed metric definition or certified table over a raw table, and a raw table over a dashboard export. Freshness is the newest date in the data (the extract's own maximum, rather than the calendar): run `scripts/receipts.py freshness DATA.csv --date-col <col>` on the extract, or the equivalent `max(date)` in the query, and record it. A window that runs past the freshness date is cut back to the last complete period.

**Done when** the source is named with its path or table and the freshness line is recorded.

## 3. Run the query and keep it

Run it against the named source. Keep the query text exactly as it ran, with every filter visible. A column the source lacks is reported as a finding; division carries a guard for zero. Separate what the data shows (observations) from what it means (interpretations).

**Done when** the query, its row count and the resulting number are in the working notes verbatim.

## 4. Cross-check by a second route

Reach the same number a different way: a compiled metric against raw SQL, two sources, a decomposition whose parts must add up, or the blessed dashboard for the same period. Compare with `scripts/receipts.py compare A.csv B.csv --key <key> --value <value>` or `scripts/receipts.py sum PARTS.csv --value <value> --total <N>`. A disagreement is the finding: it usually means two definitions, and the receipt names which one the number follows.

**Done when** the compare or sum command exits 0, or the disagreement is explained in the receipt with both definitions.

## 5. Review by someone who did not write it

A reviewer that did not write the query (a subagent where the harness has one, otherwise a colleague) looks for the wrong entity, wrong window, missing filter, wrong denominator and a stale table. Blocking findings are fixed and re-reviewed. Sign-off comes from the reviewer, with the exit code of the checks beside it.

**Done when** the reviewer's name or role and round number are recorded with no open blocking finding.

## 6. Deliver with the footer

The answer ends with a `receipt:` block carrying `question`, `source`, `freshness`, `query`, `cross-check`, `delta` and `reviewed`. Run `scripts/receipts.py footer ANSWER.md`; its exit code is 0 only when all seven are present. Restricted or personal data: deliver the query and the receipt, and leave the rows in the warehouse.

**Done when** the footer check exits 0 and the asker has the number, the receipt and, where it helps, the saved query to rerun.
