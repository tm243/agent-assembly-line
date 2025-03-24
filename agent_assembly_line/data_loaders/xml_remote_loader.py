"""
Agent-Assembly-Line
"""

from typing import List
from .base_loader import DataLoader
from agent_assembly_line.models.document import Document
from agent_assembly_line.middleware.base_dict_parser import BaseDictParser

import requests
import xmltodict

class XmlRemoteLoader(DataLoader):
    def load_data(self, url: str, params: dict, parser: BaseDictParser = BaseDictParser()) -> List[Document]:
        """
        Loads data from a remote XML source, parses it, and returns a list of Document objects.
        Args:
            url (str): The URL of the remote XML resource.
            params (dict): A dictionary of query parameters to include in the request.
            parser (BaseDictParser, optional): An instance of a parser to process the parsed XML data.
                Defaults to an instance of BaseDictParser.
        Returns:
            List[Document]: A list containing a single Document object if the data is successfully loaded
            and parsed, or an empty list if an error occurs or no valid data is available.
        Raises:
            Exception: If an unexpected error occurs during the request or parsing process.
        Notes:
            - If the HTTP response status code is 200, the XML content is parsed.
            - If the status code is 400, an error message is printed.
            - For other status codes, the response status code is logged.
            - If parsing fails or no valid data is available, an empty list is returned.
        """

        try:
            parsed_dict = None
            response = requests.get(url, params=params)
            if response.status_code == 200:
                parsed_dict = xmltodict.parse(response.content)
            elif response.status_code == 400:
                print(f"Error 400: {response.text}")
            else:
                print(f"Response status code is {response.status_code}")

            if parsed_dict is not None:
                page_content = parser.parse(parsed_dict)
                return [Document(page_content=page_content, metadata={"source": "xml", "url": url})]
            else:
                print("No valid data to create Document.")
                return []
        except Exception as e:
            print("XML Remote loading failed:", e)
            return []



