# Agent Skills Lab: `data-quality-check`

A Claude Agent Skill that audits a dataset for data-quality problems (missing values, duplicates, mixed date formats, inconsistent text, outliers, wrong data types) and writes a short, plain-English report saying whether the data is ready for analysis.

## Structure

```
.claude/skills/data-quality-check/
├── SKILL.md                    # Frontmatter (name + description) and instructions
├── references/
│   └── report-template.md      # Report layout Claude follows
└── scripts/
    └── profile_data.py         # Stdlib-only Python profiler (no installs needed)
examples/
└── messy_sales.csv             # Sample data with 7 deliberate problems, for testing
```

## Using it

Open this folder in Claude Code. The Skill is picked up automatically because it lives in `.claude/skills/`.

- **Automatically:** ask something like *"Can you sanity check examples/messy_sales.csv before I analyze it?"*
- **Directly:** type `/data-quality-check examples/messy_sales.csv`

To use it in every project, copy the `data-quality-check` folder to `~/.claude/skills/`.

## Running the profiler on its own

```bash
python .claude/skills/data-quality-check/scripts/profile_data.py examples/messy_sales.csv
```

## Test prompts

| Prompt | Should trigger? |
|---|---|
| "Can you sanity check examples/messy_sales.csv before I build a dashboard?" | Yes |
| "something feels off about this spreadsheet, is it clean?" | Yes |
| "Make a bar chart of sales by region from messy_sales.csv" | No (charting) |
