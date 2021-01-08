import pytest

from RPA.PDF import PDF

from . import TestFiles


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


def test_get_text_from_pdf(library):
    text = library.get_text_from_pdf(TestFiles.loremipsum_pdf)
    assert len(text) == 1, "text should be parsed from 1 pages"
    assert len(text[1]) == 3622
    text = library.get_text_from_pdf(TestFiles.vero_pdf)
    assert len(text) == 2, "text should be parsed from 2 pages"
    assert "Muualle lomakkeeseen kirjoittamaasi tietoa ei käsitellä." in text[2]
