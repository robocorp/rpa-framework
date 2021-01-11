from pathlib import Path

import pytest


RESOURCE_DIR = Path(__file__).resolve().parent / ".." / "resources"


class TestFiles:
    imagesandtext_pdf = RESOURCE_DIR / "imagesandtext.pdf"
    invoice_pdf = RESOURCE_DIR / "invoice.pdf"
    vero_pdf = RESOURCE_DIR / "vero.pdf"
    pytest_pdf = RESOURCE_DIR / "18467.pdf"
    loremipsum_pdf = RESOURCE_DIR / "LoremIpsum.pdf"
    encrypted_pdf = RESOURCE_DIR / "encrypted.pdf"
