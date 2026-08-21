import os
import re
import json
import logging
from config import config

logger = logging.getLogger(__name__)

class InternalLinker:
    """
    Scans newly generated articles and automatically inserts internal hyperlinks
    to previously published articles to boost Google Page Authority & SEO rankings.
    """
    def __init__(self):
        self.data_file = os.path.join(config.DATA_DIR, "articles.json")

    def insert_internal_links(self, markdown_text: str, current_slug: str) -> str:
        if not os.path.exists(self.data_file):
            return markdown_text

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception:
            return markdown_text

        linked_text = markdown_text
        link_count = 0
        max_links = 3

        for art in articles:
            if art.get("slug") == current_slug:
                continue
            if link_count >= max_links:
                break

            title = art.get("title", "")
            slug = art.get("slug", "")
            url = f"{config.BLOG_URL}/posts/{slug}.html"
            
            # Extract key nouns/phrases from title
            keywords = [w for w in re.split(r'[\s:,\-]+', title) if len(w) > 4 and w.lower() not in ["guide", "depth", "about", "everything", "know"]]
            
            for kw in keywords[:2]:
                pattern = re.compile(rf'\b({re.escape(kw)})\b(?![^\[]*\])', re.IGNORECASE)
                if pattern.search(linked_text):
                    linked_text = pattern.sub(f'[\g<1>]({url})', linked_text, count=1)
                    link_count += 1
                    break

        return linked_text

internal_linker = InternalLinker()
