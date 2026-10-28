import io
import re
from typing import List, Dict, Any
from pypdf import PdfReader

class PDFProcessingError(Exception):
    pass

class PDFProcessor:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def extract_text_with_pages(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            pages_data = []

            if len(reader.pages) == 0:
                raise PDFProcessingError("Uploaded PDF is empty.")

            total_extracted_text = ""
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                cleaned_text = re.sub(r'\s+', ' ', text).strip()
                if cleaned_text:
                    pages_data.append({
                        "page_number": idx + 1,
                        "text": cleaned_text
                    })
                    total_extracted_text += cleaned_text

            if not total_extracted_text.strip():
                raise PDFProcessingError("No readable text found in PDF. Document may be scanned images.")

            return pages_data
        except Exception as e:
            if isinstance(e, PDFProcessingError):
                raise e
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}")

    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_id = 0

        for page in pages_data:
            page_num = page["page_number"]
            words = page["text"].split()
            if not words:
                continue

            i = 0
            while i < len(words):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = " ".join(chunk_words)
                chunks.append({
                    "chunk_id": chunk_id,
                    "page_number": page_num,
                    "text": chunk_text
                })
                chunk_id += 1
                i += (self.chunk_size - self.overlap)

        return chunks
