# Unit 1 (P-2): HTTP Requests and Flask API

## Aim
Understand HTTP methods (GET, POST, PUT, DELETE), status codes, headers and query strings by building a Flask API.

## Run
```bash
cd "unit-1(P-2)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py                  # terminal 1
python client.py               # terminal 2
```

## Endpoints
| Method | URL | Purpose |
|---|---|---|
| GET | /students | list all |
| GET | /students/<id> | get one |
| POST | /students | create (JSON body) |
| PUT | /students/<id> | update |
| DELETE | /students/<id> | delete |
| GET | /inspect?q=... | show method, path, query string, headers |

## Status codes used
200 OK, 201 Created, 400 Bad Request, 404 Not Found.
