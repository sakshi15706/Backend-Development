import logging

from .models import PortalDocument
from .utils import clean_display_name, safe_upload_name

logger = logging.getLogger(__name__)


def create_portal_document(owner, uploaded_file):
    """Shared by the HTML view and the REST API (validation has already happened)."""
    document = PortalDocument(
        owner=owner,
        original_name=clean_display_name(uploaded_file.name),
        size=uploaded_file.size,
    )
    # stored name = uuid + .pdf (never the user's name); original name kept separately
    document.file.save(safe_upload_name(uploaded_file, extension=".pdf"), uploaded_file, save=False)
    document.save()
    logger.info("Portal document uploaded: id=%s owner=%s size=%s", document.id, owner.pk, document.size)
    return document
