from django.urls import path

from . import views

urlpatterns = [
    path("", views.student_list, name="student-list"),
    # fixed routes before the <int:> route is not required here, but keeps them easy to find
    path("secure-data/", views.secure_data_view, name="secure-data"),
    path("staff-data/", views.staff_data_view, name="staff-data"),
    path("records/", views.student_records_view, name="student-records"),
    path("external/<int:post_id>/", views.external_data_view, name="external-data"),
    path("<int:student_id>/", views.student_detail, name="student-detail"),
]
