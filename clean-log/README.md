# clean-log

An agent skill that cleans a data file by script and ships it with a change log computed from the two files: rows removed and added, columns changed, and per column how many cells changed and how, with examples and checksums. By Steve Solun. MIT.

## What it does

It separates the cleaning from the description of the cleaning. The cleaning is a script, one named rule per step, with dropped rows written to a side file; the log is then computed from the raw and cleaned files after the fact, so it says what changed, how many times, with examples, and it cannot disagree with the data. A cleaned file whose changes are described from memory has been edited twice, once by the cleaning and once by the description, and the second edit is the one nobody checks.

## When to reach for it

Type `/clean-log`, or the agent reaches for it on its own when a task fits: being asked to clean, normalise, dedupe or fix a data file, or a cleaned file about to replace a raw one.

| Situation | Reach for |
| --- | --- |
| A data file is being cleaned and the recipient needs to know every change | this skill |
| A number from the data is leaving the session and needs its provenance | [with-receipts](../with-receipts) |
| The cleaned file feeds questions whose answers must stay right afterwards | [answer-key](../answer-key) |

Transforming data into a different shape is a pipeline, and its log is a diff of outputs.

## Prerequisites

Python 3, the raw and cleaned files as CSV, and a column that identifies a row (`--key`); without one, rows are matched by position. The cleaning script itself can be in any language the project uses.

## The log

The **log** is computed, never narrated. It reads only the two files and prints the rows before and after with removed, added, kept and duplicate keys; the columns added, removed or renamed; per column the number of cells changed, broken down by kind (whitespace, case, normalised, number format, date format, blank filled, blanked, value replaced) with examples; and both checksums. Every line of it has to be explained by a rule in the script. A kind no rule intended, a date format change where only trimming was meant, a value replaced in a column the script never touched, is a bug in the script, found before the file ships rather than after.

```text
clean-log.py RAW.csv CLEAN.csv --key <id column> [--sample N]
```

The cleaned file goes out with the script, the log and the dropped-rows files beside it: the log is the change description, and the script is how to do it again on the next export.

## Common questions

**The log lists a change I did not mean to make.**
That is the log doing its job. In the sample run the rule "give each email its most frequent display name" turned a real name into a handle for one contributor; a narrated log would have said "normalised author names" and moved on. A kind no rule intended is a bug in the script, fixed before the file ships; a rule that did what it was told but should not have is a rule to revisit, and the log is where that shows.

**What happens to the rows I dropped?**
They go to a side file with the rule that dropped them, so every row that leaves has a trace, and the arithmetic closes: rows after equal rows before minus the rows in the dropped-rows files.

**I know what my script did. Why compute the log?**
Because a change description written by the cleaner is the cleaner grading itself. The computed log has the same counts whoever ran the cleaning, and the trim rule that changed nothing shows as nothing, by omission, rather than as a claim in a paragraph.

## It's working if

- The log in the handover was printed by the script from the two files, and every change kind in it maps to a named rule in the cleaning script.
- The row arithmetic closes: rows after equal rows before minus the rows in the dropped-rows files, by key.
- Both checksums appear in the log, and rerunning the script on the raw file reproduces the cleaned file's checksum.

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

## Where it fits

A reach-for-it-anytime standalone for the data role, at the moment a file changes hands. Its neighbours are [with-receipts](../with-receipts), because the first number computed from the cleaned file needs a source line that names which file, with which checksum, and [answer-key](../answer-key), because a cleaned file replacing a raw one is a change the key should run against. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=clean-log
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
clean-log/
├── SKILL.md                   # the skill
├── agents/openai.yaml         # Codex and ChatGPT picker metadata
└── scripts/clean-log.py       # the change log from two CSVs; --help for options
```

## License

MIT
