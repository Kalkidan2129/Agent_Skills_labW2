# SQL Review Checklist

Work top to bottom. Correctness issues give wrong answers silently, so they matter most.

## 1. Correctness: does it return the right rows and numbers?

**Joins**
- [ ] Is every join's `ON` condition complete? A missing key column (e.g. joining on `customer_id` but not `region` when both are needed) multiplies rows.
- [ ] **Fan-out:** joining a one-to-many table (orders → order_items) before `SUM`/`COUNT` repeats the "one" side's values. Check whether totals from the "one" side get inflated.
- [ ] **LEFT JOIN undone:** a `WHERE` condition on the right-hand table (other than `IS NULL`) removes the unmatched rows, turning it into an INNER JOIN. Move the condition into `ON` if the intent was to keep all left rows.
- [ ] Old-style comma joins (`FROM a, b`) with a missing condition create a cross join (every row × every row).

**NULLs**
- [ ] `= NULL` / `<> NULL` is never true. Use `IS NULL` / `IS NOT NULL`.
- [ ] `NOT IN (subquery)` returns zero rows if the subquery contains any NULL. Use `NOT EXISTS`.
- [ ] `COUNT(column)` skips NULLs; `COUNT(*)` doesn't. Is the right one used?
- [ ] `AVG` ignores NULLs. Should missing values count as 0?
- [ ] `col <> 'x'` also excludes rows where `col` is NULL. Is that intended?

**Filters and dates**
- [ ] Does the filter match the business question (e.g. "Q3" means July 1 to Sept 30 inclusive)?
- [ ] `BETWEEN '2024-01-01' AND '2024-01-31'` on a datetime column misses most of Jan 31. Prefer `>= '2024-01-01' AND < '2024-02-01'`.
- [ ] `AND`/`OR` mixed without parentheses. `a OR b AND c` means `a OR (b AND c)`.

**Aggregation**
- [ ] Every non-aggregated column in `SELECT` is in `GROUP BY` (some databases allow this silently and return arbitrary values).
- [ ] Filtering on an aggregate belongs in `HAVING`, not `WHERE`.
- [ ] Integer division: `5 / 2` is `2` in SQL Server and PostgreSQL. Cast before dividing for percentages.
- [ ] `DISTINCT` hiding a fan-out bug instead of fixing the join.

**Data-changing statements**
- [ ] `UPDATE` / `DELETE` without `WHERE` affects every row.
- [ ] Is there a transaction or backup plan for destructive changes?

## 2. Performance: will it run in reasonable time?

- [ ] `SELECT *` on wide tables. Select only the needed columns.
- [ ] Functions on filtered columns (`WHERE YEAR(order_date) = 2024`) block index use. Rewrite as a range.
- [ ] `LIKE '%text'` (leading wildcard) can't use an index.
- [ ] `UNION` deduplicates (slow). Use `UNION ALL` if duplicates are impossible or acceptable.
- [ ] Correlated subqueries in `SELECT` run once per row. Consider a join or window function.
- [ ] `ORDER BY` on large results without `LIMIT`/`TOP`, when only the top N are needed.

## 3. Readability: can the next person understand it?

- [ ] Meaningful aliases (`o` for orders is fine; `a`, `b`, `c` is not).
- [ ] Positional `GROUP BY 1, 2` / `ORDER BY 3` breaks silently when columns are reordered.
- [ ] Deeply nested subqueries. CTEs (`WITH ...`) read top to bottom.
- [ ] Consistent keyword casing and one clause per line.
- [ ] Magic numbers explained (`status = 4` → comment what 4 means).
