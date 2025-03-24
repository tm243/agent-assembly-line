"""
Agent-Assembly-Line
"""

import tempfile
import requests
from typing import List
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document
from langchain_community.document_loaders import JSONLoader as LangchainJSONLoader

class JSONLoader(DataLoader):
    # @todo: load files or urls, or rename to WebJSONLoader
    def load_data(self, url: str) -> List[Document]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_content = response.content.decode("utf-8")

            with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp_file:
                temp_file.write(json_content)
                temp_file_path = temp_file.name

            loader = LangchainJSONLoader(temp_file_path, jq_schema=".[0]", text_content = False)
            fdata = loader.load()

            documents = [Document(page_content=str(doc.page_content), metadata=doc.metadata) for doc in fdata]
            return documents
        except Exception as e:
            print(f"Error fetching {url}, exception: {e}")
            return []