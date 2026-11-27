import logging

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from .forms import StudentRegistrationForm
from .models import StudentRegistration
from .services import notify_registration

logger = logging.getLogger(__name__)


def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)         # submitted data, not an empty form
        if form.is_valid():
            try:
                # atomic: if the database rejects the row, only this save is rolled back
                with transaction.atomic():
                    student = form.save()
            except IntegrityError:
                # two people submitted the same e-mail at the same moment: the database constraint
                # is the final protection even when form validation passed
                form.add_error("email", "A student with this email already exists.")
            else:
                # log the id, not the e-mail: less personal data in the logs
                logger.info("Student registration created: id=%s", student.id)
                notify_registration(student)                  # only AFTER the data is saved
                messages.success(request, "Student registration submitted successfully.")
                return redirect("forms_app:registration-success")   # redirect after POST
    else:
        form = StudentRegistrationForm()

    return render(request, "forms/register_student.html", {"form": form})


def registration_success(request):
    return render(request, "forms/registration_success.html")


@staff_member_required
def registration_list(request):
    """exercise 4: a page that lists everyone registered (staff only: it shows personal data)."""
    return render(request, "forms/registration_list.html",
                  {"registrations": StudentRegistration.objects.all()})
