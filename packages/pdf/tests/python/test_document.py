import tempfile
from pathlib import Path

import PyPDF2
import pytest

from RPA.PDF import PDF
from . import (
    TestFiles,
)


# TODO: clean the tests


@pytest.fixture
def library():
    return PDF()


@pytest.mark.parametrize("file, number_of_pages", [
    (TestFiles.invoice_pdf, 1),
    (TestFiles.vero_pdf, 2),
    (TestFiles.pytest_pdf, 9),
])
def test_get_number_of_pages(library, file, number_of_pages):
    assert library.get_number_of_pages(file) == number_of_pages


@pytest.mark.parametrize("file, pages, encrypted, fields", [
    (TestFiles.pytest_pdf, 9, False, False),
    (TestFiles.vero_pdf, 2, False, True),
])
def test_get_info(library, file, pages, encrypted, fields):
    info = library.get_info(file)

    assert info["Pages"] == pages
    assert info["Encrypted"] == encrypted
    assert info["Fields"] == fields


def test_is_pdf_encrypted(library):
    assert not library.is_pdf_encrypted(TestFiles.vero_pdf)


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


def test_html_to_pdf(library):
    text = "let's do some testing ÄÄ"
    html = f"<html> <body> {text} </body></html>"
    with tempfile.NamedTemporaryFile() as tmp_file:
        target_pdf = tmp_file.name
        library.html_to_pdf(html, target_pdf)
        result = library.get_text_from_pdf(target_pdf)

        assert text in result[1]


def test_page_rotate(library):
    def get_source_page(pdf_file, page_num):
        reader = PyPDF2.PdfFileReader(pdf_file)
        return reader.getPage(int(page_num))

    page_to_rotate = 1
    page_before_rotation = get_source_page(str(TestFiles.vero_pdf), page_to_rotate)

    assert page_before_rotation["/Rotate"] == 0

    with tempfile.NamedTemporaryFile() as tmp_file:
        library.page_rotate(page_to_rotate, TestFiles.vero_pdf, tmp_file.name)
        page_after_rotation = get_source_page(tmp_file.name, page_to_rotate)

        assert page_after_rotation["/Rotate"] == 90


def test_pdf_encrypt(library):
    with tempfile.NamedTemporaryFile() as tmp_file:
        library.pdf_encrypt(TestFiles.vero_pdf, tmp_file.name)

        assert not library.is_pdf_encrypted(TestFiles.vero_pdf)
        assert library.is_pdf_encrypted(tmp_file.name)


def test_pdf_decrypt(library):
    passw = "secrett"

    with tempfile.NamedTemporaryFile() as tmp_file:
        library.pdf_encrypt(TestFiles.vero_pdf, tmp_file.name, passw)

        assert library.is_pdf_encrypted(tmp_file.name)

        with tempfile.NamedTemporaryFile() as another_file:
            library.pdf_decrypt(tmp_file.name, another_file.name, passw)

            assert not library.is_pdf_encrypted(another_file.name)
