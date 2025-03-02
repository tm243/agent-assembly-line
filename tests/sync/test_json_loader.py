import unittest
from unittest.mock import patch, Mock
from src.data_loaders.json_loader import JSONLoader
from src.models.document import Document

class TestJSONLoader(unittest.TestCase):
    @patch('requests.get')
    def test_load_data(self, mock_get):
        mock_response = Mock()
        mock_response.content = b'[{"message": "Mocked response"}]'
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        loader = JSONLoader()
        documents = loader.load_data('http://example.com/test.json')
        
        mock_get.assert_called_once_with("http://example.com/test.json")

        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('{"message": "Mocked response"}', documents[0].page_content)
        # @todo test for the url
        self.assertIn('json', documents[0].metadata['source'])
        self.assertEqual(documents[0].metadata['seq_num'], 1)
        # self.assertEqual(documents[0].metadata['url'], 'http://example.com/test.json')

if __name__ == '__main__':
    unittest.main()