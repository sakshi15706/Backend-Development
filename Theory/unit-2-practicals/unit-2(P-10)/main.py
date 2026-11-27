"""P-10: API versioning and documentation.

    uvicorn main:app --reload
      Swagger UI  http://127.0.0.1:8000/docs
      ReDoc       http://127.0.0.1:8000/redoc
      OpenAPI     http://127.0.0.1:8000/openapi.json
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from database import Base, engine
from routers import v1, v2


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    yield


DESCRIPTION = """
Student Management API with **two versions** running side by side.

| Version | Status | Differences |
|---|---|---|
| `/api/v1` | **deprecated**, sunset 2027-05-31 | plain array, no pagination, basic fields |
| `/api/v2` | current | pagination (`page`, `limit`, `links`), filters, department and enrolment count |

Every v1 response carries `Deprecation`, `Sunset` and `Link: rel="successor-version"` headers.

### Errors
`404` not found, `409` conflict (duplicate email), `422` validation failed.
"""

TAGS = [
    {"name": "v2", "description": "**Current** version. Use this for all new work."},
    {"name": "v1 (deprecated)", "description": "Legacy version. Returns deprecation headers on every call."},
    {"name": "meta", "description": "Service information."},
]

app = FastAPI(
    title="Student Management API",
    summary="Versioned REST API for students",
    description=DESCRIPTION,
    version="2.0.0",
    terms_of_service="https://example.com/terms",
    contact={"name": "API Support (Backend Development Lab)", "url": "https://example.com/support",
             "email": "support@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=TAGS,
    servers=[{"url": "http://127.0.0.1:8000", "description": "Development"},
             {"url": "https://your-app.onrender.com", "description": "Production (replace after deploying)"}],
    lifespan=lifespan,
)

@app.middleware("http")
async def version_headers(request: Request, call_next):
    """Adds version information to every response under /api/v1 and /api/v2 (errors included)."""
    response = await call_next(request)
    if request.url.path.startswith("/api/v1"):
        v1.apply_deprecation_headers(response)
    elif request.url.path.startswith("/api/v2"):
        response.headers["X-API-Version"] = "2"
    return response


app.include_router(v1.router)
app.include_router(v2.router)


@app.get("/", tags=["meta"], summary="Service information")
def root():
    return {"name": "Student Management API", "versions": {"v1": "deprecated", "v2": "current"},
            "docs": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"}


@app.get("/health", tags=["meta"], summary="Health check")
def health():
    return {"status": "ok"}
