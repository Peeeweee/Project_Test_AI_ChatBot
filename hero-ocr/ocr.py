import os
import pytesseract
from pdf2image import convert_from_path

# Hardcoded path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POPPLER_PATH = os.path.join(BASE_DIR, "poppler", "poppler-24.02.0", "Library", "bin")

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """
    Extracts text from a scanned PDF by converting pages to images
    and running OCR using pytesseract.
    """
    print(f"Loading PDF: {pdf_path}...")
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    
    extracted_text = []
    
    total_pages = len(pages)
    for i, page_image in enumerate(pages):
        print(f"Processing page {i + 1} of {total_pages}...")
        # Run OCR on the image
        text = pytesseract.image_to_string(page_image)
        extracted_text.append(text)
        
    # Combine all extracted text from all pages into one string
    return "\n".join(extracted_text)

