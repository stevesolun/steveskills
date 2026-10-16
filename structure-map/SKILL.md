---
name: structure-map
description: "Write or refresh a repository structure map: the facts a fresh agent cannot recover from the file tree in under a minute, each paired with the command that proves it and the output to expect, checked by one script that reports confirmed and stale. Use when a session rediscovers dependency direction, the canonical file to edit or a generated directory, when onboarding to an unfamiliar repository, or when asked to document how the repo is laid out. Not for vocabulary, decisions, or anything a directory listing already shows."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Structure Map

A fresh session re-learns the same structural facts every time: which way dependencies run, which of three similar files is the one to edit, which directory is rewritten on commit. The **map** holds exactly those facts, and nothing a tree walk recovers in a minute, at `docs/STRUCTURE.md` (or wherever the repository's agent docs already point), under 60 lines. Every entry pairs the fact with its **proof**, the command a fresh agent would otherwise have had to run, and the output to expect, so the whole file is checked by running it, and an entry whose command returns something else is stale.

The entry:

```
- <fact, one sentence> | proof: `<command>` | expect: <output>
```

`expect` is a backticked fragment the output contains, a bare number (the whole output, or its line count), `empty`, or `exit <code>`.

## 1. Check what is already there

Run `scripts/map-check.py docs/STRUCTURE.md` (`--help` for the expect rules). It runs every proof read-only from the repository root and prints one line per entry, `confirmed` or `STALE`, with each stale entry's command and actual output under it, then `confirmed C, stale S`. With no map yet it exits 2, and step 2 starts from nothing.

Fix each stale entry from the actual output when the fact is still worth keeping, and remove it when the repository has moved on.

**Done when** the output is pasted and the stale count is 0, or the map does not exist yet.

## 2. Hunt for facts

Read this session, and the repository's recent sessions where they are logged, for every moment an agent needed more than one command to answer "where does this live", "which file is canonical", "what imports what" or "is this generated". Write each fact in one sentence, with the command that answered it.

**Done when** the list is written and each item names a fact, not a search.

## 3. Apply the minute test

Look at the command that recovers each fact. One `ls`, one file read or one `--help` fails the test: the tree already says it, so the fact is dropped. A search across files, a history walk or a comparison of two files passes.

**Done when** every surviving fact has a proof command that passes the test.

## 4. Write the entries

Run each surviving proof now and copy its expect from the output. Add the entries under at most four headings chosen from: dependency direction, canonical editing surface, generated or compatibility-only, entry points for cross-cutting concerns, boundaries to check before moving files. Add one line pointing at the map to the repository's agent instructions if none is there.

**Done when** every new entry has a proof and an expect taken from a run in this session, and `wc -l docs/STRUCTURE.md` is under 60.

## 5. Confirm, then commit

Run `scripts/map-check.py docs/STRUCTURE.md` again and paste the output. Its exit code is the completion criterion: 0 means every entry confirmed, at least one entry, and the file within the cap. Commit the map after that run, and report `<N> entries: <K> confirmed, <F> fixed, <R> removed, <A> added`.

**Done when** the last run exits 0 and the commit that carries the map comes after it.
