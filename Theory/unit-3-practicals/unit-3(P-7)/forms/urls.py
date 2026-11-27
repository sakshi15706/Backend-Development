from django.urls import path

from . import views

app_name = "forms_app"          # reverse as "forms_app:register" from templates and other apps

urlpatterns = [
    path("register/", views.register_student, name="register"),
    path("register/success/", views.registration_success, name="registration-success"),
    path("registrations/", views.registration_list, name="registration-list"),
]
