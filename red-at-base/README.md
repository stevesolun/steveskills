# red-at-base

An agent skill that reruns every new or changed test at the base commit, in a throwaway worktree, and counts how many fail there. A test that passes without the change is reported as a finding and then changed or deleted, never kept with an explanation.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=red-at-base
```

```bash
npx skills@latest update red-at-base
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

An agent implements a change, writes tests, and reports a green suite. Green says the code and the tests agree now. It says nothing about whether the tests can tell the new behaviour from the old: a test written after the code, with its expected value read off the code, passes before the change exists too. The session that wrote it is the only witness that red ever happened, and in an audit of 249 agent coding sessions "tests pass" was claimed seven times with no test run in the session at all.

The check is mechanical. Take every test the diff added or edited, run it against the code as it was at the base commit, and count. A test that goes red there bites. A test that errors there needs the change to exist, which is red for the weakest reason. A test that stays green there tested nothing about the change, and the next thing that happens to it is an edit or a deletion.

## How it runs

The agent reaches for it when tests have been written for a change and are about to be called its coverage, when a diff under review adds or edits tests, or when you ask whether the tests would have caught the old behaviour. Typing `/red-at-base` works too.

1. **Pin the base.** The commit the change grew from, as a sha.
2. **Run the rerun.** `scripts/red-at-base.py <sha>` (Python, standard library and git) collects test ids at the working tree and at the base with parametrised suffixes stripped, names M as the new ids plus the ids a diff hunk lands in, adds a worktree at the base, copies the current test files over it, pins the import path to that worktree and prints where the project module resolves, runs exactly M there, removes the worktree, and prints `N of M new or changed tests fail at base (<sha>): R red, E error, G green` with the ids.
3. **Change or delete every green.** Sharpen the test until it goes red at base, or delete it. Rerun after every edit.
4. **Report.** The final headline, the ids, and one line per green saying whether it was sharpened or deleted.

## Sample output

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

## Why a script

"These tests would fail without my change" is a claim about a run that did not happen. `red-at-base.py` makes the run, in a worktree the agent cannot have been editing, with the import path pinned and the resolved module path printed so a reviewer can see which code was graded. The headline is a count, the ids are listed, and the exit code is 0 only when nothing is green at base, so a hook can hold the line without reading the transcript.

## Files

```text
red-at-base/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/red-at-base.py      # reruns new or changed tests at the base; --help for options
```

## License

MIT
