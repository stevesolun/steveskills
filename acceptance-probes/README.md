# acceptance-probes

An agent skill that turns a ticket's acceptance criteria into runnable probes before any implementation, proves each probe fails at the start commit, freezes the probes, and reruns them to accept the work as a count.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=acceptance-probes
```

```bash
npx skills@latest update acceptance-probes
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

An agent implements a ticket, then ticks the ticket's checkboxes itself. That is the agent grading its own homework, and it is how "all checks green" comes to mean nothing: a run where every attempt has green checks and every attempt is rejected by an independent evaluator, or an implement step that quietly skips its own test and review steps while still reporting done.

A probe is the criterion made runnable: one command whose exit code answers it. Written from the ticket's wording before any code exists, it has to fail on the old code, or it grades nothing. The same bytes run again at the end. The acceptance is a count, `start: 2 of 2 FAIL, end: 2 of 2 PASS`, and a criterion no command can answer is listed as `HUMAN` and never ticked.

## How it runs

The agent reaches for it when a ticket with acceptance criteria is about to be implemented, when work is being declared done against a ticket, or when you ask whether the criteria were really met. Typing `/acceptance-probes` works too.

1. **Number the criteria.** `C1..Cn`, verbatim from the ticket.
2. **Write one probe per criterion.** `.scratch/<ticket-id>/probes.sh`, one function each, printing `C<k> PASS`, `FAIL` or `HUMAN <reason>`.
3. **Run at the start.** `scripts/probes-run.sh probes.sh --start-only <commit>` runs it in a throwaway worktree. A `PASS` here is a finding: the criterion is already true, or the probe is too weak. The script is committed.
4. **Implement.** Through `tdd` or the implementer's own flow. The probes are not touched.
5. **Run at the end.** `scripts/probes-run.sh probes.sh <start-commit>` runs both ends with the same bytes, prints a checksum per run, and ends with the count.

## Sample output

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

## Why a script

A probe that is edited to pass is a self-report with extra steps. `probes-run.sh` runs the same file at both ends, prints its checksum each time, and exits 0 only when the end run reads K of K PASS, so a hook or a reviewer can hold the line without reading the transcript.

## Files

```text
acceptance-probes/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/probes-run.sh       # runs probes at start and end, prints the count; --help in the header
```

## License

MIT
