from django.contrib import admin

from .models import PortalDocument, StudentDocument, StudentPhoto

admin.site.register(StudentDocument)
admin.site.register(StudentPhoto)


@admin.register(PortalDocument)
class PortalDocumentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "size", "uploaded_at")
    readonly_fields = ("file", "size", "original_name")
