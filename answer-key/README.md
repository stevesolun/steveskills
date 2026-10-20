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
