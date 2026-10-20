---
name: decision-ledger
description: "Keep an append-only ledger of settled decisions with their source, and audit each phase artifact (spec, tickets, PR) against it before publishing, so every live decision is honoured or superseded and the implementer never re-asks a settled question. Use when an interview round is answered, when a choice is settled in conversation, or when a spec, ticket set, branch or PR is about to be published from a conversation that holds decisions. Not for recording the agent's own recommendations; only what the user settled."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Decision Ledger

Decisions leak at phase boundaries: settled in an interview round, missing from the spec, widened in a ticket, re-asked by the implementer. The **ledger** is the fix: one append-only file per effort that records every settled decision with its source, and an **audit** at each phase end that finds every live decision in the artifact or names it missing. Entries are permanent: a changed mind is a new entry that supersedes an old one.

## The ledger

Path: `.scratch/<effort-slug>/ledger.md`, created on first use. One line per entry:

```
D<n> | <source> | <decision, one sentence, in the user's words> | supersedes D<m> (when it does)
```

`<source>` is where the decision came from: `round 2 Q4, user`, `round 2 Q4, recommendation accepted`, `round 3 Q1, user overruled: <the rejected recommendation>`, `spec review, user`. Numbers run on from the last entry across rounds and sessions, so a later round's Q1 maps to a fresh D-number of its own. An entry is **live** until a later entry supersedes it.

## 1. Append

After each answered round, and whenever a choice is settled in conversation, append one entry per decision. A rejected recommendation is recorded as what the user chose instead, with the rejection named in the source.

**Done when** every answer in the round has an entry and the entry count equals the previous count plus this round's decisions.

## 2. Audit at the phase end

Before a spec, ticket set, commit series or PR is published, run `scripts/ledger-audit.py .scratch/<effort-slug>/ledger.md <artifact> [<artifact> ...]` (`--help` for options; for a tracker issue, fetch its body to a file first). For every live entry it looks for an explicit reference (`D7`, in the artifact's text) or a literal run of the decision's words, and prints the file and line of the hit. Three verdicts:

- **honoured**: a hit, with its file and line number.
- **superseded**: a later entry names it; skipped.
- **missing**: no line in the artifact carries the decision.

Tag the artifact's lines with the entry they honour (`... exit code 2 (D6)`): a tagged line is found on every future audit, a paraphrase is not.

**Done when** the script has run on the artifact as it will be published.

## 3. Report and resolve

The script's report:

```
ledger audit: <artifact>
honoured <H> of <L> live; superseded <S>; missing <M>
  D<n> MISSING <decision> ...
```

A missing entry is the finding: add the decision to the artifact, or append a superseding entry with the user's reason. Rerun step 2 after each change. The script exits 1 while anything is missing, so it can gate a publish hook.

**Done when** the report shows `missing 0` and the artifact is published after that report.

## 4. Hand the ledger forward

Every handoff, spec, ticket and implementer prompt names the ledger path, so the next session audits its artifact against the same file.

**Done when** the path appears in the artifact or the prompt.
