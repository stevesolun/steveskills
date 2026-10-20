---
name: ab-readout
description: "Write up an A/B test from its counts with the numbers computed, in order: sample ratio mismatch first, rates with intervals, lift with its confidence interval and p-value, the smallest effect this sample could detect, then one verdict line. Use when asked to summarise, read out or recommend on an A/B test or experiment, or when a test result is about to decide a launch. Not for observational comparisons with no randomised assignment."
metadata:
  author: Steve Solun
  version: "1.0"
---

# A/B Readout

An experiment write-up has four numbers that decide everything, and the order matters: whether the split was the planned split, the rates, the lift with its uncertainty, and the smallest effect the sample could have seen. The **readout** prints them in that order from the counts, so the recommendation is the last line, after the numbers.

## 1. Fix the counts and the plan

From the experiment's own assignment and event logs (the dashboard is the cross-check): users per arm (one row per user, assigned once), conversions per arm by the metric the test was planned on, the planned split, the planned minimum detectable effect and the planned duration. A metric chosen after seeing results is a second test and is labelled as such.

**Done when** the four counts, the planned split and the planned effect are written down with their sources.

## 2. Run the readout

`scripts/ab-readout.py --control USERS CONV --treatment USERS CONV --split 0.5 --mde 0.02`. It prints the sample ratio mismatch test, the conversion rate per arm with a 95% interval, the absolute and relative lift with a confidence interval and p-value, the smallest effect detectable at 80% power with this sample and the sample needed for the planned effect, and one verdict line. Exit 1 on a sample ratio mismatch.

**Done when** the output is in the write-up verbatim.

## 3. Read the verdict in order

A sample ratio mismatch ends the readout (exit code 1): the assignment is broken, and the write-up says so and stops. "Detected" is a lift whose interval excludes zero. "Not detected and underpowered" means the test could not have seen the planned effect, and the write-up says so instead of "no effect". "Not detected with adequate power" means the effect, if any, lies inside the printed interval, and the write-up quotes that interval.

**Done when** the write-up's conclusion is the script's verdict line, with its numbers.

## 4. Check the things the counts cannot show

Stopping rule honoured (the test ran its planned duration), novelty (the lift in the last week against the first), guardrail metrics unchanged, segments only as hypotheses for the next test. Each of these is a line with a number or "not measured".

**Done when** each check has a line, and any failed check is above the verdict in the write-up.

## 5. Recommend with the uncertainty attached

One line: ship, do not ship, or extend to N users per arm, with the interval it rests on. The counts, the command and the output are saved with the write-up so the next person can rerun it.

**Done when** the recommendation names the interval and the saved files exist.
