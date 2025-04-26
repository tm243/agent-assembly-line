"""
Agent-Assembly-Line
"""

from agent_assembly_line.models.document import Document
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument
from readability.readability import REGEXES

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import re
from lxml.html import document_fromstring, fragment_fromstring

class CustomDocument(ReadabilityDocument):

    def top_canidates(self, candidates, top_n=5):
        if not candidates:
            return None
        sorted_candidates = sorted(
            candidates.values(), key=lambda x: x["content_score"], reverse=True
        )
        best_candidates = {}
        for candidate in sorted_candidates[:top_n]:
            elem = candidate["elem"]
            best_candidates[elem] = candidate
        return best_candidates


    def get_article(self, candidates, best_candidate, html_partial=False):
        """
        overwrite the get_article method from readability
        """

        top_candidates = self.top_canidates(candidates, top_n=5)
        sibling_score_threshold = max([10, best_candidate["content_score"] * 0.2])

        if html_partial:
            output = fragment_fromstring("<div/>")
        else:
            output = document_fromstring("<div/>")

        best_elem = best_candidate["elem"]

        # Traverse up 3 levels to get a parent
        parent = best_elem
        for level in range(1, 3):
            if parent is not None:
                parent = parent.getparent()
            else:
                break
        if parent is None:
            parent = best_elem

        self.remove_unwanted_nodes(parent, unwanted_substrings=["newsletter", "subscription", "video",  "opt-in", "video", "youtube", "image"])

        def process_element_recursively(element):
            append = False
            # the text gets chopped when a p has text and links, this way we combine it:
            txt = ''.join(element.itertext())
            elem_key = element  # HashableElement(element)

            if (
                elem_key in top_candidates
                and top_candidates[elem_key]["content_score"] >= sibling_score_threshold
            ):
                append = True

            if element.tag in ["p"]:
                link_density = self.get_link_density(element)
                node_content = txt or ""
                node_content = node_content.strip()
                node_length = len(node_content)

                if node_length > 80 and link_density < 0.25:
                    append = True
                elif (
                    node_length <= 80
                    and link_density == 0
                    and re.search(r"\.( |$)", node_content)
                    and node_length > 0
                ):
                    append = True
                else:
                    append = False

            else:
                append = False

            if append:
                if html_partial:
                    output.append(element)
                else:
                    output.getchildren()[0].getchildren()[0].append(element)

            for child in element:
                process_element_recursively(child)

        process_element_recursively(parent)

        return output

    def remove_unwanted_nodes(self, parent, unwanted_substrings=None):
        """
        Removes nodes with class names containing specific substrings from the branch underneath the parent.

        Args:
            parent (Element): The parent element whose children will be checked.
            unwanted_substrings (list): A list of substrings to check in class names. Defaults to None.
        """

        if unwanted_substrings is None:
            unwanted_substrings = ["newsletter", "opt-in", "video", "youtube"]

        for child in list(parent):  # Use list() to avoid issues while modifying the tree

            # check link density for short elements:
            link_density = self.get_link_density(parent)
            txt = ''.join(child.itertext())
            if len(txt) < 80 and link_density > 0.25:
                parent.remove(child)
                continue

            # Check if the child has a class attribute and matches any unwanted substring
            if "class" in child.attrib:
                child_classes = child.attrib["class"].split()
                if any(unwanted_substring in cls for cls in child_classes for unwanted_substring in unwanted_substrings):
                    parent.remove(child)
                    continue

            self.remove_unwanted_nodes(child, unwanted_substrings)

class WebLoader:
    """
    - Reader mode
    - News mode (list)
    """

    def __init__(self):
        options = Options()
        options.add_argument("--headless")  # comment out for debugging
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)

    def load_data(self, url, wait_time=10):
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.driver.implicitly_wait(wait_time)
            # to debug:
            # input("Press Enter to continue...")
        except Exception as e:
            print(f"Error while waiting for elements: {e}")
            return []

        readable_doc = CustomDocument(self.driver.page_source)
        main_content_html = readable_doc.summary(html_partial=False)

        # remove leading and trailing spaces:
        main_content_html = re.sub(r"^\s+", "", main_content_html, flags=re.MULTILINE)
        main_content_html = re.sub(r"\s+$", "", main_content_html, flags=re.MULTILINE)

        # remove unwanted elements and tags:
        main_content = BeautifulSoup(main_content_html, "html.parser").get_text(separator="\n",strip=True)
        title = readable_doc.short_title()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.plain_text = "\n".join(line.strip() for line in soup.get_text().splitlines() if line.strip())

        title_and_description = self.extract_title_and_description(soup)
        title_and_description += " " + url

        h_t_pairs = self.extract_headline_text_pairs(soup)
        self.h_t_pairs = h_t_pairs

        relevant_links = self.extract_relevant_links(soup, url)
        self.relevant_links = relevant_links

        self.header_text_pairs = "\n\n".join([f"{t[0]} {t[1]}" for t in self.h_t_pairs])

        # Combine content
        content = title_and_description + "\n\n" + main_content

        if not self.header_text_pairs:
            content += "\n\n" + self.plain_text

        return [
            Document(
                page_content=main_content,
                metadata={"source": "web", "url": url, "title": title},
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
