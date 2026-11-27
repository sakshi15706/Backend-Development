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


from .utils import get_external_data  # noqa: E402  (kept next to the view that uses it)


def external_data_view(request, post_id):
    """Task 3: call the third-party API through the service utility.

    503 Service Unavailable when the dependency cannot be reached or misbehaves.
    """
    result = get_external_data(post_id)
    if result["error"]:
        return JsonResponse({"error": result["error"]}, status=503)
    return JsonResponse(result["data"])
