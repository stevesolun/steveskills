# acceptance-probes

An agent skill that turns a ticket's acceptance criteria into runnable probes before any implementation, proves each probe fails at the start commit, freezes the probes, and reruns them to accept the work as a count. By Steve Solun. MIT.

## What it does

It makes a ticket's acceptance a count instead of a self-report: one probe per criterion, written from the ticket's wording before any code exists, run at the start commit where it has to fail, and run again at the end with the same bytes. A criterion that is already true at the start grades nothing, and the skill says so rather than ticking it; a criterion no command can answer is listed as `HUMAN` and never ticked by the agent.

## When to reach for it

Type `/acceptance-probes`, or the agent reaches for it on its own when a task fits: a ticket with acceptance criteria is about to be implemented, work is being declared done against a ticket, or you ask whether the criteria were really met.

| Situation | Reach for |
| --- | --- |
| A ticket's criteria need to be proven, before and after the work | this skill |
| The tests a change added need to be shown red before the change | [red-at-base](../red-at-base) |
| Decisions from an interview need to survive into the spec and tickets | [decision-ledger](../decision-ledger) |

A change with no ticket and no criteria has nothing to probe; write the criteria first.

## Prerequisites

A git repository (the start run happens in a throwaway worktree at the start commit) and a ticket whose criteria can be listed verbatim. The probes live in `.scratch/<ticket-id>/probes.sh` and are committed.

## The probe

A **probe** is the criterion made runnable: one command whose exit code answers it (a test invocation, a CLI call diffed against expected output, a curl, a grep for a symbol), printing `C<k> PASS` or `C<k> FAIL`. Written before the implementation, it has to fail on the old code or it grades nothing; run again at the end, with its checksum printed, it is the acceptance.

```text
probes-run.sh .scratch/<ticket-id>/probes.sh --start-only <start-commit>
probes-run.sh .scratch/<ticket-id>/probes.sh <start-commit>
```

The first form runs the script at the start commit and prints the verdicts with the script's checksum. The second runs both ends with the same bytes and ends with `acceptance: <n> criteria, <K> probed, <H> human`, `start: <K> of <K> FAIL        end: <Q> of <K> PASS`. Exit 0 only when the end run reads K of K PASS and the two checksums match.

## Common questions

**A probe passes at the start. Is the probe broken?**
One of two things, and both are findings. Either the criterion is already true before any work (the planted case in the A/B below: the baseline arm ticked it as delivered), so it grades nothing and the user is asked to drop or sharpen it; or the probe is too weak to see the criterion, and it is sharpened until it reads FAIL.

**What about a criterion like "the code is readable"?**
No command answers it, so it gets a `HUMAN` line with a one-line reason, stays out of the count, and is listed for the user. The agent never ticks it.

**Can the probes be adjusted during implementation?**
The checksum is printed at both ends for exactly this: a probe edited to pass is a self-report again. A changed checksum means restore the file and rerun.

## It's working if

- The start run shows every probed criterion red, before the first implementation edit.
- The end line reads `K of K PASS`, both checksums match, and `HUMAN` criteria are listed unticked.
- A criterion that was already true is named as grading nothing, not ticked as delivered.

From the A/B that ranked this skill: the same ticket (four criteria, one of them planted so that it was already true before any work) implemented twice in fresh sessions on [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`, once with a baseline skill set and once with the same set plus this skill.

```text
start run (bd7aee35, probes fb580c1dd1ae):
  C1 FAIL
  C2 PASS
  C3 FAIL
  C4 PASS
end run (f949746f, probes fb580c1dd1ae):
  C1 PASS
  C2 PASS
  C3 PASS
  C4 PASS

acceptance: 4 criteria, 4 probed, 0 human
start: 2 of 4 FAIL        end: 4 of 4 PASS
already true at start (grades nothing): C2 C4
```

| | baseline set | baseline set + acceptance-probes |
| --- | --- | --- |
| Planted already-true criterion | ticked as delivered | flagged, left unticked |
| Real criterion checked red before the first implementation edit | no | yes |
| Blind grader, skill's own success bullets | 0 of 5 | 4 of 5 |

The baseline arm ticked all four boxes, including the one that was true before it started. Both arms' checks fail at the start commit under an independent rerun. One repetition, one repository; the full A/B material (task, plant script, both arm prompts and reports, measurement script, grader transcript) is reproducible from the pinned commits.

## Where it fits

A chain step around implementation: ticket, probes, the build, probes again. Its neighbours are [red-at-base](../red-at-base), because probes grade the ticket and red-at-base grades the tests the change added, and the two compose, and [decision-ledger](../decision-ledger), because the criteria a ticket carries are often decisions settled earlier, and the ledger is where they are kept from drifting. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=acceptance-probes
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
acceptance-probes/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/probes-run.sh       # runs probes at start and end, prints the count; --help in the header
```

## License

MIT
