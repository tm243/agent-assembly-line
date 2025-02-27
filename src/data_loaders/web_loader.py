from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from .base_loader import DataLoader
from src.models.document import Document

class WebLoader(DataLoader):
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)

    def load_data(self, url: str) -> List[Document]:
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "temperature-plus"))
            )
        except Exception as e:
            print(f"Elements did not load in time: {e}")
            return []

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        page_content = soup.get_text()
        self.driver.quit()
        return [Document(page_content=page_content, metadata={"source": "web", "url": url})]