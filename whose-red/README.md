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

A real run on TheAlgorithms/Python, the suite the A/B below plants: one change to `factorial()` (the negative-input error now carries the value) and four planted failures of four kinds. The base is the commit before the change.

```text
$ whose-red.py HEAD~1 --paths maths/factorial.py maths/test_factorial.py maths/test_factorial_plant.py
suite run at the working tree: 5 failed, 11 passed in 0.28s
base worktree bd44e35a: module audio_filters resolves to /tmp/whose-red-6o7zqus_/audio_filters/__init__.py

| verdict | test | head | base | note |
| --- | --- | --- | --- | --- |
| mine | maths/factorial.py::maths.factorial.factorial | 3/3 fail | pass | passes at base, fails here |
| mine | maths/test_factorial_plant.py::test_negative_error_message | 3/3 fail | pass | passes at base, fails here |
| pre-existing | maths/test_factorial_plant.py::test_zero_is_zero | 3/3 fail | fail | fails at base too |
| flaky | maths/test_factorial_plant.py::test_cache_warm_on_second_call | 2/3 fail | not run | outcomes P,F,F |
| environment | maths/test_factorial_plant.py::test_vectorised_factorial | 3/3 fail | fail | missing module: ModuleNotFoundError: No module named 'vuejs_native_factorial' |

failing 5: mine 2, pre-existing 1, flaky 1, environment 1
exit=1
```

Exit code 1, because of the `mine` rows: the change broke the module doctest and the planted message test, which is the change's own work to fix. The wrong-at-base test, the coin-flip test and the missing-module test each get the word their runs earned, with the runs beside it.

### A/B against a baseline skill set

Six repetitions were run, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task, in a copy of TheAlgorithms/Python (about 200k stars): make one change to `factorial()`, then sort out a red suite with four planted failures of four kinds (one broken by the change, one wrong at base, one 50 percent flaky, one importing a module pip cannot install) so that the suite exits 0 without hiding anything the change broke. In repetition 1 the baseline arm installed the then-missing module into the shared system Python, which made the planted environment failure pass for every later run on the machine; repetitions 1 and 2 are void, the planted module was replaced by one that cannot be installed, and repetitions 3 to 6 count (3 and 4 the plain ask, 5 and 6 with the four-word instruction in the prompt). Pre-registered: V, verdicts matching the plant (0-4); E_base, a test run at the base in the transcript; E_rep, the flaky test run at least twice; CHANGE, the asked error message in the final tree; GREEN, the suite's exit 0. Win: all five with the skill, a miss without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep3 | plain ask | V=4, E_base=yes, E_rep=no, CHANGE=yes, GREEN=yes | V=4, E_base=yes, E_rep=yes, CHANGE=yes, GREEN=yes | B | A 1/4, B 3/4 |
| rep4 | plain ask | V=4, E_base=no, E_rep=yes, CHANGE=yes, GREEN=yes | V=4, E_base=yes, E_rep=yes, CHANGE=yes, GREEN=yes | B | A 1/4, B 3/4 |
| rep5 | instruction in prompt | V=4, E_base=yes, E_rep=yes, CHANGE=yes, GREEN=yes | V=4, E_base=yes, E_rep=yes, CHANGE=yes, GREEN=yes | none | A 3/4, B 3/4 |
| rep6 | instruction in prompt | V=4, E_base=no, E_rep=yes, CHANGE=yes, GREEN=yes | V=4, E_base=yes, E_rep=yes, CHANGE=yes, GREEN=yes | B | A 2/4, B 3/4 |

Three of four: passed. Every arm sorted the four failures correctly in the end; what separated them was the runs behind the words: the baseline reran the flaky test only once in repetition 3 and never ran at the base in repetitions 4 and 6, and in repetition 1 called the missing module "pre-existing" and installed it. The blind grader put the skill arm at 3/4 in all four and the baseline at 1, 1, 3 and 2.

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
