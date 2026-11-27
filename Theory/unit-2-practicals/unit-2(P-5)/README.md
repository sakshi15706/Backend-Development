# Unit 2 (P-5): Designing RESTful APIs (Lecture 18)

## Lab exercise
1. Design a complete API for a Library Management System with resources Book, Member, Loan.
2. Document all endpoints with HTTP methods, request/response schemas and status codes.
3. Create Pydantic models for input validation and response serialisation.
4. Design the API for filtering books by genre, author and availability.
5. Plan the pagination strategy for listing books and members.
6. Create OpenAPI documentation using FastAPI's built-in Swagger UI.

## Files
| File | Covers |
|---|---|
| `API_DESIGN.md` | steps 1, 2, 4, 5: resources, endpoints, schemas, status codes, filtering, pagination |
| `schemas.py` | step 3: Pydantic models |
| `main.py` | working implementation of the design (in-memory data) and step 6 |
| `test_api.py` | tests proving the design works |

## Run
```bash
cd "unit-2(P-5)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q
```
Swagger UI: http://127.0.0.1:8000/docs  |  ReDoc: http://127.0.0.1:8000/redoc

Data is kept in memory and resets when the server restarts. This practical is about API design; P-3 and P-6 add the real database.
