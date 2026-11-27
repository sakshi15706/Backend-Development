from django.http import JsonResponse


def health_check(request):
    """Used by the health route created in Lecture 26 (reverse name: health-check)."""
    return JsonResponse({"status": "ok"})


def student_list(request):
    return JsonResponse({
        "students": [],
        "message": "Student list endpoint",
    })


def student_detail(request, student_id):
    return JsonResponse({
        "student_id": student_id,
        "message": "Student detail endpoint",
    })
