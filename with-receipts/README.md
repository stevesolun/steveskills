# with-receipts

An agent skill that delivers a number from data with its receipt: the question as resolved, the source and its freshness taken from the data, the query as it ran, a second route to the same number with the delta, and a reviewer who did not write the query. One script checks the receipt.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=with-receipts
```

```bash
npx skills@latest update with-receipts
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Analytics is a context and verification problem before it is a code problem: most wrong answers come from picking a plausible wrong entity ("active users" with the wrong lookback), from a stale definition, or from a silent, plausible number that nobody challenged. Anthropic's own data team, writing about running most of its business analytics through an agent, reports that an adversarial review of every query bought about six points of accuracy and that every answer carries a provenance footer with source, freshness, reviewer and owner, because a wrong-but-plausible answer is the one failure nothing else catches.

`with-receipts` makes that footer the unit of delivery. A number goes out with the question as it was actually resolved (entity, grain, window, timezone, filters, denominator), the source and its freshness as the newest date in the data, the query as it ran, a second route that lands on the same number with the delta, and the reviewer who tried to break it. The script checks the pieces mechanically: two routes agree, parts add up, the freshness line is real, the footer is complete.

## How it runs

The agent reaches for it when a data question is answered with a number, when a metrics report is produced, or when a number is about to go to a stakeholder, a board pack or a dashboard. Typing `/with-receipts` works too.

1. **Resolve the question** in one line that names the entity, grain, window (the last complete period), timezone, filters and denominator; unknown terms are looked up, then confirmed.
2. **Pick the source and read its freshness.** `receipts.py freshness DATA.csv --date-col <col>`: the newest date in the data, rather than the calendar.
3. **Run the query and keep it** verbatim, with its row count.
4. **Cross-check by a second route.** `receipts.py compare A.csv B.csv --key k --value v` or `receipts.py sum PARTS.csv --value v --total N`. A disagreement is usually two definitions; the receipt names which one the number follows.
5. **Review by someone who did not write it**, with blocking findings fixed and re-reviewed.
6. **Deliver with the footer.** `receipts.py footer ANSWER.md` exits 0 only when all seven fields are present.

## Sample output

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

## Why a script

"I double-checked it" is the same witness twice. `receipts.py` makes the cross-check a comparison of two files, the freshness a max over a column, and the footer a list of seven fields with an exit code, so a reviewer, a pre-send hook or the next analyst can see what was checked without trusting the sentence that says it was.

## Files

```text
with-receipts/
├── SKILL.md                  # the skill
├── agents/openai.yaml        # Codex picker metadata
└── scripts/receipts.py       # freshness, compare, sum, footer; --help for options
```

## License

MIT
