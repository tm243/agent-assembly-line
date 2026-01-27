"""
Agent-Assembly-Line
"""

from typing import List
import os
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

class OCRLoader(DataLoader):
    def __init__(self):
        if Image is None:
            raise ImportError(
                "Pillow is required for image processing. "
                "Please install it with: pip install pillow"
            )
        if pytesseract is None:
            raise ImportError(
                "pytesseract is required for OCR functionality. "
                "Please install it with: pip install pytesseract"
            )

    def load_data(self, file_path: str) -> List[Document]:
        """
        Load text content from image files using OCR.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            List[Document]: List containing a single document with OCR-extracted text
        """
        try:
            if not os.path.exists(file_path):
                return []
                
            image = Image.open(file_path)
            text_content = pytesseract.image_to_string(image)
            
            if not text_content.strip():
                return []
                
            document = Document(
                page_content=text_content.strip(),
                metadata={
                    "source": "ocr",
                    "file_path": file_path,
                    "image_format": image.format,
                    "image_size": image.size
                }
            )
            
            return [document]
            
        except Exception as e:
            if "tesseract" in str(e).lower() and "not installed" in str(e).lower():
                raise RuntimeError(
                    "Tesseract is not installed. Please install it:\n"
                    "  macOS: brew install tesseract\n"
                    "  Ubuntu: sudo apt install tesseract-ocr\n"
                    "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
                )
            return []