from src.models.document import Document
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

class WebLoader:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)

    def load_data(self, url, wait_time=10):
        self.driver.get(url)

        try:
            self.driver.implicitly_wait(wait_time)
        except Exception as e:
            print(f"Error while waiting for elements: {e}")
            return []

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        page_content = soup.get_text()
        return [Document(
            page_content=page_content,
            metadata={"source": "web", "url": url}
        )]

    def close(self):
        self.driver.quit()
