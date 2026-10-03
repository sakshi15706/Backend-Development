# Assignment 2: PostgreSQL as SQL + NoSQL (JSONB)

**Name:** Sakshi Jaiswal   **Sap Id.:**590015706  **Date:**03/10/2026

## Part A: Conceptual questions
> Rewrite each answer in your own words (150-250 words) before submitting.

### 1. What is `jsonb`, and how does it differ from `json`?
`json` stores an exact text copy of the input (whitespace, key order and duplicate keys preserved) and must be re-parsed on every access. `jsonb` parses once on write and stores a decomposed binary format that drops whitespace, keeps only the last duplicate key and does not preserve key order. Writes are slightly slower because of the conversion, but queries are much faster because nothing is re-parsed. `jsonb` also supports GIN indexing and the `@>` and `?` operators, which `json` does not. Use `json` only when the exact original text must be kept.

```sql
SELECT '{"a": 1, "a": 2}'::json;   -- {"a": 1, "a": 2}
SELECT '{"a": 1, "a": 2}'::jsonb;  -- {"a": 2}
```

### 2. How can PostgreSQL work as both SQL and NoSQL in the same table?
A table can mix strictly typed columns (`id`, `name`, `price`) with one `jsonb` column for attributes that vary per row. Common fields keep constraints, foreign keys, joins and transactions, while the `jsonb` column holds flexible, schema-less data (a book has `author`/`pages`, a laptop has `cpu`/`ram_gb`) with no `ALTER TABLE` and no NULL-filled sparse columns. Both parts can be queried in one statement.

```sql
CREATE TABLE products (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  attributes JSONB
);
SELECT name FROM products WHERE price < 1000 AND attributes @> '{"wireless": true}';
```

### 3. The JSONB operators
Assume `attributes = '{"cpu": "i7", "ram_gb": 16, "wireless": true}'`.

```sql
SELECT attributes -> 'cpu'           FROM products;  -- "i7"  (jsonb)
SELECT attributes ->> 'cpu'          FROM products;  -- i7    (text)
SELECT attributes @> '{"ram_gb":16}' FROM products;  -- true
SELECT attributes ? 'wireless'       FROM products;  -- true
```
`->` returns `jsonb` (strings keep quotes, can be chained). `->>` returns `text`, suited to comparison, display and casting such as `(attributes ->> 'ram_gb')::int`. `@>` tests containment and `?` tests whether a top-level key exists.

### 4. How does a GIN index change query performance?
A GIN index maps every key and value inside the documents to the rows containing them, so containment and existence queries (`@>`, `?`, `?|`, `?&`) avoid a full sequential scan. It does not help queries on extracted values, such as `WHERE (attributes ->> 'ram_gb')::int >= 16`, because it has no ordering for range checks. Use a B-tree expression index for that. GIN indexes cost extra storage and slow writes slightly.

```sql
CREATE INDEX idx_attr_gin ON products USING GIN (attributes);
CREATE INDEX idx_ram ON products (((attributes ->> 'ram_gb')::int));
```

### 5. Where could PostgreSQL + jsonb replace MongoDB, and where is MongoDB better?
**Postgres can replace MongoDB** for partly structured, partly flexible data. It has full ACID multi-row/multi-table **transactions**, native efficient **joins** (Mongo's `$lookup` is clunkier), and strong **schema enforcement** through types, constraints and CHECKs. **MongoDB is still better** for **horizontal scaling**: sharding and replica sets are built in, whereas Postgres needs Citus or manual partitioning. It also fits workloads of deeply nested documents with whole-document reads/writes, very high write throughput and fast-changing schemas.

```sql
SELECT o.id, p.name FROM orders o JOIN products p ON p.id = o.product_id
WHERE p.attributes @> '{"wireless": true}';
```

## Part B: Hands-on exercise

### Task 1 Schema
Paste screenshot of `01_schema.sql` running / `\d products`.

### Task 2 Insert data
Paste screenshot of `SELECT * FROM products;`.

### Task 3 Category-specific queries
Paste output of the three queries in `03_queries.sql`.

### Task 4 Containment query
Paste output of `attributes @> '{"wireless": true}'`.

### Task 5 Update JSONB
Paste output after running `04_update.sql`. No `ALTER TABLE` was needed because `||` merges new keys into the JSONB document.

### Task 6 Index and compare
| Query | Plan before index | Time before | Plan after index | Time after |
|---|---|---|---|---|
| `@> '{"wireless": true}'` | | | | |
| `->> 'ram_gb' >= 16` | | | | |

Observation: the containment query switches from Seq Scan to Bitmap Index Scan on the GIN index. The `->>` range query does not use it, because GIN does not support range comparisons on extracted values. With only 5 rows Postgres always chooses a Seq Scan, so 100,000 rows were generated.

### Task 7 MongoDB comparison
Paste output of `mongo.js`.

| Aspect | PostgreSQL JSONB | MongoDB |
|---|---|---|
| Syntax | `attributes ->> 'ram_gb'` plus `::int` cast | `"attributes.ram_gb": {$gte: 16}`, native types |
| Indexing | One GIN index covers all keys (containment/existence only) | Index specific paths, e.g. `attributes.wireless` |
| Ease of use | More verbose, but joins and constraints available | Simpler for pure document data |

## Conclusion
Write 3-4 sentences: when you would choose Postgres + JSONB, and when MongoDB.
