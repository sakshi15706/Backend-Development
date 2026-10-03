INSERT INTO products (name, category, price, attributes) VALUES
('Clean Code', 'book', 499.00, '{"author": "Robert C. Martin", "pages": 464}'),
('The Pragmatic Programmer', 'book', 650.00, '{"author": "Andrew Hunt", "pages": 352}'),
('ThinkPad X1', 'laptop', 125000.00, '{"ram_gb": 32, "cpu": "Intel i7"}'),
('MacBook Air', 'laptop', 99000.00, '{"ram_gb": 8, "cpu": "Apple M2"}'),
('Wireless Mouse', 'accessory', 1299.00, '{"color": "black", "wireless": true}');

SELECT * FROM products;
