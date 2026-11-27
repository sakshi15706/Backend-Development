import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from .models import Student
from .utils import get_external_data

logger = logging.getLogger(__name__)


def health_check(request):
    """Public on purpose: monitoring tools must be able to call it."""
    return JsonResponse({"status": "ok"})


def _serialize(student):
    return {"student_id": student.id, "name": student.name, "email": student.email}


# ---- AUTHENTICATION: "who are you?"  (login_required) -------------------------------
@login_required
def student_list(request):
    """PBL task 3: anonymous visitors must not see the student list.
    Anonymous -> 302 redirect to LOGIN_URL?next=/api/students/
    """
    students = [_serialize(s) for s in Student.objects.all()]
    return JsonResponse({"students": students, "count": len(students)})


@login_required
def student_detail(request, student_id):
    logger.info("Looking up student_id=%s user=%s", student_id, request.user.pk)
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    return JsonResponse(_serialize(student))


@login_required
def secure_data_view(request):
    # runs only after the user is authenticated
    return JsonResponse({
        "message": "You are authenticated.",
        "username": request.user.username,
    })


# ---- AUTHORIZATION: "what may you do?" ---------------------------------------------
@staff_member_required
def staff_data_view(request):
    """Only users with is_staff=True. Anonymous/non-staff -> redirect to the ADMIN login.
    is_staff controls access to the admin site; it is not a model permission."""
    return JsonResponse({"message": "Staff access granted."})


@permission_required("students.view_student", raise_exception=True)
def student_records_view(request):
    """Needs the model permission students.view_student.
    Anonymous or without the permission -> 403 (raise_exception=True), not a redirect."""
    records = [_serialize(s) for s in Student.objects.all()]
    return JsonResponse({
        "message": "Student record access granted.",
        "records": records,
    })


# ---- external API (Lecture 28) ------------------------------------------------------
def external_data_view(request, post_id):
    result = get_external_data(post_id)
    if result["error"]:
        return JsonResponse({"error": result["error"]}, status=503)
    return JsonResponse(result["data"])
