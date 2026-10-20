# source-bound

An agent skill for building a memo or a literature map from the sources the user supplied and nothing else: it inventories what was given and what could be read, cites every claim to a source and section, resolves every citation against the inventory, marks the points that rest on a single source, and lists the sources that were unreadable or unused.

Works in Claude Code, Codex, Copilot, Cursor and any other harness that reads the [Agent Skills](https://agentskills.io) format. By Steve Solun. MIT.

## Install

```bash
npx skills@latest add stevesolun/steveskills --skill=source-bound
```

```bash
npx skills@latest update source-bound
```

Or, in Claude Code, as a plugin that updates itself:

```bash
claude plugin marketplace add stevesolun/steveskills
claude plugin install steveskills@steveskills
```

Pick one route per agent; installing both gives you the skill twice.

## The idea

"Turn this pile of material into a memo" and "map my literature from the papers I collected" come with the same three instructions: use only the sources I gave you, tell me if a PDF could not be read, and mark any point that rests on a single source. The memo that breaks them looks like the memo that keeps them. A reference from memory sits in the same brackets as a reference to a file in the folder, and a paper whose PDF was a scan with no text layer gets summarised anyway, from its title.

`source-bound` makes the folder the boundary. The inventory says, per file, how much text could be extracted and whether it is readable. The memo cites by the inventory's ids, to the section. The check resolves every citation against the inventory and reports the ones that resolve to nothing, the files never cited, and the sentences that rest on one source. The memo ends with the accounting: used, unreadable, unused and why.

## How it runs

The agent reaches for it when turning a folder of papers, reports, notes or transcripts into a memo, a literature matrix or a reading order, or when a document must cite only given material. Typing `/source-bound` works too.

1. **Inventory the pile.** `source-bound.py inventory SOURCES_DIR`; unreadable files are reported before anything is written.
2. **Fix the question and the reader.**
3. **Read each source and write with citations to the section**, `[id]` or `[id#section]`, one per source a claim rests on.
4. **Check the memo against the inventory.** `source-bound.py check MEMO.md --sources SOURCES_DIR --sentences`.
5. **Close with the accounting.**

## Sample output

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

## Why a script

"I only used your sources" cannot be checked by reading the memo; the brackets look the same. `source-bound.py` resolves each one against the folder and counts what is left over on both sides, so the reader can see the boundary was kept, and the writer sees the one reference that walked in from memory.

## Files

```text
source-bound/
├── SKILL.md                     # the skill
├── agents/openai.yaml           # Codex picker metadata
└── scripts/source-bound.py      # inventory and check; --help for options
```

## License

MIT
