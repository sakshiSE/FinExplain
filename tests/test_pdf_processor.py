import pytest
from backend.app.pdf_processor import PDFProcessor, PDFProcessingError

def test_invalid_pdf():
    processor = PDFProcessor()
    with pytest.raises(PDFProcessingError):
        processor.extract_text_with_pages(b"invalid data")
