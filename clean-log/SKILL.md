---
name: clean-log
description: "Clean a data file as a script with a change log computed from the files: rows removed and added, columns changed, and per column how many cells changed and how (whitespace, case, normalised, number or date format, blanks filled, values replaced), with checksums of both files. Use when asked to clean, normalise, dedupe or fix a data file, or when a cleaned file is about to replace a raw one. Not for transforming data into a different shape; that is a pipeline, and its log is a diff of outputs."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Clean Log

A cleaned file whose changes are described from memory has been edited twice: once by the cleaning and once by the description. The **log** is computed from the two files after the fact, so it says what changed, how many times, with examples, and it cannot disagree with the data.

## 1. Keep the raw file

The raw file stays as it arrived. It is copied, its checksum is recorded, and every cleaning step reads from it or from the previous step's output.

**Done when** the raw file is untouched and its sha256 is in the notes.

## 2. Clean by script, one rule per step

Write the cleaning as a script (any language the project uses): one named rule per step, in order, each with the condition it matches and the change it makes. Trimming, case, encodings, number and date formats, blanks, duplicates by key, rows that fail a validation rule. Rules that drop rows write the dropped rows to a side file with the rule that dropped them, so every row that leaves has a trace.

**Done when** the script runs end to end from the raw file and produces the cleaned file plus the side files of dropped rows.

## 3. Compute the log

Run `scripts/clean-log.py RAW.csv CLEAN.csv --key <id column>`. It prints rows before and after with removed, added, kept and duplicate keys; columns added, removed or renamed; per column the number of cells changed, broken down by kind with examples; and both checksums.

**Done when** the log is in the working notes and every number in it is explained by a rule in the script.

## 4. Reconcile the log with the rules

Every change kind the log reports maps to a rule that intended it. A kind no rule intended (a date format change where only trimming was meant, a value replaced in a column the script never touched) is a bug in the script, fixed before the file ships. Row counts in the log equal the raw count minus the rows in the dropped-rows files.

**Done when** each line of the log is matched to a rule and the row arithmetic closes.

## 5. Ship the file with the log

The cleaned file goes out with the script, the log and the dropped-rows files beside it. The log is the change description; the script is how to do it again on the next export.

**Done when** the recipient has the four artifacts and can rerun the script on the raw file to get the same checksum.
