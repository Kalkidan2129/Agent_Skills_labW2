# SQL Review Template

Use this layout. Replace the bracketed parts and drop empty sections.

---

## SQL Review: [file name or "your query"]

**Verdict: [Looks correct / Correct but slow / Will return wrong results]. [One sentence: the most important thing.]**

### Findings

| # | Severity | Line | Issue | What goes wrong |
|---|---|---|---|---|
| 1 | 🔴 Wrong results | [n] | [short name] | [plain-English impact] |
| 2 | 🟡 Performance | [n] | ... | ... |
| 3 | ⚪ Readability | [n] | ... | ... |

### Details
For each 🔴 and 🟡 finding, give 2–4 sentences: what the code does, why that's a problem, and the fix as a small before/after snippet. Readability items can stay in the table only.

### Corrected query
```sql
-- Full corrected version, with a short comment on each changed line
```

**Want me to apply these changes to the file?** (Only offer this if the SQL came from a file.)

---

## Writing guidelines
- Severity order: 🔴 wrong results → 🟡 performance → ⚪ readability.
- Explain impact in business terms ("customers without orders vanish from the report").
- Give line numbers from the original file so the author can find each issue.
- Five or more readability nitpicks is noise. Keep the top three.
