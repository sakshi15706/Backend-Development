# Unit 2 (P-2): Data Modeling (Lecture 15)

## Lab exercise
1. Design a conceptual data model for an E-Commerce System (Product, Order, Customer, Cart).
2. Create SQLAlchemy models for the Student Management System with relationships.
3. Implement CRUD with SQLAlchemy: create student with department, read by branch, update branch, delete and verify cascade.
4. Create Mongoose schemas for a Blog application with Post and Comment.
5. Add validation rules (required fields, unique constraints, enum values).

## Files
| Path | Covers |
|---|---|
| `conceptual-model.md` | Part 1: E-commerce conceptual model (Mermaid ER diagram) |
| `sqlalchemy-app/models.py` | Part 2: Department, Student, Course, Enrollment models |
| `sqlalchemy-app/crud_demo.py` | Part 3: CRUD + cascade check |
| `mongoose-blog/models.js` | Parts 4 and 5: Post and Comment schemas with validation |
| `mongoose-blog/validate.test.js` | checks the validation rules (no database needed) |
| `mongoose-blog/demo.js` | full demo (needs MongoDB) |

## Run: SQLAlchemy
```bash
cd "unit-2(P-2)/sqlalchemy-app"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python crud_demo.py
```
Uses SQLite (`students.db` is created automatically). To use MySQL/PostgreSQL change `DATABASE_URL` in `models.py`.

## Run: Mongoose
```bash
cd "unit-2(P-2)/mongoose-blog"
npm install
npm test                       # validation rules, no database needed
npm start                      # full demo, needs MongoDB running
```
Set `MONGO_URI` for a different MongoDB (for example a MongoDB Atlas connection string).

## Cascade behaviour (Part 3, step 4)
`Student.enrollments` uses `cascade="all, delete-orphan"`, so deleting a student removes their `enrollments` rows but not the `courses` or `departments`. The demo prints the counts before and after to prove it.
