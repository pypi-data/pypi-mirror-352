import os
from glob import glob
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import FileSystemBlobLoader, PyMuPDFLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import (
    PyMuPDFParser,
    TesseractBlobParser,
)

from langchain.schema import Document
import pdfplumber
import pytesseract


class BasePreprocessing:
    def __init__(self, path, chunks_size=512, chunk_overlap=100):
        self.path = path if path is not None else None
        self.chunks_size = chunks_size
        self.chunk_overlap = chunk_overlap

    def __call__(self, *args, **kwds):
        return self._preprocess(
            chunks_size=self.chunks_size, chunk_overlap=self.chunk_overlap
        )

    def _extract_text_from_pdf(self) -> str:
        """
        Extract text from a PDF file.
        Args:
            pdf_path (str): Path to the PDF file.
        Returns:
            str: Extracted text from the PDF file.
        """
        pdf_path = os.path.abspath(self.path)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The file {pdf_path} does not exist.")
        if pdf_path.lower().endswith(".pdf"):
            all_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    all_text += page.extract_text() + "\n"

        else:
            files = glob(pdf_path + "/*.pdf")
            if not files:
                raise FileNotFoundError(
                    f"No PDF files found in the directory {pdf_path}."
                )
            all_text = ""
            for file in files:
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        all_text += page.extract_text() + "\n"

        return all_text

    def _fragmentar_texto(
        self, text, chunks_size: int = 512, chunk_overlap: int = 100
    ) -> list:
        """
        Fragment the text into smaller chunks.
        Args:
            texto (str): The text to be fragmented.
        Returns:
            list: A list of Document objects containing the fragmented text.
        """

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunks_size, chunk_overlap=chunk_overlap
        )
        return [
            Document(page_content=t, metadata={"source": f"chunk_{i}"})
            for i, t in enumerate(splitter.split_text(text))
        ]

    def _preprocess(self, chunks_size: int = 512, chunk_overlap: int = 100) -> list:
        """
        Preprocess the PDF file by extracting text and fragmenting it into smaller chunks.
        Args:
            chunks_size (int): Size of each chunk.
            chunk_overlap (int): Overlap between chunks.
        Returns:
            list: A list of Document objects containing the fragmented text.
        """

        texto = self._extract_text_from_pdf()
        return self._fragmentar_texto(
            texto, chunks_size=chunks_size, chunk_overlap=chunk_overlap
        )


class PyMuPDFPreprocessing(BasePreprocessing):
    def __init__(self, path, chunks_size=512, chunk_overlap=100, *args, **kwargs):
        super().__init__(path, chunks_size, chunk_overlap)
        self.tesseract_path = kwargs.get("tesseract_path", None)
        self.extract_images = kwargs.get("extract_images", True)
        self.images_parser = kwargs.get(
            "images_parser", TesseractBlobParser(langs=["spa", "eng"])
        )
        self.images_inner_format = kwargs.get("images_inner_format", "html-img")
        self.extract_tables = kwargs.get("extract_tables", "html")
        self.mode = kwargs.get("mode", "page")
        if self.tesseract_path is None:
            raise ValueError("You must provide the path to the Tesseract executable.")
        if not os.path.exists(
            os.path.join(*self.tesseract_path.split("/")[:-1] + ["\\"])
        ):
            raise FileNotFoundError(
                f"The Tesseract executable does not exist at the path: {self.tesseract_path}"
            )

        pytesseract.pytesseract.tesseract_cmd = os.path.abspath(self.tesseract_path)
        self.parser = PyMuPDFParser(
            extract_images=self.extract_images,
            images_parser=self.images_parser,
            images_inner_format=self.images_inner_format,
            extract_tables=self.extract_tables,
            mode=self.mode,
        )
        self.primary_loader = GenericLoader(
            blob_loader=FileSystemBlobLoader(path=self.path, glob="*.pdf"),
            blob_parser=self.parser,
        )

    def _preprocess(self, chunks_size: int = 512, chunk_overlap: int = 100) -> list:
        """
        Preprocess the PDF file using PyMuPDF.
        Returns:
            list: A list of Document objects containing the fragmented text.
        """
        documents = self.primary_loader.load()
        all_text = ""
        for doc in documents:
            if isinstance(doc, Document):
                all_text += doc.page_content + "\n"
            else:
                raise TypeError(
                    f"Expected Document type, but got {type(doc)}. Ensure the loader is set up correctly."
                )
        return self._fragmentar_texto(
            all_text, chunks_size=chunks_size, chunk_overlap=chunk_overlap
        )
