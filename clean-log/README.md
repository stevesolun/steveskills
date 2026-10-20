# clean-log

An agent skill that cleans a data file by script and ships it with a change log computed from the two files: rows removed and added, columns changed, and per column how many cells changed and how, with examples and checksums.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=clean-log
```

```bash
npx skills@latest update clean-log
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

"Clean a data file with a log of every change" is one of the standard asks of a data team, and the usual output is a cleaned file plus a paragraph: trimmed whitespace, normalised statuses, dropped some duplicates. The paragraph was written by the same process that did the cleaning, so it inherits every mistake and omits every surprise. A rule that touched a column it was not meant to touch is invisible in it.

`clean-log` separates the two. The cleaning is a script, one named rule per step, with dropped rows written to a side file. The log is then computed from the raw and cleaned files after the fact: row counts by key, columns added, removed or renamed, and for each column the number of cells changed broken down by kind (whitespace, case, normalised, number format, date format, blank filled, value replaced) with examples, plus both checksums. Every line in the log has to be explained by a rule; a kind no rule intended is a bug.

## How it runs

The agent reaches for it when asked to clean, normalise, dedupe or fix a data file, or when a cleaned file is about to replace a raw one. Typing `/clean-log` works too.

1. **Keep the raw file**, copy it, record its checksum.
2. **Clean by script, one rule per step**, dropped rows to a side file with the rule that dropped them.
3. **Compute the log.** `clean-log.py RAW.csv CLEAN.csv --key <id column>`.
4. **Reconcile the log with the rules.** Every change kind maps to a rule; the row arithmetic closes.
5. **Ship the file with the log**, the script and the dropped-rows files.

## Sample output

A real cleaning pass over the benchmark status tracker in [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`: trim every cell, lower-case the area, turn the status into a slug, drop rows without an id and duplicate ids.

```text
$ clean-log.py qa/ctx_benchmark_status.csv bench_clean.csv --key id
before: qa/ctx_benchmark_status.csv (43 rows, 11 cols, sha256 8180b6dc57b7)
after:  bench_clean.csv (43 rows, 11 cols, sha256 d80a8f5c82a2)

columns: 11 after (0 added, 0 removed)

rows (by id): 43 -> 43; removed 0, added 0, kept 43; duplicate keys before 0, after 0

cells changed in kept rows: 43 across 1 columns
  status: 43 changed; case 29, normalised 14
      case: 'Resolved' -> 'resolved'
      case: 'Resolved' -> 'resolved'
      normalised: 'Needs Validation' -> 'needs-validation'
      normalised: 'Needs Validation' -> 'needs-validation'

change log: rows 43->43, columns 11->11, cells changed 43
```

Two rules were written for the area column and for whitespace; the log shows zero cells changed in either, which is the reconciliation step doing its job: the file had no stray whitespace and the areas were already lower case, so those rules did nothing, and the log says so instead of the paragraph claiming they did.

## Why a script

A change description written by the cleaner is the cleaner grading itself. `clean-log.py` reads only the two files, so its counts are the same whoever ran the cleaning, and a rule that did more than it was meant to shows up as a change kind nobody intended.

## Files

```text
clean-log/
├── SKILL.md                   # the skill
├── agents/openai.yaml         # Codex picker metadata
└── scripts/clean-log.py       # the change log from two CSVs; --help for options
```

## License

MIT
