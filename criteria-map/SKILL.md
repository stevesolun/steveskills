---
name: criteria-map
description: "Draft a grant, funding or project proposal mapped to the criteria it will be judged on: an outline with one section per criterion, first drafts of the aims and significance with placeholders for preliminary data, budget and citations, and a map that shows the words devoted to each criterion, the criteria left thin or unmapped, and the placeholders still open. Use when preparing a grant or funding application, a proposal against a published template or rubric, or when asked which criteria a draft addresses weakly. Not for a document with no stated criteria."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Criteria Map

A proposal is read against a list, and the list is public: the funder's review criteria, the template's required sections, the rubric. The **map** is the draft laid over that list: for every criterion, the sections that answer it and how many words they carry, so a thin answer and a missing one are visible as numbers before a reviewer finds them, and so a placeholder is a counted thing rather than a hope.

## 1. Collect the inputs in one message

Ask once for: the funder and programme, the review criteria or template (pasted, or a link to the published text), the project idea and aims, what is new, the team and timeline, the word or page limits, and the field's register. The criteria go into `CRITERIA.txt`, one per line, with a colon and keywords where the funder's wording uses several terms for one criterion.

**Done when** `CRITERIA.txt` exists with every criterion the reviewers will score, in the funder's words.

## 2. Outline one section per criterion

Write the outline so that each criterion has a section whose heading uses the criterion's own words. Sections the limits force to merge name both criteria in the heading.

**Done when** the outline's headings cover the criteria file, and the word budget per section adds up to the limit.

## 3. Draft with placeholders, in the field's register

Draft the specific aims and significance first, then the rest. Figures the author has not supplied are placeholders in square brackets, `[PRELIMINARY DATA]`, `[BUDGET]`, `[CITATION]`, with a note of what should go there; a placeholder stays a placeholder until the author supplies the figure. The register is the field's, as in the author's own prior documents.

**Done when** every section has text or an explicit placeholder, and every number, result and reference in the draft came from the author's material.

## 4. Map the draft

Run `scripts/criteria-map.py CRITERIA.txt DRAFT.md --placeholders`. Per criterion it prints the mapped sections, the words devoted, the share of the draft and the placeholders in them, then the criteria that are unmapped (NONE) or thin, and every placeholder with its line.

**Done when** the map output is in the notes.

## 5. Strengthen the weak criteria, then close the placeholders

For each criterion the map shows as NONE, THIN or small in share relative to its weight in the review, say what would strengthen it (a specific aim that speaks to it, a paragraph the author can write from their data, a collaborator) and draft it where the material exists. Placeholders are closed by the author's figures, or the draft ships with the list of what is still open.

**Done when** the map's exit code is 0, or the author has the list of open placeholders and weak criteria with a suggestion for each.
