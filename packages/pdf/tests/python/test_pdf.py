from pathlib import Path
import pytest

from RPA.PDF import PDF

from . import TestFiles


@pytest.fixture
def library():
    return PDF()



# def test_set_anchor_to_element(library):
#     library.open_pdf_document(invoice_pdf)
#     result = library.set_anchor_to_element("text:due date")
#     assert result
#     result = library.set_anchor_to_element("text:due to the date")
#     assert not result


# def test_get_value_from_anchor_by_default_from_right(library):
#     library.open_pdf_document(invoice_pdf)
#     invoice_number = library.get_value_from_anchor("text:invoice number")
#     order_number = library.get_value_from_anchor("text:order number")
#     invoice_date = library.get_value_from_anchor("text:invoice date")
#     due_date = library.get_value_from_anchor("text:due date")
#     total_due = library.get_value_from_anchor("text:total due")
#     assert invoice_number.text == "INV-3337"
#     assert order_number.text == "12345"
#     assert invoice_date.text == "January 25, 2016"
#     assert due_date.text == "January 31, 2016"
#     assert total_due.text == "$93.50"
#

# def test_get_value_from_anchor_from_left(library):
#     library.open_pdf_document(invoice_pdf)
#     invoice_label = library.get_value_from_anchor("text:INV-3337", direction="left")
#     assert invoice_label.text == "Invoice Number"


# def test_get_from_anchor_from_bottom(library):
#     library.open_pdf_document(invoice_pdf)
#     service = library.get_value_from_anchor("text:service", direction="bottom")
#     assert "Web Design" in service.text


# def test_get_from_anchor_from_top(library):
#     library.open_pdf_document(invoice_pdf)
#     item = library.get_value_from_anchor("text:Tax", direction="top")
#     assert item.text == "Sub Total"





# def test_get_pdf_xml_dump(library):
#     library.open_pdf_document(invoice_pdf)
#     xml = library.dump_pdf_as_xml()
#     assert '<?xml version="1.0" encoding="utf-8" ?>' in xml
#

# def test_get_input_fields(library):
#     fields = library.get_input_fields(vero_pdf)
#     assert fields["Puhelinnumero"]["value"] == ""
#     assert isinstance(fields["Puhelinnumero"]["rect"], list)
#     fields = library.get_input_fields(vero_pdf, replace_none_value=True)
#     assert fields["Puhelinnumero"]["value"] == "Puhelinnumero"


# @pytest.mark.skip(reason="known issue of reading fields of already updated pdf")
# def test_update_field_values(library):
#     update_fields = {"Puhelinnumero": "10-1231233", "Paivays": "01.01.2020"}
#     target_pdf = TEMP_DIR / "values_updated.pdf"
#
#     fields = library.get_input_fields(vero_pdf)
#     assert fields["Puhelinnumero"]["value"] == ""
#
#     library.update_field_values(vero_pdf, target_pdf, update_fields)
#     fields = library.get_input_fields(target_pdf)
#     assert fields["Puhelinnumero"]["value"] == update_fields["Puhelinnumero"]
#     assert fields["Paivays"]["value"] == update_fields["Paivays"]


# def test_set_field_value(library):
#     target_pdf = TEMP_DIR / "copy_of_vero.pdf"
#     library.open_pdf_document(vero_pdf)
#     library.set_field_value("Puhelinnumero", "+358-55-12322121312")
#     library.set_field_value("Paivays", "31.12.2020")
#     library.save_pdf(vero_pdf, target_pdf)

#
# def test_get_texts_matching_regexp(library):
#     pass
