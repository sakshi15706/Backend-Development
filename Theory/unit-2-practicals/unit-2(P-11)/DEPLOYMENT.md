# Deploying to a cloud platform (Render, Railway or Heroku)

**Status:** the deployment files and start command were tested locally (the app starts in production mode with `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and answers `/health`). **The actual deployment is yours to do:** it needs your account and your repository, and I cannot do it for you. The `Dockerfile` was not built here (no Docker daemon available), so test it yourself if you plan to use it.

Free plans, limits and screen layouts change often. Check the platform's current documentation and pricing before you start.

## Before you deploy
1. Push this project to GitHub (see "Git" below).
2. Tests pass locally: `pytest -q`.
3. Decide your admin login (email and a strong password). The app creates this admin on first start from the `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables.

## Environment variables
| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` (the app then refuses to start with the default secret) |
| `SECRET_KEY` | a long random string: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | the PostgreSQL URL from the platform (`postgres://...` is converted automatically) |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | first admin; remove `ADMIN_PASSWORD` after the first successful start |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | optional, default 30 |

SQLite is fine locally but **not** on these platforms: their disks are usually erased on every deploy, so use their PostgreSQL add-on.

## Option A: Render (blueprint file included)
1. Push the repository to GitHub.
2. Render dashboard, **New +**, **Blueprint**, select the repository. Render reads `render.yaml`, creates the web service and a PostgreSQL database, and generates `SECRET_KEY`.
3. When asked, enter `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
4. If the project is not at the repository root, keep the `rootDir` line in `render.yaml`; otherwise delete it.
5. Wait for the build to finish. Your URL looks like `https://student-api-xxxx.onrender.com`.

**Manual setup instead of the blueprint:** New, Web Service, connect the repo, Runtime Python 3, Build `pip install -r requirements.txt`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, Health check path `/health`, then add the variables above. Create a PostgreSQL database and paste its internal connection URL into `DATABASE_URL`.

## Option B: Railway
1. New Project, Deploy from GitHub repo.
2. Add a PostgreSQL service, then in the web service add a variable reference for `DATABASE_URL`.
3. Set the variables above. Railway detects Python; the included `Procfile` provides the start command. Generate a public domain in Settings, Networking.

## Option C: Heroku
```bash
heroku create your-student-api
heroku addons:create heroku-postgresql
heroku config:set ENVIRONMENT=production SECRET_KEY=<random> ADMIN_EMAIL=you@example.com ADMIN_PASSWORD=<strong>
git push heroku main        # the Procfile defines the web process
```
Heroku has no free tier any more, so check the current pricing.

## Verify the deployment (put screenshots in your report)
Replace `BASE` with your URL.
```bash
curl BASE/health                                   # {"status":"ok","environment":"production"}
open BASE/docs                                     # Swagger UI
curl -X POST BASE/api/v1/auth/login -d "username=ADMIN_EMAIL&password=ADMIN_PASSWORD"
curl BASE/api/v1/students                          # 401 without a token
```
Free web services often **sleep when idle**, so the first request can take 30 to 60 seconds.

## Postman against the live API
1. Import `docs/openapi.json` (File, Import) to get a collection, or Import, Link, `BASE/openapi.json`.
2. Create two environments, **Development** (`base_url = http://127.0.0.1:8000`) and **Production** (`base_url = BASE`).
3. Log in, copy the token, and set it as the collection's Authorization (Bearer Token) using `{{token}}`.
4. Run the requests against Production and screenshot the results.

## Troubleshooting
| Symptom | Likely cause |
|---|---|
| Build fails on `psycopg2` | keep `psycopg2-binary` in `requirements.txt`, and use a current `PYTHON_VERSION` |
| App exits at start with "SECRET_KEY must be set" | add `SECRET_KEY` (this protects you from the public default) |
| `sqlalchemy.exc.NoSuchModuleError: postgres` | `DATABASE_URL` starts with `postgres://`; the app converts it, so make sure you deployed this version of `config.py` |
| 502 / port errors | the start command must bind `0.0.0.0` and `$PORT` |
| Data disappears after a deploy | you are using SQLite; switch to the platform PostgreSQL |
| Cannot log in as admin | check `ADMIN_EMAIL` / `ADMIN_PASSWORD` were set before the first start (an existing account is never overwritten) |

## Git
```bash
cd Theory
git add .
git commit -m "Unit 2 practicals"
git push
```
`.env`, `*.db`, `uploads/` and `venv/` are ignored; never commit secrets.
