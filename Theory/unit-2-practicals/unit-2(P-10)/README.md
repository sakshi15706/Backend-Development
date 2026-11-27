# Unit 2 (P-10): API Documentation and Versioning (Lecture 23)

## Lab exercise
1. Implement versioned endpoints: `/api/v1/students` (basic response) and `/api/v2/students` (enhanced response with pagination).
2. Add deprecation headers to the v1 endpoints.
3. Customise the Swagger UI documentation: title and description, contact information, tags, request/response examples.
4. Export the API as a Postman collection.
5. Create Postman environments for development and production.
6. Test the documentation: Swagger UI, ReDoc, and import the Postman collection and run it.

## Run
```bash
cd "unit-2(P-10)"
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q                      # 15 tests
python generate_postman.py     # re-create the Postman files after you change the API
```
| What | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI JSON | http://127.0.0.1:8000/openapi.json |

## Structure
```
main.py                  app metadata (title, contact, tags, servers) + middleware that adds version headers
routers/v1.py            /api/v1  (deprecated)
routers/v2.py            /api/v2  (current)
services.py              logic shared by both versions
schemas.py               StudentV1, StudentV2, pagination envelope, examples
generate_postman.py      builds the Postman files from the live OpenAPI spec
postman/                 the 3 generated files (collection + Development + Production environments)
```

## v1 versus v2
| | `/api/v1/students` | `/api/v2/students` |
|---|---|---|
| Response | plain JSON array (max 100 rows) | `{items, page, limit, total, total_pages, links}` |
| Student fields | `id, name, email, branch` | adds `enrollment_date`, nested `department`, `enrollment_count` |
| Filters | `branch` | `branch`, `department_id`, `search` |
| Status | **deprecated** | current |

New versions share one `services.py`, so a business rule is fixed once for both versions.

## Deprecation headers (step 2)
Every `/api/v1` response, including 404 and 422 errors, carries:
```
Deprecation: @1793491200                         (RFC 9745: when it was deprecated, as a timestamp)
Sunset: Mon, 31 May 2027 23:59:59 GMT            (RFC 8594: when it will stop working)
Link: </api/v2/students>; rel="successor-version"
X-API-Version: 1
```
They are added by middleware, because a normal dependency would be skipped on error responses. In Swagger UI the v1 operations appear struck through (`deprecated=True`).

## Swagger customisation (step 3)
| Requirement | Where |
|---|---|
| Title, description, version | `FastAPI(title=..., description=..., version=...)` in `main.py` |
| Contact, licence, terms | `contact=`, `license_info=`, `terms_of_service=` |
| Tags | `openapi_tags` (v2, v1 (deprecated), meta) and `tags=[...]` on each router |
| Request examples | `Field(examples=...)` and `json_schema_extra` in `schemas.py`; three named examples (`full`, `minimal`, `invalid`) on `POST /api/v2/students` through `Body(openapi_examples=...)` |
| Response examples | `json_schema_extra` on `StudentV1` / `StudentV2` |
| Error responses | `responses={404: ..., 409: ...}` on the routes |
| Servers | `servers=[Development, Production]` |

Change the placeholder contact details (`example.com`) and the production URL to your own before submitting.

## Postman (steps 4 to 6)
`python generate_postman.py` writes three files into `postman/`:
- `Student_Management_API.postman_collection.json`: 8 requests in folders v2, v1 (deprecated), meta. Each request has test scripts (status code, response time, JSON body, deprecation headers on v1, pagination keys on v2).
- `Development.postman_environment.json`: `base_url = http://127.0.0.1:8000`
- `Production.postman_environment.json`: `base_url = https://your-app.onrender.com` (**replace with your deployed URL**)

**Import and run**
1. Start the API (`uvicorn main:app --reload`).
2. Postman, **Import**, select all three files from `postman/`.
3. Top-right environment dropdown, choose **Development**.
4. Right-click the collection, **Run collection**, **Run**. All tests should be green.
5. Switch to **Production** after you deploy to test the live server.

Notes: create requests use Postman's `{{$randomEmail}}`, so the collection can be re-run without duplicate-email errors; the `POST` test script saves the new `student_id` for the later `GET .../:student_id` requests. The test `test_collection_runs_green_like_newman` replays the exported collection against the app, so you know the files work before you open Postman.

## Testing checklist for your report
- [ ] Swagger UI: open `/docs`, expand v1 (struck through) and v2, **Try it out** on `GET /api/v2/students`.
- [ ] Check the response headers of a v1 call (Swagger shows them under the response).
- [ ] ReDoc: open `/redoc`, check the tags, descriptions and examples read well.
- [ ] Postman: import the collection and environment, run the collection, screenshot the green results.
