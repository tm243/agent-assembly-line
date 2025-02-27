import requests
from .base_loader import DataLoader
from .web_loader import WebLoader
from .rss_feed_loader import RSSFeedLoader
from .json_loader import JSONLoader
from .text_loader import TextLoader
from .pdf_loader import PDFLoader
from .rest_api_loader import RESTAPILoader

class DataLoaderFactory:
    @staticmethod
    def get_loader(source_type: str) -> DataLoader:
        if source_type == "web":
            return WebLoader()
        elif source_type == "rss":
            return RSSFeedLoader()
        elif source_type == "json":
            return JSONLoader()
        elif source_type == "text":
            return TextLoader()
        elif source_type == "pdf":
            return PDFLoader()
        elif source_type == "rest_api":
            return RESTAPILoader()
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    @staticmethod
    def guess_source_type(config) -> tuple[str, str]:
        if config.doc:
            if config.doc.endswith(".pdf"):
                return 'pdf', config.doc
            elif config.doc.endswith(".txt"):
                return 'text', config.doc
            # @todo add json file loader
        try:
            response = requests.head(config.url)
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type:
                return 'json', config.url
            elif 'application/rss+xml' in content_type or 'text/xml' in content_type:
                return 'rss', config.url
            elif 'text/html' in content_type:
                return 'web', config.url
            elif 'application/pdf' in content_type:
                return 'pdf', config.url
            elif 'text/plain' in content_type:
                return 'text', config.url
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
        except Exception as e:
            print(f"Error guessing source type for {config.url}, exception: {e}")
            raise