---
name: tool-diet
description: "Put tool results on a diet. Measure which tool, CLI, script or MCP results in a session cost the most tokens for the least use, cut the fat at its source, and prove the saving. Use when a tool result floods the context, the same lookup keeps repeating, a CLI or MCP server returns far more than the task used, or the user asks why a session burned tokens. Not for shortening the agent's own replies."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Tool Diet

Every tool result lands in the context window and competes with the instructions for attention on every turn that follows. A result is **lean** when the task used nearly all of it. The rest is **fat**: tokens paid for nothing, on every later turn. Find the fat, cut it where it is produced, prove the saving.

Quote commands and results with secrets redacted: `<REDACTED>` in place of any key, token or password.

## 1. Measure

Measure from the session's own tool results, as they came back, not as remembered. If the harness keeps a session log on disk, run `scripts/rank-tool-results.py` (it finds the newest log for this directory; `--help` for options). It ranks every result by size, flags repeats, errors and truncated outputs, and totals by tool. Without a log, rank the results in this context by hand: characters divided by four is the token estimate.

For each of the ten largest results, work out what the task used: the lines quoted, the fields acted on, the one fact extracted. The fat is the rest.

**Done when** each of the ten largest results (or all of them, if fewer) carries the tool, the call, its tokens, and what the task used from it.

## 2. Name the fat

Match each large result against these kinds. Each reads _what it is_ → _the cut_.

- **Unfiltered**: the whole thing came back when the task wanted a slice (a 2,000-line file for one function, full JSON for one field). → Filter at the source: a search pattern, a line range, a field selector, `head`.
- **Unbounded**: a list, log or history with no limit. → Cap it: `-n`, `--limit`, `tail`, a time window.
- **Chatty**: banners, progress bars, ANSI colour, install logs, verbose test runners, full stack traces. → Quiet flags (`-q`, `--silent`, `--no-progress`, `CI=1`), then `tee` the full output to a file and keep only the signal lines.
- **Repeated**: the same call again, because the first result scrolled away or was never kept. → Save the result to a file once and read the slice, or write the one fact into a note the next step reads.
- **Truncated**: the harness cut the output, saved it to a file, and the file was then read in full: paid twice. → Produce less in the first place (Unfiltered and Unbounded usually apply), or write to a file deliberately and read the slice.
- **Wrong tool**: a general tool where a specific one exists (`cat` then grep where a search tool exists, `curl` plus parsing where the CLI has a field flag, a screenshot where a DOM query answers). → Reach for the specific tool.
- **Raw blob**: minified bundles, lockfiles, generated code, base64, binary dumps. → Skip them by default; extract the one field with a parser.
- **Missing wrapper**: a multi-step lookup rebuilt by hand in every session. → One script in the repo with a `--help`, so the lookup is one short command.

## 3. Cut it where the next session finds it

Before touching the repo, show the user the fat you found and the cut you intend for each; if they are away, proceed. Cut the fattest result first. Prefer the cheapest cut that outlives this session, in this order:

1. **A flag the tool already has.** Record nothing: the tool's own `--help` is the source of truth.
2. **A wrapper script** in the repo, with a `--help`, where the lean call is a pipeline nobody would guess.
3. **A narrower tool, a parameter, or a sharper tool description** on the MCP server, so the lean form is the one the agent picks. The description decides which call gets made.
4. **One line** in the repo's agent instructions, only for a lean form that most sessions need and none would guess. That file loads on every turn, so everything else stays out of it.

A cut applied only to the current call is right when the fat is local to this task. Say so, so nobody hunts for a durable cut later.

## 4. Prove it

Run the lookup the lean way and measure it. Report one line per cut: the call, the kind of fat, the cut, tokens before → after. End with one line: tool-result tokens recovered, as a share of the session's total.

**Done when** every cut has a before and after measurement, every durable cut lives in the environment (the tool's flag, a script in the repo, an MCP description, a line in the agent instructions), and every one-off is labelled as one.
