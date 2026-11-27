import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PortalDocumentForm, StudentDocumentForm, StudentPhotoForm
from .models import PortalDocument
from .services import create_portal_document
from .utils import safe_upload_name

logger = logging.getLogger(__name__)


def upload_document(request):
    if request.method == "POST":
        # request.POST holds the text fields, request.FILES the uploaded files: both are needed
        form = StudentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            uploaded_file = form.cleaned_data["document"]
            # save under a generated name instead of the user's original name
            document.document.save(safe_upload_name(uploaded_file), uploaded_file, save=False)
            document.save()
            logger.info("Document uploaded: id=%s", document.id)
            messages.success(request, "Document uploaded successfully.")
            return redirect("uploads:upload-success")
    else:
        form = StudentDocumentForm()
    return render(request, "uploads/upload_document.html", {"form": form})


def upload_success(request):
    return render(request, "uploads/upload_success.html")


def upload_photo(request):
    if request.method == "POST":
        form = StudentPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            uploaded_file = form.cleaned_data["photo"]
            photo.photo.save(safe_upload_name(uploaded_file), uploaded_file, save=False)
            photo.save()
            logger.info("Photo uploaded: id=%s", photo.id)
            messages.success(request, "Photo uploaded successfully.")
            return redirect("uploads:upload-success")
    else:
        form = StudentPhotoForm()
    return render(request, "uploads/upload_photo.html", {"form": form})


# ------------------------------------------------------------------ student document portal
@login_required
def portal(request):
    """List MY documents and upload a new one."""
    if request.method == "POST":
        form = PortalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            create_portal_document(request.user, form.cleaned_data["file"])
            messages.success(request, "Assignment uploaded.")
            return redirect("uploads:portal")
    else:
        form = PortalDocumentForm()
    documents = PortalDocument.objects.filter(owner=request.user)      # only my own files
    return render(request, "uploads/portal.html", {"form": form, "documents": documents})


@login_required
def portal_download(request, pk):
    # The query itself includes owner=request.user: somebody else's file is simply "not found"
    # (404, not 403), so the response does not even confirm that the id exists.
    document = get_object_or_404(PortalDocument, pk=pk, owner=request.user)
    try:
        handle = document.file.open("rb")
    except FileNotFoundError:
        raise Http404("File is missing from storage")
    logger.info("Portal document downloaded: id=%s user=%s", document.id, request.user.pk)
    return FileResponse(handle, as_attachment=True, filename=document.original_name,
                        content_type="application/pdf")
