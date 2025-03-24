"""
Agent-Assembly-Line
"""

from typing import Dict, List
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document
from langchain_community.document_loaders import RSSFeedLoader as LangchainRSSFeedLoader

class RSSFeedLoader(DataLoader):
    def load_data(self, url: str) -> List[Dict[str, str]]:
        try:
            loader = LangchainRSSFeedLoader(urls=[url])
            fdata = loader.load()
            return [Document(page_content=str(fdata[0]), metadata={"source": "rss", "url": url})]
        
        except Exception as e:
            print(f"Error fetching {url}, exception: {e}")
            return []