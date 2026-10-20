# cite-or-cut

An agent skill for revising a draft section in the author's voice: the one structural issue, the argument flow, line-level edits as original then revised, and a scan that lists every sentence asserting something without support or asserting more than the evidence carries.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=cite-or-cut
```

```bash
npx skills@latest update cite-or-cut
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

The research-role version of "revise my draft" is specific: keep my terminology and claims, do not add results or citations, give edits as original-then-revised rather than rewriting in your voice, and list the sentences that need a citation or overstate the evidence. The last item is the one an editor does by instinct and an agent does unevenly: it lists the first three it notices and misses the eleventh.

`cite-or-cut` makes the list exhaustive by making it mechanical. A sentence bears a claim when it states a result, a cause, a comparison, a quantity or a generalisation; it is supported when the same sentence carries a citation, a footnote, or a table or figure reference. Overstatement is a word list: proves, clearly, always, all, well established, significant with no number beside it. The scan prints both lists with line numbers and counts; the author decides each line, and the counts before and after the revision are the measure of the pass.

## How it runs

The agent reaches for it when asked to revise, tighten or review a draft section of a paper, thesis, proposal or report before a reviewer sees it. Typing `/cite-or-cut` works too.

1. **Fix the venue, the audience and the voice.** Nothing is added that the author did not supply.
2. **Name the one structural issue** and propose the flow as a numbered list.
3. **Scan.** `cite-or-cut.py DRAFT.md`.
4. **Give line-level edits as pairs**: `[CITE]`, soften, or cut; a kept sentence gets its reason.
5. **Close with the reviewer's questions**, and the counts before and after.

## Sample output

A real run on the database section (2,360 words) of [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (about 290k stars), a text written for engineers rather than reviewers, which is exactly why it reads as one long list of unsupported assertions to this scan.

```text
$ cite-or-cut.py database-section.md --show 5
claims without support (39):
  L15: * **Atomicity** - Each transaction is all or nothing
  L50: * Most master-master systems are either loosely consistent (violating ACID) or have increased write latency due to synch
  L51: * Conflict resolution comes more into play as more write nodes are added and as latency increases.
  L58: * The more read slaves, the more you have to replicate, which leads to greater replication lag.
  L75: Smaller databases result in more data that can fit in memory, which in turn results in more cache hits due to improved c

overstatements (2):
  L122 [significant]: A read resulting in a complex database join can be very expensive, spending a significant amount of time on di
  L190 [guarantees]: * **Basically available** - the system guarantees availability.

claims: 40, unsupported 39, overstated 2  (sentences read: 143)
```

Exit code 1. Line 15 is a definition and stays, with the reason recorded; line 50 is the kind of sentence a reviewer circles, and it gets a `[CITE]` or a softening. The scan does not know the difference, and says so in its own help text; the author does, and the counts after the pass show how many lines they chose to leave.

## Why a script

An editor's list of unsupported sentences is as long as the editor's attention. `cite-or-cut.py` reads every sentence and applies the same two tests to each, so the author sees the whole list once, decides each line, and can show a reviewer the count that went from 39 to whatever they chose to leave.

## Files

```text
cite-or-cut/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex picker metadata
└── scripts/cite-or-cut.py      # unsupported claims and overstatements by line; --help for options
```

## License

MIT
