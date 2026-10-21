# with-receipts

> **Archived.** Removed in 1.8.0. In four blind repetitions against a baseline skill set it won the two plain asks (the baseline gave the numbers with no query and no second route) and tied the two where the prompt asked for the receipt; two of four is under the bar. Nothing replaces it; [driver-split](../driver-split) and [ab-readout](../ab-readout) carry their own provenance lines. The page below is as it was.

An agent skill that delivers a number from data with its receipt: the question as resolved, the source and its freshness taken from the data, the query as it ran, a second route to the same number with the delta, and a reviewer who did not write the query. One script checks the receipt. By Steve Solun. MIT.

## What it does

It makes a number from data checkable by someone who was not there. The number goes out with the question as it was actually resolved (entity, grain, window, timezone, filters, denominator), the source and its freshness as the newest date in the data, the query as it ran, a second route that lands on the same number with the delta, and the reviewer who tried to break it. The receipt travels with the number in the same message, every time; a number without one does not leave the session.

## When to reach for it

Type `/with-receipts`, or the agent reaches for it on its own when a task fits: answering a data question with a number, producing a metrics report, or sending a number to a stakeholder, a board pack or a dashboard.

| Situation | Reach for |
| --- | --- |
| One number is leaving the session and someone will act on it | this skill |
| The same questions must stay right across every change to the data model or the definitions | [answer-key](../answer-key) |
| The number is known and the question is why it moved | [driver-split](../driver-split) |

Exploratory profiling with no number leaving the session needs no receipt.

## Prerequisites

Python 3. The extract as a CSV for the freshness, compare and sum commands (or the equivalent `max(date)` and comparison in the query itself), and a second route to the number: a compiled metric beside raw SQL, two sources, a decomposition whose parts must add up, or the blessed dashboard for the same period. The reviewer is a subagent where the harness has one, otherwise a colleague.

## The receipt

A **receipt** is the set of facts that lets a reader check a number without trusting the sentence that delivered it. Most wrong answers from data come from a plausible wrong entity ("active users" with the wrong lookback), a stale definition, or a silent, plausible number nobody challenged; Anthropic's own data team, writing about running most of its business analytics through an agent, reports that an adversarial review of every query bought about six points of accuracy and that every answer carries a provenance footer with source, freshness, reviewer and owner. The receipt is that footer as the unit of delivery, with the pieces checked mechanically rather than asserted.

```text
receipts.py freshness DATA.csv --date-col <col>
receipts.py compare A.csv B.csv --key <key> --value <value>
receipts.py sum PARTS.csv --value <value> --total <N>
receipts.py footer ANSWER.md
```

`freshness` prints the newest date in the data and its distance from today. `compare` prints one row per key with the delta and a verdict, `agree`, `DISAGREE` or `only on one side`, then the totals. `sum` checks that parts add up to a reported total. `footer` lists the seven fields of the `receipt:` block (`question`, `source`, `freshness`, `query`, `cross-check`, `delta`, `reviewed`) and exits 0 only when all seven are present.

## Common questions

**The two routes disagree. Which number goes out?**
The one whose definition the receipt names. A disagreement is usually two definitions rather than a bug: in the sample run, counting the committer instead of the author moved one count by one and put seventeen commits under "GitHub", because squash merges are committed by GitHub. The script reports the disagreement rather than averaging it away, and the `delta` line says which reading the headline follows.

**What counts as freshness?**
The newest date in the data, read from the extract or by `max(date)` in the query, rather than the calendar. In the sample run that was 740 days before the day of the run, which a window that ran to "last month" would have hidden. A window that runs past the freshness date is cut back to the last complete period.

**Who is the reviewer when I work alone?**
A subagent where the harness has one, otherwise a colleague, looking for the wrong entity, wrong window, missing filter, wrong denominator and a stale table. The footer needs the reviewer's name or role and the round number; the author of the query signing their own work is the one witness the receipt refuses.

## It's working if

- The number arrives with a `receipt:` block of seven lines, and the trace shows `receipts.py footer` printing `7 of 7 fields present`.
- A cross-check command ran, its verdict line is quoted next to the number, and a disagreement is explained as two definitions rather than smoothed over.
- The freshness line is a date read from the data, with its distance from today.
- The `reviewed` line names someone other than the query's author, with the round.

A real run on the git history of [vuejs/vue](https://github.com/vuejs/vue) (212k stars), clone at `9e887079`, exported to a CSV of 3,593 commits. Question as resolved: commits in calendar 2023, counted per author name, the whole repository. Route A is a Python pass over the export, route B is `git log` on the repository itself.

```text
$ receipts.py freshness vue-commits.csv --date-col date
freshness: 3593 rows, 3593 dated, max date = 2024-10-10, 740 days before today

$ receipts.py compare 2023_by_author_python.csv 2023_by_author_gitlog.csv --key author --value commits
key                                   A              B        delta  verdict
Adam Hines                            1              1           +0  agree
Evan You                             30             30           +0  agree
Grigorii K. Shartsev                  1              1           +0  agree
...
webfansplz                            4              4           +0  agree
xonx                                  2              2           +0  agree

cross-check: 13 agree, 0 disagree, 0 only on one side (tolerance 0)
```

The other reading of "whose commit", the committer instead of the author, gives a different table, and the script says so instead of averaging it away: squash merges are committed by GitHub.

```text
$ receipts.py compare 2023_by_author_python.csv 2023_by_committer.csv --key author --value commits
key                                   A              B        delta  verdict
Evan You                             30             29           -1  DISAGREE
GitHub                                -           17.0               only on one side
webfansplz                          4.0              -               only on one side
...
cross-check: 0 agree, 1 disagree, 13 only on one side (tolerance 0)
```

Exit code 1. The receipt then names the definition the number follows. The decomposition and the footer check:

```text
$ receipts.py sum 2023_by_author_python.csv --value commits --total 46
sum of 13 parts = 46; reported total = 46; delta +0; parts add up (tolerance 0)

$ receipts.py footer answer.md
  question     ok    commits whose author date falls in calendar 2023 (UTC dates as git records them), counted
  source       ok    git history of vuejs/vue, clone at 9e887079, exported to vue-commits.csv (3593 rows)
  freshness    ok    newest commit date in the export 2024-10-10, 740 days before today
  query        ok    git log --since=2023-01-01 --until=2024-01-01 --format=%aN HEAD | sort | uniq -c
  cross-check  ok    a python pass over vue-commits.csv with the same window and the same author-name column
  delta        ok    0 on 13 of 13 authors; counting the committer instead of the author gives Evan You 29 and
  reviewed     ok    second pass by a reviewer that did not write the query, round 1, no blocking findings
receipt: 7 of 7 fields present
```

Remove the `reviewed` line and the footer check reports `6 of 7 fields present; missing reviewed` with exit code 1.

## Where it fits

A reach-for-it-anytime standalone for the data role, and the one the other data answers end in: a split or a readout is still a number going to someone. Its neighbours are [answer-key](../answer-key), because a receipt covers one number on one day and the key keeps a whole set of them right over time, and [driver-split](../driver-split), because once the number has its receipt the next question is usually why it moved. The index of every skill is the [root README](../README.md#skills).

## Install

Not installable since 1.8.0; the folder holds this page only.

## Files

```text
with-receipts/
├── SKILL.md                  # the skill
├── agents/openai.yaml        # Codex and ChatGPT picker metadata
└── scripts/receipts.py       # freshness, compare, sum, footer; --help for options
```

## License

MIT
