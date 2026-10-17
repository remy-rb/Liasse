"""Turning a PDF into a searchable PDF, and reading each page's text."""

import logging
from io import BytesIO

import ocrmypdf
from pypdf import PdfReader

# OCRmyPDF logs every step; keep the worker's output readable.
logging.getLogger("ocrmypdf").setLevel(logging.WARNING)


def ocr(pdf: bytes) -> tuple[bytes, list[str]]:
    """Return the PDF with an invisible text layer, and the text of each page."""
    searchable = BytesIO()
    ocrmypdf.ocr(
        BytesIO(pdf),
        searchable,
        language=["fra", "eng"],
        deskew=True,
        # Pages that already carry text (a PDF made on a computer) are kept as they are.
        skip_text=True,
        # A plain PDF, not PDF/A: avoids needing Ghostscript.
        output_type="pdf",
        rasterizer="pypdfium",
        optimize=0,
        progress_bar=False,
    )
    output = searchable.getvalue()
    # The text layer holds Tesseract's text for scanned pages and the original text otherwise.
    texts = [page.extract_text().strip() for page in PdfReader(BytesIO(output)).pages]
    return output, texts
