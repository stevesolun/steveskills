# structure-map

An agent skill that writes or refreshes a repository structure map: the facts a fresh agent cannot recover from the file tree in under a minute, each paired with the command that proves it and the output to expect. One script runs every proof and reports `confirmed C, stale S`; the map is committed only after that reads `stale 0`. By Steve Solun. MIT.

## What it does

It writes the handful of structural facts every fresh session otherwise re-learns, and makes the file executable: each entry carries the command that recovers the fact and the output to expect, so running the file confirms or stales every line. The map admits only facts that take more than one `ls`, one file read or one `--help` to recover, and it stays under 60 lines.

## When to reach for it

Type `/structure-map`, or the agent reaches for it on its own when a task fits: a session rediscovers dependency direction, the canonical file to edit or a generated directory, an agent is onboarding to an unfamiliar repository, or you ask it to document how the repo is laid out.

| Situation | Reach for |
| --- | --- |
| A structural fact is re-learned every session and a listing does not show it | this skill |
| A tool result is bigger than the task used, or the same lookup repeats within a session | [tool-diet](../tool-diet) |
| A session is ending and the next piece of work needs naming | [reconcile](../reconcile) |

A fact one listing shows belongs to the tree, not the map; the minute test drops it.

## Prerequisites

A git repository. The map is written to `docs/STRUCTURE.md` (or wherever the repository's agent docs already point), with one line pointing at it added to the agent instructions if none is there.

## The map

The **map** holds exactly the facts a tree walk does not recover in a minute, each as `- <fact, one sentence> | proof: \`<command>\` | expect: <output>`, where `expect` is a backticked fragment the output contains, a bare number, `empty`, or `exit <code>`. The **proof** is the command a fresh agent would otherwise have had to work out, and an entry whose command returns something else is stale:

```text
map-check.py docs/STRUCTURE.md
```

It runs every proof read-only from the repository root, prints `confirmed` or `STALE` per entry with each stale entry's command and actual output under it, then `confirmed C, stale S`. Exit 0 means every entry confirmed, at least one entry, and the file within the cap; exit 2 means there is no map yet.

## Common questions

**Two entries were recoverable with a single `ls`. Does that matter?**
It is the one clause the A/B below left unmet (two of nineteen, one more than the limit), and it matters because every line of the map costs attention in every session that reads it. The minute test is applied before writing: one `ls`, one file read or one `--help` fails it, a search across files, a history walk or a comparison of two files passes.

**The expect was written from memory and the proof said otherwise. Which wins?**
The run. In the sample below one entry's expect was written from memory rather than from a run, the check flagged it with the actual output, and the entry was corrected from that output. The expect is always copied from a run in the current session.

**How long can the map be?**
Under 60 lines, checked by the script. A first version of this skill without the runner lost the A/B on the one bullet that said every proof passes; this version makes that bullet an exit code.

## It's working if

- `docs/STRUCTURE.md` is under 60 lines, and every entry has a proof command and an expect copied from a run.
- `map-check.py` reports `stale 0` before the commit that carries the map, and the report reads `<N> entries: <K> confirmed, <F> fixed, <R> removed, <A> added`.
- A fresh session reads the map and skips the search it would otherwise have run.

A real run on [stevesolun/ctx](https://github.com/stevesolun/ctx) at `11b582a7`, in a scratch worktree where a seven-entry `docs/STRUCTURE.md` was written. One entry's expect was written from memory rather than from a run.

```text
$ scripts/map-check.py docs/STRUCTURE.md
map: docs/STRUCTURE.md (19 lines, cap 60)
confirmed  L7    `ctx.engine` is the leaf layer: nothing in it imports another `ctx` su
STALE      L8    The flat `src/*.py` modules and the `src/ctx/` package ship together o
  proof:  grep -cE '^(py-modules|packages) = \[' pyproject.toml
  expect: 3
  actual: 2
  reason: expected 3, output was '2' (1 lines)
confirmed  L12   `ctx fit` is registered from `src/ctx/cli/run.py`; `src/ctx/cli/fit.py
confirmed  L13   Root `STATE.md` is frozen history; the live checkpoint is `docs/ctx-fi
confirmed  L17   `README.md`, `docs/index.md`, `docs/knowledge-graph.md` and `docs/cata
confirmed  L18   `src/config.json` and `src/skill-registry.json` are byte-identical cop
confirmed  L19   The Fit sandbox needs the `bwrap` binary; without it the live runner r

confirmed 6, stale 1
```

Exit code 1. The entry was corrected from the actual output (two sections, not three), and the second run reads `confirmed 7, stale 0` with exit code 0. The entries themselves look like this:

```text
- `ctx.engine` is the leaf layer: nothing in it imports another `ctx` subpackage, while core, runtime, fit and cli all import it | proof: `grep -rlE '^\s*(from|import) ctx\.(core|runtime|fit|cli|adapters)' src/ctx/engine | wc -l` | expect: 0
- Root `STATE.md` is frozen history; the live checkpoint is `docs/ctx-fit/STATE.md` | proof: `grep -n 'docs/ctx-fit/STATE.md' AGENTS.md | head -1` | expect: `canonical operational checkpoint`
```

A first version of this skill, without the script, was run as an A/B on the same repository. The arm with the skill wrote 14 facts with proof commands, of which 13 reproduced under an independent rerun; the arm without it wrote 27 facts with no proofs and one wrong one (it named the superseded root `STATE.md` as live). The blind grader scored them 4 of 5 against 1 of 5, and the skill lost on the one bullet that said every proof passes. This version ships the runner, so that bullet is an exit code.

This version was then run as its own A/B: the same task (document how the repository is laid out for agents, in the smallest file that saves a fresh session time) in two fresh sessions on the repository at `11b582a7`, once with a baseline skill set and once with the same set plus this skill.

| | baseline set | baseline set + structure-map |
| --- | --- | --- |
| Entries with a proof command | 1 of 23 | 19 of 19 |
| Proofs that reproduce under an independent rerun | 0 of 1 | 19 of 19 |
| Wrong facts found | 1 | 0 |
| `map-check` run with `stale 0` before the map was committed | no | yes |
| Lines | 70 | 37 |
| Blind grader, skill's own success bullets | 0 of 5 | 3 of 5 |

The design's one unmet clause: two of the nineteen entries were recoverable with a single `ls` or file read, one more than the limit. One repetition, one repository; the full A/B material is reproducible from the pinned commit.

## Where it fits

Periodic maintenance: refreshed whenever a session rediscovers something the map should have said, and checked before each commit that touches it. Its neighbours are [tool-diet](../tool-diet), because a lookup rebuilt in every session is sometimes a fact for the map and sometimes a fat result to cut, and [reconcile](../reconcile), because the closing report hands the next session its work while the map hands it the layout. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=structure-map
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
structure-map/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/map-check.py        # runs every proof, prints confirmed and stale; --help for the expect rules
```

## License

MIT
