"""
Agent-Assembly-Line
"""

import aiounittest
from unittest.mock import patch, Mock
from agent_assembly_line.data_loaders.web_loader import WebLoader
from agent_assembly_line.models.document import Document

class TestWebLoader(aiounittest.AsyncTestCase):
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager.install')
    async def test_load_data(self, mock_install, mock_chrome):
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><body><span class="temperature-plus">25°C</span></body></html>'
        mock_install.return_value = '/path/to/chromedriver'

        loader = WebLoader()
        documents = loader.load_data('http://example.com/test.html')

        mock_driver.get.assert_called_once_with('http://example.com/test.html')
        self.assertEqual(len(documents), 2)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('25°C', documents[0].page_content)
        self.assertIn('web', documents[0].metadata['source'])
        self.assertEqual(documents[0].metadata['url'], 'http://example.com/test.html')

        loader.close()
        mock_driver.quit.assert_called_once()

if __name__ == '__main__':
    aiounittest.main()