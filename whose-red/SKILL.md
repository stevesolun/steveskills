---
name: whose-red
description: "When a test fails, say whose red it is before anything else, from runs rather than words: mine (fails at the working tree, passes at the base commit in a throwaway worktree), pre-existing (fails at base too), flaky (isolated reruns disagree) or environment (the failure names a missing binary, module, network, permission or sandbox). Use when a test run shows red, when a failure is about to be called unrelated or pre-existing, or before any test is deselected or skipped. Not for making a run green, and not for proving new tests bite; that is red-at-base."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Whose Red

A red test has an owner, and the owner decides what happens next. The **verdict** is one of four words, each earned by a run rather than by reading the test: `mine` (fails at the working tree, passes at the base commit in a throwaway worktree, or did not exist there), `pre-existing` (fails at base too), `flaky` (isolated reruns at the working tree disagree with each other, or all pass although the suite failed it), `environment` (the failure text names a missing binary, module, network, permission or sandbox, and base fails or lacks the test too). Calling a failure "unrelated" from its name, or rerunning it until it passes, is a claim; the verdict is a table row with the runs behind it.

## 1. Collect the red

Run the suite once, as the project runs it, and list every failed or errored test id in the runner's `file::name` form. Where the run is long, keep the ids rather than the output; the script reruns what it needs.

**Done when** the ids are listed, or the run was green and the skill ends with `failing 0`.

## 2. Run the three checks

Run `scripts/whose-red.py <base> <id> ...` from the repository root, with the base the change grew from (the commit the user names, else the merge base with the default branch); with no ids it runs the suite itself over `--paths` and takes the failures from that run (`--help` for options). Per test it runs the id alone three times at the working tree, searches the failure text for an environment cause, adds a worktree at the base with the working tree's test files copied over it, pins the import path to that worktree and prints where the project module resolves, runs the id there, and removes the worktree. It prints one row per test:

```
| verdict | test | head | base | note |
| mine | tests/test_cli.py::test_help | 3/3 fail | pass | passes at base, fails here |
```

then `failing N: mine a, pre-existing b, flaky c, environment d`, and exits 1 when any row says `mine`. Paste the table as it came out. For a runner the script cannot drive, do the same runs by hand and write the same rows.

**Done when** every id from step 1 has a row, and the module path printed for the base worktree lies inside it.

## 3. Act by verdict

- `mine`: the change broke it, or wrote it broken. Fix the change, or the test when the test is the change's own, and rerun step 2 until the row reads otherwise.
- `pre-existing`: leave the test and the code as they are; name the separate fix in the report, next to the row.
- `flaky`: keep the test in the suite; report the outcomes column as the record of what was seen.
- `environment`: report the cause the row names; installing the missing piece is the fix, and until then the row is the record.

A deselect, skip or exclusion is allowed only for a test whose row says `pre-existing`, `flaky` or `environment`, and the row is pasted where the deselect happens: the command line, the marker, the configuration entry or the commit message that adds it.

**Done when** every `mine` row has turned into another verdict through a fix, and every deselect in the change carries its row.

## 4. Report

Report the summary line first, then the table, then one line per row saying what was done about it. The reader reruns the script against the same base and gets the same rows.

**Done when** the report's first line is the `failing N:` line from the last run and it shows `mine 0`.
