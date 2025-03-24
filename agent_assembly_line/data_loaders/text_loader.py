"""
Agent-Assembly-Line
"""

from typing import List
from langchain_community.document_loaders import TextLoader as LangchainTextLoader
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document

class TextLoader(DataLoader):
    def load_data(self, file_path: str) -> List[Document]:
        try:
            loader = LangchainTextLoader(file_path)
            documents = loader.load()
            return [Document(page_content=doc.page_content, metadata={"source": "text", "file_path": file_path}) for doc in documents if doc.page_content.strip()]
        except Exception as e:
            print("Text loading failed:", e)

class InlineTextLoader(DataLoader):
    def load_data(self, content: str) -> List[Document]:
        try:
            return [Document(page_content=content, metadata={"source": "text", "type": "inline"})]
        except Exception as e:
            print("Text loading failed:", e)