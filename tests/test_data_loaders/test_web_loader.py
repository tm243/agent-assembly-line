import unittest
from unittest.mock import patch, MagicMock
from src.data_loaders.web_loader import WebLoader
from src.models.document import Document

class TestWebLoader(unittest.TestCase):
    @patch('src.data_loaders.web_loader.webdriver.Chrome')
    @patch('src.data_loaders.web_loader.ChromeDriverManager')
    def test_load_data(self, mock_chrome_driver_manager, mock_chrome):
        # Mock the Chrome WebDriver
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><body><span class="temperature-plus">25°C</span></body></html>'
        
        # Create an instance of WebLoader and load data
        loader = WebLoader()
        documents = loader.load_data('http://example.com', wait_class_name='temperature-plus')
        
        # Assertions
        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('25°C', documents[0].page_content)
        self.assertEqual(documents[0].metadata['source'], 'web')
        self.assertEqual(documents[0].metadata['url'], 'http://example.com')

        loader.close()

if __name__ == '__main__':
    unittest.main()