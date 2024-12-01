import logging
from typing import List, Tuple
import os
import requests
from pdf2image import convert_from_path
import pytesseract
from fpdf import FPDF
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GrobidService:
    """
    A service class for interacting with a GROBID server to process PDF
    documents and convert them into structured TEI format.
    """
    def __init__(self, base_url: str = "http://34.100.191.240:8070"):
        self.base_url: str = base_url

    def convert_pdf_to_ocr_pdf(self, pdf_path: str, output_path: str, lang: str = 'eng'):
        logging.info(f"Starting OCR conversion for: {pdf_path}")
        pages = convert_from_path(pdf_path, 300)

        text_pages = []
        for page in pages:
            text = pytesseract.image_to_string(page, lang=lang)
            text_pages.append(text)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for text in text_pages:
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))

        pdf.output(output_path)
        logging.info(f"OCR conversion completed for: {pdf_path}, saved to: {output_path}")

    def process_pdf(
            self,
            input_pdf_path: str,
            output_tei_path: str,
            timeout: Tuple[int, int] = (120, 1200),
            use_ocr: bool = False,
            lang: str = 'eng'
    ) -> str:
        logging.info(f"Processing PDF: {input_pdf_path}")
        if use_ocr:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                ocr_pdf_path = temp_file.name
            self.convert_pdf_to_ocr_pdf(input_pdf_path, ocr_pdf_path, lang=lang)
            input_pdf_path = ocr_pdf_path

        try:
            with open(input_pdf_path, "rb") as file:
                files = {"input": (input_pdf_path, file, "application/pdf")}
                response = requests.post(
                    f"{self.base_url}/api/processFulltextDocument",
                    files=files,
                    timeout=timeout
                )

            if response.status_code == 200:
                with open(output_tei_path, "w", encoding="utf-8") as output_file:
                    output_file.write(response.text)
                logging.info(f"Successfully processed PDF: {input_pdf_path}, TEI saved to: {output_tei_path}")
                return response.text
            else:
                error_message = f"GROBID server returned status code: {response.status_code}"
                logging.error(error_message)
                return error_message

        except requests.exceptions.Timeout:
            error_message = "The request timed out."
            logging.error(error_message)
            return error_message
        except Exception as e:
            logging.error(f"An error occurred while processing PDF: {input_pdf_path}, Error: {e}")
            return str(e)

    def process_multiple_pdfs(
            self,
            input_pdf_paths: List[str],
            output_tei_paths: List[str],
            timeout: Tuple[int, int] = (120, 1200),
            use_ocr: bool = False,
            lang: str = 'eng'
    ) -> List[str]:
        logging.info("Starting batch processing of PDFs...")
        results = []
        for input_pdf_path, output_tei_path in zip(input_pdf_paths, output_tei_paths):
            result = self.process_pdf(input_pdf_path, output_tei_path, timeout, use_ocr, lang)
            results.append(result)
        logging.info("Batch processing completed.")
        return results
