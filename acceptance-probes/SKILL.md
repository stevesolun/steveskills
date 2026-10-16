---
name: acceptance-probes
description: "Turn a ticket's acceptance criteria into runnable probes before any implementation, prove each probe fails at the start commit, freeze the probes, and rerun them to accept the work as a count. Use when a ticket with acceptance criteria is about to be implemented, when work is being declared done against a ticket, or when asked whether the criteria were really met. Not for criteria no command can answer; those are listed as HUMAN, never ticked."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Acceptance Probes

An acceptance criterion graded by the agent that did the work is a self-report. A **probe** is the criterion made runnable: one command whose exit code answers it. Written from the ticket before any implementation exists, run at the start commit where it must fail, and run again at the end where it must pass, the probes are the acceptance, and the report is a count.

## 1. Number the criteria

Fetch the ticket. List its acceptance criteria as `C1..Cn`, verbatim.

**Done when** `n` is written down and matches the ticket.

## 2. Write one probe per criterion

Before any implementation code exists, and from the ticket's wording alone (where the harness has subagents, dispatch one that sees the ticket and the repository and nothing of the plan), write `.scratch/<ticket-id>/probes.sh`: one function per criterion that runs a command (a test invocation, a CLI call diffed against expected output, a curl, a grep for a symbol) and prints `C<k> PASS` or `C<k> FAIL`; the script exits non-zero if any line is `FAIL`. A criterion no command can answer ("the code is readable") gets a line `C<k> HUMAN` and a one-line reason. Grep source files, never build output, so a stale cache cannot flip a verdict.

**Done when** every criterion has a function or a `HUMAN` line.

## 3. Run at the start

Run `scripts/probes-run.sh .scratch/<ticket-id>/probes.sh --start-only <start-commit>` (`--help` for options); it runs the script in a throwaway worktree at that commit and prints the verdicts with the script's checksum. Paste the output. Each `PASS` here is a finding, one of two kinds:

- The criterion is already true at the start: it grades nothing; report it and ask the user to drop or sharpen it.
- The probe is too weak to see the criterion: sharpen it until it reads `FAIL`.

Commit the script. **Done when** every probed criterion reads `FAIL` at the start, or is reported as already true with the user's decision recorded, and `probes.sh` is committed.

## 4. Implement

Hand the work to the build step: call the Skill tool with "tdd" at the agreed seams, or follow the implementer's own flow. The probes stay untouched during implementation; a probe edited to pass is a self-report again.

**Done when** the implementer reports done.

## 5. Run at the end

Run `scripts/probes-run.sh .scratch/<ticket-id>/probes.sh <start-commit>` on the finished work. It runs both ends with the same bytes, prints the checksum of each run, and ends with:

```
acceptance: <n> criteria, <K> probed, <H> human
start: <K> of <K> FAIL        end: <Q> of <K> PASS
human: C<k> <reason> ...
```

A probe still `FAIL` at the end is work left undone, and the ticket stays open. A checksum that changed between the runs is a probe edited during implementation: restore it and rerun.

**Done when** the end line reads `<K> of <K> PASS`, both checksums match, every `HUMAN` criterion is listed for the user, and the ticket's checkboxes are ticked only for the `K` probed criteria.
