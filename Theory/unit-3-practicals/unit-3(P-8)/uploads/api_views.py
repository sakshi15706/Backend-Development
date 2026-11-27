import logging

from django.http import FileResponse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PortalDocument
from .serializers import PortalDocumentSerializer, StudentDocumentSerializer

logger = logging.getLogger(__name__)


class StudentDocumentUploadAPIView(APIView):
    """The lecture's open demo endpoint. AllowAny is deliberate and explicit: it mirrors the
    slides' curl example. Anything real should use the authenticated portal API below."""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentDocumentSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        document = serializer.save()
        logger.info("API document uploaded: id=%s", document.id)
        return Response(StudentDocumentSerializer(document, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class PortalDocumentListCreateAPIView(APIView):
    """GET: my documents.   POST (multipart, field `file`): upload a PDF. Login required."""
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        documents = PortalDocument.objects.filter(owner=request.user)
        return Response(PortalDocumentSerializer(documents, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = PortalDocumentSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        document = serializer.save()
        return Response(PortalDocumentSerializer(document, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)


class PortalDocumentDownloadAPIView(APIView):
    def get(self, request, pk):
        try:
            document = PortalDocument.objects.get(pk=pk, owner=request.user)
        except PortalDocument.DoesNotExist:
            raise NotFound("Document not found.")      # same answer for "missing" and "not yours"
        return FileResponse(document.file.open("rb"), as_attachment=True,
                            filename=document.original_name, content_type="application/pdf")
