# answer-key

An agent skill that keeps a file of data questions with known answers, runs it against the database or warehouse on every change to the data model, the metric definitions or the analysis skill, logs every run, and gates on the pass rate.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=answer-key
```

```bash
npx skills@latest update answer-key
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

An analytics agent is only as accurate as the last time someone checked, and nobody checks on the day it drifts. Anthropic's data team published the numbers from their own warehouse agent: without curated skills and docs, accuracy on their internal question set stayed at 21 percent; with them it ran above 95 percent; and when they stopped maintaining the skills, offline accuracy fell from about 95 to about 65 percent within a month, while the agent kept answering. Their fix is an eval set of question-answer pairs run in CI, each run recorded with the skill version, git SHA and model, and a launch gate per domain of about 90 percent.

`answer-key` is that practice as one file and one command. The key holds questions in the stakeholder's words, the query that answers each, the verified expected value and a tolerance, anchored to closed windows so the answers stay true. The script runs it, prints pass or FAIL per question with expected and actual, logs the run with its git SHA and label, and exits 1 below the gate. Corrections from stakeholders become rows, so the key grows from what people were wrong about.

## How it runs

The agent reaches for it when a data model, metric definition, reference doc or data skill is about to change, when an analytics agent is about to be launched to stakeholders, or when a stakeholder corrects a number. Typing `/answer-key` works too.

1. **Write the key.** `id, question, query, expected, tolerance`, verified by a person, anchored to a snapshot.
2. **Run it.** `answer-key.py KEY.csv --sqlite DB` or `--runner '<warehouse cli> {query_file}'`, with `--log results.csv --label <skill version or model>`.
3. **Read a failure as a finding**: stale expected value, moved definition, or a wrong answer; each id gets a verdict and an owner.
4. **Gate.** `--gate 0.9` to launch a domain, higher once live; a change merges only at exit code 0.
5. **Harvest corrections** into new rows, and fix the definition where it lives.

## Sample output

A real run on a SQLite copy of the bug tracker in [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`, with six questions, one of them carrying an expected value from before the last triage pass.

```text
$ answer-key.py key.csv --sqlite bugs.sqlite --gate 0.9 --label tracker-v1 --log answer-key-log.csv
id         verdict      expected       actual  question
K1         pass               92           92  How many bugs are in the tracker?
K2         pass               11           11  How many P0 bugs?
K3         pass             81.5         81.5  Share of bugs marked Fixed (percent)
K4         pass                6            6  Open (not Fixed) P0 or P1 bugs
K5         pass           trials       trials  Journey with the most bugs
K6         FAIL                9            7  Deferred bugs (a stale expected value, from before the last triage)

answer key: 5 of 6 pass (83%); failed K6; errors none; 0.0s
logged to answer-key-log.csv
```

Exit code 1: 83 percent is under the 90 percent gate. The log row:

```text
time,git_sha,key_sha,label,n,pass,rate,elapsed_s,failed_ids
2026-10-20T13:38:45,11b582a7,148c47fdbb16,tracker-v1,6,5,0.833,0.0,K6
```

K6 is the first kind of failure, a stale expected value: the tracker moved from 9 deferred bugs to 7 and the key did not. The fix is a new verified value with the person who closed the two, and the log keeps the run that caught it.

## Why a script

An accuracy claim about an analytics agent is a number that was true on one day. `answer-key.py` turns it into a run that leaves a row: when, which commit, which key, which label, how many passed, which ids failed. Two rows apart show drift; the gate stops a change that would lower the rate; the failed ids say where to look.

## Files

```text
answer-key/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/answer-key.py       # runs the key, logs the run, gates on the rate; --help for options
```

## License

MIT
