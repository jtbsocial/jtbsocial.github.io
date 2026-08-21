import os
import json
import random
import logging
import requests
import xml.etree.ElementTree as ET
from config import config

logger = logging.getLogger(__name__)

class TopicHunter:
    def __init__(self):
        self.published_file = os.path.join(config.DATA_DIR, "published_topics.json")
        self.published_topics = self._load_published()

    def _load_published(self) -> set:
        if os.path.exists(self.published_file):
            try:
                with open(self.published_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("topics", []))
            except Exception as e:
                logger.warning(f"Could not load published topics: {e}")
        return set()

    def mark_published(self, topic: str):
        self.published_topics.add(topic)
        try:
            with open(self.published_file, "w", encoding="utf-8") as f:
                json.dump({"topics": list(self.published_topics)}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save published topic: {e}")

    def get_google_trends_topics(self) -> list:
        topics = []
        try:
            url = "https://trends.google.com/trending/rss?geo=US"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        topics.append(title.text.strip())
        except Exception as e:
            logger.warning(f"Google Trends RSS: {e}")
        return topics

    def get_evergreen_keywords(self, niche: str = None) -> list:
        seeds = [
            "Best Free AI Productivity Tools for Students and Professionals in 2026",
            "How to Use Open Source LLMs Locally for Coding and Research",
            "Top 7 Free Alternatives to Midjourney for Realistic AI Images",
            "How to Build Automated Python Workflows with Zero Coding Experience",
            "The Ultimate Guide to Starting a High-Traffic Blog with Zero Cost in 2026",
            "Top 5 Cloud Hosting Platforms That Are 100% Free Forever",
            "How to Protect Your Online Privacy and Passwords in 2026",
            "Best Lightweight Laptops for Programming, AI, and Multitasking",
            "Step-by-Step Guide to Monetizing Websites with Google AdSense and Affiliates",
            "How Agentic AI Will Transform Remote Jobs and Freelancing"
        ]
        return seeds

    def get_next_topic(self, custom_topic: str = None) -> str:
        if custom_topic:
            return custom_topic

        trends = self.get_google_trends_topics()
        for t in trends:
            candidate = f"Everything You Need to Know About {t}: In-Depth 2026 Guide"
            if candidate not in self.published_topics:
                return candidate

        seeds = self.get_evergreen_keywords()
        random.shuffle(seeds)
        for t in seeds:
            if t not in self.published_topics:
                return t

        return f"Comprehensive Guide to {config.BLOG_NICHE} Trends & Best Practices (2026)"

topic_hunter = TopicHunter()
