---
name: red-at-base
description: "Rerun every new or changed test at the base commit in a throwaway worktree and count how many fail there, so a test that passes without the change is found and then changed or deleted rather than kept. Use when tests have been written for a change and are about to be called its coverage, when a diff under review adds or edits tests, or when asked whether the tests would have caught the old behaviour. Not for tests the change left alone, and not for deciding whose fault a failing test is; that is whose-red."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Red at Base

A test counts as evidence about a change only when it is **red at base**: run against the code as it was before the change, it fails. A test that passes at base checked something that was already true, however green it is now, and the session that wrote it is the only witness that it was ever red. Here the verdict is mechanical and exhaustive: every new or changed test is rerun at the base commit in a throwaway worktree, the result is a count, and a green there is a finding that ends in an edit or a deletion.

## 1. Pin the base

Resolve the base to a sha with `git rev-parse`: the commit the user names, else the merge base with the default branch (`git merge-base HEAD main`). Every later line refers to that sha.

**Done when** one sha is written and `git diff --name-only <sha>` lists the test files the change touched. An empty list ends the skill with the line `no test changes since <sha>`.

## 2. Run the rerun

Run `scripts/red-at-base.py <sha>` from the repository root (`--help` for options; a path argument narrows it to some test files). It collects test ids at the working tree and at the base with parametrised suffixes stripped, so a test with six cases counts once; names M as the ids that are new plus the ids whose body a diff hunk lands in; adds a worktree at the base and copies the working tree's test files over it; pins the import path to the worktree and prints where the project module resolves, since an editable install can quietly import the current tree instead; runs exactly M there, by id; removes the worktree; and prints:

```
N of M new or changed tests fail at base (<sha>): R red, E error, G green
red:   <id>
error: <id>: <first line of the error>
green: <id>
```

Three verdicts, read from the runner's own output:

- **red**: the test ran at base and its assertion failed. This is the proof.
- **error**: the test could not run at base (it imports a symbol the change introduces). Red for the weakest reason: the test needs the change to exist, which says nothing about what the change does.
- **green**: the test passed, or was skipped, at base. It proved nothing about the change.

Paste the output as it came out. For a runner the script cannot drive, do the same steps by hand and write the same headline.

**Done when** the headline and the id list are pasted, the printed module path lies inside the worktree, and the `worktrees: N before, N after` line shows the same number twice.

## 3. Change or delete every green

A green at base is a finding, closed by an edit or a deletion. For each green id, pick one:

- Sharpen it: assert the behaviour the change introduced, with the expected value taken from the spec or the ticket rather than from the new code, until it goes red at base.
- Delete it: what it checks was already true, so the test belongs to no change.

Rerun step 2 after every edit. A characterisation test added on purpose is green at base by design: commit it first, on its own, and pass that commit as the base, so M holds the change's own tests only.

**Done when** the latest run reads `0 green` and exits 0.

## 4. Report

Report the final headline, the id list, and one line per green from step 3: `<id>: sharpened, now red at base` or `<id>: deleted, asserted what was already true`. A reader reruns the script against the same sha and gets the same lines.

**Done when** every green from the first run appears in the report as sharpened or deleted, and the final headline's G is 0.
