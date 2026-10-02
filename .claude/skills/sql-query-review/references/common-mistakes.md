# Common SQL Mistakes: Explanations and Fixes

Each entry: what it looks like, why it's wrong in plain English, and the fix. The IDs match the lint script's rule names where one exists.

---

## null-comparison: `= NULL`

```sql
-- Wrong: returns zero rows, always
SELECT * FROM customers WHERE email = NULL;
-- Fixed
SELECT * FROM customers WHERE email IS NULL;
```
**Plain English:** NULL means "unknown." Asking "is this unknown thing equal to another unknown thing?" gives "unknown," not "yes," so no row ever matches.

---

## not-in-subquery: `NOT IN` with NULLs

```sql
-- Wrong: returns nothing if any returns.customer_id is NULL
SELECT name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM returns);
-- Fixed
SELECT c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM returns r WHERE r.customer_id = c.customer_id);
```
**Plain English:** One blank value in the list makes SQL unsure whether *any* customer is "not in" it, so it returns no one. `NOT EXISTS` doesn't have this trap.

---

## left-join-filtered: LEFT JOIN turned into INNER JOIN

```sql
-- Wrong: customers with no 2024 orders disappear
SELECT c.name, o.total
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';
-- Fixed: move the right-table condition into ON
SELECT c.name, o.total
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
                  AND o.order_date >= '2024-01-01';
```
**Plain English:** LEFT JOIN means "keep every customer, even without orders." But customers without orders have a blank `order_date`, and the WHERE filter throws those rows away, which undoes the LEFT JOIN.

---

## Join fan-out: inflated totals (no lint rule; needs judgment)

```sql
-- Wrong: each order's shipping_fee is repeated once per item
SELECT SUM(o.shipping_fee)
FROM orders o JOIN order_items i ON i.order_id = o.order_id;
-- Fixed: aggregate before joining, or don't join at all
SELECT SUM(shipping_fee) FROM orders;
```
**Plain English:** An order with 3 items appears 3 times after the join, so its shipping fee is counted 3 times.

---

## implicit-join: comma joins

```sql
-- Risky: forgetting the WHERE condition gives every customer × every order
SELECT * FROM customers c, orders o WHERE c.customer_id = o.customer_id;
-- Clearer
SELECT * FROM customers c JOIN orders o ON o.customer_id = c.customer_id;
```
**Plain English:** Writing the join condition next to the join makes it hard to forget, and forgetting it multiplies rows.

---

## delete-without-where / update-without-where

```sql
-- Dangerous: deletes every row
DELETE FROM orders;
-- Intended
DELETE FROM orders WHERE status = 'cancelled' AND order_date < '2023-01-01';
```
**Plain English:** Without a WHERE clause, the change applies to the whole table. Run the same WHERE as a `SELECT COUNT(*)` first to see how many rows it will touch.

---

## function-on-column: filters that block indexes

```sql
-- Slow: the database must compute YEAR() for every row
WHERE YEAR(order_date) = 2024
-- Fast: a range can use an index on order_date
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
```
**Plain English:** An index is like a sorted phone book. Asking for "names whose third letter is R" means reading every page, while asking for "names from Ra to Rz" lets you jump straight there.

---

## leading-wildcard: `LIKE '%text'`

**Plain English:** Same phone-book problem: "ends with *son*" can't use the alphabetical order. If this is a frequent search, consider a full-text index or a stored reversed column.

---

## select-star: `SELECT *`

**Plain English:** Fetches every column, including ones you don't use. That makes it slower, and the results change if someone adds a column later. List what you need.

---

## union-without-all: `UNION` vs `UNION ALL`

**Plain English:** `UNION` sorts and removes duplicates, which is extra work. If the two parts can't overlap (e.g. 2023 rows and 2024 rows), `UNION ALL` gives the same result faster. If they *can* overlap and you want duplicates removed, `UNION` is correct, so check before recommending a change.

---

## select-distinct: `DISTINCT` as a band-aid

**Plain English:** If duplicates appear "for no reason," a join is usually multiplying rows. `DISTINCT` hides the symptom, and any `SUM` alongside it is still wrong.

---

## ordinal-reference: `GROUP BY 1` / `ORDER BY 2`

**Plain English:** "Sort by the 2nd column" silently changes meaning when someone reorders the SELECT list. Use column names.
