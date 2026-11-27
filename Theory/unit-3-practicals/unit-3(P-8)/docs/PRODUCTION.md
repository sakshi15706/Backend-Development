# Production notes for uploads and static files

Not executed in the lab environment; this is the design the slides describe, plus a sample configuration you should adapt and test yourself.

## 1. Why the application server should not be the file server
Django (like FastAPI or Express) is good at routing, authentication, validation and database work. A busy API worker that is also streaming large files cannot serve other requests, and mature web servers and CDNs do caching, range requests, compression and TLS better. It is a recommendation, not a limitation: the development server and small internal tools are fine.

```
Browser --> CDN / Nginx  --> static files (and public media)
        --> Nginx / Caddy --> Gunicorn --> Django (dynamic requests, /uploads/api/, ...)
```

## 2. Static files (CSS, JS)
```bash
python manage.py collectstatic --noinput      # copies app static/ folders into STATIC_ROOT (staticfiles/)
```
Serve `staticfiles/` from Nginx, a CDN, object storage, or (modest sites) WhiteNoise. `collectstatic` does not compile SCSS: compile first (`npx sass frontend/scss/site.scss uploads/static/uploads/css/site.css`) in your build step, then collect.

## 3. Uploaded media
| Kind | Here | Production |
|---|---|---|
| Public (`StudentDocument`, `StudentPhoto`) | `MEDIA_ROOT`, served by `static()` only when `DEBUG` | persistent volume served by Nginx, or object storage with a CDN |
| Private (`PortalDocument`) | `PRIVATE_MEDIA_ROOT`, no URL, download view with owner check | private bucket plus short-lived **signed URLs** after the permission check, or Nginx `X-Accel-Redirect` from the download view |

Container disks are usually ephemeral: files disappear on restart unless you mount a persistent volume or use object storage (S3-compatible, Azure Blob, Google Cloud Storage; `django-storages` adds the storage backend).

## 4. Sample Nginx server block (untested sample)
```nginx
server {
    listen 443 ssl;
    server_name example.edu;

    client_max_body_size 11m;                # a little above PORTAL_MAX_BYTES (10 MB); reject big bodies early

    location /static/ { alias /srv/student_system/staticfiles/; expires 30d; }
    location /media/  { alias /srv/student_system/media/; }        # public uploads only
    # NO location for private_media/: it must never be reachable directly

    location / {
        proxy_pass http://127.0.0.1:8000;    # gunicorn student_system.wsgi
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 5. Production checklist (from the lecture) and where this project stands
| Item | Status |
|---|---|
| `DEBUG = False`, `ALLOWED_HOSTS` | `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS` env vars; also enables secure cookies and the HTTPS redirect |
| HTTPS | configure at the proxy |
| size limits at proxy and application | application: yes. Proxy: `client_max_body_size` above |
| validate extension, content, size, dimensions | yes (`validators.py`) |
| generated storage names | yes |
| private files outside the web root, authenticated downloads | yes (`PrivateStorage`, owner check) |
| virus scanning for documents | **not implemented** |
| object storage for durability | **not implemented** (design only) |
| `collectstatic` during deployment | command works; add it to your build step |
| process manager (Gunicorn/Uvicorn) | add to your deployment; not included |
| secrets from the environment | `DJANGO_SECRET_KEY`; keep storage keys out of Git |
| test failed / interrupted / oversized / unauthorized uploads | oversized, wrong type and unauthorized are tested; interrupted uploads are not |
