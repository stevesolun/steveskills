# deeper

An agent skill that rewrites a task for expert depth, not size: before the work starts it names what a top practitioner would do that was not asked, the rawest material they would start from, the instruments they would use and the outside check that proves the result, rewrites the prompt to ask for exactly that, measures the rewrite, and runs it against that check.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=deeper
```

```bash
npx skills@latest update deeper
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Asked to work like an expert, a model swaps its vocabulary and keeps its methods: it says "cohort analysis" and produces a markdown table. The bigger version of a task has the same problem with more words. The deeper version is the same task done the way the best people in the field do it: from raw material instead of summaries, with the field's real instruments, proven by something other than the model's own review.

The technique comes from Felix Rieseberg's post [How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (October 2026), which also makes the point this skill enforces hardest: do not ask the model to judge itself. Insist on outside validation, ideally a tool it can run.

`deeper` does one thing: turn an ordinary prompt into that version, show the difference in numbers, and make the outside check the definition of done.

## How it runs

The agent reaches for it when you ask for a deeper, more expert or more rigorous version of a task, or when a task is about to run on summaries, generic methods and self-review. Typing `/deeper` followed by the prompt works too. `--full` adds the outcome behind the task and the other fields that would attack it; `--run` skips the stop before execution.

1. **Name the depth.** Five points, one or two lines each: the expert gap, the raw inputs, the instruments, the outside proof, the assumptions to test.
2. **Rewrite and measure.** A self-contained prompt that asks for exactly that, ending with a definition of done that is the outside check. `scripts/depth-check.py` (Python, standard library only) counts the five markers in the original and the rewrite, flags role-play without instruments and requests for self-review, and says whether the rewrite is deeper or just bigger.
3. **Pre-flight.** Access, tools to install, and the outside check wired up before the task starts. Then one question: run it?
4. **Run and prove.** The rewrite runs in a fresh context. The outside check's verdict comes first; a failure is reported as a failure.

## Sample output

A one-line churn prompt, rewritten:

```text
                      original   rewrite
words                       25       152
raw inputs named             0         7   events.parquet, raw data, subscriptions table in Po... (+4)
instruments named            0        11   duckdb, analysis/churn.sql, lifelines (+8)
outside proof                0         5   held-out month, reproduces, measured (+2)
definition of done           0         2   Definition of done, passes when
assumptions tested           0         2   Test whether, We believe
role-play phrases            2         0
self-review asks             2         0
depth markers              0/5       5/5
flags               original: role-play without instruments; self-review asked for

Verdict: deeper. Markers 0/5 -> 5/5, 6.1x the words.
```

The same original rewritten the usual way, with more sections, more coverage and "make sure it is correct":

```text
Verdict: bigger, not deeper. 3.5x the words, markers 0/5 -> 0/5.
```

The script exits 0 only when the last prompt carries at least four of the five markers and no flags, so it can gate a rewrite.

## Why a script

The counts are word lists and patterns. They measure whether the prompt names concrete things (a file, a tool, a held-out month, a belief to test), not whether the things named are the right ones; that is what step 4 is for. The number is there so the difference between a deeper prompt and a longer one is visible before anything expensive runs, and so the skill's own claim can be checked.

## Files

```text
deeper/
├── SKILL.md                  # the skill
├── agents/openai.yaml        # Codex picker metadata
└── scripts/depth-check.py    # counts depth markers in a prompt; --help for options
```

## License

MIT
