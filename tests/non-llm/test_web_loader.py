"""
Agent-Assembly-Line
"""

import os
import aiounittest
from unittest.mock import patch, Mock
from agent_assembly_line.data_loaders.web_loader import WebLoader, WebLoaderMode
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


    # tests some real web pages stored in the test directory
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager.install')
    async def test_load_data_real(self, mock_install, mock_chrome):
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        loader = WebLoader()

        test_data = ["webpage_1", "webpage_2"]

        def test_webpage(webpage):
            html_relative_filepath = f"data/{webpage}.html"
            expected_relative_filepath = f"data/{webpage}_expected.txt"
            html_url = f"file://tests/{webpage}.html"

            file_path = os.path.join(os.path.dirname(__file__), html_relative_filepath)
            with open(file_path, 'r') as f:
                mock_driver.page_source = f.read()
            mock_install.return_value = '/path/to/chromedriver'

            documents = loader.load_data(html_url, WebLoaderMode.READER)

            mock_driver.get.assert_called_once_with(html_url)
            self.assertEqual(len(documents), 2)
            self.assertIsInstance(documents[0], Document)

            file_path = os.path.join(os.path.dirname(__file__), expected_relative_filepath)
            with open(file_path, 'r') as f:
                expected = f.read()

            self.assertEqual(expected, documents[0].page_content)
            self.assertIn('web', documents[0].metadata['source'])
            self.assertEqual(documents[0].metadata['url'], html_url)

            loader.close()
            mock_driver.quit.assert_called_once()

            mock_driver.get.reset_mock()
            mock_driver.quit.reset_mock()

        for webpage in test_data:
            test_webpage(webpage)

    # tests some real news pages stored in the test directory
    @patch('selenium.webdriver.Chrome')
    @patch('webdriver_manager.chrome.ChromeDriverManager.install')
    async def test_load_data_real_newsfeed(self, mock_install, mock_chrome):
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        loader = WebLoader()

        test_data = ["webpage_3"]

        def test_webpage(webpage):
            html_relative_filepath = f"data/{webpage}.html"
            expected_relative_filepath = f"data/{webpage}_expected.txt"
            html_url = f"file://tests/{webpage}.html"

            file_path = os.path.join(os.path.dirname(__file__), html_relative_filepath)
            with open(file_path, 'r') as f:
                mock_driver.page_source = f.read()
            mock_install.return_value = '/path/to/chromedriver'

            documents = loader.load_data(html_url, WebLoaderMode.FEED)

            mock_driver.get.assert_called_once_with(html_url)
            self.assertEqual(len(documents), 2)
            self.assertIsInstance(documents[0], Document)

            file_path = os.path.join(os.path.dirname(__file__), expected_relative_filepath)
            with open(file_path, 'r') as f:
                expected = f.read()
            self.maxDiff = None
            self.assertEqual(expected, documents[0].page_content)
            self.assertIn('web', documents[0].metadata['source'])
            self.assertEqual(documents[0].metadata['url'], html_url)

            loader.close()
            mock_driver.quit.assert_called_once()

            mock_driver.get.reset_mock()
            mock_driver.quit.reset_mock()

        for webpage in test_data:
            test_webpage(webpage)

if __name__ == '__main__':
    aiounittest.main()