# Data Quality Report Template

Use this structure for every report. Replace the bracketed parts.

---

## Data Quality Report: [file name]

**Verdict: [Ready for analysis / Ready with caveats / Not ready yet]. [One sentence on why.]**

**Dataset at a glance:** [N] rows × [M] columns · checked [date]

### Findings

| Severity | Column | Problem | Impact on analysis | Suggested fix |
|---|---|---|---|---|
| 🔴 | ... | ... | ... | ... |
| 🟡 | ... | ... | ... | ... |

(Sort 🔴 first, then 🟡. Leave out 🟢 rows; mention clean areas in one line below.)

**Looks good:** [e.g. "No missing values in customer_id, region, or product."]

### Recommended next steps
1. [Most important fix]
2. [Next fix]
3. [Optional: offer to create a cleaned copy as a new file]

---

## Writing guidelines
- Lead with the verdict. Busy readers may stop there.
- Describe impact in business terms ("totals will be inflated"), not just counts.
- Use exact numbers from the profiler. Never estimate a count you could measure.
- If there are no 🔴 or 🟡 findings, say so plainly and keep the report to a few lines.
