"""
Agent Assembly Line
"""

class DataLoadError(Exception):
    """Exception raised for errors in the data loading process."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EmptyDataError(Exception):
    """Exception raised when no data is loaded from the file."""
    def __init__(self, filepath: str):
        self.message = f"No text loaded, the data source doesn't seem to contain any text."
        super().__init__(self.message)