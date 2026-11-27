# Unit 2 (P-1): Database Schema Design (Lecture 14)

## Lab exercise
1. Draw an ER diagram for a Library Management System: Book, Member, Loan, Author.
2. Design the schema with proper relationships (a Book can have many Authors; a Member can borrow many Books).
3. Write SQL `CREATE TABLE` statements with primary keys, foreign keys and constraints.
4. Normalise the given order table to 3NF.
5. Create the normalised tables in MySQL/PostgreSQL and insert sample data.

## Files
| File | Covers |
|---|---|
| `er-diagram.md` | Part 1: ER diagram (Mermaid, renders on GitHub and in VS Code) |
| `01_library_schema.sql` | Parts 2 and 3: tables, PK, FK, constraints, indexes |
| `02_library_sample_data.sql` | sample data for the library |
| `03_normalization.sql` | Parts 4 and 5: 3NF design, tables and data |
| `run_sql.py` | runs all SQL on SQLite and prints checks |

## Run
**MySQL / PostgreSQL:** run `01`, `02`, `03` in that order (Workbench, `psql -f file.sql`, or `mysql < file.sql`).

**Quick check without a database server:**
```bash
python run_sql.py
```

## Relationships used
| Relationship | Type | How it is built |
|---|---|---|
| Book and Author | M:N | junction table `book_authors` |
| Member and Book | M:N | `loans` is the junction entity, with its own attributes (dates) |
| Loan to Book, Loan to Member | M:1 | foreign keys in `loans` |

## Normalisation of the order table
Candidate key is `(order_id, product_name)`.

| Step | Problem found | Fix |
|---|---|---|
| 1NF | none, values are atomic | keep as is |
| 2NF | `order_id -> customer_*` and `product_name -> product_price` depend on only part of the key | split into `orders`, `products`, `order_items` |
| 3NF | `order_id -> customer_email -> customer_name` is a transitive dependency | move customer data into `customers` |

Final tables: `customers`, `products`, `orders`, `order_items`. Joining them (query at the bottom of `03_normalization.sql`) gives back the original 3 rows.
