-- Task 3: one query per category
-- books with more than 400 pages
SELECT name, attributes ->> 'author' AS author
FROM products
WHERE category = 'book' AND (attributes ->> 'pages')::int > 400;

-- laptops with at least 16GB RAM
SELECT name, attributes ->> 'cpu' AS cpu
FROM products
WHERE category = 'laptop' AND (attributes ->> 'ram_gb')::int >= 16;

-- black wireless accessories
SELECT name, attributes ->> 'color' AS color
FROM products
WHERE category = 'accessory'
  AND attributes ->> 'color' = 'black'
  AND (attributes ->> 'wireless')::boolean;

-- Task 4: containment
SELECT name FROM products WHERE attributes @> '{"wireless": true}';
