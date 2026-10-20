# whose-red

An agent skill that answers, when a test fails, whose red it is before anything else, with runs rather than words: `mine` (fails at the working tree, passes at the base commit in a throwaway worktree), `pre-existing` (fails at base too), `flaky` (isolated reruns disagree) or `environment` (the failure names a missing binary, module, network, permission or sandbox). One table row per failing test, a summary count, and a deselect allowed only for a row that is not `mine`. By Steve Solun. MIT.

## What it does

It gives every failing test an owner, as one of four words, each earned by a run: alone three times at the working tree, once at the base commit in a throwaway worktree, with the failure text searched for an environment cause. A failure may be deselected, skipped or excluded only when its row says `pre-existing`, `flaky` or `environment`, and the row is pasted where the deselect happens; "unrelated" written next to a test name is not a verdict.

## When to reach for it

Type `/whose-red`, or the agent reaches for it on its own when a task fits: a test run shows red, a failure is about to be called unrelated or pre-existing, or any test is about to be deselected or skipped.

| Situation | Reach for |
| --- | --- |
| A test is failing and the question is whose fault it is | this skill |
| The tests a change added must be shown to fail without the change | [red-at-base](../red-at-base) |

A green run has nothing to sort; the skill ends with `failing 0`.

## Prerequisites

A git repository with a base commit the change grew from, and a test runner the script can drive (pytest); for another runner, the same runs are done by hand and the same rows written.

## The verdict

The **verdict** is one of four words, each earned by a run rather than by reading the test. Disagreement between isolated reruns is `flaky`. A pass at the base commit, in a worktree with the current test files copied over it, means the change broke it: `mine`. A failure at base whose text names a missing binary, module, network, permission or sandbox is `environment`; any other failure at base is `pre-existing`.

```text
whose-red.py <base> <id> ...
whose-red.py <base> --paths <test files or ids>
```

The first form takes the failing ids from a suite run; the second runs the suite itself and takes the failures from that. Per test it prints `| verdict | test | head | base | note |`, then `failing N: mine a, pre-existing b, flaky c, environment d`, with the resolved module path for the base worktree above the table. Exit 1 when any row says `mine`.

## Common questions

**Both arms of the A/B sorted the planted failures correctly. What did the skill change?**
The shape of the evidence and the cost of getting it. The arm with the skill produced a table with a base run and repeat counts per failing test, which the blind grader credited (4 of 5 against 1 of 5); the baseline reached the same verdicts in prose, with nothing a reader could rerun. The failure the skill was written against was observed in 17 of 18 earlier sessions on the same repository, where nothing told the agent to look.

**The sandbox test fails on every machine without the binary. Can I deselect it?**
Yes, once its row says `environment`, and the row goes where the deselect happens: the command line, the marker, the configuration entry or the commit message. A deselect that carries its row is auditable; one that does not is a self-report.

**Why three reruns?**
Because `flaky` is a claim about disagreement, and one run cannot disagree with itself. Three isolated runs at the working tree give an outcomes column (`P,F,P`) that is the record of what was seen.

## It's working if

- Every failing test has a row with a head count, a base result and a note, and the summary line reads `failing N: mine a, pre-existing b, flaky c, environment d`.
- The base worktree's `module <name> resolves to <path>` line points inside the worktree.
- Every deselect in the change carries its row, and no row says `mine` in the final run.

A real run on [stevesolun/ctx](https://github.com/stevesolun/ctx), in a scratch worktree built on `11b582a7`. The base for the run is a commit that quietly broke the parser's error path (a pre-existing failure); the working tree on top of it hides a subcommand from the help (which breaks a second test), adds a test whose outcome alternates between runs, and the machine lacks the Bubblewrap sandbox the live runner test needs.

```text
$ scripts/whose-red.py 45c05ff5 --paths src/tests/fit/test_cli_surface.py src/tests/fit/test_scan_cache.py \
    "src/tests/fit/test_live_runner.py::test_one_environment_serves_the_whole_campaign_and_follows_each_workspace"
suite run at the working tree: 4 failed, 11 passed in 13.95s
base worktree 45c05ff5: module ctx resolves to /tmp/whose-red-t7bh1tg7/src/ctx/__init__.py

| verdict | test | head | base | note |
| --- | --- | --- | --- | --- |
| mine | src/tests/fit/test_cli_surface.py::test_help_advertises_only_the_product_surface | 3/3 fail | pass | passes at base, fails here |
| pre-existing | src/tests/fit/test_cli_surface.py::test_unknown_command_error_does_not_leak_the_hidden_surface | 3/3 fail | fail | fails at base too |
| flaky | src/tests/fit/test_scan_cache.py::test_scan_cache_is_warm_on_second_run | 1/3 fail | not run | outcomes P,F,P |
| environment | src/tests/fit/test_live_runner.py::test_one_environment_serves_the_whole_campaign_and_follows_each_workspace | 3/3 fail | fail | sandbox: ...command could not be isolated: the Bubblewrap Linux sandbox is unavailable" is None |

failing 4: mine 1, pre-existing 1, flaky 1, environment 1
```

Exit code 1, because of the `mine` row. The whole run took 57 seconds, most of it the sandbox test failing seven seconds at a time.

This skill was also run as an A/B: a task on the repository at `11b582a7` with two failures planted before the work (a quietly broken parser test and the sandbox test that fails wherever the sandbox binary is missing), in two fresh sessions, once with a baseline skill set and once with the same set plus this skill.

| | baseline set | baseline set + whose-red |
| --- | --- | --- |
| Failures left behind of the arm's own | 0 | 0 |
| Tests deselected without a verdict row | 0 | 0 |
| Verdict table with a run behind every row | no | yes |
| Blind grader, skill's own success bullets | 1 of 5 | 4 of 5 |

On this task both arms sorted the planted failures correctly, so the pre-registered metric could not separate them; what the skill changed was the shape of the evidence (a table with a base run and repeat counts per failing test, which the grader credited) and the cost of getting it (one command). The seed failure itself was observed in 17 of 18 earlier sessions on the same repository, where nothing told the agent to look. One repetition, one repository.

## Where it fits

A reach-for-it-anytime standalone: whenever a run is red, before anything is deselected or called unrelated. Its neighbour is [red-at-base](../red-at-base), because the two questions about a test, whose red it is and whether it was ever red, are answered by the same kind of run at the same base commit, and the two scripts share that machinery. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=whose-red
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
whose-red/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/whose-red.py        # one row per failing test, by runs; --help for options
```

## License

MIT
