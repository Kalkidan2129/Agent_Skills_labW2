---
name: sql-query-review
description: Reviews SQL queries for correctness bugs, performance problems, and readability, then explains each finding in plain English with a corrected version. Catches issues like comparing to NULL with =, NOT IN with NULLs, LEFT JOINs silently turned into INNER JOINs, join fan-out that inflates totals, UPDATE/DELETE without WHERE, SELECT *, and filters that block index use. Use this whenever the user shares SQL (a .sql file or a query pasted into the chat) and asks to review, check, debug, explain, optimize, or "look over" it, or says a query returns wrong numbers, too many or too few rows, or runs slowly, even if they never say "review." Not for writing brand-new queries from scratch or for running queries against a database.
argument-hint: "[file.sql]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(python "${CLAUDE_SKILL_DIR}/scripts/lint_sql.py" *)
disallowed-tools:
  - Edit
  - Write
  - NotebookEdit
---

# SQL Query Review

You are reviewing someone else's SQL. Your job is to find what will give **wrong answers** first, then what will be **slow**, then what is **hard to read**, and explain each in terms the author cares about ("your revenue total is double-counted") rather than jargon.

## Ground rules

- **Review only. Don't change files or run queries.** The author may be mid-edit, the file may be shared, and running even a SELECT against a production database can be slow or costly. File editing tools are switched off while this Skill is active. Show corrected SQL in your reply instead, and offer to apply it if they want. They can say so in their next message.
- **Confirm before you claim.** The lint script flags patterns, not proven bugs. Read the surrounding query before reporting a finding, and drop false alarms.
- **Ask about the dialect only if it changes the answer.** Otherwise infer it from syntax (`TOP` means SQL Server, `ILIKE` means PostgreSQL, backticks mean MySQL or BigQuery).

## Workflow

### 1. Get the SQL
- File path given (or `$ARGUMENTS`): read it.
- SQL pasted in chat: use it directly.
- Nothing provided: ask for the query. Don't invent one.

### 2. Run the lint script
Run it on a file:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/lint_sql.py" path/to/query.sql
```
For pasted SQL, pipe it in with `-`:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/lint_sql.py" - <<'SQL'
SELECT ...
SQL
```
It prints findings with line numbers and severity. It is fast and exact for pattern-level problems.

### 3. Review the logic yourself
The script can't understand intent: whether a join duplicates rows, whether a filter matches the business question, or whether a date range is off by one. Work through **[references/review-checklist.md](references/review-checklist.md)** for these. This step is where most real bugs are found.

### 4. Explain the findings
For each confirmed issue, look up the matching entry in **[references/common-mistakes.md](references/common-mistakes.md)**. It has before/after examples and plain-English explanations you can adapt. Read **[references/dialect-notes.md](references/dialect-notes.md)** only when a fix depends on the database (date functions, `LIMIT` vs `TOP`, string concatenation).

### 5. Write the review
Use the layout in **[assets/review-template.md](assets/review-template.md)**: verdict first, findings by severity, then one full corrected query. If the query is fine, say so in two lines. Don't pad the review with nitpicks.
