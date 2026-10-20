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

A real run on the bug tracker in [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7` (92 rows). Question as resolved: P0 or P1 bugs whose fix status is anything other than Fixed, per journey, whole tracker. Route A is a Python pass over the CSV, route B is SQL over the same rows in SQLite.

```text
$ receipts.py compare open_python.csv open_sql.csv --key journey --value n
key                                   A              B        delta  verdict
budget                                4              4           +0  agree
recommend                             1              1           +0  agree
trials                                1              1           +0  agree

cross-check: 3 agree, 0 disagree, 0 only on one side (tolerance 0)
```

The same question with "open" read as Deferred only, the other reading a reader could take, gives a different table, and the script says so instead of averaging it away:

```text
$ receipts.py compare open_python.csv open_deferred_only.csv --key journey --value n
key                                   A              B        delta  verdict
budget                              4.0              -               only on one side
recommend                             1              1           +0  agree
trials                              1.0              -               only on one side

cross-check: 1 agree, 0 disagree, 2 only on one side (tolerance 0)
```

Exit code 1. The receipt then names the definition the number follows. The decomposition and the footer check:

```text
$ receipts.py sum open_python.csv --value n --total 6
sum of 3 parts = 6; reported total = 6; delta +0; parts add up (tolerance 0)

$ receipts.py footer answer.md
  question     ok    P0 or P1 bugs whose fix_status is not Fixed (Already Fixed and Deferred both count), per j
  source       ok    qa/ctx_fit_bug_tracker.csv at 11b582a7 (92 rows)
  freshness    ok    tracker rows carry no date; file last changed in commit 11b582a7
  query        ok    select journey, count(*) from bugs where severity in ('P0','P1') and fix_status<>'Fixed' g
  cross-check  ok    same count from a python pass over the CSV with the same definition
  delta        ok    0 on 3 of 3 journeys; a reading of "open" as Deferred only gives 1, so the definition abov
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
