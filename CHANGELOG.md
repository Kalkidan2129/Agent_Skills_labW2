# Changelog

All notable changes to the Skills in this repo. Newest first.

Version numbers follow **MAJOR.MINOR.PATCH**:
- **PATCH** (1.0.**1**): small fixes. Safe to update.
- **MINOR** (1.**1**.0): new Skills or features. Nothing existing breaks.
- **MAJOR** (**2**.0.0): a Skill behaves differently than before. Read the notes before updating.

## [1.1.0] - 2026-10-02

### Added
- **`sql-query-review` Skill.** Reviews SQL for wrong-result bugs, slow patterns, and readability, and explains each finding in plain English with a corrected query. Read-only: file-editing tools are switched off while it runs. Includes a pattern checker (`lint_sql.py`), a review checklist, before/after explanations, dialect notes, and a review template.
- **Sample SQL file** `examples/sql/monthly_customer_report.sql` with 12 deliberate problems, for testing.
- **Skill checkup script** `tools/check_skills.py`. Finds the common reasons a Skill doesn't trigger: a misnamed `SKILL.md`, invalid frontmatter, a vague or missing description, `disable-model-invocation`, and "when to use" text placed in the body.
- **Owner and feedback section** in the README, with how to report problems and a checklist for proposing changes.

### Fixed
- **`data-quality-check`:** the profiler script now runs when the Skill is installed outside this project (e.g. in `~/.claude/skills/`). It previously used a path that only worked from this repo's root.

## [1.0.0] - 2026-10-02

### Added
- **`data-quality-check` Skill.** Audits a dataset for missing values, duplicates, mixed date formats, inconsistent text, outliers, and wrong data types, then writes a plain-English readiness report. Includes a stdlib-only profiler script and a report template.
- **Sample dataset** `examples/messy_sales.csv` with 7 deliberate problems, for testing.
