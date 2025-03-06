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
        options.add_argument("--headless")  # comment out for debugging
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")

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

        relevant_links = self.extract_relevant_links(soup, url)
        self.relevant_links = relevant_links

        page_content = "\n".join(line.strip() for line in soup.get_text().splitlines() if line.strip())

        return [
            Document(
                page_content=page_content,
                metadata={"source": "web", "url": url},
            )
        ]

    def extract_relevant_links(self, soup, base_url):
        relevant_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = self.get_full_url(href, base_url)
            relevant_links.append(full_url)
        return relevant_links

    def get_full_url(self, href, base_url):
        if href.startswith("http"):
            return href
        else:
            return base_url + href

    def close(self):
        self.driver.quit()
