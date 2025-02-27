import unittest
from unittest.mock import patch, MagicMock
from src.data_loaders.rest_api_loader import RESTAPILoader
from src.models.document import Document

class TestRESTAPILoader(unittest.TestCase):
    @patch('src.data_loaders.rest_api_loader.requests.get')
    def test_load_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = '{"key": "value"}'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        loader = RESTAPILoader()
        documents = loader.load_data('http://example.com/api')

        mock_get.assert_called_once_with("http://example.com/api")

        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('{"key": "value"}', documents[0].page_content)
        self.assertEqual(documents[0].metadata['source'], 'rest_api')
        self.assertEqual(documents[0].metadata['url'], 'http://example.com/api')

if __name__ == '__main__':
    unittest.main()