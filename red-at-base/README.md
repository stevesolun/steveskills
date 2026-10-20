# red-at-base

An agent skill that reruns every new or changed test at the base commit, in a throwaway worktree, and counts how many fail there. A test that passes without the change is reported as a finding and then changed or deleted, never kept with an explanation. By Steve Solun. MIT.

## What it does

It takes every test a diff added or edited, runs it against the code as it was at the base commit, and reports the count: red, error, green. A test that is green at base tested nothing about the change, and the only two moves the skill allows on it are an edit that turns it red and a deletion; a paragraph explaining why it was kept is not one of them.

## When to reach for it

Type `/red-at-base`, or the agent reaches for it on its own when a task fits: tests have been written for a change and are about to be called its coverage, a diff under review adds or edits tests, or you ask whether the tests would have caught the old behaviour.

| Situation | Reach for |
| --- | --- |
| The tests a change added must be shown to fail without it | this skill |
| A test is failing and the question is whose fault it is | [whose-red](../whose-red) |
| A ticket's acceptance criteria need proving, not the tests | [acceptance-probes](../acceptance-probes) |

Tests the change left alone are out of scope; the count is over new or changed tests only.

## Prerequisites

A git repository with a base commit to pin and a test runner the script can drive (pytest); for another runner, the same steps are done by hand and the same headline written.

## Red at base

A test counts as evidence about a change only when it is **red at base**: run against the code before the change, it fails. Green now says only that the code and the tests agree now; a test written after the code, with its expected value read off the code, passes before the change exists too, and the session that wrote it is the only witness that red ever happened.

```text
red-at-base.py <sha> [path ...]
```

The script collects test ids at the working tree and at the base with parametrised suffixes stripped, names M as the new ids plus the ids a diff hunk lands in, adds a worktree at the base, copies the current test files over it, pins the import path to that worktree and prints where the project module resolves, runs exactly M there, removes the worktree, and prints `N of M new or changed tests fail at base (<sha>): R red, E error, G green` with the ids. Exit 0 only when G is 0.

## Common questions

**My green test is a boundary guard, on purpose. Can I keep it?**
Not as part of the change's tests. The first version of this skill, run as an A/B, produced the right headline and then kept two green-at-base tests as "boundary guards, on purpose"; that is the failure this version closes. A characterisation test added on purpose is committed first, on its own, and that commit is passed as the base, so M holds only the change's own tests.

**Why does it print where the module resolves?**
Because an editable install imports the current tree even from inside the base worktree, and grades the wrong code. The printed path has to lie inside the worktree; the sample run below shows the line.

**What is the difference between error and red?**
Red: the test ran at base and its assertion failed, which is the proof. Error: the test could not run at base, usually because it imports a symbol the change introduces. That is red for the weakest reason: the test needs the change to exist, which says nothing about what the change does.

## It's working if

- The trace holds a headline in the shape `N of M new or changed tests fail at base (<sha>): R red, E error, G green`, with the ids under it.
- Above it, a `module <name> resolves to <path>` line whose path lies under the throwaway worktree, and `worktrees: N before, N after` with the same number twice.
- The final run reads `0 green`, and the report says `sharpened` or `deleted` for every earlier green.

A real run on [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`, in a scratch worktree where `ctx fit --max-depth` was given a floor of 1 and three tests were added to `src/tests/fit/test_cli_surface.py`. One of them asserted that `--max-depth 1` is accepted, which was already true.

```text
$ scripts/red-at-base.py 11b582a7
base: 11b582a7  test files in diff: 1  (src/tests/fit/test_cli_surface.py)
M = 3 (3 new, 0 changed)
import path pinned: PYTHONPATH=/tmp/red-at-base-nhyb0b9n/src
module ctx resolves to /tmp/red-at-base-nhyb0b9n/src/ctx/__init__.py
runner at base: src/tests/fit/test_cli_surface.py: 2 failed, 1 passed in 2.04s

2 of 3 new or changed tests fail at base (11b582a7): 2 red, 0 error, 1 green
red:   src/tests/fit/test_cli_surface.py::test_max_depth_below_one_is_rejected[-1]
red:   src/tests/fit/test_cli_surface.py::test_max_depth_below_one_is_rejected[0]
green: src/tests/fit/test_cli_surface.py::test_max_depth_of_one_is_accepted
worktrees: 16 before, 16 after
```

Exit code 1. The green test was sharpened to also assert that the help text now documents the floor, which the old code did not print:

```text
$ scripts/red-at-base.py 11b582a7
base: 11b582a7  test files in diff: 1  (src/tests/fit/test_cli_surface.py)
M = 3 (3 new, 0 changed)
import path pinned: PYTHONPATH=/tmp/red-at-base-8gvin7__/src
module ctx resolves to /tmp/red-at-base-8gvin7__/src/ctx/__init__.py
runner at base: src/tests/fit/test_cli_surface.py: 3 failed in 2.02s

3 of 3 new or changed tests fail at base (11b582a7): 3 red, 0 error, 0 green
red:   src/tests/fit/test_cli_surface.py::test_max_depth_below_one_is_rejected[-1]
red:   src/tests/fit/test_cli_surface.py::test_max_depth_below_one_is_rejected[0]
red:   src/tests/fit/test_cli_surface.py::test_max_depth_of_one_is_accepted_and_the_floor_is_documented
worktrees: 16 before, 16 after
```

Exit code 0. The `module ctx resolves to` line matters: this repository is installed in editable mode, so without the pinned import path the base worktree would have imported the current tree's package and graded the wrong code.

A first version of this skill, without the script, was run as an A/B on the same repository. The arm with the skill produced the right headline (`4 of 6 new tests fail at base`, matching an independent rerun) and then kept its two green-at-base tests as "boundary guards, on purpose". That is the failure this version closes: the script exits 1 while any test is green at base, and the only two moves the skill allows on a green are an edit and a deletion.

This version was then run as its own A/B: the same task (give `ctx fit --max-depth` a floor of 1, add tests, report which tests would fail without the change) in two fresh sessions on the repository at `11b582a7`, once with a baseline skill set and once with the same set plus this skill.

| | baseline set | baseline set + red-at-base |
| --- | --- | --- |
| New tests that pass at base, by independent rerun | 1 of 4 | 0 of 4 |
| Green-at-base test kept and explained away | 1 | 0 |
| Headline in the `N of M` shape, verdicts matching the rerun | no | yes, 4 of 4 |
| Blind grader, skill's own success bullets | 0 of 5 | 4 of 5 |

One repetition, one repository; the full A/B material is reproducible from the pinned commit.

## Where it fits

A chain step after the tests are written and before the change is called covered or sent to review. Its neighbours are [whose-red](../whose-red), because the other question about a red test is whose it is, and that one is answered by runs too, and [acceptance-probes](../acceptance-probes), because probes grade the ticket while this skill grades the tests, and the two compose. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=red-at-base
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
red-at-base/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/red-at-base.py      # reruns new or changed tests at the base; --help for options
```

## License

MIT
