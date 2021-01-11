import tempfile
from pathlib import Path

import pytest

from RPA.PDF import PDF
from . import (
    TestFiles,
)


# TODO: clean the tests


@pytest.fixture
def library():
    return PDF()


def test_get_number_of_pages(library):
    assert library.get_number_of_pages(TestFiles.invoice_pdf) == 1
    assert library.get_number_of_pages(TestFiles.vero_pdf) == 2
    assert library.get_number_of_pages(TestFiles.pytest_pdf) == 9


def test_get_info(library):
    info = library.get_info(TestFiles.pytest_pdf)
    assert info["Pages"] == 9
    assert not info["Encrypted"]
    assert not info["Fields"]
    info = library.get_info(TestFiles.vero_pdf)
    assert info["Fields"]
    assert info["Pages"] == 2


def test_get_text_from_pdf_all_pages(library):
    text = library.get_text_from_pdf(TestFiles.loremipsum_pdf)
    assert len(text) == 1, "text should be parsed from 1 pages"
    assert len(text[1]) == 3622
    text = library.get_text_from_pdf(TestFiles.vero_pdf)
    assert len(text) == 2, "text should be parsed from 2 pages"
    assert "Muualle lomakkeeseen kirjoittamaasi tietoa ei käsitellä." in text[2]


def test_get_text_from_pdf_specific_page(library):
    text = library.get_text_from_pdf(TestFiles.pytest_pdf, pages=[7])

    assert "Plugins for Web Development" in text[7]


def test_extract_pages_from_pdf(library):
    pages = [7, 8]
    with tempfile.NamedTemporaryFile() as tmp_file:
        target_pdf = tmp_file.name
        library.extract_pages_from_pdf(TestFiles.pytest_pdf, target_pdf, pages)
        text = library.get_text_from_pdf(target_pdf)

        assert library.get_number_of_pages(target_pdf) == 2
        assert "Plugins for Web Development" in text[1]


def test_add_pages(library):
    # library.add_pages()
    pass

def test_html_to_pdf(library):
    text = "let's do some testing ÄÄ"
    html = f"<html> <body> {text} </body></html>"
    with tempfile.NamedTemporaryFile() as tmp_file:
        target_pdf = tmp_file.name
        library.html_to_pdf(html, target_pdf)
        result = library.get_text_from_pdf(target_pdf)

        assert text in result[1]
