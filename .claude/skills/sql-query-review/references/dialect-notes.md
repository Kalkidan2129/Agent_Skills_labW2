# Dialect Notes

Read this only when a suggested fix depends on which database the user has. If unsure, give the fix in the user's apparent dialect and mention the alternative.

## How to recognize the dialect

| Clue in the query | Likely database |
|---|---|
| `SELECT TOP 10`, `[square brackets]`, `GETDATE()`, `ISNULL()` | SQL Server |
| `ILIKE`, `::date` casts, `DATE_TRUNC`, `"double-quoted"` identifiers | PostgreSQL |
| `` `backticks` ``, `IFNULL()`, `NOW()`, `LIMIT` | MySQL |
| `` `project.dataset.table` ``, `SAFE_CAST`, `DATE_TRUNC(date, MONTH)` | BigQuery |
| `strftime(...)`, `||` with few other clues | SQLite |

## Common differences

| Task | PostgreSQL | MySQL | SQL Server | BigQuery |
|---|---|---|---|---|
| First N rows | `LIMIT 10` | `LIMIT 10` | `SELECT TOP 10` / `OFFSET … FETCH` | `LIMIT 10` |
| Replace NULL | `COALESCE(x, 0)` | `COALESCE` / `IFNULL` | `COALESCE` / `ISNULL` | `COALESCE` / `IFNULL` |
| Concatenate | `a || b` | `CONCAT(a, b)` | `a + b` / `CONCAT` | `CONCAT(a, b)` |
| Current date | `CURRENT_DATE` | `CURDATE()` | `CAST(GETDATE() AS date)` | `CURRENT_DATE()` |
| Start of month | `DATE_TRUNC('month', d)` | `DATE_FORMAT(d, '%Y-%m-01')` | `DATETRUNC(month, d)` (2022+) | `DATE_TRUNC(d, MONTH)` |
| Case-insensitive match | `ILIKE` | `LIKE` (default collation) | `LIKE` (default collation) | `LOWER(a) LIKE LOWER(b)` |
| `5 / 2` | `2` (integers) | `2.5000` | `2` (integers) | `2.5` |
| NULL-safe equals | `IS NOT DISTINCT FROM` | `<=>` | `IS NOT DISTINCT FROM` (2022+) | `IS NOT DISTINCT FROM` |

## Percentages without integer division

```sql
-- PostgreSQL / SQL Server
100.0 * returned_count / total_count
-- or
CAST(returned_count AS decimal(10,2)) / total_count
```
