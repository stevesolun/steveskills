---
name: deeper
description: "Rewrite a task for expert depth, not size. Before the work starts, name what a top practitioner would do that was not asked, the rawest material they would start from, the instruments they would use and the outside check that proves the result; rewrite the prompt to ask for exactly that, measure the rewrite, then run it against that check. Use when the user asks for a deeper, more expert or more rigorous version of a task, types /deeper, or a task is about to run on summaries, generic methods and self-review. Not for making a task bigger, longer or broader, and not for quick questions."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Deeper

A task done at **depth** is the same task done the way a top practitioner would do it: from the raw material, with the field's real instruments, proven by something other than the model's own opinion. Asked to act like an expert, a model usually swaps vocabulary and keeps its methods. This skill forces the swap of methods, writes it into the prompt, measures the rewrite, and makes the proof the definition of done.

The original prompt is `$ARGUMENTS`, or the task the user just described. Flags before it: `--full` adds the two points in `FULL.md` to step 1; `--run` skips the stop before step 4. With no prompt at all, ask for one in a line and stop.

## 1. Name the depth

Answer each point in one or two concrete lines, each adding something the task did not say.

- **Expert gap.** What a top practitioner in this field would do here that the request does not ask for.
- **Raw inputs.** The material before anyone processed it for the user: raw data, logs, original documents, primary sources. Name the access that needs.
- **Instruments.** The specific methods, tools, libraries, models or datasets they would actually use, by name. Where a markdown table is the lazy option and a database query or a statistical model is the expert option, the expert option. The user does not have to know what the experts use; the model usually does.
- **Outside proof.** What, other than the model's judgment or the user's, shows the result is right: a test suite, a held-out dataset, a reproduction, a benchmark, an independent source. Prefer a check the model can run and get an answer from at once.
- **Assumptions.** The beliefs baked into the request that should be tested against the raw material instead of accepted.

With `--full`, read `FULL.md` and answer its two points as well.

**Done when** every point names at least one source, tool, check or belief by name, ready to paste into a prompt.

## 2. Rewrite and measure

Rewrite the original prompt to ask for exactly what step 1 found, in one code block. The rewrite:

- Runs in a fresh session with no access to this conversation.
- Names the raw inputs, the instruments and the outside check.
- Treats the ambitious version as achievable; where something looks out of reach, says what would make it reachable instead of shrinking the goal.
- Ends with a definition of done that is the outside check, run and reported rather than judged.

Save the original and the rewrite to files and run `scripts/depth-check.py original.md rewrite.md` (`--help` for options). It counts, per prompt, the raw inputs, instruments, outside proof, definition of done and tested assumptions named, flags role-play without instruments and requests for self-review, and gives a verdict: deeper, or bigger. Fix the rewrite until it passes. Without the script, count the same five markers by hand and show both columns.

**Done when** the rewrite passes depth-check and the user has seen the markers before → after.

## 3. Pre-flight

A short checklist before anything runs: the access the rewrite needs and whether this session has it, tools to install, and how the outside check gets wired up before the task starts. Without a computer and the data, stop here and say which parts of the rewrite need an agentic session.

Then stop and ask one question: run it? With `--run`, or once the user says go, continue.

**Done when** the outside check exists in the environment and returns a result, even a failing one, before the task starts.

## 4. Run and prove

Run the rewritten prompt in a fresh context: a general-purpose subagent given the rewrite and the pre-flight checklist, or this session when none is available. Report the outside check's result in the first line, then the work. A failed check is reported as a failure, not softened into a caveat.

**Done when** the report carries the outside check's verdict and the depth markers before → after from step 2.
