# decision-ledger

An agent skill that keeps an append-only ledger of settled decisions with their source, and audits each phase artifact (spec, tickets, PR) against it before publishing, so every live decision is honoured or superseded and the implementer never re-asks a settled question.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=decision-ledger
```

```bash
npx skills@latest update decision-ledger
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

You answer twenty questions in an interview round, and the spec forgets five of them. The tickets widen two more. The implementer, in a fresh session, asks you the same questions again. The same leaks show up in every interview-to-implementation workflow: decisions from the interview missing from the spec, test seams agreed in the spec dropped by the ticket template so the implementer never writes a test first, decisions widening between interview and tickets and only caught at code review, an agent re-asking settled questions and recording recommendations the user had rejected, and question numbers restarting at Q1 in a later round, colliding with answers already given.

The ledger is one append-only file per effort: one line per settled decision, with where it came from (`round 3 Q1, user overruled: <the rejected recommendation>`), numbered without restarting across rounds or sessions. A changed mind is a new line that supersedes an old one, never an edit. Before a spec, ticket set or PR goes out, every live entry is looked up in the artifact and the report is a count: `honoured 15 of 16 live, missing 1`. Publication waits for `missing 0`.

## How it runs

The agent reaches for it when an interview round is answered, when a choice is settled in conversation, or when a spec, ticket set, branch or PR is about to be published from a conversation that holds decisions. Typing `/decision-ledger` works too.

1. **Append.** One entry per decision, in the user's words, with its source.
2. **Audit at the phase end.** `scripts/ledger-audit.py ledger.md <artifact>...` finds each live entry by an explicit reference (`(D7)` in the text) or a literal run of its words, and prints the file and line.
3. **Report and resolve.** A missing entry is the finding: add it to the artifact, or supersede it with the user's reason. Rerun until `missing 0`.
4. **Hand the ledger forward.** Every handoff, spec, ticket and implementer prompt names the ledger path.

## Sample output

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

## Why a script

"The spec reflects everything we agreed" is the agent's opinion of its own spec. `ledger-audit.py` turns it into a lookup with a line number per hit and an exit code, so a pre-publish hook can refuse a spec that lost a decision, and a reviewer can see which line honours which one without reading the interview.

## Files

```text
decision-ledger/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/ledger-audit.py      # audits an artifact against the ledger; --help for options
```

## License

MIT
