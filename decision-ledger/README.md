# decision-ledger

An agent skill that keeps an append-only ledger of settled decisions with their source, and audits each phase artifact (spec, tickets, PR) against it before publishing, so every live decision is honoured or superseded and the implementer never re-asks a settled question. By Steve Solun. MIT.

## What it does

It keeps every settled decision in one append-only file per effort, with where it came from, and looks each live one up in the spec, the ticket set or the PR before that artifact goes out. Publication waits for `missing 0`: a decision the artifact does not carry is added to it or superseded with the user's reason, and a changed mind is a new entry rather than an edit.

## When to reach for it

Type `/decision-ledger`, or the agent reaches for it on its own when a task fits: an interview round is answered, a choice is settled in conversation, or a spec, ticket set, branch or PR is about to be published from a conversation that holds decisions.

| Situation | Reach for |
| --- | --- |
| Decisions settled in conversation must survive into the next phase's artifact | this skill |
| A session is ending and git, the tracker and the chat may disagree | [reconcile](../reconcile) |
| A ticket's acceptance criteria need proving before and after the work | [acceptance-probes](../acceptance-probes) |

A choice nobody settled is a question, not an entry; the ledger records answers.

## Prerequisites

A workspace to write into: the ledger lives at `.scratch/<effort-slug>/ledger.md` and is created on first use. The artifacts audited are files; a tracker issue is fetched to a file first.

## The ledger

The **ledger** is one line per decision, `D<n> | <source> | <decision, in the user's words> | supersedes D<m>`, numbered without restarting across rounds and sessions, so a later round's Q1 maps to a fresh D-number. The **audit** looks every live entry up in the artifact by an explicit reference (`(D7)` in the text) or a literal run of its words, and prints the file and line of each hit:

```text
ledger-audit.py .scratch/<effort-slug>/ledger.md <artifact> [<artifact> ...]
```

Three verdicts per entry: honoured (with a line number), superseded (a later entry names it), missing. The report ends `honoured <H> of <L> live; superseded <S>; missing <M>`, and the exit code is 1 while anything is missing, so a publish hook can refuse the artifact.

## Common questions

**The audit says MISSING, but the spec does say it.**
In other words. The script counts an explicit reference or a literal run of the decision's words; a paraphrase ("bare `ctx` follows the same rule") is invisible to it, and in the sample below that is exactly the one line out of sixteen it flagged. Tag the line with its D-number and it is found on every future audit.

**The user changed their mind. Do I edit the entry?**
No. Append a new entry that supersedes the old one, with the source of the change. The old line stays, marked superseded on the next audit, so the history of the decision is readable.

**Why not restart the numbering each round?**
Because a later round's Q1 then collides with an earlier Q1, which is one of the observed leaks this skill was written against: an agent recording a recommendation the user had rejected under a number that already meant something else.

## It's working if

- Every answered interview round adds entries, each with a source and the user's words.
- Before a spec or ticket set goes out, an audit report shows `honoured H of L live` with a file and line per hit, and `missing 0`.
- The implementer's prompt names the ledger path, and the implementer asks no question the ledger already answers.

From the A/B that ranked this skill: an interview about adding `--format table|json|markdown` to `ctx fit`, answered from a fixed sheet of 12 decisions (three of them overruling the agent's own recommendation), then written up as a spec and tickets, twice in fresh sessions on [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`, once with a baseline skill set and once with the same set plus this skill.

```text
$ scripts/ledger-audit.py .scratch/fit-format/ledger.md .scratch/fit-format/spec.md
ledger audit: .scratch/fit-format/spec.md
honoured 16 of 16 live; superseded 0; missing 0
  D1   honoured  spec.md:55  reference D1
  D2   honoured  spec.md:56  reference D2
  ...
  D16  honoured  spec.md:97  reference D16

$ scripts/ledger-audit.py .scratch/fit-format/ledger.md .scratch/fit-format/issues/*.md
ledger audit: issues/01-replace-json-with-format.md +3 files
honoured 15 of 16 live; superseded 0; missing 1
  D1   honoured  issues/01-replace-json-with-format.md:5   "when stdout is a tty"
  D4   honoured  issues/01-replace-json-with-format.md:19  "no new dependency no rich"
  ...
  D15  MISSING   Bare `ctx` (no subcommand) runs `cmd_fit` with the default namespace, so the TTY rule in D1 applies
```

The missing line is a paraphrase ("bare `ctx` follows the same rule"), which the script does not count: tag the line with `(D15)` and it is found on every future audit.

| | baseline set | baseline set + decision-ledger |
| --- | --- | --- |
| Scripted decisions that survived into the tickets | 11 of 12 | 12 of 12 |
| Open questions left for the implementer | 11 | 1 |
| Rejected recommendations recorded as accepted | 0 | 0 |
| Blind grader, skill's own success bullets | 1 of 4 | 3 of 4 |

One repetition, one repository; the full A/B material is reproducible from the pinned commits.

## Where it fits

A chain step across phases: interview, spec, tickets, implementation, PR, with an audit at each boundary. Its neighbours are [reconcile](../reconcile), because a decision the transcript holds and no durable record carries is one of the discrepancies it lists at close, and [acceptance-probes](../acceptance-probes), because a ticket's criteria are often ledger entries made runnable. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=decision-ledger
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
decision-ledger/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/ledger-audit.py      # audits an artifact against the ledger; --help for options
```

## License

MIT
