"""
Agent-Assembly-Line
"""

import re
from typing import List
import requests
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document

class WordPressLoader(DataLoader):
    def load_data(self, source: str, max: int = 100) -> List[Document]:

        if not isinstance(source, str):
            raise TypeError(f"Expected string, got {type(source)}")
        if not source:
            raise ValueError("Source URL cannot be empty")

        source = source.rstrip("/")
        if "://" in source:
            if not source.startswith(("http://", "https://")):
                raise ValueError(f"Unsupported URL scheme: {source}")
                return
        else:
            source = "https://" + source

        source = f"{source}/wp-json/wp/v2/posts"

        try:
            response = requests.get(source, params={"per_page": max})
            response.raise_for_status()
            posts = response.json()

            documents = []
            for post in posts:
                plain_text_content = re.sub(r"<[^>]+>", "", post["content"]["rendered"])

                document = Document(
                    metadata={
                        "id": post["id"],
                        "title": post["title"]["rendered"],
                        "source": "wordpress",
                        "url": f"{source}"
                    },
                    page_content=plain_text_content
                )
                documents.append(document)

            return documents

        except requests.RequestException as e:
            print(f"Error fetching posts from {source}: {e}")
            return []
        except Exception as e:
            return []