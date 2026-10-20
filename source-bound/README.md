# source-bound

An agent skill for building a memo or a literature map from the sources the user supplied and nothing else: it inventories what was given and what could be read, cites every claim to a source and section, resolves every citation against the inventory, marks the points that rest on a single source, and lists the sources that were unreadable or unused. By Steve Solun. MIT.

## What it does

It makes the folder the boundary of the memo. A reference from memory sits in the same brackets as a reference to a file the reader gave, and a paper whose PDF was a scan with no text layer gets summarised from its title; the memo that breaks the instruction "use only my sources" looks like the memo that keeps it. Here every citation has to resolve to a file in the inventory, every file has to be accounted for, and a script says which citations resolve to nothing.

## When to reach for it

Type `/source-bound`, or the agent reaches for it on its own when a task fits: turning a folder of papers, reports, notes or transcripts into a memo, a literature matrix or a reading order, or writing any document that must cite only given material.

| Situation | Reach for |
| --- | --- |
| The memo's citations must resolve to the files the reader gave | this skill |
| The summary's numbers must come from the source | [number-trace](../number-trace) |
| The draft's claims need support or softening, cited or not | [cite-or-cut](../cite-or-cut) |

A summary of one source is a number trace, not a bound memo.

## Prerequisites

Sources are text files, or PDFs with a text layer: `pdftotext` (poppler) is used when present, `pypdf` otherwise. A scanned PDF with no text layer is listed as `UNREADABLE` in the inventory and reported before anything is written.

## Bound to the pile

**Bound** means three things at once: every citation in the memo resolves to a file the user gave, every file is accounted for (read, unreadable, or unused and why), and a claim that rests on one source says so. The inventory is what tells a reference from memory apart from a reference to the folder; the citations use the inventory's ids, to the section (`[pastebin#Design the core components]`), so a reader can open the file at the place the claim came from.

```text
source-bound.py inventory SOURCES_DIR
source-bound.py check MEMO.md --sources SOURCES_DIR --sentences
```

`inventory` prints one row per file: id, kind, pages, characters of text extracted, `READABLE` or `UNREADABLE`. `check` resolves every citation (`[id]`, `[file.pdf]`, `[id#section]`, `(Author, 2020)`, `{{id}}`) against the inventory and prints the resolved ones with their counts, the `UNRESOLVED` ones, the provided files never cited, and, with `--sentences`, the sentences that rest on exactly one source. Exit 1 while any citation is unresolved.

## Common questions

**One file in the folder is a scanned PDF. What happens to it?**
The inventory shows it with zero characters extracted and `UNREADABLE`, the user hears about it before the memo is written, and it appears in the memo only in the closing accounting. Nothing in the memo is attributed to a file whose text could not be read; a summary from the title alone is the failure the inventory exists to catch.

**The check flagged a citation to a book that exists. Why is a real reference unresolved?**
`UNRESOLVED` says the reference is not in the folder, not that it is wrong. The sample run below flagged `[Kleppmann 2017]`, a real book that the user never supplied. The fix is one of two: add the file to the folder and cite it from the inventory, or drop the claim that rested on it.

**A readable file was never cited. Is that a failure?**
It is a line in the output and a decision for the writer: work the source in, or list it as unused with the reason. Either way the accounting at the end names every file exactly once, so the reader can see what the memo rests on and what it set aside.

## It's working if

- Every bracketed citation in the memo names a file from the folder, and the check prints `unresolved 0`.
- The unreadable files are named in the memo's accounting, and no claim in the memo is attributed to one of them.
- Each readable file is either cited or listed as unused with a reason, one line per file.
- The sentences that rest on one source are marked as such in the memo.

A real run on four worked designs from [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (about 290k stars), plus a PDF with no text layer dropped into the folder, and a memo that cites three of the designs and one book from memory.

```text
$ source-bound.py inventory sources/
id                                   kind  pages    chars  status
pastebin                             md        0    15781  READABLE
sales_rank                           md        0    14884  READABLE
scanned-appendix                     pdf       0        0  UNREADABLE
twitter                              md        0    16642  READABLE
web_crawler                          md        0    17047  READABLE

sources: 5 provided, 4 readable, 1 unreadable

$ source-bound.py check memo.md --sources sources/ --sentences
citations in doc: 9; resolved to 3 provided source(s); unresolved 1
  ok          pastebin  (3 citations)
  ok          twitter  (3 citations)
  ok          sales_rank  (2 citations)
  UNRESOLVED  [Kleppmann 2017]  (not among the provided sources)
  unused      scanned-appendix
  unused      web_crawler

sentences resting on a single source: 3
  [pastebin] Pastebin writes the paste to object storage and keeps only metadata in SQL [pastebin#Design the core component
  [twitter] The timeline design fans out writes to each follower's in-memory timeline [twitter#Use case: User posts a twee
  [sales_rank] The sales-rank design is a MapReduce over logs rather than a live service [sales_rank].
```

Exit code 1 for the citation from memory. The memo then drops the book, works the crawler design in or lists it as unused with the reason, marks the three single-source sentences, and ends with the accounting of all five files.

### A/B against a baseline skill set

Four blind repetitions, each a fresh headless session: arm A had a baseline skill set, arm B the same set plus this skill. The task was a memo from a nine-file folder (seven primer write-ups, a scanned PDF with no text layer, an empty file); two repetitions said "use only these files and say what you could not read", two asked plainly. Pre-registered counts, from the memo and the folder listing only: R, citations resolving to no file in the folder; P and E, the two unreadable files named as such; Z, readable files neither cited nor listed as unused. Win: R = 0, P = E = 1, Z = 0 with the skill and at least one miss without.

| Rep | Design | Arm A (baseline set) | Arm B (baseline + skill) | Win | Blind grader (bullets) |
| --- | --- | --- | --- | --- | --- |
| rep1 | instruction in prompt | C=31, R=0, P=1, E=1, Z=0 | C=50, R=0, P=1, E=1, Z=0 | none | A 4/4, B 3/4 |
| rep2 | instruction in prompt | C=36, R=0, P=1, E=1, Z=0 | C=46, R=0, P=1, E=1, Z=0 | none | A 4/4, B 3/4 |
| rep3 | plain ask | C=33, R=0, P=1, E=1, Z=0 | C=41, R=0, P=1, E=1, Z=0 | none | A 3/4, B 4/4 |
| rep4 | plain ask | C=29, R=0, P=1, E=1, Z=0 | C=34, R=0, P=1, E=1, Z=0 | none | A 3/4, B 4/4 |

The baseline matched the skill on every count in all four repetitions, with or without the instruction: it read the folder, reported both unreadable files and cited by file name on its own. The skill arm cited to the section (`[mint#Step 4]`), 34 to 50 citations against 29 to 36, and marked single-source sentences, which the screener did not measure. The blind grader split two to two; the bullet it docked the skill arm on twice, "the memo ends with what the sources do not cover", is one the skill's own closing step contradicts by ending with the accounting. No measured advantage on a folder of this size. The case for the skill is a pile too large to hold in one context, which these runs did not test.

## Where it fits

A reach-for-it-anytime standalone for the research role. Its neighbours are [number-trace](../number-trace), because a memo's citations and its numbers are two different checks and a memo with figures needs both, and [cite-or-cut](../cite-or-cut), because a sentence can resolve to a file and still claim more than the file supports. The index of every skill is the [root README](../README.md#skills).

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=source-bound
```

Other routes (Claude Code plugin, Codex, by hand) are in the [root README](../README.md#install).

## Files

```text
source-bound/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex and ChatGPT picker metadata
└── scripts/source-bound.py      # inventory and check; --help for options
```

## License

MIT
