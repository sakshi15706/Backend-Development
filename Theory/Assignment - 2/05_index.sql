-- Task 6: bulk data so the index matters (5 rows would always seq scan)
INSERT INTO products (name, category, price, attributes)
SELECT 'Item ' || g, 'accessory', 100,
       jsonb_build_object('color', 'red', 'wireless', (g % 1000 = 0))
FROM generate_series(1, 100000) g;
ANALYZE products;

-- BEFORE index
EXPLAIN ANALYZE SELECT name FROM products WHERE attributes @> '{"wireless": true}';
EXPLAIN ANALYZE SELECT name FROM products WHERE category = 'laptop' AND (attributes ->> 'ram_gb')::int >= 16;

CREATE INDEX idx_products_attributes ON products USING GIN (attributes);
ANALYZE products;

-- AFTER index
EXPLAIN ANALYZE SELECT name FROM products WHERE attributes @> '{"wireless": true}';
EXPLAIN ANALYZE SELECT name FROM products WHERE category = 'laptop' AND (attributes ->> 'ram_gb')::int >= 16;
