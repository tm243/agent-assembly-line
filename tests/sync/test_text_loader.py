import unittest
from unittest.mock import patch, MagicMock
from src.data_loaders.text_loader import TextLoader
from src.models.document import Document

class TestTextLoader(unittest.TestCase):
    @patch('src.data_loaders.text_loader.LangchainTextLoader')
    def test_load_data(self, mock_text_loader):
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [Document(page_content='Test content', metadata={})]
        mock_text_loader.return_value = mock_loader_instance
        
        loader = TextLoader()
        documents = loader.load_data('/path/to/text/file.txt')
        
        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('Test content', documents[0].page_content)
        self.assertEqual(documents[0].metadata['source'], 'text')
        self.assertEqual(documents[0].metadata['file_path'], '/path/to/text/file.txt')

if __name__ == '__main__':
    unittest.main()