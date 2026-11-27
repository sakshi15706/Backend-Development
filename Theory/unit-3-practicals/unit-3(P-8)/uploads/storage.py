import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateStorage(FileSystemStorage):
    """Stores files under PRIVATE_MEDIA_ROOT, which has no URL.

    The location is read from settings on every use (instead of being cached) so tests can
    point it at a temporary folder with override_settings.
    """

    @property
    def base_location(self):
        return settings.PRIVATE_MEDIA_ROOT

    @property
    def location(self):
        return os.path.abspath(self.base_location)

    @property
    def base_url(self):
        return None

    def url(self, name):
        raise ValueError("Private files have no public URL; use the download view.")
