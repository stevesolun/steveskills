# micromanager

> **Candidate.** Built and tested by hand (a simulated board and one live run with a real worker subagent, both below), not yet through the [benchmark](../README.md#the-benchmark). It is installable by name and is not in the index tables or the plugin until it passes.

An agent skill that supervises other agents until every ticket is verified closed: it hands tickets out from a board, inspects each worker's diff on a fixed cadence, treats a diff that has not moved as stale, nudges, re-briefs, replaces, verifies before anything closes, and never leaves a seat idle while work is ready. By Steve Solun. MIT.

## What it does

It runs the loop a manager runs over a team of workers, with one difference that fits agents: nothing a worker says counts. Progress is a fingerprint of the worker's worktree (HEAD, index, working tree) taken by `scripts/board.py`; **quiet** is minutes since the fingerprint last changed, and past the threshold the ticket is **stale** whatever the status message said. A worker's "done" is a claim the manager verifies against the ticket's acceptance criteria before the ticket closes. The board also counts the manager's own failure, **idle seat-minutes**: time a seat was free while a ticket was ready.

## When to reach for it

Type `/micromanager`, or the agent reaches for it on its own when you want a set of tickets driven to done by several agents, say supervise, babysit or keep them working, or ask why delegated work stalled.

| Situation | Reach for |
| --- | --- |
| Several tickets, several workers, and you want them driven to verified done without watching | this skill |
| One ticket, and you want its acceptance criteria turned into probes that prove it | [acceptance-probes](../acceptance-probes) |
| A worker's test suite is red and you want to know whose red it is | [whose-red](../whose-red) |

The manager never does a ticket itself. If there is one ticket and one agent, there is nothing to manage; do the ticket.

## Prerequisites

Git, so each worker gets its own worktree and the board can fingerprint it. A harness that can spawn subagents in the background (Claude Code, Codex). Tickets in one of three places: a folder of markdown files with a `Blocked by:` line, a GitHub label (`gh` installed), or a JSON list. Across sessions, a scheduler: Claude Code `/loop 20m /micromanager`, a Codex automation, or cron running `claude -p` or `codex exec`. The board file, `.micromanager/board.json`, is the state a waking session resumes from.

## Quiet and stale

Every check prints one row per seat: lines changed since the ticket was assigned, minutes quiet, and a flag.

```text
board.py check [--stale-minutes M]      # exit 1 when anyone is stale
```

A stale ticket climbs a three-rung ladder, one rung per check, each recorded with `board.py nudge`: ask for the diff and the next edit; re-brief with the gap between the criteria and the diff named and a step small enough for one tick; replace the worker with a fresh one and a handoff file. A decision only a human can make is parked with its exact question (`board.py block`) and the seat is refilled. "Done" is `claim-done`; the manager runs the criteria and then `verify --pass` or `verify --fail "reason"`. The frontier recomputes after every close, so a blocked ticket appears the moment its blocker is verified.

## Common questions

**The worker keeps saying "making progress". Why does the board call it stale?**
Because its diff has not changed. The fingerprint is taken from git, not from the message. A worker that is thinking for ten minutes without committing looks the same as one that is stuck, and both get the same first rung: show the diff, name the next edit.

**What if the worker is right that nothing needs to change yet, say it is reading the codebase?**
Then rung 1 costs one message and the worker answers with the plan and the next edit. The ladder is slow on purpose: three ticks before anyone is replaced. Set `--stale-minutes` to the reading time a ticket in this repo needs.

**The manager verified my ticket but said it could not run part of it.**
That is the intended behaviour. In the live run below the repository had no tests and no server, so the manager read the diff against each criterion, said which criteria it could check and which it could only read, and closed on the ones it could check. It does not run the worker's summary of the tests; it runs the tests, or says there were none.

**Does it need the harness's scheduler to be "always on"?**
Inside one session it loops until the frontier is empty. For longer work the schedule is the cadence: the board file carries the state, so a session that wakes every twenty minutes reads it, checks, works the ladder, fills seats and exits.

## It's working if

- Every check prints a row per seat with lines changed and minutes quiet, and the manager's first move on a quiet row is to read the diff, never to ask how it is going.
- No ticket closes without a `verify --pass` that names the commands run, and a failed verification goes back to the worker with the reason as its next step.
- The final report carries the counts: closed, nudges, replacements, failed verifications, escalations, minutes per ticket, idle seat-minutes.

From a simulated run (two git worktrees, clocks backdated so the stale case shows). Three tickets, two seats, ticket 2 blocked by ticket 1. Worker `alpha` committed a migration; worker `beta` had not touched its worktree in 14 minutes:

```text
$ board.py check --stale-minutes 10
  id  status        worker       lines  quiet  flag
   1  assigned      alpha            2     0m
   3  assigned      beta             0    14m  STALE (0 nudges, attempt 1)

seats 2/2 busy, 0 ready and unassigned, 1 stale, idle seat-minutes so far: 0

$ board.py claim-done 1
1: worker claims done. Verify before closing: board.py verify 1 --pass|--fail REASON
$ board.py verify 1 --fail "migration does not apply: missing down()"
1: FAILED verification (1x): migration does not apply: missing down(). Back to the worker.
$ board.py verify 1 --pass
1: verified and closed after 11 minutes, 1 attempt(s), 0 nudge(s), 1 failed verification(s).
$ board.py frontier
Frontier: 1 ready  |  seats: 1/2 busy  |  free seats: 1
     2  02: POST /invoices endpoint

$ board.py report
Tickets: 3  open: 1  assigned: 1  closed: 1
Nudges: 3  replacements: 1  failed verifications: 1  escalations: 0
Minutes per closed ticket: median 11, max 11
Idle seat-minutes (free seat while work was ready): 0
     3  03: Document the invoices API                      nudges 3  fails 0  attempts 1
     1  01: Add the invoices table                         nudges 0  fails 1  attempts 1
```

Live run: installed as the Claude Code plugin and pointed at a one-ticket repository, a headless session as the manager built the board, created the worktree, spawned a worker subagent with the brief, read `git diff main ticket-03` itself (25 lines, README.md only, every criterion met), merged with `--no-ff`, closed with `verify --pass`, and reported `Tickets: 1 closed: 1`, nudges 0, idle seat-minutes 0. It also said what it could not verify: no server, so the curl example was read, not run.

### A/B against a baseline skill set

Not yet run. The pre-registered design: arm A a baseline skill set, arm B the same plus this skill, each managing the same three-ticket board with one planted stall (a worker briefed to stop after its first commit) on real material; metric computed by the screener from the arms' trees, never from `board.py`: the stalled ticket is replaced or re-briefed within two checks, and no ticket is closed whose criteria the screener's own probes fail. Win: both, in at least three of four repetitions, two designs.

## Where it fits

A standalone that sits above the engineering skills: it is the session that hands tickets to workers and decides when they are done. Its neighbours are [acceptance-probes](../acceptance-probes), which gives the manager runnable probes to verify a claim with instead of reading the diff by eye, and [whose-red](../whose-red), for the moment a worker's suite goes red and the manager has to know whether the worker caused it. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=micromanager
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install). The plugin carries screened skills only, so until the benchmark runs this one installs by name.

## Files

```text
micromanager/
├── SKILL.md              # the skill
├── WORKER-BRIEF.md       # the brief, the re-brief, the handoff
├── agents/openai.yaml    # Codex and ChatGPT picker metadata
└── scripts/board.py      # the board: init, frontier, assign, check, nudge, claim-done, verify, block, report
```

## License

MIT
