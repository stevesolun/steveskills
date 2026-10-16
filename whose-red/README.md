# whose-red

An agent skill that answers, when a test fails, whose red it is before anything else, with runs rather than words: `mine` (fails at the working tree, passes at the base commit in a throwaway worktree), `pre-existing` (fails at base too), `flaky` (isolated reruns disagree) or `environment` (the failure names a missing binary, module, network, permission or sandbox). One table row per failing test, a summary count, and a deselect allowed only for a row that is not `mine`.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=whose-red
```

```bash
npx skills@latest update whose-red
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

A suite goes red and the agent writes "unrelated, pre-existing" next to the failure, or reruns it alone until it passes, or deselects it to get a green run. In eighteen fresh sessions on one repository, every session met the same failing test (it needs a sandbox binary the machine does not have) and seventeen handled it ad hoc: 54 rerun or retry hits across fifteen sessions, verdicts of "pre-existing" with no run at the base commit ("I did not rerun it on the base commit"), and a `--deselect` to make the run green. The repository's own agent instructions said the opposite: flaky and infrastructure failures are represented, not retried away, and an agent's self-report is never verification.

The verdict is cheap to earn. Run the test alone a few times at the working tree: disagreement is `flaky`. Run it at the base commit in a worktree with the current test files: a pass there means the change broke it, `mine`. A failure there whose text names a missing binary, module, network, permission or sandbox is `environment`; any other failure there is `pre-existing`. Each verdict is a row with the runs behind it, and only a row that is not `mine` may be deselected, with the row pasted where the deselect happens.

## How it runs

The agent reaches for it when a test run shows red, when a failure is about to be called unrelated or pre-existing, or before any test is deselected or skipped. Typing `/whose-red` works too.

1. **Collect the red.** The failed and errored ids from one suite run.
2. **Run the three checks.** `scripts/whose-red.py <base> <id> ...` (Python, standard library and git; with no ids it runs the suite over `--paths` and takes the failures from it) runs each id alone three times at the working tree, searches the failure text for an environment cause, runs it at the base in a throwaway worktree with the import path pinned and the resolved module path printed, and prints one row per test plus `failing N: mine a, pre-existing b, flaky c, environment d`. Exit 1 when any row is `mine`.
3. **Act by verdict.** `mine` is fixed and rerun; the other three are reported with their rows, and a deselect carries its row.
4. **Report.** The summary line first, then the table, then what was done per row.

## Sample output

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

## Why a script

"Pre-existing" and "flaky" are the two words that let a red run be reported as green, and nothing in a transcript shows whether the runs behind them happened. `whose-red.py` makes the runs, prints the resolved module path for the base worktree so a reviewer can see the base was graded and not an editable install of the current tree, and exits 1 while any row says `mine`. A deselect that carries its row is auditable; one that does not is a self-report.

## Files

```text
whose-red/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/whose-red.py        # one row per failing test, by runs; --help for options
```

## License

MIT
