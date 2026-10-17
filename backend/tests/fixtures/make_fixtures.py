"""Regenerate the fixture Documents: `uv run python tests/fixtures/make_fixtures.py [font.ttf]`.

Every name, address and amount is invented. The outputs are committed so tests don't depend on
the fonts installed on the machine running them; rerun this only to change a fixture.
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
FONT = sys.argv[1] if len(sys.argv) > 1 else "/System/Library/Fonts/Supplemental/Arial.ttf"
A4 = (1654, 2339)  # A4 at 200 dpi

# File name → pages of text lines. `expected` lists words OCR must find on each page.
FIXTURES = {
    "fr-facture-electricite.pdf": {
        "pages": [
            [
                "Électricité de France",
                "Facture d'électricité",
                "Date de facture : 14/03/2025",
                "Client : Jeanne Dupont",
                "12 rue des Lilas, 69003 Lyon",
                "Référence client : 5012 8841 07",
                "Montant TTC à payer : 84,32 €",
                "Échéance : 28/03/2025",
            ],
            [
                "Détail de votre consommation",
                "Période : du 10/01/2025 au 10/03/2025",
                "Énergie consommée : 312 kWh",
                "Abonnement : 23,47 €",
            ],
        ],
        "expected": [["Électricité", "Facture", "84,32", "Dupont"], ["consommation", "312 kWh"]],
    },
    "en-payslip.jpg": {
        "pages": [
            [
                "Acme Ltd",
                "Payslip - March 2025",
                "Employee: John Smith",
                "Pay date: 31/03/2025",
                "Gross pay: 3,200.00 GBP",
                "Income tax: 412.40 GBP",
                "Net pay: 2,480.15 GBP",
            ]
        ],
        "expected": [["Acme", "Payslip", "3,200.00", "Smith"]],
    },
}


def render(lines: list[str]) -> Image.Image:
    page = Image.new("RGB", A4, "white")
    draw = ImageDraw.Draw(page)
    title, body = ImageFont.truetype(FONT, 56), ImageFont.truetype(FONT, 40)
    for number, line in enumerate(lines):
        draw.text((160, 220 + number * 90), line, fill="black", font=title if number == 0 else body)
    return page


def as_photo(page: Image.Image) -> Image.Image:
    """Make a page look photographed: slightly turned, greyish paper, a little blur and noise."""
    random.seed(7)
    photo = page.rotate(2.5, expand=True, fillcolor=(205, 200, 190))
    photo = Image.blend(photo, Image.new("RGB", photo.size, (235, 230, 220)), 0.25)
    noise = Image.effect_noise(photo.size, 18).convert("RGB")
    return Image.blend(photo, noise, 0.08).filter(ImageFilter.GaussianBlur(0.8))


def main() -> None:
    expected = {}
    for name, fixture in FIXTURES.items():
        pages = [render(lines) for lines in fixture["pages"]]
        if name.endswith(".pdf"):
            # A scanned letter: images only, no text layer, slightly skewed.
            scans = [page.rotate(1.2, expand=True, fillcolor="white") for page in pages]
            scans[0].save(
                HERE / name, "PDF", resolution=200, save_all=True, append_images=scans[1:]
            )
        else:
            as_photo(pages[0]).save(HERE / name, "JPEG", quality=80)
        expected[name] = fixture["expected"]
    (HERE / "expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
