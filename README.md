# Agent Skills Lab

Claude Agent Skills for data analysis work. Open this folder in Claude Code and both Skills are picked up automatically because they live in `.claude/skills/`.

| Skill | What it does | Try it |
|---|---|---|
| [`data-quality-check`](.claude/skills/data-quality-check/SKILL.md) | Audits a dataset for missing values, duplicates, mixed formats and outliers; writes a readiness report | `/data-quality-check examples/messy_sales.csv` |
| [`sql-query-review`](.claude/skills/sql-query-review/SKILL.md) | Reviews SQL for wrong-result bugs, slow patterns and readability; read-only | `/sql-query-review examples/sql/monthly_customer_report.sql` |

To use a Skill in every project, copy its folder to `~/.claude/skills/`.

**Current version:** 1.1.0. See [CHANGELOG.md](CHANGELOG.md) for what changed.

## Structure

```
.claude/skills/
├── data-quality-check/              # Single-purpose Skill
│   ├── SKILL.md
│   ├── references/report-template.md
│   └── scripts/profile_data.py
└── sql-query-review/                # Multi-file Skill with tool restrictions
    ├── SKILL.md                     # Frontmatter + workflow (the "table of contents")
    ├── references/
    │   ├── review-checklist.md      # What to check, by severity
    │   ├── common-mistakes.md       # Before/after explanations
    │   └── dialect-notes.md         # Database differences, read only when needed
    ├── assets/
    │   └── review-template.md       # Output layout
    └── scripts/
        └── lint_sql.py              # Stdlib-only pattern checker
examples/
├── messy_sales.csv                  # 7 deliberate data problems
└── sql/monthly_customer_report.sql  # 12 deliberate SQL problems
```

## Tool access in `sql-query-review`

```yaml
allowed-tools:          # pre-approved: no permission prompt while the Skill runs
  - Read
  - Grep
  - Glob
  - Bash(python "${CLAUDE_SKILL_DIR}/scripts/lint_sql.py" *)
disallowed-tools:       # removed entirely while the Skill runs
  - Edit
  - Write
  - NotebookEdit
```

`allowed-tools` does **not** limit Claude to those tools; it only skips the approval prompt for them. `disallowed-tools` is what blocks tools. Both last until your next message.

## Running the scripts on their own

```bash
python .claude/skills/data-quality-check/scripts/profile_data.py examples/messy_sales.csv
python .claude/skills/sql-query-review/scripts/lint_sql.py examples/sql/monthly_customer_report.sql
```

## Test prompts

| Prompt | Expected Skill |
|---|---|
| "Can you sanity check examples/messy_sales.csv before I build a dashboard?" | data-quality-check |
| "my revenue query returns way too many rows, can you look at it?" (with SQL) | sql-query-review |
| "Why does this LEFT JOIN drop customers?" | sql-query-review |
| "Write me a query that lists the top 10 customers by revenue" | Neither (new query, not a review) |
| "Make a bar chart of sales by region" | Neither (charting) |

## Owner and feedback

**Maintainer:** Kalkidan ([@Kalkidan2129](https://github.com/Kalkidan2129))

| Skill | Owner |
|---|---|
| `data-quality-check` | @Kalkidan2129 |
| `sql-query-review` | @Kalkidan2129 |

**Found a problem or have an idea?** [Open an issue](https://github.com/Kalkidan2129/Agent_Skills_labW2/issues/new) and include:
1. **Which Skill:** e.g. `sql-query-review`
2. **What you typed:** the exact request or command
3. **What happened vs. what you expected:** e.g. "It didn't start" or "It missed the duplicate rows"
4. **The file you used**, if you can share it (remove any real customer data first)

**Skill didn't start when you expected it to?** Run `python tools/check_skills.py` first. It catches the most common setup mistakes.

**Want to change a Skill?** Make the change on a new branch and open a pull request. Before submitting:
- [ ] `python tools/check_skills.py` shows **OK** for every Skill
- [ ] The Skill still catches every problem in its file under `examples/`
- [ ] [CHANGELOG.md](CHANGELOG.md) has an entry describing the change
