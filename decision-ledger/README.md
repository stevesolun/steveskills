# decision-ledger

> **Archived.** Removed in 1.9.0. Rerun at the four-repetition bar on TheAlgorithms/Python, it won the two plain asks (the baseline dropped two of twelve decisions from the tickets each time) and tied the two where the prompt said nothing may be lost; two of four is under the bar. Nothing replaces it. The page below is as it was, with the final run beneath "It's working if".

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
In other words. The script counts an explicit reference or a literal run of the decision's words; a paraphrase ("the same rule applies to the bare command") is invisible to it. Tag the line with its D-number and it is found on every future audit.

**The user changed their mind. Do I edit the entry?**
No. Append a new entry that supersedes the old one, with the source of the change. The old line stays, marked superseded on the next audit, so the history of the decision is readable.

**Why not restart the numbering each round?**
Because a later round's Q1 then collides with an earlier Q1, which is one of the observed leaks this skill was written against: an agent recording a recommendation the user had rejected under a number that already meant something else.

## It's working if

- Every answered interview round adds entries, each with a source and the user's words.
- Before a spec or ticket set goes out, an audit report shows `honoured H of L live` with a file and line per hit, and `missing 0`.
- The implementer's prompt names the ledger path, and the implementer asks no question the ledger already answers.

A real run on TheAlgorithms/Python: an interview with twelve settled decisions, five of them against a recommendation, written into a spec and four tickets. The audit of the ledger against the artifacts:

```text
$ ledger-audit.py .scratch/*/ledger.md SPEC.md tickets/*.md
ledger audit: SPEC.md +4 files
honoured 12 of 12 live; superseded 0; missing 0
  D1   honoured  SPEC.md:4  reference D1
  D2   honoured  SPEC.md:25  reference D2
  D3   honoured  SPEC.md:34  reference D3
  D4   honoured  SPEC.md:5  reference D4
  D5   honoured  SPEC.md:37  reference D5
  D6   honoured  SPEC.md:38  reference D6
  D7   honoured  SPEC.md:39  reference D7
  D8   honoured  SPEC.md:41  reference D8
  D9   honoured  SPEC.md:27  reference D9
  D10  honoured  SPEC.md:45  reference D10
  D11  honoured  SPEC.md:47  reference D11
  D12  honoured  SPEC.md:4  reference D12
exit=0
```

Exit code 0: every live decision has a tagged line in the spec, so a future audit finds it by reference rather than by paraphrase.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill, in a clone of [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) (about 200k stars). Two repetitions spelled the behaviour out in the prompt, two asked plainly. Pre-registered: S, decisions present in the spec and in at least one ticket (0-12); W, rejected recommendations written as the decision. Win: S = 12 and W = 0 with the skill; S <= 11 or W >= 1 without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | S=12, W=no | S=12, W=no | none | A 3/4, B 4/4 |
| rep2 | instruction in prompt | S=12, W=no | S=12, W=no | none | A 3/4, B 4/4 |
| rep3 | plain ask | S=10, W=no | S=12, W=no | B | A 3/4, B 4/4 |
| rep4 | plain ask | S=10, W=no | S=12, W=no | B | A 2/4, B 4/4 |

Two of four: under the bar. Told that nothing decided may be lost or re-asked, the baseline carried all twelve decisions in both repetitions. Asked plainly for the spec and the tickets, it dropped two decisions from the tickets each time (the file name and the exit code once, the required seed and the standard-library rule once), while the skill arm carried all twelve with a ledger line for each. The same pattern as reconcile: the skill makes the difference only when the prompt does not say it.

## Where it fits

A chain step across phases: interview, spec, tickets, implementation, PR, with an audit at each boundary. Its neighbours are [reconcile](../reconcile), because a decision the transcript holds and no durable record carries is one of the discrepancies it lists at close, and [acceptance-probes](../acceptance-probes), because a ticket's criteria are often ledger entries made runnable. The index of every skill is the [root README](../README.md#skills).

## Install

Not installable since 1.9.0; the folder holds this page only.

## Files

```text
decision-ledger/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/ledger-audit.py      # audits an artifact against the ledger; --help for options
```

## License

MIT
