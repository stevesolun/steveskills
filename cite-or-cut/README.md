# cite-or-cut

> **Archived.** Removed in 1.7.0. In four blind repetitions against a baseline skill set the baseline fixed all nine planted defects every time, with or without the instruction in the prompt, so the skill never beat it on the pre-registered counts; the grader's preference for its edit pairs is not the benchmark. Nothing replaces it; for a summary's numbers use [number-trace](../number-trace), for a proposal against its criteria [criteria-map](../criteria-map). The page below is as it was.

An agent skill for revising a draft section in the author's voice: the one structural issue, the argument flow, line-level edits as original then revised, and a scan that lists every sentence asserting something without support or asserting more than the evidence carries. By Steve Solun. MIT.

## What it does

It makes the reviewer's list exhaustive. An editor flags unsupported sentences by instinct and an agent does it unevenly: it lists the first three it notices and misses the eleventh. Here the list comes from a scan of every sentence, with line numbers and counts, and the author decides each line; nothing is added to the draft that the author did not supply, no result and no reference.

## When to reach for it

Type `/cite-or-cut`, or the agent reaches for it on its own when a task fits: revising, tightening or reviewing a draft section of a paper, thesis, proposal or report before a reviewer sees it.

| Situation | Reach for |
| --- | --- |
| The draft's claims need support or softening, number or not | this skill |
| The summary's numbers must come from the source | [number-trace](../number-trace) |

Writing new content, or adding results and citations the author did not supply, is outside it.

## Cite or cut

The rule is **cite or cut**: a sentence that asserts a result, a cause, a comparison, a quantity or a generalisation carries its support in the same sentence, or it is softened to what the author can show, or it goes. A sentence is supported when it carries a citation, a footnote, or a table or figure reference; overstatement is a word list (proves, clearly, always, all, well established, significant with no number beside it). The scan prints both lists; the author resolves each line with a `[CITE]` placeholder, a softening, a cut, or a recorded reason to keep it.

```text
cite-or-cut.py DRAFT.md [--show N]
```

It prints the claims without support and the overstatements, each with its line number, then `claims: C, unsupported U, overstated O`. Exit 1 while U or O is above zero. The counts before and after the revision are the measure of the pass.

## Common questions

**The scan flagged a definition. Is that wrong?**
The lists are form, not judgement, and the script's own help says so. A definition ("Atomicity: each transaction is all or nothing") belongs on the list because it asserts without support, and it stays in the draft with the reason recorded next to it. The count after the pass is the number of lines the author chose to leave, which is a different number from the count of lines the agent happened to notice.

**Does it add citations?**
It adds `[CITE]` where a citation is owed and leaves the reference for the author. A revision that supplies a plausible reference the author never read is the one edit a reviewer cannot forgive, so the skill's first rule is that every result and every reference in the revised file was already in the draft.

**Why edits as pairs rather than a rewritten section?**
Because the voice is the author's. Original-then-revised lets the author accept or reject each change and keeps their terminology; a section rewritten in one go reads like the agent and loses the claims the author meant to keep.

## It's working if

- Every sentence the scan listed has an edit pair or a recorded reason, and the revised file carries no result or reference the draft did not.
- Overstatement words are gone or qualified, and `[CITE]` marks what the author still owes.
- The before and after counts are in the notes, so the author can show a reviewer how many lines they chose to leave.

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

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task was a 460-word thesis Background section with nine planted defects (six unsupported assertions, three overstatements) and five real references; two repetitions said "make every claim one I can defend", two asked plainly for a revision. Pre-registered counts: D, planted defects still present in a sentence with no citation; I, citation markers or references not in the draft. Win: D <= 1 and I = 0 with the skill, D >= 3 or I >= 1 without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | D=0, I=0 | D=0, I=0 | none | A 3/4, B 3/4 |
| rep2 | instruction in prompt | D=0, I=0 | D=0, I=0 | none | A 2/4, B 4/4 |
| rep3 | plain ask | D=0, I=0 | D=1, I=0 | none | A 2/4, B 3/4 |
| rep4 | plain ask | D=0, I=0 | D=2, I=0 | none | A 3/4, B 3/4 |

The baseline fixed all nine defects in every repetition. The skill arm left one and then two on the plain ask: a claim softened and marked `[CITE]` for the author to fill, which is the skill's own option for a claim only the author can source and which the screener counts as unsupported until it is filled, and one claim kept. No measured advantage on the counts. The blind grader, scoring the bullets above, preferred the skill arm in two repetitions (its original-then-revised pairs and its before and after counts) and tied in two.

## Where it fits

A reach-for-it-anytime standalone for the research role. Its neighbours are [number-trace](../number-trace), because a claim with a figure in it needs the figure traced as well as the sentence supported, and [criteria-map](../criteria-map), because a proposal's sentences have to earn their claims after its sections are mapped. The index of every skill is the [root README](../README.md#skills).

## Install

Not installable since 1.7.0; the folder holds this page only.

## Files

```text
cite-or-cut/
├── SKILL.md                    # the skill
├── agents/openai.yaml          # Codex and ChatGPT picker metadata
└── scripts/cite-or-cut.py      # unsupported claims and overstatements by line; --help for options
```

## License

MIT
