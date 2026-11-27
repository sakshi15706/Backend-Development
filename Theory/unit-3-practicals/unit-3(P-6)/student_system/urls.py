from django.contrib import admin
from django.urls import include, path

from students import views as student_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Step 6: Django's built-in login/logout/password views (login needs the template
    # in templates/registration/login.html)
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/health/", student_views.health_check, name="health-check"),
    path("api/departments/", student_views.department_list, name="department-list"),   # per-view cache
    path("api/students/", include("students.urls")),
]
