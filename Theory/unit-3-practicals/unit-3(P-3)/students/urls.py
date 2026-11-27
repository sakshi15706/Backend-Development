from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_list, name="student-list"),
    path("<int:student_id>/", views.student_detail, name="student-detail"),
    # Task 4: GET /api/students/external/1/
    path("external/<int:post_id>/", views.external_data_view, name="external-data"),
]
