---
name: data-quality-check
description: Audits a dataset (CSV, Excel, or a table pasted into the chat) for data-quality problems and writes a short, plain-English report. Checks for missing values, duplicate rows, inconsistent formats (dates, capitalization, units), outliers, and columns with the wrong data type. Use this whenever the user wants to check, inspect, validate, profile, or "sanity check" a dataset before analysis, asks whether their data is clean or trustworthy, or mentions messy, dirty, or weird data, even if they don't say "data quality." Do not use it for building charts or running the actual analysis; this Skill only checks data readiness.
argument-hint: "[path to data file]"
---

# Data Quality Check

Your job is to tell the user, in plain English, whether their dataset is ready for analysis and what to fix first. The reader is often a student or business analyst, not a programmer, so explain problems in terms of their impact ("your monthly totals will be too high") rather than technical jargon.

This Skill **reports problems; it does not fix them.** Never modify, overwrite, or delete the user's original file. Changing data without being asked can silently corrupt someone's analysis. If the user wants fixes, offer them as a separate next step and write the cleaned data to a new file.

## Workflow

### 1. Get the data
- If the user gave a file path, use it. If they pasted a table, save it to a temporary CSV first.
- If no data was provided, ask for it. Don't guess.
- For Excel files, convert the relevant sheet to CSV (with pandas if it's available) and say which sheet you checked.

### 2. Run the profiler
Run the bundled script. It's stdlib-only Python, so it needs no installation:

```bash
python .claude/skills/data-quality-check/scripts/profile_data.py <path-to-csv>
```

The script prints a factual profile: row and column counts, missing values, duplicates, inferred types, mixed formats, and outliers. Using a script instead of eyeballing the data makes the counts exact and the same every time.

### 3. Interpret the results
Numbers alone aren't a report. For each finding, decide:
- **Severity**:
  - 🔴 *Fix before analysis*: will produce wrong answers, e.g. duplicate transactions or text in a numeric column.
  - 🟡 *Worth reviewing*: might be fine, e.g. outliers or a few missing optional fields.
  - 🟢 *Looks good*.
- **Impact**: what goes wrong in the analysis if this is ignored.
- **Suggested fix**: one concrete action.

Use judgment. A missing `middle_name` is normal, but a missing `order_total` isn't. Outliers can be real (a big customer), so flag them for review rather than calling them errors.

### 4. Write the report
Follow the template in `references/report-template.md`. Keep it short: lead with the verdict, then a findings table sorted by severity, then the next steps.

## Example

**User:** "Can you sanity check sales_q3.csv before I build my dashboard?"

**Good response (abbreviated):**
> **Verdict: Not ready yet. 2 issues to fix first.**
> | Severity | Column | Problem | Impact | Fix |
> |---|---|---|---|---|
> | 🔴 | (all) | 14 duplicate rows | Revenue overstated by ~3% | Remove exact duplicates |
> | 🔴 | `order_date` | 3 date formats mixed (2024-07-01, 07/01/2024, July 1) | Monthly grouping will split or drop rows | Standardize to YYYY-MM-DD |
> | 🟡 | `amount` | 2 values above $50,000 | May skew averages | Confirm they're real orders |
