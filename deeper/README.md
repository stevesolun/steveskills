# deeper

> **Archived.** Removed in 1.8.0. In four blind repetitions against a baseline skill set (two with "the expert version, not a longer one" in the prompt, two with the plain question) the baseline tested the question's false premise, worked from the raw history and anchored its answer on the repository's own dates every time, so the skill never beat it on the pre-registered counts. Nothing replaces it. The page below is as it was. Retested at the user's request on a task where the shipped instrument misleads (the repository's own sort benchmark covers eleven comparison sorts and none of the distribution sorts): one win (the skill arm found that `bucket_sort` is five times faster on the repository's target interpreter and cannot import on the environment's default one, while the baseline spent the hour without an answer), one tie, and two runs in which the skill arm itself spent the hour without an answer. One of four: it stays archived.

An agent skill that rewrites a task for expert depth, not size: before the work starts it names what a top practitioner would do that was not asked, the rawest material they would start from, the instruments they would use and the outside check that proves the result, rewrites the prompt to ask for exactly that, measures the rewrite, and runs it against that check. By Steve Solun. MIT.

## What it does

It turns an ordinary prompt into the version a top practitioner would run, shows the difference as a count of depth markers, and makes an outside check the definition of done. The model is never asked to judge its own result: the rewrite ends with a check that runs and returns a verdict, and that verdict is the first line of the report.

## When to reach for it

Type `/deeper` followed by the prompt, or the agent reaches for it on its own when a task fits: you ask for a deeper, more expert or more rigorous version of a task, or a task is about to run on summaries, generic methods and self-review. `--full` adds the outcome behind the task and the other fields that would attack it; `--run` skips the stop before execution.

| Situation | Reach for |
| --- | --- |
| The task would be done from summaries, with generic methods, checked by the model's own review | this skill |
| The outside check is a ticket's acceptance criteria | [acceptance-probes](../acceptance-probes) |
| The session is expensive because of what tools return, not because of what was asked | [tool-diet](../tool-diet) |

A task that already names its raw inputs, instruments and outside check is deep; the skill measures it and stops.

## Depth

A task done at **depth** is the same task done the way the best people in the field do it: from raw material instead of summaries, with the field's real instruments, proven by something other than the model's own review. Asked to work like an expert, a model swaps its vocabulary and keeps its methods: it says "cohort analysis" and produces a markdown table. The bigger version of a task has the same problem with more words.

The technique comes from Felix Rieseberg's post [How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (October 2026), which also makes the point this skill enforces hardest: do not ask the model to judge itself. Insist on outside validation, ideally a tool it can run.

Five points name the depth (the expert gap, the raw inputs, the instruments, the outside proof, the assumptions to test), the prompt is rewritten to ask for exactly that, and the script counts the markers in both versions:

```text
depth-check.py original.md rewrite.md
```

It prints a table of markers per prompt, flags role-play without instruments and requests for self-review, and gives one verdict: deeper, or bigger. Exit 0 only when the last prompt carries at least four of the five markers and no flags.

## Common questions

**Is a longer prompt a deeper one?**
No, and the script says so. The same original rewritten the usual way, with more sections, more coverage and "make sure it is correct", came out at 3.5x the words and 0 of 5 markers: bigger, not deeper. The rewrite that named seven raw inputs, eleven instruments and a held-out month came out at 5 of 5.

**Does the script judge whether the instruments are the right ones?**
No. The counts are word lists and patterns: they measure whether the prompt names concrete things (a file, a tool, a held-out month, a belief to test), not whether the things named are right. That is what the run in step 4 is for. The number is there so the difference between a deeper prompt and a longer one is visible before anything expensive runs.

**What does `--full` add?**
Two more points in step 1, kept in `FULL.md`: the outcome the user wants once the task is done (if aiming at that changes the task, aim at that), and two to four other fields that would attack the task differently, one of them adversarial, each as methods rather than role-play.

## It's working if

- The report opens with the outside check's verdict, and a failed check is reported as a failure.
- The rewrite names files, tools and a check by name; the markers table shows the count going up.
- The run happens in a fresh context that never saw this conversation.

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

## Where it fits

A chain step at the very start of a task, before any work runs. Its neighbours are [acceptance-probes](../acceptance-probes), because when the outside check is a ticket's criteria the probes are that check made runnable, and [tool-diet](../tool-diet), because a deeper prompt that pulls raw material into the context is the moment to keep the results lean. The index of every skill is the [root README](../README.md#skills).

## Install

Not installable since 1.8.0; the folder holds this page only.

## Files

```text
deeper/
├── SKILL.md                  # the skill
├── FULL.md                   # the two extra points for --full
├── agents/openai.yaml        # Codex and ChatGPT picker metadata
└── scripts/depth-check.py    # counts depth markers in a prompt; --help for options
```

## License

MIT
