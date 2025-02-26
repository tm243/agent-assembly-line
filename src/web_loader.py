from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from langchain_core.documents import Document

class WebLoader:
    def __init__(self):
        # Set up Selenium WebDriver
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no browser window)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)

    def load_page(self, url, wait_class_name):
        # Open the webpage
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, wait_class_name))
            )
        except Exception as e:
            print(f"Elements did not load in time: {e}")
            return None

        # Extract the page source and parse with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        page_content = soup.get_text()
        return Document(
            page_content=page_content,
            metadata={"source": "web", "url": url}
        )

    def close(self):
        # Close the Selenium browser
        self.driver.quit()

# # Define the target weather URL
# url = "https://en.ilmatieteenlaitos.fi/weather/helsinki"

# # Create an instance of WebLoader
# web_loader = WebLoader()

# # Load the page and get the soup
# soup = web_loader.load_page(url, "temperature-plus")
# if soup:
#     print(soup.get_text())

# # Close the Selenium browser
# web_loader.close()
