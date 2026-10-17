"""Builders for uploaded files, so tests don't need binary fixtures."""

from io import BytesIO

import pillow_heif
from PIL import Image
from pypdf import PdfWriter


def pdf(pages: int = 1) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=595, height=842)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def encrypted_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.encrypt("secret")
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def image(format: str, size: tuple[int, int] = (300, 200), orientation: int | None = None) -> bytes:
    picture = Image.new("RGB", size, "white")
    output = BytesIO()
    if format == "HEIF":
        pillow_heif.from_pillow(picture).save(output, quality=50)
        return output.getvalue()
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation
    picture.save(output, format, exif=exif)
    return output.getvalue()
