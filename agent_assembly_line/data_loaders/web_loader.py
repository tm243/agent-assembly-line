"""
Agent-Assembly-Line
"""

from agent_assembly_line.models.document import Document
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

        self.plain_text = "\n".join(line.strip() for line in soup.get_text().splitlines() if line.strip())

        title_and_description = self.extract_title_and_description(soup)
        title_and_description += " " + url

        h_t_pairs = self.extract_headline_text_pairs(soup)
        self.h_t_pairs = h_t_pairs

        relevant_links = self.extract_relevant_links(soup, url)
        self.relevant_links = relevant_links

        self.header_text_pairs = "\n\n".join([f"{t[0]} {t[1]}" for t in self.h_t_pairs])

        content = title_and_description + "\n\n" + self.header_text_pairs

        if not self.header_text_pairs:
            content += "\n\n" + self.plain_text

        return [
            Document(
                page_content=content,
                metadata={"source": "web", "url": url},
            ),
            Document(
                page_content="\n".join(self.relevant_links),
                metadata={"source": "web", "url": url, "type": "links"},
            )
        ]

    def extract_title_and_description(self, soup):
        result = ""
        if soup.title:
            result += soup.title.string
        description = soup.find("meta", attrs={"name": "description"})
        if description:
            result += description["content"]
        return result

    def extract_headline_text_pairs(self, soup):
        headline_text_pairs = []
        for headline in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "header"]):
            text = self.find_nearest_text(headline)
            headline_text = "** " + headline.get_text(". ", strip=True) + " **\n"
            if text:
                headline_text_pairs.append((headline_text, text))
        return headline_text_pairs

    def find_nearest_text(self, headline):
        for sibling in headline.find_next_siblings():
            if sibling.name in ["p", "div", "section"] and sibling.get_text(". ",strip=True):
                return sibling.get_text(strip=True)
        return ""

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
