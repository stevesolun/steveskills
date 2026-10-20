---
name: answer-key
description: "Keep a file of data questions with known answers, run it against the warehouse or database on every change to the data model, the metric definitions or the analysis skill, and gate on the pass rate, with each run logged so drift is visible. Use when a data model, metric definition, reference doc or data skill is about to change, when an analytics agent is about to be launched to stakeholders, or when a stakeholder corrects a number. Not for a one-off query; that is a receipt, not a key."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Answer Key

An analytics setup is accurate on the day it is checked and drifts from then on: tables are renamed, definitions move, a doc goes stale, and the agent keeps answering with the same confidence. The **key** is a file of questions whose answers are known, anchored to a snapshot so they stay true, run as a test suite: the pass rate is the accuracy, the log is the drift, and the gate decides whether anything ships.

## 1. Write the key

One row per question: `id, question, query, expected, tolerance`. The question in the stakeholder's words, the query that answers it against the governed source, the expected value as it was verified by a person, and a tolerance where the value is a rate or an estimate. Anchor each row to a stable snapshot (a frozen table, a date window that is complete and closed) so the expected value does not move with the data. Start with the questions the blessed dashboards already answer, then the ones stakeholders actually ask, then every correction a stakeholder has ever sent.

**Done when** the key has at least a few dozen rows per domain, each verified by a person against the dashboard or the source, and none depends on today's date.

## 2. Run it

`scripts/answer-key.py KEY.csv --sqlite DB` or `--runner '<command> {query_file}'` for any warehouse CLI that prints the first value. It prints pass, FAIL or ERROR per row with expected and actual, then `P of N pass`. With `--log results.csv` it appends time, git SHA, key checksum, a label (model, skill version), the counts, the rate and the failed ids, so every run is a row that can be compared with the last.

**Done when** the run has a row in the log with its label and git SHA.

## 3. Read a failure as a finding

A FAIL is one of three things, decided by reading the row and the source once: the data changed (the expected value is stale; update it with the person who verified it), the definition changed (the query or a doc behind it moved; fix the doc and the query together), or the answer is wrong (the bug). An ERROR is a missing table or a dead connection. The verdict is written next to the id in the run's notes.

**Done when** every failed or errored id has a verdict and an owner.

## 4. Gate

A change to the data model, the metric definitions, a reference doc or the analysis skill merges only when the key passes the gate: `--gate 0.9` to launch a domain, higher once it is live, and at least the last logged rate unless a written reason lowers it. A domain is announced to stakeholders once its slice of the key clears the gate, with the exit code 0 run in the log.

**Done when** the gate exit code is 0 on the change as it will merge, and the log shows the rate did not fall.

## 5. Harvest corrections

Every correction a stakeholder sends ("reactivated accounts should not count as signups") becomes a new row in the key, with the corrected value as expected and the definition fixed where it lives. The key grows from what people were wrong about; that is where the next wrong answer lives.

**Done when** the correction is a row, the row passes, and the definition that caused it is fixed in its source, not only in the query.
