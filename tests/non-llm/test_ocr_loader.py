"""
Agent-Assembly-Line
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from agent_assembly_line.data_loaders.ocr_loader import OCRLoader
from agent_assembly_line.models.document import Document

class TestOCRLoader(unittest.TestCase):
    
    @patch('agent_assembly_line.data_loaders.ocr_loader.Image')
    @patch('os.path.exists')
    def test_load_data_success(self, mock_exists, mock_image):
        mock_exists.return_value = True
        
        mock_image_instance = MagicMock()
        mock_image_instance.format = "PNG"
        mock_image_instance.size = (800, 600)
        mock_image.open.return_value = mock_image_instance
        
        with patch('agent_assembly_line.data_loaders.ocr_loader.pytesseract') as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "Sample text from image"
            
            loader = OCRLoader()
            documents = loader.load_data('/path/to/image.png')
            
            self.assertEqual(len(documents), 1)
            self.assertIsInstance(documents[0], Document)
            self.assertEqual(documents[0].page_content, "Sample text from image")
            self.assertEqual(documents[0].metadata['source'], 'ocr')
            self.assertEqual(documents[0].metadata['file_path'], '/path/to/image.png')
            self.assertEqual(documents[0].metadata['image_format'], 'PNG')
            self.assertEqual(documents[0].metadata['image_size'], (800, 600))
            
            mock_image.open.assert_called_once_with('/path/to/image.png')
            mock_tesseract.image_to_string.assert_called_once_with(mock_image_instance)

    @patch('agent_assembly_line.data_loaders.ocr_loader.Image')
    @patch('os.path.exists')
    def test_load_data_empty_text(self, mock_exists, mock_image):
        mock_exists.return_value = True
        
        mock_image_instance = MagicMock()
        mock_image.open.return_value = mock_image_instance
        with patch('agent_assembly_line.data_loaders.ocr_loader.pytesseract') as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "   "
            
            loader = OCRLoader()
            documents = loader.load_data('/path/to/empty_image.png')
            
            self.assertEqual(len(documents), 0)

    @patch('os.path.exists')
    def test_load_data_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        
        with patch('agent_assembly_line.data_loaders.ocr_loader.pytesseract'):
            loader = OCRLoader()
            documents = loader.load_data('/nonexistent/image.png')
            
            self.assertEqual(len(documents), 0)

    @patch('agent_assembly_line.data_loaders.ocr_loader.Image')
    @patch('os.path.exists')
    def test_load_data_exception_handling(self, mock_exists, mock_image):
        mock_exists.return_value = True
        mock_image.open.side_effect = Exception("Failed to open image")
        
        with patch('agent_assembly_line.data_loaders.ocr_loader.pytesseract'):
            loader = OCRLoader()
            documents = loader.load_data('/path/to/corrupted_image.png')
            
            self.assertEqual(len(documents), 0)

    @patch('agent_assembly_line.data_loaders.ocr_loader.Image')
    @patch('os.path.exists')
    def test_load_data_with_whitespace_text(self, mock_exists, mock_image):
        mock_exists.return_value = True
        
        mock_image_instance = MagicMock()
        mock_image_instance.format = "JPEG"
        mock_image_instance.size = (1024, 768)
        mock_image.open.return_value = mock_image_instance
        with patch('agent_assembly_line.data_loaders.ocr_loader.pytesseract') as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "  \n  Text with whitespace  \n  "
            
            loader = OCRLoader()
            documents = loader.load_data('/path/to/image.jpg')
            
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0].page_content, "Text with whitespace")

if __name__ == '__main__':
    unittest.main()