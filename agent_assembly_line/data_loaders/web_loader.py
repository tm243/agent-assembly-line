"""
Agent-Assembly-Line
"""

from agent_assembly_line.models.document import Document
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument
from readability.readability import REGEXES
from enum import Enum, auto

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

class WebLoaderMode(Enum):
    """Mode for web content loading and parsing."""
    NORMAL = auto()  # Standard webpage parsing
    READER = auto()  # Reader mode for article content
    FEED = auto()    # Feed mode for websites with many article links

class WebLoader:
    """
    Web content loader with different parsing modes:
    - NORMAL: Standard web page parsing
    - READER: Reader mode for better article reading
    - FEED: News feed mode for sites with many article links
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

    def load_data(self, url, mode=WebLoaderMode.READER, wait_time=10):
        self.mode = mode
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

        if self.mode == WebLoaderMode.READER:
            return self._process_reader_mode(url)
        elif self.mode == WebLoaderMode.FEED:
            return self._process_feed_mode(url)
        else:  # NORMAL mode
            return self._process_normal_mode(url)

    def _process_normal_mode(self, url):
        """Process webpage in normal mode with balanced content extraction."""
        readable_doc = CustomDocument(self.driver.page_source)
        main_content_html = readable_doc.summary(html_partial=False)

        # remove leading and trailing spaces:
        main_content_html = re.sub(r"^\s+", "", main_content_html, flags=re.MULTILINE)
        main_content_html = re.sub(r"\s+$", "", main_content_html, flags=re.MULTILINE)

        # remove unwanted elements and tags:
        main_content = BeautifulSoup(main_content_html, "html.parser").get_text(separator="\n", strip=True)
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
                metadata={"source": "web", "url": url, "title": title, "mode": "normal"},
            ),
            Document(
                page_content="\n".join(self.relevant_links),
                metadata={"source": "web", "url": url, "type": "links", "mode": "normal"},
            )
        ]

    def _process_reader_mode(self, url):
        """Process webpage in reader mode, focusing on main article content."""
        readable_doc = CustomDocument(self.driver.page_source)
        main_content_html = readable_doc.summary(html_partial=False)

        # Remove leading spaces from each line in the HTML content
        main_content_html = re.sub(r"^\s+", "", main_content_html, flags=re.MULTILINE)
        # Remove trailing spaces from each line in the HTML content
        main_content_html = re.sub(r"\s+$", "", main_content_html, flags=re.MULTILINE)

        # More aggressive cleaning of non-content elements
        soup = BeautifulSoup(main_content_html, "html.parser")
        for element in soup.find_all(["aside", "nav", "footer", "script", "style", "iframe"]):
            element.decompose()

        main_content = soup.get_text(separator="\n", strip=True)
        title = readable_doc.short_title()

        relevant_links = self.extract_relevant_links(soup, url)
        self.relevant_links = relevant_links

        return [
            Document(
                page_content=main_content,
                metadata={"source": "web", "url": url, "title": title, "mode": "reader"},
            ),
            Document(
                page_content="\n".join(self.relevant_links),
                metadata={"source": "web", "url": url, "type": "links", "mode": "normal"},
            )
        ]

    def _find_articles_in_section(self, section):
        """
        Find articles in a given section of the webpage.

        Handles nested structures such as:
        - <section><article></article><article></article></section>
        - <section><a><div><ul><li><article></li><li><article></li></ul></div></a></section>
        """
        articles = []

        # First approach: find direct article elements (simplest structure)
        direct_articles = section.find_all("article", recursive=False)

        # Second approach: find nested articles at any level
        nested_articles = []
        if not direct_articles:
            nested_articles = section.find_all("article", recursive=True)

        # Third approach: handle the <section><a><div><ul><li> structure
        list_items = []
        if not direct_articles and not nested_articles:
            ul_elements = section.find_all("ul", recursive=True)
            for ul in ul_elements:
                list_items.extend(ul.find_all("li", recursive=False))

        elements_to_process = direct_articles or nested_articles or list_items

        if not elements_to_process: # fallback
            elements_to_process = section.find_all(
                ["div", "section", "a"],
                class_=lambda c: c and any(term in str(c).lower() for term in ["post", "article", "entry", "item", "card"])
            )

        for element in elements_to_process:
            headline = ""
            headline_elem = element.find(["h1", "h2", "h3", "h4"], recursive=True)
            if headline_elem:
                # we might have sub elements here in the h1 h2 h3 h4 elements, such as span, p or div:
                headline_elems = headline_elem.find(["span", "div", "p", "a"], recursive=True)
                for elem in headline_elems:
                    if elem.get_text(strip=False):
                        headline += elem.get_text(strip=False) + ".  "

            # If no headline found through headings, look for title attributes or strong text
            if not headline:
                title_elem = element.find(attrs={"title": True}, recursive=True)
                if title_elem:
                    headline = title_elem["title"]

            # If still no headline, try links with substantial text
            if not headline:
                link_elem = element.find("a", recursive=True)
                if link_elem and link_elem.get_text(strip=True):
                    link_text = link_elem.get_text(strip=True)
                    if len(link_text.split()) >= 3:  # Only use if it has enough words to be a title
                        headline = link_text

            link = ""
            link_elem = element.find("a", href=True, recursive=True)
            if link_elem and "href" in link_elem.attrs:
                link = self.get_full_url(link_elem["href"], self.base_url)

            summary = ""
            # Strategy 1: Look for paragraph elements
            summary_elem = element.find("p", recursive=True)
            if summary_elem:
                summary = summary_elem.get_text(strip=True)

            # Strategy 2: Look for specially marked content
            if not summary or len(summary.split()) < 5:
                summary_elem = element.find(
                    ["div", "span"],
                    class_=lambda c: c and any(term in str(c).lower() for term in
                                              ["excerpt", "summary", "desc", "teaser", "content"]),
                    recursive=True
                )
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)

            # Strategy 3: For very simple structures, use the main text of the article
            if not summary and element.name == "article":
                # Get all text but exclude the headline text
                all_text = element.get_text(strip=True)
                if headline and headline in all_text:
                    summary = all_text.replace(headline, "", 1).strip()

            # Filter out entries without sufficient content
            if headline and len(headline.split()) >= 3 and link:
                # Avoid duplicate content between headline and summary
                if summary and headline in summary:
                    summary = summary.replace(headline, "").strip()

            articles.append({
                "headline": headline,
                "link": link,
                "summary": summary
            })

        return articles

    def _extract_base_url(self, url):
        """ Extract the base URL from a given URL. """
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return base_url

    def _process_feed_mode(self, url):
        """Process webpage as a feed, extracting article links and summaries."""

        self.base_url = self._extract_base_url(url)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        title = soup.title.string if soup.title else "Unknown Feed"

        # Extract article links with context
        articles = []
        sections = soup.find_all(["section"],
                                        class_=lambda c: c and any(term in str(c).lower()
                                                                  for term in ["post", "article", "entry", "item", "grid"]))

        article_elements = []
        for section in sections:
            articles = self._find_articles_in_section(section) if sections else []
            article_elements.extend(articles)

        # Create formatted feed content
        feed_content = f"# {title}\n\n"
        for article in article_elements:
            feed_content += f"## {article['headline']}\n"
            if article['summary']:
                feed_content += f"{article['summary']}\n"
            feed_content += f"[Read more]({article['link']})\n\n"

        # Extract all links as separate document
        all_links = [a["href"] for a in soup.find_all("a", href=True)]
        relevant_links = [self.get_full_url(link, url) for link in all_links]

        return [
            Document(
                page_content=feed_content,
                metadata={"source": "web", "url": url, "title": title, "mode": "feed"},
            ),
            Document(
                page_content="\n".join(relevant_links),
                metadata={"source": "web", "url": url, "type": "links", "mode": "feed"},
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
