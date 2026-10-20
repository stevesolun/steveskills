---
name: cite-or-cut
description: "Revise a draft section in the author's voice: name the one structural issue, propose the argument flow, give line-level edits as original then revised, and list every sentence that asserts something without support or asserts more than the evidence carries, from a scan of the text rather than a reading of it. Use when asked to revise, tighten or review a draft section of a paper, thesis, proposal or report before a reviewer sees it. Not for writing new content or adding results and citations the author did not supply."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Cite or Cut

A reviewer reads a draft sentence by sentence and asks two things of each one: what supports this, and does the wording claim more than that support can hold. The rule is **cite or cut**: a sentence that asserts a result, a cause, a comparison or a generalisation carries its support in the same sentence, or it is softened to what the author can show, or it goes. The scan finds the candidates; the author decides each one.

## 1. Fix the venue, the audience and the voice

Ask for the venue (journal, thesis, conference, funder), the audience, and the citation style in use. The draft's terminology and claims are the author's: edits keep both, and nothing is added that the author did not supply, no result and no reference.

**Done when** venue, audience and citation style are written at the top of the notes.

## 2. Name the one structural issue

Read the section once for shape. State the single largest structural problem in one sentence (the claim arrives after its evidence, two arguments interleave, the section answers a question the introduction did not ask), and propose the flow as an ordered list of the section's moves.

**Done when** the structural issue is one sentence and the proposed flow is a numbered list the author can accept or reject.

## 3. Scan for support and overstatement

Run `scripts/cite-or-cut.py DRAFT.md`. It lists, with line numbers, the sentences that bear a claim and carry no support in the sentence (no citation, footnote, table or figure reference), and the sentences with overstatement words (proves, clearly, always, all, well established, significant with no number). The lists are form; a sentence may belong on a list and be right for the venue.

**Done when** the scan output is in the notes.

## 4. Give line-level edits as pairs

For each sentence the author wants changed, one pair: the original, then the revision, in the author's voice. A listed claim is resolved by the rule, cite or cut: a citation placeholder for the author to fill (`[CITE]`), a softening to what the evidence shows, or removal. A listed overstatement is reworded to the evidence's strength or kept with the author's reason recorded next to it.

**Done when** every listed sentence has an edit pair or a recorded reason to keep it, and the revised draft is written to a new file.

## 5. Close with the reviewer's questions

Rerun the scan on the revised file and record the counts before and after: the sentences still to cite or cut. End with a short list of the questions a reviewer is likely to raise, each tied to a line.

**Done when** the before and after counts are in the notes, and the reviewer questions each cite a line of the revised draft.
