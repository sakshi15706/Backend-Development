from django.urls import path

from . import api_views, views

app_name = "uploads"

urlpatterns = [
    # normal Django forms
    path("document/", views.upload_document, name="upload"),
    path("document/success/", views.upload_success, name="upload-success"),
    path("photo/", views.upload_photo, name="upload-photo"),
    # private student document portal (login required)
    path("portal/", views.portal, name="portal"),
    path("portal/<int:pk>/download/", views.portal_download, name="portal-download"),
    # REST API
    path("api/documents/", api_views.StudentDocumentUploadAPIView.as_view(), name="document-api"),
    path("api/portal/", api_views.PortalDocumentListCreateAPIView.as_view(), name="portal-api"),
    path("api/portal/<int:pk>/download/", api_views.PortalDocumentDownloadAPIView.as_view(), name="portal-api-download"),
]
