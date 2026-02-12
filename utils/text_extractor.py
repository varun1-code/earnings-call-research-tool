import fitz
from docx import Document
import os

from pdf2image import convert_from_path
import pytesseract


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = extract_from_pdf(file_path)

        print("Normal PDF text length:", len(text))

        # OCR fallback
        if len(text.strip()) < 50:
            print("Running OCR fallback...")
            text = extract_from_pdf_ocr(file_path)

            print("OCR text length:", len(text))

        return text



def extract_from_pdf(file_path: str) -> str:
    text = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)


def extract_from_pdf_ocr(file_path: str) -> str:
    images = convert_from_path(file_path, dpi=200, first_page=1, last_page=5)

    all_text = []
    for img in images:
        t = pytesseract.image_to_string(img)
        all_text.append(t)

    return "\n".join(all_text)


def extract_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])
