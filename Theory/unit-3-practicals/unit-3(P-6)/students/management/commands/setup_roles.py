"""python manage.py setup_roles

Creates the 'Registrar' group with the model permissions used in this practical.
Add a user to it in /admin/ (Users -> Groups) and they can open /api/students/records/.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the Registrar group (view_student permission)."

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Registrar")
        perm = Permission.objects.get(
            content_type__app_label="students", codename="view_student"
        )
        group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS(
            f"Group 'Registrar' {'created' if created else 'already existed'} with students.view_student"
        ))
