"""
Agent-Assembly-Line
"""

from typing import List, Dict

class DataLoader:
    def load_data(self, source: str) -> List[Dict[str, str]]:
        raise NotImplementedError("This method should be overridden by subclasses")