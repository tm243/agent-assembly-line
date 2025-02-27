from typing import List
from langchain_community.document_loaders import PyPDFLoader as LangchainPDFLoader
from .base_loader import DataLoader
from src.models.document import Document

class PDFLoader(DataLoader):
    def load_data(self, file_path: str) -> List[Document]:
        loader = LangchainPDFLoader(file_path)
        documents = loader.load()
        return [Document(page_content=doc.page_content, metadata={"source": "pdf", "file_path": file_path}) for doc in documents]