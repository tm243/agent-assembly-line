"""
Agent-Assembly-Line
"""

from typing import List
import requests
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document

class RESTAPILoader(DataLoader):
    def load_data(self, url: str) -> List[Document]:
        try:
            # @todo: implement the logic to fetch data from the REST API
            response = requests.get(url)
            response.raise_for_status()
            content = response.content
            return [Document(page_content=str(content), metadata={"source": "rest_api", "url": url})]
        except Exception as e:
            print(f"Error fetching {url}, exception: {e}")
            return []