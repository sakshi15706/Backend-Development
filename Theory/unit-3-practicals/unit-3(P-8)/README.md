# Unit 3 (P-8): Django File Uploads, Normal Forms and REST APIs

Tutorial and PBL: upload, validate, rename and serve student files through a normal Django form and a REST API, and understand how static and media files are served in production.

Builds on P-3 (project, `students` app, logging middleware). The new app is `uploads`. The project is `student_system` here (the slides call it `students_project`).

## Setup
```bash
cd "unit-3(P-8)"
python -m venv venv
venv\Scripts\activate           # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt           # Django, requests, djangorestframework, Pillow
python manage.py migrate
python manage.py createsuperuser          # then create a normal user in /admin/ for the portal
python manage.py runserver
python manage.py test                     # 95 tests (uploads: 71)
```
No `uv` needed; the slides use `uv add` and `uv run`, but plain `pip` and `python` do the same thing.

## What is where
| Slide part | Pages / endpoints | Files |
|---|---|---|
| 3-9 normal upload form | `/uploads/document/` | `uploads/forms.py`, `views.py`, `templates/uploads/` |
| 4 media settings | `MEDIA_URL`, `MEDIA_ROOT`, `static()` in DEBUG only | `settings.py`, `student_system/urls.py` |
| 5 model, `upload_to` | `StudentDocument` | `uploads/models.py` |
| 7 safe filename | `safe_upload_name()` | `uploads/utils.py` |
| 10 images with `ImageField` | `/uploads/photo/` | `StudentPhoto`, `StudentPhotoForm`, `validators.py` |
| 12-15 DRF upload | `POST /uploads/api/documents/` | `serializers.py`, `api_views.py` |
| 17-18 static CSS | `{% static %}`, `collectstatic` | `uploads/static/uploads/css/site.css` |
| 19-22 production design | | `docs/PRODUCTION.md` |
| 23 tests | | `uploads/tests.py` |
| 25 PBL portal | `/uploads/portal/`, `/uploads/api/portal/` | `PortalDocument`, `services.py`, `views.py`, `api_views.py` |

## PBL: student document portal, requirement by requirement
| Requirement | How it is met | Test |
|---|---|---|
| upload a PDF assignment | `/uploads/portal/` form and `POST /uploads/api/portal/` | `test_valid_pdf_upload`, `test_upload_returns_201_and_download_url` |
| limit 10 MB | `PORTAL_MAX_BYTES`; exactly 10 MB passes, 1 byte more fails | `test_exactly_ten_mb_accepted`, `test_oversized_pdf_rejected_and_nothing_stored` |
| only PDF | extension **and** content check (`%PDF-` magic bytes), so a renamed `.txt` or `.exe` fails | `test_non_pdf_extension_rejected`, `test_renamed_non_pdf_content_rejected` |
| stored filename is a UUID | `safe_upload_name(..., ".pdf")` | `test_stored_name_is_uuid_and_original_name_kept_separately` |
| original name stored separately | `PortalDocument.original_name` (cleaned, display only) | same test, `test_hostile_original_name_is_neutralised` |
| a student lists and downloads only their own files | queries filter on `owner=request.user`; others get **404** | `PortalAccessTests` |
| same feature through DRF | `PortalDocumentListCreateAPIView`, `PortalDocumentDownloadAPIView` | `PortalAPITests` |
| tests: valid, bad extension, oversized, unauthorized | see above | |
| static CSS collected during deployment | `collectstatic` into `STATIC_ROOT` | `test_collectstatic_gathers_the_css` |
| media on a persistent volume or object storage | design in `docs/PRODUCTION.md`; **not deployed here** | - |

### Try it with curl
```bash
# the slide's open demo endpoint (no login, AllowAny on purpose)
curl -X POST http://127.0.0.1:8000/uploads/api/documents/ -F "student_name=Aarav Sharma" -F "document=@./sample.pdf"

# the portal API needs a login. HTTP Basic is allowed for curl; use it over HTTPS only.
curl -u alice:PASSWORD -X POST http://127.0.0.1:8000/uploads/api/portal/ -F "file=@./hw.pdf"
curl -u alice:PASSWORD http://127.0.0.1:8000/uploads/api/portal/
curl -u alice:PASSWORD -OJ http://127.0.0.1:8000/uploads/api/portal/1/download/
```
I ran these against a real `runserver`: 201 on a valid PDF, `{"file": ["This file is not a valid PDF."]}` for a text file renamed `.pdf`, 403 anonymous, 404 when a second user asked for the first user's file, and `/media/portal/...` returns 404.

## Design decisions to explain in the viva
- **The user's file name is never a path.** Files are stored as `<uuid>.<ext>`. Even `../../evil.pdf` lands inside the upload folder under a generated name (`test_path_traversal_name_cannot_escape_the_media_folder`). Renaming alone does not make a file safe: content is checked too.
- **Extension checks are not enough.** `ImageField` makes Pillow decode the image (a text file named `.png` fails). Portal PDFs must start with `%PDF-`. This is a sanity check, not a malware scan; for untrusted documents in production add virus scanning and private storage (slide checklist).
- **Two input boundaries, one set of rules.** The HTML form and the REST serializer both call `uploads/validators.py`, so the web page and the API cannot drift apart. The API does not trust the form having run.
- **Private vs public files.** Lecture examples go to `MEDIA_ROOT` (public in development). Portal files go to `PRIVATE_MEDIA_ROOT` via `PrivateStorage`, which has no URL at all: the only way to get a file is the download view, which checks the owner.
- **404 instead of 403** for somebody else's file, so the response does not reveal that the id exists. The tests check that both answers are identical to a missing id.
- **Download headers.** `Content-Disposition: attachment` (the browser saves it instead of rendering it) and `X-Content-Type-Options: nosniff`.
- **CSRF** applies to the form and to session-authenticated API calls (tests post without a token and expect 403).
- **Size limits also belong at the reverse proxy.** Django only sees the size after receiving the body. `FILE_UPLOAD_MAX_MEMORY_SIZE` makes larger uploads stream to a temporary file instead of memory.
- **The open demo endpoint** `/uploads/api/documents/` uses `AllowAny` because the slide's curl example has no login. It is not for real use; the portal API is the secure version (`IsAuthenticated` is the project default).

## Known limits
- Deleting a database row does not delete the file on disk (add a `post_delete` signal or a clean-up job if you need that).
- No virus scanning, no download audit trail beyond the log line, no per-user quota, no object storage. `docs/PRODUCTION.md` describes what a real deployment adds.
- The tests use small stand-in PDFs (`%PDF-1.4 ...`) and PNGs generated with Pillow. They are not full, valid PDFs, which is enough for these checks.
- Static files, SCSS and the Nginx/Caddy/S3 setup in the slides are explained, not deployed. The Nginx sample was not run here.
