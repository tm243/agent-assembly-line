"""
Agent-Assembly-Line
"""

import unittest
from unittest.mock import patch, Mock
from agent_assembly_line.data_loaders.wordpress_loader import WordPressLoader
from agent_assembly_line.models.document import Document
from requests.exceptions import RequestException

class TestWordPressLoader(unittest.TestCase):

    def setUp(self):
        self.wordpress_loader = WordPressLoader()

    @patch("agent_assembly_line.data_loaders.wordpress_loader.requests.get")
    def test_load_data_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": {"rendered": "Test Post"},
                "content": {"rendered": "This is a test post content."}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        source = "example.com"
        documents = self.wordpress_loader.load_data(source)

        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertEqual(documents[0].metadata["id"], 1)
        self.assertEqual(documents[0].metadata["title"], "Test Post")
        self.assertEqual(documents[0].metadata["source"], "wordpress")
        self.assertEqual(documents[0].metadata["url"], "https://example.com/wp-json/wp/v2/posts")
        self.assertEqual(documents[0].page_content, "This is a test post content.")

    @patch("agent_assembly_line.data_loaders.wordpress_loader.requests.get")
    @patch("builtins.print")
    def test_load_data_failure(self, mock_print, mock_get):
        mock_get.side_effect = RequestException("Network error")

        source = "https://example.com"
        documents = self.wordpress_loader.load_data(source)

        self.assertEqual(documents, [])
        mock_print.assert_called_once_with("Error fetching posts from https://example.com/wp-json/wp/v2/posts: Network error")

    @patch("agent_assembly_line.data_loaders.wordpress_loader.requests.get")
    def test_html_tags_removed_from_page_content(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": {"rendered": "Test Post"},
                "content": {"rendered": "<p>This is a <strong>test</strong> post content.</p>"}
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        source = "example.com"
        documents = self.wordpress_loader.load_data(source)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content, "This is a test post content.")

    @patch("agent_assembly_line.data_loaders.wordpress_loader.requests.get")
    def test_url_handling(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        source_without_https = "example.com"
        self.wordpress_loader.load_data(source_without_https)
        mock_get.assert_called_with("https://example.com/wp-json/wp/v2/posts", params={"per_page": 100})

        source_with_https = "https://example.com"
        self.wordpress_loader.load_data(source_with_https)
        mock_get.assert_called_with("https://example.com/wp-json/wp/v2/posts", params={"per_page": 100})

        source_messed_up = "example.com/"
        self.wordpress_loader.load_data(source_messed_up)
        mock_get.assert_called_with("https://example.com/wp-json/wp/v2/posts", params={"per_page": 100})
        self.assertTrue(mock_get.call_args[0][0].endswith("wp-json/wp/v2/posts"))
        self.assertTrue(mock_get.call_args[0][0].startswith("https://"))
        self.assertIn("example.com", mock_get.call_args[0][0])

        mock_get.reset_mock()
        bad_url = "gopher://example.com"
        with self.assertRaises(ValueError):
            self.wordpress_loader.load_data(bad_url)
        mock_get.assert_not_called()

    def test_empty_url(self):
        with self.assertRaises(ValueError):
            self.wordpress_loader.load_data("")

    def test_non_string_url(self):
        with self.assertRaises(TypeError):
            self.wordpress_loader.load_data(None)
        with self.assertRaises(TypeError):
            self.wordpress_loader.load_data(123)

if __name__ == "__main__":
    unittest.main()