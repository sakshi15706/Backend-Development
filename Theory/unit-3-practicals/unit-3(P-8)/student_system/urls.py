from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from students import views as student_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),       # login for the private portal
    path("api/health/", student_views.health_check, name="health-check"),
    path("api/students/", include("students.urls")),
    path("uploads/", include("uploads.urls")),
]

# Development convenience ONLY: lets runserver show public uploads (MEDIA_URL).
# In production Nginx/Caddy/a CDN/object storage serves them; see docs/PRODUCTION.md.
# Private portal files are NOT under MEDIA_ROOT, so this never exposes them.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
