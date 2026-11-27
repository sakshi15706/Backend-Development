import logging

from django.http import JsonResponse

from .models import Student
from .utils import get_external_data

logger = logging.getLogger(__name__)


def health_check(request):
    return JsonResponse({"status": "ok"})


def _serialize(student):
    return {"student_id": student.id, "name": student.name, "email": student.email}


def student_list(request):
    students = [_serialize(s) for s in Student.objects.all()]
    return JsonResponse({"students": students, "count": len(students)})


def student_detail(request, student_id):
    logger.info("Looking up student_id=%s", student_id)
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        logger.warning("Student not found: student_id=%s", student_id)
        return JsonResponse({"error": "Student not found"}, status=404)
    return JsonResponse(_serialize(student))


def external_data_view(request, post_id):
    result = get_external_data(post_id)
    if result["error"]:
        return JsonResponse({"error": result["error"]}, status=503)
    return JsonResponse(result["data"])
