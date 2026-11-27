from django.urls import reverse
from rest_framework import serializers

from .models import PortalDocument, StudentDocument
from .services import create_portal_document
from .utils import safe_upload_name
from .validators import validate_document, validate_pdf_upload


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = ["id", "student_name", "document", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

    # The API must not depend on the HTML form: it validates for itself, with the same rules.
    def validate_document(self, uploaded_file):
        return validate_document(uploaded_file)

    def create(self, validated_data):
        uploaded_file = validated_data.pop("document")
        document = StudentDocument(**validated_data)
        document.document.save(safe_upload_name(uploaded_file), uploaded_file, save=False)
        document.save()
        return document


class PortalDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, validators=[validate_pdf_upload])
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = PortalDocument
        fields = ["id", "original_name", "size", "uploaded_at", "download_url", "file"]
        read_only_fields = ["id", "original_name", "size", "uploaded_at", "download_url"]

    def get_download_url(self, obj):
        # a URL to the permission-checked download endpoint, NOT a link to the file itself
        return self.context["request"].build_absolute_uri(reverse("uploads:portal-api-download", args=[obj.pk]))

    def create(self, validated_data):
        return create_portal_document(self.context["request"].user, validated_data["file"])
