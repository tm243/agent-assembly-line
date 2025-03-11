"""
Agent-Assembly-Line
"""

import unittest
from unittest.mock import patch, MagicMock
from src.data_loaders.rss_feed_loader import RSSFeedLoader
from src.models.document import Document

class TestRSSFeedLoader(unittest.TestCase):
    @patch('feedparser.http.get')
    @patch('newspaper.Article')
    def test_load_data(self, mock_article, mock_http_get):

        xml = b'''<?xml version="1.0" encoding="UTF-8" ?>
            <rss version="2.0">
            <channel>
                <item>
                <title>Sample Article</title>
                <link>https://www.example.com</link>
                <description>Short description</description>
                </item>
            </channel>
            </rss>'''
        mock_http_get.return_value = xml

        # Create a mock article object for newspaper3k
        mock_article_instance = MagicMock()
        mock_article_instance.text = "Full article text"
        mock_article_instance.title = "Sample Article"
        mock_article.return_value = mock_article_instance

        loader = RSSFeedLoader()
        documents = loader.load_data('http://example.com/rss')

        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        self.assertIn('Sample Article', documents[0].page_content)
        self.assertEqual(documents[0].metadata['source'], 'rss')
        self.assertEqual(documents[0].metadata['url'], 'http://example.com/rss')

if __name__ == '__main__':
    unittest.main()