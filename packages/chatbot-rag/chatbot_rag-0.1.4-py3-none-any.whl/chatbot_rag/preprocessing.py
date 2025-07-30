import os
from glob import glob
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import pdfplumber


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
