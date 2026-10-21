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

Two real runs on TheAlgorithms/Python, same change (reject inputs above 1000 in `factorial()`), on the tests each arm of the A/B below wrote for it:

```text
$ red-at-base.py 243b9375    # the baseline arm's tests
base: 243b9375  test files in diff: 1  (maths/test_factorial.py)
M = 3 (3 new, 0 changed)
import path pinned: PYTHONPATH=/tmp/red-at-base-albsqi2k
module maths resolves to /tmp/red-at-base-albsqi2k/maths/__init__.py
runner at base: maths/test_factorial.py: 2 failed, 1 passed in 0.22s

2 of 3 new or changed tests fail at base (243b9375): 2 red, 0 error, 1 green
red:   maths/test_factorial.py::test_argument_above_limit_raises[1001]
red:   maths/test_factorial.py::test_argument_above_limit_raises[5000]
green: maths/test_factorial.py::test_argument_at_limit_is_accepted
worktrees: 1 before, 1 after
exit=1
```

```text
$ red-at-base.py 243b9375    # the skill arm's tests
base: 243b9375  test files in diff: 1  (maths/test_factorial.py)
M = 5 (5 new, 0 changed)
import path pinned: PYTHONPATH=/tmp/red-at-base-zi0u06e5
module maths resolves to /tmp/red-at-base-zi0u06e5/maths/__init__.py
runner at base: maths/test_factorial.py: 5 failed in 0.37s

5 of 5 new or changed tests fail at base (243b9375): 5 red, 0 error, 0 green
red:   maths/test_factorial.py::test_factorial_limit_boundary
red:   maths/test_factorial.py::test_factorial_rejects_any_argument_above_1000[1002]
red:   maths/test_factorial.py::test_factorial_rejects_any_argument_above_1000[20000]
red:   maths/test_factorial.py::test_factorial_rejects_any_argument_above_1000[5000]
red:   maths/test_factorial.py::test_factorial_rejects_argument_above_1000
worktrees: 1 before, 1 after
exit=0
```

The baseline's `test_argument_at_limit_is_accepted` asserts that `factorial(1000)` works, which was already true: green at base, so it proves nothing about the change and the first run exits 1. The skill arm's five tests are all red at base, exit 0.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill, in a clone of [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) (about 200k stars). Two repetitions spelled the behaviour out in the prompt, two asked plainly. Pre-registered: the screener reruns each arm's new or changed test ids at the base commit in a fresh worktree with the arm's test files copied over it. M, new or changed ids; G, ids that pass at base; CHANGE, the asked behaviour on the final tree. Win: G = 0 with the skill, G >= 1 without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | M=2, G=yes, CHANGE=yes | M=3, G=no, CHANGE=yes | B | A 0/4, B 4/4 |
| rep2 | instruction in prompt | M=2, G=yes, CHANGE=yes | M=2, G=no, CHANGE=yes | B | A 0/4, B 4/4 |
| rep3 | plain ask | M=2, G=yes, CHANGE=yes | M=yes, G=no, CHANGE=yes | B | A 0/4, B 4/4 |
| rep4 | plain ask | M=2, G=yes, CHANGE=yes | M=2, G=no, CHANGE=yes | B | A 0/4, B 4/4 |

Four of four: passed. In every repetition the baseline added a boundary test that the limit is still accepted, which passes without the change; the skill arm's tests were red at base every time, and its report carried the `N of M` headline from the rerun.

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
