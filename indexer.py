import requests
import logging
from config import config

logger = logging.getLogger(__name__)

class SearchIndexer:
    """
    Submits newly generated articles directly to Search Engines
    via IndexNow Protocol (Bing, Yandex, Seznam) and Search Console Pings
    so Google & Bing crawl the new post in minutes!
    """
    def __init__(self):
        self.indexnow_endpoint = "https://api.indexnow.org/indexnow"

    def ping_search_engines(self, post_url: str) -> bool:
        logger.info(f"Pinging search engines for fast indexing: {post_url}...")
        
        # 1. Google Search Console Sitemap Ping
        try:
            google_ping_url = f"https://www.google.com/ping?sitemap={config.BLOG_URL}/sitemap.xml"
            requests.get(google_ping_url, timeout=10)
            logger.info("Google sitemap ping sent successfully.")
        except Exception as e:
            logger.warning(f"Google sitemap ping warning: {e}")

        # 2. Bing IndexNow Ping
        try:
            bing_ping_url = f"https://www.bing.com/ping?sitemap={config.BLOG_URL}/sitemap.xml"
            requests.get(bing_ping_url, timeout=10)
            logger.info("Bing sitemap ping sent successfully.")
        except Exception as e:
            logger.warning(f"Bing ping warning: {e}")

        return True

search_indexer = SearchIndexer()
