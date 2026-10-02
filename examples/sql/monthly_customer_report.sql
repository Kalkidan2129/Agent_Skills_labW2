-- Monthly customer report (sample with deliberate mistakes for testing the sql-query-review Skill)

-- Query 1: 2024 revenue per customer, including customers with no orders
SELECT c.customer_id, c.name, SUM(o.total) AS revenue
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01'          -- turns the LEFT JOIN into an INNER JOIN
GROUP BY 1, 2
ORDER BY 3 DESC;

-- Query 2: customers missing an email who never returned anything
SELECT *
FROM customers
WHERE email = NULL
  AND customer_id NOT IN (SELECT customer_id FROM returns);

-- Query 3: shipping fees for 2024 orders
SELECT DISTINCT o.order_id, o.shipping_fee
FROM orders o, order_items i
WHERE o.order_id = i.order_id
  AND YEAR(o.order_date) = 2024;

-- Query 4: customers whose last name ends in "son", from both regions
SELECT name FROM customers_east WHERE name LIKE '%son'
UNION
SELECT name FROM customers_west WHERE name LIKE '%son';

-- Query 5: clean up test orders
DELETE FROM orders;
