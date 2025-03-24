"""
Agent-Assembly-Line
"""

from typing import List
from langchain_community.document_loaders import PyPDFLoader as LangchainPDFLoader
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document

class PDFLoader(DataLoader):
    def load_data(self, file_path: str) -> List[Document]:
        try:
            loader = LangchainPDFLoader(file_path)
            documents = loader.load()
            # Filter out documents with empty page_content
            return [Document(page_content=doc.page_content, metadata={"source": "pdf", "file_path": file_path}) for doc in documents if doc.page_content.strip()]
        except Exception as e:
            print("PDF loading failed:", e)
            return []
