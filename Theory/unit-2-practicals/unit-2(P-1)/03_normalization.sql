-- P-1 Part 4 and 5: normalise the order table to 3NF, create the tables and insert sample data

-- ---------------------------------------------------------------------------
-- 0. The UNNORMALISED table given in the lab exercise
--    order_id | customer_name | customer_email | product_name | product_price | quantity
--    1 | Aarav | aarav@email    | Laptop   | 65000 | 1
--    1 | Aarav | aarav@email    | Mouse    |   500 | 2
--    2 | Diya  | diya@email     | Keyboard |  1500 | 1
--
-- Candidate key: (order_id, product_name)
--
-- Functional dependencies
--    order_id       -> customer_email                 (partial dependency, breaks 2NF)
--    product_name   -> product_price                  (partial dependency, breaks 2NF)
--    customer_email -> customer_name                  (transitive: order_id -> email -> name, breaks 3NF)
--    (order_id, product_name) -> quantity             (full dependency, OK)
--
-- 1NF: already atomic, no repeating groups, composite key identifies each row.
-- 2NF: remove partial dependencies -> split into orders / products / order_items.
-- 3NF: remove the transitive dependency -> move customer facts into customers.
-- ---------------------------------------------------------------------------

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id    INT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    id    INT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE orders (
    id          INT PRIMARY KEY,
    customer_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    order_id   INT NOT NULL,
    product_id INT NOT NULL,
    quantity   INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (id, name, email) VALUES
 (1, 'Aarav', 'aarav@email'),
 (2, 'Diya',  'diya@email');

INSERT INTO products (id, name, price) VALUES
 (1, 'Laptop',   65000),
 (2, 'Mouse',      500),
 (3, 'Keyboard',  1500);

INSERT INTO orders (id, customer_id) VALUES (1, 1), (2, 2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
 (1, 1, 1),
 (1, 2, 2),
 (2, 3, 1);

-- Verification: this join must give back exactly the original unnormalised rows
-- SELECT o.id AS order_id, c.name AS customer_name, c.email AS customer_email,
--        p.name AS product_name, p.price AS product_price, oi.quantity
-- FROM order_items oi
-- JOIN orders    o ON o.id = oi.order_id
-- JOIN customers c ON c.id = o.customer_id
-- JOIN products  p ON p.id = oi.product_id
-- ORDER BY o.id, p.id;
