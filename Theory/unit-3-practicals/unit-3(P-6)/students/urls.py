from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_list, name="student-list"),
    path("slow/", views.student_list_slow, name="student-list-slow"),      # N+1, for measuring
    path("courses/", views.student_courses_view, name="student-courses"),  # prefetch_related
    path("names/", views.student_names, name="student-names"),             # values()
    path("summary/", views.student_summary_view, name="student-summary"),  # low-level cache
    path("secure-data/", views.secure_data_view, name="secure-data"),
    path("staff-data/", views.staff_data_view, name="staff-data"),
    path("records/", views.student_records_view, name="student-records"),
    path("external/<int:post_id>/", views.external_data_view, name="external-data"),
    path("<int:student_id>/", views.student_detail, name="student-detail"),
]
