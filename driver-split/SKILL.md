---
name: driver-split
description: "Explain why a number moved by splitting the change into named parts that add up to it: per segment, how much came from the segment's weight shifting (mix) and how much from the rate inside it moving, with a residual called a residual. Use when asked why a metric fell or rose, what is driving a move, or how much of a change is one segment versus everything else. Not for a number with no before and after."
metadata:
  author: Steve Solun
  version: "1.0"
---

# Driver Split

"Why is it down?" has one honest shape of answer: a **split**, a list of named parts that add up to the change, biggest first, with anything unexplained called a residual and sized. A paragraph that names a cause without a size is a guess; a split that does not add up is two guesses.

## 1. Fix the number and the two points

Write the metric as it is defined (numerator, denominator, filters, window, timezone) and the two points being compared: last complete period against the one before, this region against that one, this cohort against the last. Confirm both ends are computed the same way; a definition change between the two points is the first driver to check.

**Done when** the before and after values are reproduced from the source with the same query, and they match the numbers the asker quoted or the difference is explained.

## 2. Choose the segmentation

Pick the dimension most likely to carry the move (region, product, channel, plan, cohort) and extract one row per segment: for a rate, `segment,before_num,before_den,after_num,after_den`; for a total, `segment,before,after`. Every row of the source belongs to exactly one segment, so the segments sum to the whole; an "other" bucket catches the rest.

**Done when** the segment file's numerators and denominators sum to the overall before and after values.

## 3. Split the change

Run `scripts/driver-split.py SEGMENTS.csv`. For a rate it prints, per segment, the mix effect (the segment's weight moved), the rate effect (the rate inside it moved) and the interaction, in percentage points, ranked by size, and checks that the parts add up to the change. For a total it prints each segment's change and share. Segments that pull in opposite directions are reported as such; a small net move can hide two large offsetting drivers.

**Done when** the script reports that the parts add up, and the largest driver is named with its size.

## 4. Go one level down on the largest driver

Take the largest driver and split it again on a second dimension (the UK on product mix, the trials journey on failure category) until the remaining move inside a segment is small or has a known cause with a date. Each level is its own run of the script, kept with its file.

**Done when** the largest remaining unexplained part is smaller than the smallest part the asker would act on, or is labelled residual with its size.

## 5. Write the answer as the split

One sentence with the move and its largest driver, then the table from the script, then one line per driver with the mechanism and its date (a promotion that started, a surcharge, a definition change), and the residual stated as approximate. Observations first, interpretation second, the segment file and the query saved beside the answer so the split can be rerun.

**Done when** the parts in the answer add up to the change the asker quoted, the residual is sized, and the files to rerun the split are saved.
