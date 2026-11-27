import re
from pathlib import Path
from uuid import uuid4


def safe_upload_name(uploaded_file, extension=None):
    """Return a generated storage name; the user's own file name is never used.

    This does NOT make an unsafe file safe, it only removes user control over the path and
    avoids collisions. Content validation (validators.py) is still required.
    """
    if extension is None:
        extension = Path(uploaded_file.name).suffix.lower()
    return f"{uuid4().hex}{extension}"


def clean_display_name(name, limit=255):
    """Make the user's file name safe to STORE and DISPLAY (never to use as a path)."""
    name = Path(str(name).replace("\\", "/")).name            # drop any folder part: ../../x.pdf -> x.pdf
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()       # drop control characters
    return (name or "document.pdf")[:limit]
