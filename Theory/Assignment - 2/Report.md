# PostgreSQL as SQL + NoSQL

**Working with JSONB: A Product Catalog using PostgreSQL and MongoDB**

*Database Systems / NoSQL, Assignment 2: Report*

Student: Sakshi Jaiswal | Sap Id: 590015706  

## 1. Introduction and Objective

This assignment studies how PostgreSQL's `jsonb` data type lets one relational database work as both a SQL engine and a NoSQL (document-style) engine. A product catalog is built in which every product has fixed typed columns (`id`, `name`, `category`, `price`) and one `jsonb` column (`attributes`) that holds category-specific details such as `author`/`pages` for books, `cpu`/`ram_gb` for laptops and `color`/`wireless` for accessories. The same data is then recreated in MongoDB for comparison.

Objectives:

- Understand `jsonb` and how it differs from `json` (storage format, write speed, query and index speed).
- Build a hybrid table that combines strictly typed columns with a flexible `jsonb` column.
- Query JSONB data using the operators `->`, `->>`, `@>` and `?`.
- Add new attributes to existing rows without altering the table structure.
- Measure the effect of a GIN index using `EXPLAIN ANALYZE`.
- Compare PostgreSQL + `jsonb` with MongoDB and decide where each is the better fit.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Relational database | PostgreSQL | SQL engine with `jsonb` document support |
| Document database | MongoDB Community Server | Native NoSQL store used for comparison |
| PostgreSQL client | `psql` | Runs SQL files from the terminal |
| MongoDB client | `mongosh` | Runs MongoDB shell scripts |
| Editor | Visual Studio Code | Writing and running the project files |
| Index type | GIN (Generalized Inverted Index) | Speeds up JSONB containment queries |
| Version control (optional) | Git and GitHub | Code hosting and submission |

## 3. Installation and Setup

### 3.1 Prerequisites

- PostgreSQL installed (check with `psql --version`).
- MongoDB server running at `mongodb://127.0.0.1:27017`, and `mongosh` installed (check with `mongosh --version`).
- A code editor such as VS Code.

### 3.2 Steps

1. Open a terminal inside the project folder `assignment2`.
2. Create the PostgreSQL database:

```
   psql -U postgres -c "CREATE DATABASE assignment2;"
```

3. Run the SQL files in order:

```
   psql -U postgres -d assignment2 -f 01_schema.sql
   psql -U postgres -d assignment2 -f 02_insert.sql
   psql -U postgres -d assignment2 -f 03_queries.sql
   psql -U postgres -d assignment2 -f 04_update.sql
   psql -U postgres -d assignment2 -f 05_index.sql
```

4. Make sure the MongoDB service is running, then run the MongoDB script:

```
   mongosh --file mongo.js
```

5. Each command prints its results in the terminal. These outputs are used as screenshots in this report.

### 3.3 Database Configuration

| Setting | PostgreSQL | MongoDB |
|---|---|---|
| Host / port | localhost : 5432 | 127.0.0.1 : 27017 |
| Database | assignment2 | assignment2 |
| Table / collection | products | products |
| Created by | `01_schema.sql` | Created automatically on first insert |

## 4. Project Structure

```
assignment2/
├── 01_schema.sql     # Task 1: create products table
├── 02_insert.sql     # Task 2: insert 5 products, 3 categories
├── 03_queries.sql    # Tasks 3 and 4: attribute and containment queries
├── 04_update.sql     # Task 5: add attribute without ALTER TABLE
├── 05_index.sql      # Task 6: bulk data, GIN index, EXPLAIN ANALYZE
├── mongo.js          # Task 7: MongoDB equivalent
└── REPORT.md         # This report
```

## 5. Part A: Conceptual Questions

### 5.1 What is `jsonb`, and how does it differ from `json`?

PostgreSQL offers two types for JSON data. The `json` type stores an exact copy of the input text, so whitespace, key order and duplicate keys are all preserved. Because it is only text, the whole value must be re-parsed every time it is accessed. The `jsonb` type parses the input once, at write time, and stores it in a decomposed binary format. During that conversion it removes insignificant whitespace, keeps only the last value of any duplicate key, and does not preserve key order.

*Write speed:* `jsonb` is slightly slower to insert because of the conversion step. *Query speed:* it is much faster to read and process, since nothing needs re-parsing. *Indexing:* only `jsonb` supports GIN indexes and the containment and existence operators (`@>`, `?`). For these reasons `jsonb` is the better choice in almost every case; `json` is useful only when the exact original text must be preserved.

```sql
SELECT '{"a": 1, "a": 2}'::json;   -- {"a": 1, "a": 2}   (stored as-is)
SELECT '{"a": 1, "a": 2}'::jsonb;  -- {"a": 2}           (normalised)
```

### 5.2 How can PostgreSQL work as both a SQL and a NoSQL database in the same table?

PostgreSQL allows strictly typed relational columns and a flexible `jsonb` column to live in the same table. Attributes that every row shares, such as `id`, `name` and `price`, are defined as normal columns with data types and constraints (`PRIMARY KEY`, `NOT NULL`). Attributes that differ from row to row are stored in the `jsonb` column. A book can hold `author` and `pages`, while a laptop holds `cpu` and `ram_gb`, with no `ALTER TABLE` and without many mostly-NULL columns.

This gives document-style flexibility where it is needed, while the core data keeps foreign keys, joins and ACID transactions. Both kinds of data can be filtered together in a single query, which a separate SQL database plus a separate document database cannot do without application-side merging.

```sql
CREATE TABLE products (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    attributes JSONB
);

SELECT name FROM products
WHERE price < 1000 AND attributes @> '{"wireless": true}';
```

### 5.3 JSONB operators `->`, `->>`, `@>`, `?`

Assume a row where `attributes = '{"cpu": "i7", "ram_gb": 16, "wireless": true}'`.

| Operator | Example | Returns |
|---|---|---|
| `->` | `SELECT attributes -> 'cpu' FROM products;` | `"i7"` (type `jsonb`, quotes kept) |
| `->>` | `SELECT attributes ->> 'cpu' FROM products;` | `i7` (type `text`) |
| `@>` | `SELECT attributes @> '{"ram_gb":16}' FROM products;` | `true` (boolean) |
| `?` | `SELECT attributes ? 'wireless' FROM products;` | `true` (boolean) |

**Difference between `->` and `->>`.** The operator `->` returns a `jsonb` value, so a string keeps its JSON quotes and the result can be chained further, for example `attributes -> 'specs' -> 'cpu'`. The operator `->>` returns plain `text`, which is what is needed for comparisons, display or casting, for example `(attributes ->> 'ram_gb')::int >= 16`. The operator `@>` checks whether the left document contains the right one, and `?` checks whether a top-level key exists.

### 5.4 How can a GIN index on a `jsonb` column change query performance?

A GIN (Generalized Inverted Index) records every key and value found inside the documents together with the rows that contain them. Without it, PostgreSQL has to perform a sequential scan, reading every row and inspecting each document. With a GIN index it looks up the matching rows directly. The index speeds up **containment and key-existence queries**: `@>`, `?`, `?|` and `?&`.

It does **not** help queries on a value extracted with `->>`, such as `WHERE (attributes ->> 'ram_gb')::int >= 16`. The index stores whole key/value entries and has no ordering, so range comparisons cannot use it. A B-tree expression index suits that case. The trade-off is that GIN indexes use extra disk space and make writes slightly slower.

```sql
CREATE INDEX idx_attr_gin ON products USING GIN (attributes);          -- helps @>
CREATE INDEX idx_ram ON products (((attributes ->> 'ram_gb')::int));   -- helps range on ram_gb
```

### 5.5 Where could PostgreSQL + `jsonb` replace MongoDB, and where is MongoDB the better fit?

| Factor | PostgreSQL + jsonb | MongoDB |
|---|---|---|
| **Transactions** | Full multi-row, multi-table ACID by default | Multi-document transactions exist but are newer and costlier |
| **Joins** | Native, optimised relational joins | `$lookup` works but is clunkier and slower |
| **Schema enforcement** | Typed columns, constraints, `CHECK` on JSON content | Flexible by default; validation is optional |
| **Horizontal scaling** | Mainly vertical; sharding needs Citus or manual partitioning | Built-in sharding and replica sets |

PostgreSQL with `jsonb` can replace MongoDB for catalogs, user profiles and event metadata, where data is partly structured and partly flexible and where transactions and joins matter. MongoDB remains the better fit when the workload is mostly deeply nested documents, needs very high write throughput, or must be distributed across many nodes, because sharding is a built-in feature there.

```sql
SELECT o.id, p.name
FROM orders o JOIN products p ON p.id = o.product_id
WHERE p.attributes @> '{"wireless": true}';   -- relational join + JSON filter together
```

## 6. Part B: Working of the Exercise

### 6.1 Overview of Tasks

| Task | File | Purpose |
|---|---|---|
| 1 | `01_schema.sql` | Create the `products` table with fixed columns and one `jsonb` column |
| 2 | `02_insert.sql` | Insert 5 products in 3 categories with different attribute keys |
| 3 | `03_queries.sql` | One query per category filtering on a category-specific attribute |
| 4 | `03_queries.sql` | Containment query using `@>` |
| 5 | `04_update.sql` | Add a new attribute to an existing row without `ALTER TABLE` |
| 6 | `05_index.sql` | Create a GIN index and compare `EXPLAIN ANALYZE` before and after |
| 7 | `mongo.js` | Recreate the data and queries in MongoDB |

### 6.2 Application Flow

```
Task 1: Create table
   |
   v
Task 2: Insert 5 products  --->  Task 3 and 4: Query (->>, @>)
   |
   v
Task 5: Update JSONB (||)
   |
   v
Task 6: Bulk data --> EXPLAIN ANALYZE --> GIN index --> EXPLAIN ANALYZE
   |
   v
Task 7: Same data and queries in MongoDB --> Comparison
```

### 6.3 How each task works

**Task 1: Schema.** The table has four typed columns with constraints (`id` is an identity primary key, `name`, `category` and `price` are `NOT NULL`) and one nullable `jsonb` column named `attributes`.

```sql
CREATE TABLE products (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    attributes JSONB
);
```
*Output:* *(screenshot of `\d products`)*

**Task 2: Insert data.** Five products are inserted across three categories. Each category uses different keys in `attributes`.

```sql
INSERT INTO products (name, category, price, attributes) VALUES
('Clean Code', 'book', 499.00, '{"author": "Robert C. Martin", "pages": 464}'),
('The Pragmatic Programmer', 'book', 650.00, '{"author": "Andrew Hunt", "pages": 352}'),
('ThinkPad X1', 'laptop', 125000.00, '{"ram_gb": 32, "cpu": "Intel i7"}'),
('MacBook Air', 'laptop', 99000.00, '{"ram_gb": 8, "cpu": "Apple M2"}'),
('Wireless Mouse', 'accessory', 1299.00, '{"color": "black", "wireless": true}');
```
*Output:* *(screenshot of `SELECT * FROM products;`)*

**Task 3: Query by category-specific attribute.** The value is extracted with `->>` (text) and cast to the required type before comparing.

```sql
SELECT name, attributes ->> 'author' AS author FROM products
WHERE category = 'book' AND (attributes ->> 'pages')::int > 400;

SELECT name, attributes ->> 'cpu' AS cpu FROM products
WHERE category = 'laptop' AND (attributes ->> 'ram_gb')::int >= 16;

SELECT name, attributes ->> 'color' AS color FROM products
WHERE category = 'accessory'
  AND attributes ->> 'color' = 'black'
  AND (attributes ->> 'wireless')::boolean;
```

| Query | Expected result |
|---|---|
| Books with more than 400 pages | Clean Code, Robert C. Martin |
| Laptops with at least 16 GB RAM | ThinkPad X1, Intel i7 |
| Black wireless accessories | Wireless Mouse, black |

*Output:* *(screenshot)*

**Task 4: Containment query.** The `@>` operator finds rows whose document contains the given key/value pair.

```sql
SELECT name FROM products WHERE attributes @> '{"wireless": true}';
```
*Expected result:* `Wireless Mouse`  |  *Output:* *(screenshot)*

**Task 5: Update JSONB without altering the table.** The `||` operator merges a new key into the existing document. The table structure does not change and no other row is affected.

```sql
UPDATE products
SET attributes = attributes || '{"discount_pct": 10}'
WHERE name = 'Wireless Mouse';
```
*Expected result:* `{"color": "black", "wireless": true, "discount_pct": 10}`  |  *Output:* *(screenshot)*

**Task 6: Index and compare.** With only 5 rows PostgreSQL always prefers a sequential scan, so 100,000 extra rows are generated first. `EXPLAIN ANALYZE` is run before and after creating the GIN index.

```sql
CREATE INDEX idx_products_attributes ON products USING GIN (attributes);
EXPLAIN ANALYZE SELECT name FROM products WHERE attributes @> '{"wireless": true}';
```

| Query | Scan before index | Time before (ms) | Scan after index | Time after (ms) |
|---|---|---|---|---|
| `attributes @> '{"wireless": true}'` | | | | |
| `(attributes ->> 'ram_gb')::int >= 16` | | | | |

*Output:* *(screenshots of both EXPLAIN ANALYZE results)*

*Observation (complete using your results):* The containment query changes from a Seq Scan to a Bitmap Index Scan on `idx_products_attributes` and its execution time drops. The `->>` range query does not use the GIN index, because GIN supports containment and existence operators, not range comparisons.

**Task 7: MongoDB comparison.** The same five products are inserted as documents with a nested `attributes` object, and the equivalents of the Task 3 queries are run. MongoDB uses dot notation for nested fields and native types, so no casting is needed.

```javascript
db.products.find({ category: "book", "attributes.pages": { $gt: 400 } })
db.products.find({ category: "laptop", "attributes.ram_gb": { $gte: 16 } })
db.products.find({ category: "accessory", "attributes.color": "black", "attributes.wireless": true })
db.products.createIndex({ "attributes.wireless": 1 })
```
*Output:* *(screenshot of `mongosh` results)*

## 7. Database Design

**PostgreSQL.** Each product is one row in the `products` table. Common fields are typed columns; variable fields are a `jsonb` document.

| Column | Type | Constraint |
|---|---|---|
| id | INTEGER | Identity, primary key |
| name | VARCHAR(100) | NOT NULL |
| category | VARCHAR(50) | NOT NULL |
| price | NUMERIC(10,2) | NOT NULL |
| attributes | JSONB | Nullable, holds category-specific keys |

**MongoDB.** The same product is one document in the `products` collection:

```json
{
  "_id": "ObjectId(...)",
  "name": "ThinkPad X1",
  "category": "laptop",
  "price": 125000.00,
  "attributes": { "ram_gb": 32, "cpu": "Intel i7" }
}
```

*Design reasoning:* the hybrid PostgreSQL design keeps data integrity on the fields every product needs, while the `jsonb` column avoids one column per possible attribute, which would leave most cells NULL. In MongoDB, the whole product is one flexible document and the database enforces no structure unless validation rules are added.

## 8. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| `psql` is not recognized | PostgreSQL `bin` folder is not in PATH | Add the folder (for example `C:\Program Files\PostgreSQL\16\bin`) to PATH, or use the full path to `psql.exe` |
| `password authentication failed` | Wrong password for the `postgres` user | Use the password set during installation |
| `relation "products" does not exist` | Files were run out of order | Run `01_schema.sql` first, then the others in order |
| Duplicate rows after re-running `02_insert.sql` | Insert was executed twice | Re-run `01_schema.sql` (it drops and recreates the table), then insert once |
| Comparison on `pages` or `ram_gb` gives a text or operator error | `->>` returns text, not a number | Cast the value, e.g. `(attributes ->> 'pages')::int` |
| Index not used after `CREATE INDEX` | Only 5 rows, so a sequential scan is cheaper | Generate 100,000 rows and run `ANALYZE products` before comparing |
| GIN index not used for the laptop RAM query | GIN does not support range comparison on `->>` values | Use a B-tree expression index on `((attributes ->> 'ram_gb')::int)` |
| `mongosh < mongo.js` fails in PowerShell | `<` redirection is not supported | Use `mongosh --file mongo.js` |

## 9. Testing

| Test | Expected Result |
|---|---|
| Run `SELECT * FROM products;` after inserts | 5 rows in 3 categories with different attribute keys |
| Books with more than 400 pages | Only Clean Code |
| Laptops with at least 16 GB RAM | Only ThinkPad X1 |
| Black wireless accessories | Only Wireless Mouse |
| `attributes @> '{"wireless": true}'` | Wireless Mouse |
| Update Wireless Mouse with `\|\|` | `discount_pct: 10` added; table structure unchanged; other rows unchanged |
| `EXPLAIN ANALYZE` before the GIN index | Seq Scan on `products` |
| `EXPLAIN ANALYZE` after the GIN index | Bitmap Index Scan on `idx_products_attributes`, lower execution time |
| MongoDB queries from `mongo.js` | Same products returned as in PostgreSQL |

## 10. Comparison: PostgreSQL JSONB vs MongoDB

| Aspect | PostgreSQL JSONB | MongoDB |
|---|---|---|
| **Syntax** | SQL with `->>` and casts, e.g. `(attributes ->> 'ram_gb')::int >= 16` | JSON-style filters with dot notation, e.g. `"attributes.ram_gb": {$gte: 16}` |
| **Data types** | Values extracted as text, then cast | Native types, no casting |
| **Indexing** | One GIN index covers all keys (containment/existence only); B-tree expression indexes for ranges | Index on specific paths, e.g. `attributes.wireless` |
| **Schema** | Fixed columns plus flexible JSON | Fully flexible documents |
| **Joins / transactions** | Native and strong | Limited (`$lookup`) |
| **Scaling** | Vertical; sharding needs extensions | Built-in horizontal sharding |
| **Ease of use** | More verbose for JSON, but combines with relational data | Simpler for pure document data |

## 11. Limitations and Future Scope

Current limitations:

- Only 5 sample products are used; real performance differences appear only with large data (hence the 100,000 generated rows in Task 6).
- The benchmark runs on a single local machine, so horizontal scaling is not tested.
- JSON content is not validated; any key or value can be stored in `attributes`.
- Only top-level keys are indexed and queried; nested documents are not explored.

Possible improvements:

- Add `CHECK` constraints or JSON-schema validation on the `attributes` column.
- Add B-tree expression indexes for frequently filtered keys such as `ram_gb` and `pages`.
- Use `jsonb_path_ops` GIN indexes for smaller, faster containment-only indexes.
- Test sharding with Citus (PostgreSQL) and a sharded cluster (MongoDB).
- Build a small application on top of the catalog, for example a product search page.

## 12. Conclusion

This assignment shows that PostgreSQL's `jsonb` type allows one database to act as both a relational and a document store. Fixed attributes stay in typed columns with constraints, while variable attributes live in a `jsonb` column that can be queried with `->>`, `@>` and `?`, and extended with `||` without changing the table. A GIN index speeds up containment queries but not range queries on extracted values. Compared with MongoDB, PostgreSQL gives stronger transactions, joins and schema control, whereas MongoDB is simpler for pure document data and easier to scale horizontally. For mixed structured and flexible data such as a product catalog, PostgreSQL with `jsonb` is a strong single-database choice.

## References

1. PostgreSQL Documentation: JSON Types, https://www.postgresql.org/docs/current/datatype-json.html
2. PostgreSQL Documentation: JSON Functions and Operators, https://www.postgresql.org/docs/current/functions-json.html
3. PostgreSQL Documentation: GIN Indexes, https://www.postgresql.org/docs/current/gin.html
4. MongoDB Manual, https://www.mongodb.com/docs/manual/
