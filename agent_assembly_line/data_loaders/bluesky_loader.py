"""
Agent-Assembly-Line
"""

from typing import List
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document
from atproto import Client

class BlueskyLoader(DataLoader):
    """
    Loader for Bluesky social media feeds.
    """
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        try:
            self.client = Client()
            self.client.login(self.username, self.password)
        except Exception as e:
            print("Login failed:", e)
            self.client = None
            raise ValueError("Bluesky client not initialized. Check your credentials.")

    def load_data(self, feed: str, limit: int = 50) -> List[Document]:
        try:
            # posts_with_replies, posts_no_replies, include_pins
            feed_data = self.client.app.bsky.feed.get_author_feed(params={"actor": feed, "limit": limit})

            if not hasattr(feed_data, "feed") or not feed_data.feed:
                print(f"No feed data found for feed '{feed}' with limit {limit}.")
                return []

            documents = []
            for post in feed_data.feed:
                post_data = post.post # type PostView
                record = post_data.record
                url, title, description, thumb, text = "", "", "", "", ""
                if hasattr(record, "embed") and hasattr(record.embed, "external"):
                    url = record.embed.external['uri']
                    description = record.embed.external["description"]
                    title = record.embed.external["title"]
                    thumb = record.embed.external["thumb"]

                if hasattr(record, "text"):
                    text = record.text
                else:
                    text = description

                documents.append(
                    Document(
                        page_content = text,
                        metadata={
                            "source": "bluesky",
                            "author": post_data.author.handle,
                            "post_id": post_data.uri,
                            "timestamp": record.created_at,
                            "external_url": url,
                            "external_title": title,
                            "external_description": description,
                            "external_thumb": thumb,
                            "like_count": post_data.like_count,
                            "reply_count": post_data.reply_count,
                            "quote_count": post_data.quote_count,
                        },
                    )
                )

            return documents
        except Exception as e:
            print(f"Failed to load data for feed '{feed}' with limit {limit}: {e}")
            return []
