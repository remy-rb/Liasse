"""Recognising uploaded files and turning them into PDFs."""

from dataclasses import dataclass
from io import BytesIO

import pillow_heif
from PIL import Image, ImageOps, UnidentifiedImageError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

pillow_heif.register_heif_opener()

PDF = "application/pdf"
IMAGE_TYPES = {"JPEG": "image/jpeg", "PNG": "image/png", "HEIF": "image/heic"}


class UnsupportedFile(ValueError):
    """The file can't become a Document; the message is shown to the Owner."""


@dataclass(frozen=True)
class Inspected:
    content_type: str
    page_count: int


def inspect(data: bytes) -> Inspected:
    """Identify a file from its content (never its name or declared type) and check it opens."""
    if data.startswith(b"%PDF-"):
        try:
            reader = PdfReader(BytesIO(data))
            encrypted = reader.is_encrypted
            pages = 0 if encrypted else len(reader.pages)
        except (PdfReadError, ValueError, KeyError):
            raise UnsupportedFile("This PDF is damaged and can't be read.") from None
        if encrypted:
            raise UnsupportedFile("Password-protected PDFs aren't supported.")
        if pages == 0:
            raise UnsupportedFile("This PDF has no pages.")
        return Inspected(PDF, pages)
    try:
        with Image.open(BytesIO(data)) as image:
            content_type = IMAGE_TYPES.get(image.format or "")
            image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise UnsupportedFile("Only PDF, JPEG, PNG and HEIC files are supported.") from None
    if content_type is None:
        raise UnsupportedFile("Only PDF, JPEG, PNG and HEIC files are supported.")
    return Inspected(content_type, 1)


def to_pdf(data: bytes, content_type: str) -> bytes:
    """The Document as a PDF; images become a one-page PDF, upright as the camera saw them."""
    if content_type == PDF:
        return data
    with Image.open(BytesIO(data)) as image:
        page = ImageOps.exif_transpose(image).convert("RGB")
    output = BytesIO()
    page.save(output, "PDF", resolution=300)
    return output.getvalue()
