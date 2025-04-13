"""
Agent Assembly Line
"""

import unittest
from unittest.mock import MagicMock, patch
from agent_assembly_line.data_loaders.bluesky_loader import BlueskyLoader
from agent_assembly_line.models.document import Document

class TestBlueskyLoader(unittest.TestCase):
    @patch("agent_assembly_line.data_loaders.bluesky_loader.Client")
    def test_load_data_success(self, MockClient):
        # Mock the Client and its methods
        mock_client_instance = MockClient.return_value
        mock_client_instance.app.bsky.feed.get_author_feed.return_value = MagicMock(
            feed=[
                MagicMock(
                    post=MagicMock(
                        record=MagicMock(
                            created_at="2025-04-13T12:00:00Z",
                            text="Test post content",
                            embed=MagicMock(
                                external={
                                    "uri": "https://example.com",
                                    "description": "Test description",
                                    "title": "Test title",
                                    "thumb": "https://example.com/thumb.jpg",
                                }
                            ),
                        ),
                        author=MagicMock(handle="test_author"),
                        uri="test_post_id",
                        like_count=10,
                        reply_count=5,
                        quote_count=2,
                    )
                )
            ]
        )

        loader = BlueskyLoader(username="test_user", password="test_pass")
        loader.client = mock_client_instance

        documents = loader.load_data(feed="test_feed", limit=1)

        self.assertEqual(len(documents), 1)
        document = documents[0]
        self.assertIsInstance(document, Document)
        self.assertEqual(document.page_content, "Test post content")
        self.assertEqual(document.metadata["author"], "test_author")
        self.assertEqual(document.metadata["post_id"], "test_post_id")
        self.assertEqual(document.metadata["timestamp"], "2025-04-13T12:00:00Z")
        self.assertEqual(document.metadata["external_url"], "https://example.com")
        self.assertEqual(document.metadata["external_title"], "Test title")
        self.assertEqual(document.metadata["external_description"], "Test description")
        self.assertEqual(document.metadata["external_thumb"], "https://example.com/thumb.jpg")
        self.assertEqual(document.metadata["like_count"], 10)
        self.assertEqual(document.metadata["reply_count"], 5)
        self.assertEqual(document.metadata["quote_count"], 2)

    @patch("agent_assembly_line.data_loaders.bluesky_loader.Client")
    @patch("builtins.print")
    def test_load_data_failure(self, mock_print, MockClient):

        mock_client_instance = MockClient.return_value
        mock_client_instance.app.bsky.feed.get_author_feed.side_effect = Exception("API error")

        loader = BlueskyLoader(username="test_user", password="test_pass")
        loader.client = mock_client_instance

        documents = loader.load_data(feed="test_feed", limit=1)

        mock_print.assert_called_with("Failed to load data for feed 'test_feed' with limit 1: API error")

        self.assertEqual(documents, [])

if __name__ == "__main__":
    unittest.main()