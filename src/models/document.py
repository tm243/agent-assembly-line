"""
Agent-Assembly-Line
"""

from typing import Dict, Any

class Document:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata