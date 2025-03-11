"""
Agent-Assembly-Line
"""

from langchain_core.text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)