# structure-map

An agent skill that writes or refreshes a repository structure map: the facts a fresh agent cannot recover from the file tree in under a minute, each paired with the command that proves it and the output to expect. One script runs every proof and reports `confirmed C, stale S`; the map is committed only after that reads `stale 0`.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=structure-map
```

```bash
npx skills@latest update structure-map
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Every fresh session re-learns the same handful of structural facts: dependencies run from this package to that one and not back, this file is the canonical one of three that look alike, that directory is rewritten on commit, the root state file is frozen history and the live one is two levels down. A directory listing shows none of this, and a layout document written from memory goes stale the week after it is written, with nobody able to tell which lines still hold.

The map admits only facts that take more than one `ls`, one file read or one `--help` to recover, and every entry carries the command that recovers it plus the output to expect. That makes the file executable: run the commands, compare the outputs, and every entry is confirmed or stale. Stale entries are fixed from the actual output or removed, and the file stays under 60 lines.

## How it runs

The agent reaches for it when a session rediscovers dependency direction, the canonical file to edit or a generated directory, when onboarding to an unfamiliar repository, or when you ask it to document how the repo is laid out. Typing `/structure-map` works too.

1. **Check what is already there.** `scripts/map-check.py docs/STRUCTURE.md` runs every proof, prints `confirmed` or `STALE` per entry with the stale entries' commands and actual output, and ends with `confirmed C, stale S`. Stale entries are fixed or removed first.
2. **Hunt for facts.** Every moment in the session where an agent needed more than one command to answer where something lives, which file is canonical, what imports what, or whether something is generated.
3. **Apply the minute test.** A fact one `ls`, one read or one `--help` recovers is dropped.
4. **Write the entries.** `- <fact> | proof: \`<command>\` | expect: <output>`, with the expect copied from a run, under at most four headings.
5. **Confirm, then commit.** The script runs again; its exit 0 (every entry confirmed, at least one entry, under the cap) is the completion criterion, and the commit comes after it.

## Sample output

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

## Why a script

A layout document is a set of claims about the repository, and claims age. `map-check.py` turns each one into a command and an expected output, runs them read-only, and prints the actual output under every entry that no longer holds. The exit code is 0 only when every entry is confirmed and the file is under the cap, so a pre-commit hook or a reviewer can refuse a map that has gone stale without reading the repository.

## Files

```text
structure-map/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/map-check.py        # runs every proof, prints confirmed and stale; --help for the expect rules
```

## License

MIT
