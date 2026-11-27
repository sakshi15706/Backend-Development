from django.contrib import admin
from django.urls import include, path

from students import views as student_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", student_views.health_check, name="health-check"),
    path("api/students/", include("students.urls")),
    path("forms/", include("forms.urls")),
]
