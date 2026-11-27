# Unit 1 (P-3): RESTful APIs with FastAPI

## Aim
Build a REST API with FastAPI showing resources, HTTP verbs, validation (Pydantic), query parameters and automatic docs.

## Run
```bash
cd "unit-1(P-3)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints
| Method | URL | Status |
|---|---|---|
| GET | /books?author=martin | 200 |
| GET | /books/{id} | 200 / 404 |
| POST | /books | 201 / 422 (validation) |
| PUT | /books/{id} | 200 / 404 |
| DELETE | /books/{id} | 204 / 404 |
