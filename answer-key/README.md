# answer-key

An agent skill that keeps a file of data questions with known answers, runs it against the database or warehouse on every change to the data model, the metric definitions or the analysis skill, logs every run, and gates on the pass rate. By Steve Solun. MIT.

## What it does

It turns "the analytics agent is accurate" from a claim into a run that leaves a row. The key holds questions in the stakeholder's words, the query that answers each, the expected value a person verified and a tolerance, anchored to closed windows so the answers stay true. Each run prints pass or FAIL per question with expected and actual, logs the run with its git SHA and label, and exits 1 below the gate. The pass rate is the accuracy, the log is the drift, and a change to the data model, a definition or a skill merges only on an exit code of 0.

## When to reach for it

Type `/answer-key`, or the agent reaches for it on its own when a task fits: a data model, metric definition, reference doc or data skill is about to change; an analytics agent is about to be launched to stakeholders; a stakeholder corrects a number.

| Situation | Reach for |
| --- | --- |
| A set of questions must keep answering right across changes, with a gate | this skill |
| One number is leaving the session today | [with-receipts](../with-receipts) |
| A cleaned file is replacing a raw one and the changes need a log | [clean-log](../clean-log) |

A one-off query is a receipt, not a key.

## Prerequisites

Python 3 and a way to run the key's queries: a SQLite file (`--sqlite`) or any warehouse CLI that prints the first value of a query (`--runner '<command> {query_file}'`). A person to verify each expected value against the dashboard or the source before it goes in, and a git repository so each run can record its SHA.

## The key

The **key** is a file of questions whose answers are known, run as a test suite. Accuracy on an analytics setup is true on the day it is checked and drifts from then on: tables are renamed, definitions move, a doc goes stale, and the agent keeps answering with the same confidence. Anthropic's data team published the numbers from their own warehouse agent: without curated skills and docs, accuracy on their internal question set stayed at 21 percent; with them it ran above 95 percent; and when they stopped maintaining the skills, offline accuracy fell from about 95 to about 65 percent within a month, while the agent kept answering. Their fix is an eval set of question-answer pairs run in CI, each run recorded with the skill version, git SHA and model, and a launch gate per domain of about 90 percent. The key is that practice as one file and one command.

```text
answer-key.py KEY.csv --sqlite DB | --runner '<command> {query_file}' [--gate 0.9] [--label <skill version or model>] [--log results.csv]
```

The key's rows are `id, question, query, expected, tolerance`. The run prints one row per question, `pass`, `FAIL` or `ERROR` with expected and actual, then `P of N pass (rate)`, the failed ids and the errors. With `--log` it appends time, git SHA, key checksum, label, counts, rate and failed ids, so two rows apart show drift. With `--gate` it exits 1 below the rate. Corrections from stakeholders become new rows, so the key grows from what people were wrong about.

## Common questions

**A row fails. Is the agent wrong?**
One of three things, decided by reading the row and the source once: the data changed (the expected value is stale, as with K6 in the sample run, where one more large commit landed after the tag the value was verified at), the definition changed (the query or a doc behind it moved; fix both together), or the answer is wrong. An ERROR is a missing table or a dead connection. Each failed id gets its verdict and an owner next to it.

**Where do the expected values come from?**
From a person checking the dashboard or the source with an independent command, never from the agent that will be tested. A first draft of the sample key had two values written from memory (a first-commit date of 2013, a share of 68.6 percent), and both failed against the data; that is the key doing its job on its author.

**How many rows does a domain need?**
A few dozen, each anchored to a closed window so it does not move with the data. Start with the questions the blessed dashboards already answer, then the ones stakeholders actually ask, then every correction a stakeholder has ever sent.

## It's working if

- Every run leaves a row in the log with its git SHA, label, pass count and failed ids, so the rate can be compared with the last run.
- A FAIL has a verdict beside it (stale value, moved definition, or wrong answer) and an owner, rather than a rerun until green.
- A change to the data model, a definition or a skill merges only after a run with exit code 0 at the gate, and the rate did not fall between consecutive rows.

A real run over the git history of [vuejs/vue](https://github.com/vuejs/vue) (212k stars), clone at `9e887079`, loaded into SQLite as one row per commit. Six questions; every expected value was verified with an independent `git` command before it went into the key, except K6, whose value was verified at the `v2.7.0` tag and left there on purpose.

```text
$ answer-key.py key.csv --sqlite vue.sqlite --gate 0.9 --label commits-v1 --log answer-key-log.csv
id         verdict      expected       actual  question
K1         pass             3593         3593  How many commits are in the repository?
K2         pass               46           46  How many commits landed in 2023?
K3         pass         Evan You     Evan You  Who authored the most commits?
K4         pass             71.9         71.9  What share of all commits did the top author write (percent)?
K5         pass       2016-04-10   2016-04-10  When was the first commit?
K6         FAIL              228          229  How many commits touched 10 or more files? (expected value verified at

answer key: 5 of 6 pass (83%); failed K6; errors none; 0.0s
logged to answer-key-log.csv

$ cat answer-key-log.csv
time,git_sha,key_sha,label,n,pass,rate,elapsed_s,failed_ids
2026-10-20T14:01:57,9e887079,993e848f2e8c,commits-v1,6,5,0.833,0.0,K6
```

Exit code 1: 83 percent is under the 90 percent gate. K6 is the first kind of failure, a stale expected value: one more large commit landed after 2.7.0 and the key did not move. The run before this one is worth telling too: a first draft of the key had two values written from memory (a first-commit date of 2013, a share of 68.6 percent), and both failed against the data. That is the key doing its job on its author.

## Where it fits

Periodic maintenance and a gate for the data role: it runs on every change and before every launch rather than once. Its neighbours are [with-receipts](../with-receipts), because a receipt proves one number on one day and the key is what keeps the rest of them right afterwards, and [clean-log](../clean-log), because a cleaned file that replaces a raw one is exactly the kind of change that moves a key's expected values. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=answer-key
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
answer-key/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/answer-key.py       # runs the key, logs the run, gates on the rate; --help for options
```

## License

MIT
