"""
Agent-Assembly-Line
"""

import unittest
from unittest.mock import patch, MagicMock
from agent_assembly_line.data_loaders.pdf_loader import PDFLoader
from agent_assembly_line.models.document import Document

class TestPDFLoader(unittest.TestCase):
    @patch('agent_assembly_line.data_loaders.pdf_loader.LangchainPDFLoader')
    def test_load_data(self, mock_pdf_loader):
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [Document(page_content='PDF content', metadata={})]
        mock_pdf_loader.return_value = mock_loader_instance
        
        loader = PDFLoader()
        documents = loader.load_data('/path/to/pdf/file.pdf')
        
        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('PDF content', documents[0].page_content)
        self.assertEqual(documents[0].metadata['source'], 'pdf')
        self.assertEqual(documents[0].metadata['file_path'], '/path/to/pdf/file.pdf')

if __name__ == '__main__':
    unittest.main()