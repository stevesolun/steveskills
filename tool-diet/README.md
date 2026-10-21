# tool-diet

An agent skill that puts tool results on a diet: it measures which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cuts the fat at its source, and proves the saving with before and after numbers. By Steve Solun. MIT.

## What it does

It finds the tool results a session paid for and barely used, cuts each one where it is produced, and shows the tokens before and after. Every cut is a change in the environment (a flag, a wrapper script, a sharper tool description, one line in the agent instructions), so the saving holds in the next session without anyone reading a transcript; a rule of thumb in a steering file is not a cut.

## When to reach for it

Type `/tool-diet`, or the agent reaches for it on its own when a task fits: a tool result floods the context, the same lookup keeps repeating, a CLI or MCP server returns far more than the task used, or you ask why a session burned tokens.

| Situation | Reach for |
| --- | --- |
| Results come back bigger than the task used, or the same result comes back twice | this skill |
| A structural fact is re-learned every session (which file is canonical, what imports what) | [structure-map](../structure-map) |

A session that used what it fetched has no fat to cut; the skill ends with the measurement.

## Prerequisites

Works best where the harness keeps a session log on disk: `scripts/rank-tool-results.py` finds the newest log for the current directory and ranks from it. Without a log the ranking is done by hand from the results in context, at four characters to a token.

## Lean and fat

A result is **lean** when the task used nearly all of it. The rest is **fat**: tokens paid for nothing, on every later turn of the session, because every tool result stays in the context window and competes with the instructions for attention. The script ranks every result by size, flags repeats, errors and truncated outputs, and totals by tool:

```text
rank-tool-results.py [--log PATH] [--top N]
```

Each large result is then named as one of eight kinds, and the kind decides the cut: Unfiltered (a slice was wanted, the whole thing came back), Unbounded (no limit), Chatty (banners, progress bars, install logs), Repeated (the same call again), Truncated (the harness cut it, saved it, and the file was read in full: paid twice), Wrong tool, Raw blob, Missing wrapper. The cheapest cut that outlives the session wins: a flag the tool already has, then a wrapper script with a `--help`, then a narrower MCP tool or description, and only last one line in the agent instructions, which costs on every turn.

## Common questions

**The two biggest results in my session are the agent reading files the harness wrote. Is that fat?**
Yes, and it is the most common kind. The harness truncated a result, saved the full text to a file, and the agent read the file back: the same text paid for twice. The cut is in the first command (fewer files per loop, a search instead of a dump), so the file is never needed.

**Does it work without a session log?**
Yes, by hand: the agent ranks the results it can see in its own context and estimates tokens from characters. The log makes it exact and lets the ranking include results that have already scrolled out of view.

**Why not a rulebook: be concise, avoid re-reading, set a budget?**
A rule the model already follows changes nothing, and a rule it ignores changes nothing either. The skill points at a specific call and a token count, so you can tell whether it did anything.

## It's working if

- The report names specific calls with a token count each, and a kind of fat next to every one.
- Every durable cut is a file, flag or description you can see in the repository or the tool, with no new paragraph in the steering file.
- The last line is a share: tool-result tokens recovered, as a fraction of the session's total.

```text
Log: ~/.claude/projects/-home-me-app/3f1c....jsonl
Tool results: 127  Estimated tokens: 118,761

Largest results (top 6, 28% of all result tokens)
  tokens  tool             flags                  call
   8,241  Read                                    Read file_path=~/.claude/projects/.../tool-results/b5wz.txt
   8,145  Read                                    Read file_path=~/.claude/projects/.../tool-results/b4dk.txt
   5,022  Bash                                    Bash command=head -120 CHANGELOG.md && grep -n '^## ' ...
   4,344  Read                                    Read file_path=README.md

Truncated results (the full output was saved to a file, so reading it pays twice)
     545  Bash             Bash command=for f in docs/*.md; do cat "$f"; done
     528  Bash             Bash command=for f in adr/*.md; do cat "$f"; done

By tool
  93,901    79%    69 calls  Read
  13,001    11%    16 calls  Bash
```

The two biggest results here are the agent reading back outputs the harness had already cut and saved: the same text, paid for twice, about 16,000 tokens. The cut is in the first command (fewer files per loop, or a search instead of a dump).

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. Phase 1: in a clone of vuejs/vue, answer four weekly questions whose naive lookups are large (a year of `git log`, a `git log -p` on one file, a `wc -l` over every TypeScript file) and make next week's session cheaper; two repetitions asked for the fat found and before and after per lookup, two asked only to make it cheaper. Phase 2, the measurement: a fresh session with no skills, in each arm's final tree, answered the same four questions, and the screener summed the bytes of every tool result that session received. Pre-registered: PROBE, the skill arm's next session paid at most 0.7 of the baseline's; CUT, the skill arm's report carries before and after figures. Win: both.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | probe_bytes=8129, CUT=yes | probe_bytes=1693, CUT=yes | B | A 2/4, B 4/4 |
| rep2 | instruction in prompt | probe_bytes=9806, CUT=no | probe_bytes=2657, CUT=yes | B | A 2/4, B 3/4 |
| rep3 | plain ask | probe_bytes=14708, CUT=no | probe_bytes=3551, CUT=yes | B | A 1/4, B 4/4 |
| rep4 | plain ask | probe_bytes=14882, CUT=no | probe_bytes=1999, CUT=yes | B | A 0/4, B 2/4 |

Four of four: passed. The next session's lookups cost 4 to 7 times fewer bytes in the skill arm's tree (a wrapper script with `--help` and one line in the agent instructions, found by a session that knew nothing of the first), and the baseline arm reported no before and after figures in three repetitions. The blind grader put the skill arm at 4, 3, 4 and 2 of 4 and the baseline at 2, 2, 1 and 0.

## Where it fits

Periodic maintenance for any session that leans on tools, and a reach-for-it-anytime standalone when one result is obviously the problem. Its neighbour is [structure-map](../structure-map), because a lookup rebuilt in every session is sometimes a fact that belongs in the map rather than a wrapper script. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=tool-diet
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
tool-diet/
├── SKILL.md                      # the skill
├── agents/openai.yaml            # Codex and ChatGPT picker metadata
└── scripts/rank-tool-results.py  # ranks a session log; --help for options
```

## License

MIT
