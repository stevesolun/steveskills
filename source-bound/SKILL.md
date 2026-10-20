---
name: source-bound
description: "Build a memo or a literature map from the sources the user supplied and nothing else: inventory what was given and what could be read, cite every claim to a specific source and section, resolve every citation against the inventory, mark the points that rest on a single source, and list the sources that were unreadable or unused. Use when turning a folder of papers, reports, notes or transcripts into a memo, a literature matrix or a reading order, or when a document must cite only given material. Not for a summary of one source; that is a number trace."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Source Bound

A memo written from a pile of sources is worth exactly as much as the reader's ability to check it against the pile. **Bound** means every citation in the memo resolves to a file the user gave, every file is accounted for (read, unreadable, or unused and why), and a claim that rests on one source says so. References that arrive from memory look identical on the page; the inventory is what tells them apart.

## 1. Inventory the pile

Run `scripts/source-bound.py inventory SOURCES_DIR`. One row per file: id, kind, pages, characters of text extracted, READABLE or UNREADABLE. An unreadable file (a scanned PDF, an empty export) is reported to the user now, before anything is written about it; nothing is summarised from a file whose text could not be extracted.

**Done when** the inventory is in the notes and the user has the list of unreadable files.

## 2. Fix the question and the reader

Ask for the research question or the question the memo must answer, who will read it, and the length. The matrix columns for a literature map are fixed: citation, research question, method, sample or data, key findings, position taken in the debate, and confidence that the source was read correctly.

**Done when** the question, reader and length are written at the top of the working notes.

## 3. Read each source and write with citations to the section

Every claim carries a citation in the form `[id]` or `[id#section]` (`[pastebin#Design the core components]`), one per source it rests on. The inventory's ids are the only citable names. A finding grouped by theme lists the sources on each side where they disagree; a gap is stated as the question no source answers.

**Done when** every claim sentence carries at least one citation and the matrix (where asked) has one row per readable source with the confidence column filled.

## 4. Check the memo against the inventory

Run `scripts/source-bound.py check MEMO.md --sources SOURCES_DIR --sentences`. It resolves every citation to a provided source, lists UNRESOLVED citations (a reference from memory, or to a file that was not given), lists provided sources never cited, and lists the sentences that rest on exactly one source. An unresolved citation is removed or replaced with a provided source; a never-cited readable source is either worked in or listed at the end with the reason it was not used.

**Done when** the check exits 0 and every single-source sentence is marked as such in the memo.

## 5. Close with the accounting

The memo ends with the bottom line restated, the next steps, and the accounting: sources used, sources unreadable, sources unused and why. The inventory and the check output are saved beside the memo.

**Done when** the accounting lists every file in the inventory exactly once.
