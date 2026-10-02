
from pypdf import PdfReader
from io import BytesIO


def extract_pdf_text(file_bytes: bytes):
    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page": page_number,
            "text": text
        })

    return pages