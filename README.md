# tool-diet

An agent skill that puts tool results on a diet: it measures which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cuts the fat at its source, and proves the saving with before and after numbers.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=tool-diet
```

```bash
npx skills@latest update tool-diet
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

Every tool result lands in the context window and competes with your instructions for attention on every turn that follows. Most of that text is never used: a 2,000-line file read for one function, an install log, a list with no limit, the same lookup run three times. That is fat, and it is paid for again on every later turn of the session.

`tool-diet` does one thing: find the fat, cut it where it is produced, and show the number.

## How it runs

The agent reaches for it when a tool result floods the context, the same lookup keeps repeating, a CLI or MCP server returns far more than the task used, or you ask why a session burned tokens. Typing `/tool-diet` works too.

1. **Measure.** `scripts/rank-tool-results.py` (Python, standard library only) finds the newest session log for the current directory and ranks every tool result by size, flagging repeats, errors and truncated outputs, with totals by tool. Without a log, the agent ranks the results in its context by hand.
2. **Name the fat.** Each large result is matched against eight kinds, each with its own cut: Unfiltered, Unbounded, Chatty, Repeated, Truncated, Wrong tool, Raw blob, Missing wrapper.
3. **Cut it where the next session finds it.** Cheapest durable cut first: a flag the tool already has, a wrapper script with a `--help`, a narrower MCP tool or sharper tool description, and only as a last resort one line in the agent instructions.
4. **Prove it.** The same lookup, run lean, with tokens before → after per cut and the share of the session's tool tokens recovered.

## Sample output

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

## Why not a rulebook

Most "token efficiency" skills are lists of habits: be concise, avoid re-reading, set a budget. A rule the model already follows changes nothing, and a rule it ignores changes nothing either. `tool-diet` points at a specific call and a token count, and the result of the work is a measurement, so you can tell whether it did anything.

## Files

```text
.claude-plugin/                   # Claude Code plugin + marketplace manifests
skills/tool-diet/
├── SKILL.md                      # the skill
├── agents/openai.yaml            # Codex picker metadata
└── scripts/rank-tool-results.py  # ranks a session log; --help for options
```

## License

MIT
