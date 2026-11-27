from django.contrib import admin

from .models import StudentRegistration


@admin.register(StudentRegistration)
class StudentRegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "age", "course", "created_at")
    search_fields = ("name", "email", "course")
