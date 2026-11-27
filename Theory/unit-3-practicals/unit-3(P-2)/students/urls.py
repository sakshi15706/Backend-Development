"""Task 3: app-level routes. Included under /api/students/ by the project URLconf."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_list, name="student-list"),
    path("<int:student_id>/", views.student_detail, name="student-detail"),
]
