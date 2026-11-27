from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .storage import PrivateStorage


class StudentDocument(models.Model):
    """Lecture example: public document upload (pdf, txt, docx)."""
    student_name = models.CharField(max_length=100)
    # upload_to builds a sub-folder from the date so one folder does not hold every file
    document = models.FileField(upload_to="student_documents/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.document.name}"


class StudentPhoto(models.Model):
    """Lecture example: image upload, checked by Pillow."""
    photo = models.ImageField(
        upload_to="student_photos/%Y/%m/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.photo.name


class PortalDocument(models.Model):
    """PBL: student document portal. Private PDF, owned by one user.

    * the stored name is generated (uuid) and kept in `file`
    * the name the student chose is kept separately in `original_name`, for display only
    * the file lives in PRIVATE storage and can only be fetched through the download view
    """
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portal_documents")
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="portal/%Y/%m/", storage=PrivateStorage())
    size = models.PositiveBigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at", "-id"]

    def __str__(self):
        return f"{self.original_name} ({self.owner})"
