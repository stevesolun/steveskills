# steveskills

## 1.9.0

### Minor Changes

- The five engineering skills screened with one repetition in the first rounds were rerun at the four-repetition bar on TheAlgorithms/Python, with every sample run on their pages retaken there. **`red-at-base`** passed 4 of 4 (the baseline added a green-at-base boundary test every time), **`structure-map`** 4 of 4 (every entry of the skill arm's maps reproduced under the screener; the baseline's reproduced 0 to 17 of 15 to 33), **`acceptance-probes`** 3 of 4 (the baseline ticked the planted already-true criterion in three runs).
- Remove **`reconcile`** and **`decision-ledger`**: two wins of four each, on the plain asks only. When the prompt spelled the behaviour out (compare git with the claims and act on nothing; let nothing decided be lost) the baseline matched them. Their pages stay, archived, with the final runs.
- `deeper` was retested on a task where the shipped instrument misleads: one win, one tie, two runs in which the skill arm spent the hour without an answer. It stays archived.
- The plugin ships ten skills.

## 1.8.0

### Minor Changes

- Every remaining skill has now been through the benchmark. Screened this release, four repetitions each, two designs, pre-registered: **`tool-diet`** passed 4 of 4 (a fresh session's lookups cost 4 to 7 times fewer bytes in its tree), **`clean-log`** 3 of 4, **`driver-split`** 3 of 4, **`ab-readout`** 3 of 4, and **`whose-red`**, re-screened on four planted failures of four kinds, 3 of 4 (two earlier repetitions void: the baseline arm installed the missing module into the shared environment; the planted module is now one pip cannot install). Each README carries its table under "It's working if".
- Remove **`deeper`**: four ties of four. The baseline tested the question's false premise, worked from the raw history and anchored on the repository's own dates every time. Its page stays, archived.
- Remove **`with-receipts`**: two wins (the plain asks, where the baseline gave numbers with no query and no second route) and two ties when the prompt asked for the receipt; under the bar. Its page stays, archived.
- Remove **`answer-key`**: one win of four. The skill arm ran every standard question and kept a rerunnable key, but its report summarised the unchanged questions instead of listing expected against actual for each. Its page stays, archived.
- The plugin ships twelve skills.

## 1.7.0

### Minor Changes

- The benchmark is now the bar for being listed: a blind A/B against a baseline skill set, metric and win condition written down first, two designs, four repetitions, pass at three of four; a skill that fails is removed and its page stays as an archive. The root README carries the procedure and every result.
- Remove **`source-bound`**: four ties of four. The baseline read the folder, reported the unreadable files and cited by file name on its own, with or without the instruction. Nothing replaces it; its page stays, archived.
- Remove **`cite-or-cut`**: no win of four. The baseline fixed all nine planted defects every time; the grader's preference for the skill's edit pairs is not the benchmark. Nothing replaces it; its page stays, archived.
- `number-trace` rerun under the corrected unit rule (a number in a table whose column header carries the unit counts as found, flagged `unit apart`), four fresh repetitions: passed, three of four.

## 1.6.0

### Minor Changes

- Every skill's README is now a docs page in one shape: what it does and its defining constraint, when to reach for it (with the confusable siblings in a table), the skill's own leading word, common questions observed while building it, "it's working if" tells a reader can check in their own trace with the real sample run beneath, and where it fits among the other skills. Install blocks live in the root README once; each page carries the single-skill command only.
- `deeper`: the two `--full` points move to `FULL.md` beside the skill, loaded only on that branch; the leading word is `depth`.
- `acceptance-probes`: the build step hands off to the repository's own test-first flow instead of naming a skill that may not be installed, and step 4 is done when the implementation is committed with the probes file's checksum unchanged.
- The four research skills ran through a blind A/B against a baseline skill set, four repetitions each on tasks built from the system-design-primer and the Kubernetes enhancement template, with the metric and the win condition pre-registered. `criteria-map` won three of four. `number-trace` won none by the pre-registered rule (one source figure under a column header, the same row every time) while the baseline shipped up to 13 unlabelled figures on the plain ask and the blind grader scored the skill arm 4/4 every time. `source-bound` and `cite-or-cut` showed no measured advantage: the baseline kept to the folder and fixed the planted defects on its own. Each README says so under "It's working if".
- `number-trace`: a number whose unit sits apart from it in the source (a column header) is matched on the bare number and marked `unit apart`; `bytes` and `objects` are units.

### Patch Changes

- Completion criteria sharpened where a line could be met by opinion (`tool-diet` steps 2 and 3, `reconcile` step 3, `source-bound`, `criteria-map`, `number-trace`), and prohibitions rewritten as the behaviour wanted (`deeper`, `acceptance-probes`, `answer-key`, `decision-ledger`, `criteria-map`).

## 1.5.1

### Patch Changes

- `number-trace`: the trace is unit-aware (`10 ms` is not the `10` in `10,000 us`), skips dates, versions and section or figure numbers, traces a range such as `6-7` as one quantity, prints the source line each number matched (the line sharing the most words with the sentence when a number recurs), and counts a number the summary labels `(computed ...)`, `(assumed ...)`, `(estimated ...)` or `(from memory)` apart from the ones not found. Exit 1 only while a number is neither found nor labelled. SKILL.md 1.1.

## 1.5.0

### Minor Changes

- Add the research skills `number-trace`, `source-bound`, `cite-or-cut` and `criteria-map`, built from the standard research asks: understand a paper with its numbers, a memo or literature map from a folder of material, a draft revised for an advisor, a proposal against the funder's criteria. Sample runs on the system-design-primer and kubernetes/enhancements.
- Data skills' sample runs moved to vuejs/vue.

## 1.4.0

### Minor Changes

- Add the data skills `with-receipts`, `driver-split`, `answer-key`, `clean-log` and `ab-readout`, built from the standard data asks: a number with its receipt, why a metric moved, an answer key that gates analytics changes, a cleaned file with a computed change log, an A/B readout in the only safe order.

## 1.3.0

### Minor Changes

- Add `red-at-base`, `whose-red` and `structure-map`.

## 1.2.0

### Minor Changes

- Add `acceptance-probes`, `reconcile` and `decision-ledger`.

## 1.1.0

### Minor Changes

- Add `deeper`: rewrite a task for expert depth, not size, with `depth-check.py` counting the markers before and after.

## 1.0.0

### Minor Changes

- First release: `tool-diet`, with `rank-tool-results.py`, the Claude Code plugin and marketplace manifests, and Codex picker metadata.
