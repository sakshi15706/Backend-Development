"""Profile-photo validation. Never trust the client: check size, declared type AND the file's real bytes."""
from fastapi import HTTPException, UploadFile

MAX_PHOTO_BYTES = 2 * 1024 * 1024                      # 2 MB
ALLOWED = {                                            # content-type -> (extension, magic number)
    "image/jpeg": ("jpg", b"\xff\xd8\xff"),
    "image/png": ("png", b"\x89PNG\r\n\x1a\n"),
}


async def read_and_validate_photo(file: UploadFile) -> tuple[bytes, str]:
    """Returns (content, extension) or raises the proper HTTP error."""
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type '{file.content_type}'. Allowed: JPEG or PNG")
    extension, magic = ALLOWED[file.content_type]

    content = bytearray()
    while chunk := await file.read(64 * 1024):         # read in chunks, stop as soon as it is too big
        content += chunk
        if len(content) > MAX_PHOTO_BYTES:
            raise HTTPException(413, f"File too large. Maximum size is {MAX_PHOTO_BYTES // (1024 * 1024)} MB")
    if not content:
        raise HTTPException(400, "The uploaded file is empty")
    if not content.startswith(magic):                   # e.g. a .txt renamed to .png
        raise HTTPException(400, f"File content is not a valid {extension.upper()} image")
    return bytes(content), extension
