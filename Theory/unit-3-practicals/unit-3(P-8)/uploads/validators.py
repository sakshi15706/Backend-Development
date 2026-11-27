"""Reusable validators, shared by the HTML forms and the REST serializers.

Each input boundary needs validation: a form protects the web page, a serializer protects
the API. Both call these functions so the rules cannot drift apart.
"""
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError

PDF_MAGIC = b"%PDF-"


def human_size(n_bytes):
    return f"{n_bytes / (1024 * 1024):g} MB"


def extension_of(uploaded_file):
    return Path(uploaded_file.name).suffix.lower().lstrip(".")


def validate_document(uploaded_file):
    """Lecture rules for StudentDocument: 5 MB, pdf / txt / docx."""
    if uploaded_file.size > settings.DOCUMENT_MAX_BYTES:
        raise ValidationError(f"The file must be smaller than {human_size(settings.DOCUMENT_MAX_BYTES)}.")
    if extension_of(uploaded_file) not in {"pdf", "txt", "docx"}:
        raise ValidationError("Only PDF, TXT, and DOCX files are allowed.")
    return uploaded_file


def validate_photo(uploaded_file):
    """Size and pixel dimensions, on top of ImageField's check that Pillow can decode it."""
    if uploaded_file.size > settings.PHOTO_MAX_BYTES:
        raise ValidationError(f"The image must be smaller than {human_size(settings.PHOTO_MAX_BYTES)}.")
    limit = settings.PHOTO_MAX_DIMENSION
    if uploaded_file.image.width > limit or uploaded_file.image.height > limit:
        raise ValidationError(f"The image dimensions must not exceed {limit} by {limit} pixels.")
    return uploaded_file


def validate_pdf_upload(uploaded_file):
    """PBL rules: PDF only, at most 10 MB, and the CONTENT must look like a PDF.

    The extension is chosen by the user, so it proves nothing: a renamed .exe or .txt must
    be rejected. A real PDF starts with the bytes '%PDF-'.
    """
    if uploaded_file.size > settings.PORTAL_MAX_BYTES:
        raise ValidationError(f"The file must be at most {human_size(settings.PORTAL_MAX_BYTES)}.")
    if extension_of(uploaded_file) != "pdf":
        raise ValidationError("Only PDF files are allowed.")
    head = uploaded_file.read(len(PDF_MAGIC))
    uploaded_file.seek(0)                                    # rewind so the file can still be saved
    if head != PDF_MAGIC:
        raise ValidationError("This file is not a valid PDF.")
    return uploaded_file
