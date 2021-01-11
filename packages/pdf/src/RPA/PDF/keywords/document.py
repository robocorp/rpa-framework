from pathlib import Path
from typing import Any

import PyPDF2
from fpdf import FPDF, HTMLMixin

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1

from RPA.core.helpers import required_param
from RPA.core.notebook import notebook_print
from RPA.PDF.keywords import (
    LibraryContext,
    keyword,
)

class PDF(FPDF, HTMLMixin):
    pass


class DocumentKeywords(LibraryContext):
    """Keywords for basic PDF operations"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.fpdf = PDF()
        self.output_directory = Path(".")  # TODO: make this a property with setter?

    # def __del__(self):
    #     self.close_all_pdf_documents()

    # FIXME: doesn't work
    def close_all_pdf_documents(self) -> None:
        """Close all opened PDF file descriptors."""
        for filename, fileobject in self.ctx.fileobjects.items():
            fileobject.close()
            self.logger.debug('PDF "%s" closed', filename)
        self.ctx.anchor_element = None
        self.ctx.fileobjects = {}
        self.ctx.active_pdf = None
        self.ctx.active_fileobject = None
        self.ctx.active_fields = None
        self.ctx.rpa_pdf_document = None

    def open_pdf_document(self, source_pdf: str = None) -> None:
        """Open PDF document.

        :param source_pdf: filepath to the source pdf
        :raises ValueError: if PDF is already open

        Also opens file for reading.
        """
        if source_pdf is None:
            raise ValueError("Source PDF is missing")
        if str(source_pdf) in self.ctx.fileobjects.keys():
            raise ValueError(
                "PDF file is already open. Please close it before opening again."
            )
        self.ctx.active_pdf = str(source_pdf)
        self.ctx.active_fileobject = open(source_pdf, "rb")
        self.ctx.active_fields = None
        self.ctx.fileobjects[source_pdf] = self.ctx.active_fileobject
        self.ctx.rpa_pdf_document = None

    @keyword
    def html_to_pdf(
        self,
        content: str = None,
        target_pdf: str = None,
        variables: dict = None,
        create_dirs: bool = True,
        exists_ok: bool = True,
    ) -> None:
        """Use HTML content to generate PDF file.

        :param content: HTML content
        :param target_pdf: filepath where to save PDF document
        :param variables: dictionary of variables to fill into template, defaults to {}
        :param create_dirs: directory structure is created if it is missing,
         default `True`
        :param exists_ok: file is overwritten if it exists, default `True`
        """
        required_param([content, target_pdf], "html_to_pdf")
        variables = variables or {}

        html = content.encode("utf-8").decode("latin-1")
        # html = content

        for key, value in variables.items():
            html = html.replace("{{" + key + "}}", str(value))

        if target_pdf:
            output_filepath = Path(target_pdf)
        else:
            output_filepath = Path(self.output_directory / "html2pdf.pdf")

        self._write_html_to_pdf(html, output_filepath, create_dirs, exists_ok)

    def _write_html_to_pdf(self, html, output_path, create_dirs, exists_ok):
        # TODO: is this needed?
        # if create_dirs:
        #     Path(output_path).resolve().parent.mkdir(parents=True, exist_ok=True)
        # if not exists_ok and Path(output_path).exists():
        #     raise FileExistsError(output_path)
        notebook_print(link=str(output_path))
        self.add_pages(1)
        self.fpdf.write_html(html)

        pdf_content = self.fpdf.output(dest="S").encode("latin-1")
        with open(output_path, "wb") as outfile:
            outfile.write(pdf_content)
        # self.__init__()  # TODO: what should happen here exactly?
        self.fpdf = PDF()

    @keyword
    def add_pages(self, pages: int = 1) -> None:
        """Adds pages into PDF documents.

        :param pages: number of pages to add, defaults to 1
        """
        for _ in range(int(pages)):
            self.fpdf.add_page()

    @keyword
    def get_info(self, source_pdf: str = None) -> dict:
        """Get information from PDF document.

        :param source_pdf: filepath to the source pdf
        :return: dictionary of PDF information
        """
        self.switch_to_pdf_document(source_pdf)
        pdf = PyPDF2.PdfFileReader(self.ctx.active_fileobject)
        docinfo = pdf.getDocumentInfo()
        parser = PDFParser(self.ctx.active_fileobject)
        document = PDFDocument(parser)
        try:
            fields = resolve1(document.catalog["AcroForm"])["Fields"]
        except KeyError:
            fields = None
        info = {
            "Author": docinfo.author,
            "Creator": docinfo.creator,
            "Producer": docinfo.producer,
            "Subject": docinfo.subject,
            "Title": docinfo.title,
            "Pages": pdf.getNumPages(),
            "Encrypted": self.is_pdf_encrypted(source_pdf),
            "Fields": bool(fields),
        }
        return info

    def is_pdf_encrypted(self, source_pdf: str = None) -> bool:
        """Check if PDF is encrypted.

        Returns True even if PDF was decrypted.

        :param source_pdf: filepath to the source pdf
        :return: True if file is encrypted
        """
        self.switch_to_pdf_document(source_pdf)
        reader = PyPDF2.PdfFileReader(self.ctx.active_fileobject)
        return reader.isEncrypted

    @keyword
    def get_number_of_pages(self, source_pdf: str = None) -> int:
        """Get number of pages in the document.

        :param source_pdf: filepath to the source pdf
        :raises PdfReadError: if file is encrypted or other restrictions are in place
        """
        self.switch_to_pdf_document(source_pdf)
        reader = PyPDF2.PdfFileReader(self.ctx.active_fileobject)
        return reader.getNumPages()

    def switch_to_pdf_document(self, source_pdf: str = None) -> None:
        """Switch library's current fileobject to already open file
        or open file if not opened.

        :param source_pdf: filepath
        :raises ValueError: if PDF filepath is not given and there are no active
            file to activate
        """
        if source_pdf is not None and str(source_pdf) not in self.ctx.fileobjects.keys():
            self.open_pdf_document(source_pdf)
            return
        if source_pdf is None and self.ctx.active_fileobject is None:
            raise ValueError("No PDF is open")
        if (
            source_pdf is not None
            and self.ctx.active_fileobject != self.ctx.fileobjects[source_pdf]
        ):
            self.logger.debug("Switching to another open document")
            self.ctx.active_pdf = str(source_pdf)
            self.ctx.active_fileobject = self.ctx.fileobjects[str(source_pdf)]
            self.ctx.active_fields = None
            self.ctx.rpa_pdf_document = None

    @keyword
    def get_text_from_pdf(self, source_pdf: str = None, pages: Any = None) -> dict:
        """Get text from set of pages in source PDF document.

        :param source_pdf: filepath to the source pdf
        :param pages: page numbers to get text (numbers start from 0)
        :return: dictionary of pages and their texts

        PDF needs to be parsed before text can be read.
        """
        self.switch_to_pdf_document(source_pdf)
        if self.ctx.rpa_pdf_document is None:
            self.ctx.convert()

        if pages and not isinstance(pages, list):
            pages = pages.split(",")
        if pages is not None:
            pages = list(map(int, pages))
        pdf_text = {}
        for idx, page in self.ctx.rpa_pdf_document.get_pages().items():
            self.logger.info("%s:%s", idx, pages)
            for _, item in page.get_textboxes().items():
                if pages is None or idx in pages:
                    if idx in pdf_text:
                        pdf_text[idx] += item.text
                    else:
                        pdf_text[idx] = item.text
        return pdf_text

    @keyword
    def extract_pages_from_pdf(
        self, source_pdf: str = None, target_pdf: str = None, pages: Any = None
    ) -> None:
        """Extract pages from source PDF and save to target PDF document.

        Page numbers start from 1.

        :param source_pdf: filepath to the source pdf
        :param target_pdf: filepath to the target pdf, stored by default
            in `output_directory`
        :param pages: page numbers to extract from PDF (numbers start from 0)
            if None then extracts all pages
        """
        self.switch_to_pdf_document(source_pdf)
        reader = PyPDF2.PdfFileReader(self.ctx.active_fileobject)
        writer = PyPDF2.PdfFileWriter()

        if target_pdf:
            output_filepath = Path(target_pdf)
        else:
            output_filepath = Path(self.output_directory / "extracted.pdf")

        if pages and not isinstance(pages, list):
            pages = pages.split(",")
        elif pages is None:
            pages = range(reader.getNumPages())
        pages = list(map(int, pages))
        for pagenum in pages:
            writer.addPage(reader.getPage(int(pagenum) - 1))
        with open(str(output_filepath), "wb") as f:
            writer.write(f)
