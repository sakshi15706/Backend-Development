from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # Single-valued relationship -> select_related().  Nullable so students without a
    # department are still valid (and so older rows/tests keep working).
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="students"
    )
    # Multi-valued relationship -> prefetch_related().
    courses = models.ManyToManyField(Course, blank=True, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
