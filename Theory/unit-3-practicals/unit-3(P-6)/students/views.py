import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from .cache_keys import SUMMARY_KEY, summary_timeout
from .models import Course, Department, Student
from .utils import get_external_data

logger = logging.getLogger(__name__)


def health_check(request):
    """Public on purpose: monitoring tools must be able to call it."""
    return JsonResponse({"status": "ok"})


def _serialize(student):
    # NOTE: reads student.department -> one extra query per student unless the queryset used
    # select_related("department").  That is the N+1 problem of Lecture 31.
    return {
        "student_id": student.id,
        "name": student.name,
        "email": student.email,
        "department": student.department.name if student.department else None,
    }


def _page_params(request):
    """?page=2&page_size=20 with sane limits (the testing checklist asks for pagination)."""
    try:
        page = max(int(request.GET.get("page", 1)), 1)
        size = int(request.GET.get("page_size", settings.DEFAULT_PAGE_SIZE))
    except ValueError:
        return 1, settings.DEFAULT_PAGE_SIZE
    return page, min(max(size, 1), settings.MAX_PAGE_SIZE)


def _paged_json(request, queryset, serialize, key):
    page_number, size = _page_params(request)
    paginator = Paginator(queryset, size)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return JsonResponse({
        key: [serialize(obj) for obj in page.object_list],
        "count": paginator.count,
        "page": page.number,
        "page_size": size,
        "total_pages": paginator.num_pages,
    })


# ---- student list: BEFORE and AFTER the N+1 fix ------------------------------------
@login_required
def student_list_slow(request):
    """BEFORE: deliberately inefficient, kept only so you can measure it.
    1 query for the students + 1 query per student for its department = N + 1.
    """
    queryset = Student.objects.all()
    return _paged_json(request, queryset, _serialize, "students")


@login_required
def student_list(request):
    """AFTER: select_related() makes ONE query with a JOIN (single-valued relationship).

    Not wrapped in cache_page: the list contains personal data, and a shared per-view cache
    would hand the same stored response to every user (see the README "Safe caching" part).
    """
    queryset = Student.objects.select_related("department")
    return _paged_json(request, queryset, _serialize, "students")


@login_required
def student_courses_view(request):
    """prefetch_related() for the multi-valued relationship: 2 queries in total
    (students, then all their courses in one go) instead of 1 + N."""
    queryset = Student.objects.select_related("department").prefetch_related("courses")

    def serialize(student):
        data = _serialize(student)
        # .all() on a prefetched relation uses the cache; .filter() would query again
        data["courses"] = [course.name for course in student.courses.all()]
        return data

    return _paged_json(request, queryset, serialize, "students")


@login_required
def student_names(request):
    """values() returns only the columns needed (no model objects, no department join)."""
    page, size = _page_params(request)
    rows = list(Student.objects.values("id", "name")[(page - 1) * size: page * size])
    return JsonResponse({"students": rows, "page": page, "page_size": size})


@login_required
def student_detail(request, student_id):
    logger.info("Looking up student_id=%s user=%s", student_id, request.user.pk)
    try:
        student = Student.objects.select_related("department").get(pk=student_id)
    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    return JsonResponse(_serialize(student))


# ---- caching ------------------------------------------------------------------------
@login_required
def student_summary_view(request):
    """Low-level cache API. The cached value is an AGGREGATE (counts only), identical for
    every user, so sharing it is safe.  Invalidated by signals.py when data changes and
    expires on its own after SUMMARY_CACHE_TIMEOUT seconds (300 = five minutes)."""
    summary = cache.get(SUMMARY_KEY)
    cache_status = "HIT"
    if summary is None:                         # cache miss
        cache_status = "MISS"
        summary = {
            "total_students": Student.objects.count(),
            "total_departments": Department.objects.count(),
            "total_courses": Course.objects.count(),
            "students_without_department": Student.objects.filter(department__isnull=True).count(),
        }
        cache.set(SUMMARY_KEY, summary, timeout=summary_timeout())
    response = JsonResponse(summary)
    response["X-Cache"] = cache_status          # handy for the before/after table
    return response


@cache_page(settings.PUBLIC_CACHE_SECONDS)
def department_list(request):
    """Per-view cache: PUBLIC data only (department names and head-counts, nothing personal).
    The whole response is stored for 5 minutes, so it can be up to 5 minutes stale."""
    rows = Department.objects.annotate(student_count=Count("students")).values("id", "name", "student_count")
    return JsonResponse({"departments": list(rows)})


# ---- authorization (Lecture 30) ----------------------------------------------------
@login_required
def secure_data_view(request):
    return JsonResponse({
        "message": "You are authenticated.",
        "username": request.user.username,
    })


@staff_member_required
def staff_data_view(request):
    return JsonResponse({"message": "Staff access granted."})


@permission_required("students.view_student", raise_exception=True)
def student_records_view(request):
    records = [_serialize(s) for s in Student.objects.select_related("department")]
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
