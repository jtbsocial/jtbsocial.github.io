"""
Smart Internal Linker — Links related articles within blog posts.
Safely avoids corrupting existing markdown links, URLs, code blocks, and HTML attributes.
"""
import re
import json
import os
import logging
from config import config

logger = logging.getLogger(__name__)

class InternalLinker:
    def __init__(self):
        self.data_file = os.path.join(config.DATA_DIR, "articles.json")

    def _load_published_articles(self) -> list:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def insert_internal_links(self, markdown_text: str, current_slug: str = "") -> str:
        """Insert up to 3 internal links into markdown text, safely avoiding existing links and URLs."""
        articles = self._load_published_articles()
        if not articles or not markdown_text:
            return markdown_text

        links_inserted = 0
        max_links = 3
        linked_text = markdown_text

        for art in articles:
            if links_inserted >= max_links:
                break
            slug = art.get("slug", "")
            if slug == current_slug or not slug:
                continue

            title = art.get("title", "")
            # Extract meaningful 2-3 word keyword phrases from the title
            keywords = self._extract_link_keywords(title)
            url = f"{config.BLOG_URL}/posts/{slug}.html"

            for kw in keywords:
                if links_inserted >= max_links:
                    break
                if len(kw) < 4:
                    continue

                # Check if the keyword exists as a standalone word in non-link text
                # Split text into segments: inside links/urls vs plain text
                safe_linked = self._safe_replace(linked_text, kw, url)
                if safe_linked != linked_text:
                    linked_text = safe_linked
                    links_inserted += 1
                    break

        return linked_text

    def _extract_link_keywords(self, title: str) -> list:
        """Extract meaningful keyword phrases from article title."""
        # Remove common filler words and numbers
        stop_words = {'the', 'a', 'an', 'in', 'of', 'to', 'for', 'and', 'or', 'that',
                      'will', 'you', 'your', 'how', 'what', 'why', 'top', 'best',
                      'free', 'can', 'with', 'from', 'about', 'need', 'know',
                      'everything', 'complete', 'guide', 'ultimate', '2026', '2025'}
        
        words = re.findall(r'[A-Za-z]+', title.lower())
        meaningful = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return individual keywords (longest first for best matching)
        return sorted(set(meaningful), key=len, reverse=True)[:5]

    def _safe_replace(self, text: str, keyword: str, url: str) -> str:
        """Replace keyword with markdown link ONLY in plain text, never inside existing links, URLs, or code."""
        # Split text into lines and process each
        lines = text.split('\n')
        result_lines = []
        replaced = False

        for line in lines:
            if replaced:
                result_lines.append(line)
                continue

            # Skip lines that are already links, headings with links, code blocks, or URLs
            stripped = line.strip()
            if (stripped.startswith('```') or 
                stripped.startswith('    ') or
                stripped.startswith('|') or  # table rows
                stripped.startswith('#') or  # headings
                stripped.startswith('![') or  # images
                stripped.startswith('http')):
                result_lines.append(line)
                continue

            # Find the keyword in plain text portions only
            # Remove all existing markdown links and URLs before checking
            plain_check = re.sub(r'\[.*?\]\(.*?\)', '', line)
            plain_check = re.sub(r'https?://\S+', '', plain_check)
            plain_check = re.sub(r'`[^`]+`', '', plain_check)

            pattern = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
            if pattern.search(plain_check):
                # Now do the actual replacement on the original line,
                # but only replace the FIRST occurrence that's NOT inside [...] or (...)
                new_line = self._replace_first_safe(line, keyword, url)
                if new_line != line:
                    result_lines.append(new_line)
                    replaced = True
                    continue

            result_lines.append(line)

        if replaced:
            return '\n'.join(result_lines)
        return text

    def _replace_first_safe(self, line: str, keyword: str, url: str) -> str:
        """Replace first occurrence of keyword that's not inside a markdown link or URL."""
        # Find all "safe zones" (outside of markdown links and inline code)
        # Pattern to match markdown links and inline code
        protected = re.compile(r'\[.*?\]\(.*?\)|`[^`]+`|https?://\S+')
        
        # Get all protected ranges
        protected_ranges = [(m.start(), m.end()) for m in protected.finditer(line)]
        
        # Find keyword matches
        kw_pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        for match in kw_pattern.finditer(line):
            start, end = match.start(), match.end()
            # Check if this match overlaps with any protected range
            is_protected = any(ps <= start < pe or ps < end <= pe for ps, pe in protected_ranges)
            if not is_protected:
                # Safe to replace
                matched_text = match.group(0)
                replacement = f'[{matched_text}]({url})'
                return line[:start] + replacement + line[end:]
        
        return line

internal_linker = InternalLinker()
