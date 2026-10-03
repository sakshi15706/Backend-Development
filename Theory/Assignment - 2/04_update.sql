-- Task 5
UPDATE products
SET attributes = attributes || '{"discount_pct": 10}'
WHERE name = 'Wireless Mouse';

SELECT name, attributes FROM products WHERE name = 'Wireless Mouse';
