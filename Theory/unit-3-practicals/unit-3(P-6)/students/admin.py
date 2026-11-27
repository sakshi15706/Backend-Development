from django.contrib import admin

from .models import Course, Department, Student

admin.site.register(Department)
admin.site.register(Course)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department")
    list_select_related = ("department",)       # same N+1 fix, applied to the admin list page
    search_fields = ("name", "email")
