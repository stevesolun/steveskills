---
name: number-trace
description: "Summarise a paper, a report or a data analysis so that every number in the summary traces to the source text or to an output the analysis computed, and every number that does not is named as assumed, remembered or missing. Use when summarising a paper or report with its key numbers, writing up an analysis of a data file, or when a document with figures is about to be sent as a faithful account of a source. Not for prose with no numbers; that is a citation check."
metadata:
  author: Steve Solun
  version: "1.1"
---

# Number Trace

The numbers are what a reader takes from a summary, and they are also what a summariser is most likely to round, remember or invent. A **trace** is the link from each number in the summary back to the place it came from: a line of the source, a cell of a table, a row of the analysis output. Numbers with a trace are quoted; numbers without one are labelled; nothing in between.

## 1. Fix the source set

Name the files the summary is allowed to draw on: the paper's text (PDF text layer or a text export), the report, the data file and the analysis output log. Where the task is a data analysis, the analysis writes every figure it computes to a log file first, and that log is a source. Material from memory is outside the set.

**Done when** the source files are listed with paths and each one has extractable text (a scanned PDF with no text layer is reported, and its figures are out of reach).

## 2. Write the summary with numbers quoted, not rounded

Quote each number as the source prints it (units, precision, the table or section it sits in). Where the summary needs a derived figure (a difference, a ratio, a per-year rate), compute it from quoted inputs, show the inputs beside it and mark it `(computed from ...)`. A figure the sources do not carry is marked `(assumed ...)`, `(estimated ...)` or `(from memory)` in the same sentence, or left out.

**Done when** every sentence with a number also names where the number sits in the source, or carries its label.

## 3. Trace

Run `scripts/number-trace.py --doc SUMMARY.md SOURCE [SOURCE ...]`. It takes each number in the summary with its unit (10 ms, 45%, 2.5 GB/s, 6-7 round trips) and searches the sources for that number with that unit; dates, versions and section, figure, table and reference numbers are skipped as labels. One row per number: the source line it matched, `labelled` with the label's kind, or NOT FOUND; then `numbers: N in doc, F found, L labelled, M not found`. `--help` has the matching rules.

**Done when** the trace has run on the summary as it will be sent.

## 4. Resolve every NOT FOUND

Each unfound number is one of: a derived figure (show the computation from quoted inputs and mark it `(computed from ...)`), a number from memory or outside the set (mark it `(assumed)` or remove it), a transcription error (fix it), or a figure the source carries only in an image (say "the paper reports it in Figure 3; the text does not carry the value"). A number whose part of the source could not be found is reported as such rather than estimated. A found number is checked once by eye against the source line the trace printed: the same figure can appear in a source with another meaning.

**Done when** the trace's exit code is 0 (every number found or labelled) and the found rows read right against their source lines.

## 5. Close with what the source does not say

End the summary with the questions the source leaves open and the details that could not be found, so the reader knows the edge of what was read.

**Done when** the open questions and the unfound details are listed, and the trace output is saved beside the summary.
