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

A real cleaning pass over the author table of [vuejs/vue](https://github.com/vuejs/vue) (212k stars): one row per commit with the author name and email as git recorded them, 3,593 rows. Three rules: trim every cell, lower-case the email, and give each email one display name (the name it was recorded with most often). Fourteen emails had been recorded under more than one name.

```text
$ clean-log.py authors-raw.csv authors-clean.csv --key sha --sample 3
before: authors-raw.csv (3593 rows, 4 cols, sha256 4b91e8e56145)
after:  authors-clean.csv (3593 rows, 4 cols, sha256 8d80fa138970)

columns: 4 after (0 added, 0 removed)

rows (by sha): 3593 -> 3593; removed 0, added 0, kept 3593; duplicate keys before 0, after 0

cells changed in kept rows: 107 across 2 columns
  email: 61 changed; case 61
      case: '43554061+Moriango@users.noreply.github.c' -> '43554061+moriango@users.noreply.github.c'
      case: '67939848+Rudeus3Greyrat@users.noreply.gi' -> '67939848+rudeus3greyrat@users.noreply.gi'
      case: 'Orkhan.Alikhanov@gmail.com' -> 'orkhan.alikhanov@gmail.com'
  author: 46 changed; value replaced 45, case 1
      value replaced: 'Carlos Rodrigues' -> 'pikax'
      value replaced: 'Carlos Rodrigues' -> 'pikax'
      value replaced: 'Carlos Rodrigues' -> 'pikax'
      case: 'pooya parsa' -> 'Pooya Parsa'

change log: rows 3593->3593, columns 4->4, cells changed 107
```

Every line maps to a rule: the 61 email changes are rule two, the 46 author changes are rule three, and the trim rule changed nothing, which the log states by omission rather than the write-up claiming otherwise. The log also surfaces a rule choice to revisit: "most frequent name" turned a real name into a handle for one contributor, which is exactly the kind of change a narrated log would have described as "normalised author names" and moved on.

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
