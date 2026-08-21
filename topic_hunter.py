"""
Topic Hunter — Discovers trending TECH topics and high-CPC seed keywords.
STRICTLY filters for technology/AI niche to maintain topical authority.
"""
import os
import json
import random
import logging
import requests
import xml.etree.ElementTree as ET
from config import config

logger = logging.getLogger(__name__)

# Tech-related keywords that MUST appear in a trending topic for it to qualify
TECH_FILTER_KEYWORDS = {
    'ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural',
    'gpt', 'llm', 'chatgpt', 'gemini', 'claude', 'copilot', 'openai', 'google',
    'apple', 'microsoft', 'nvidia', 'amd', 'intel', 'samsung', 'meta', 'amazon',
    'robot', 'quantum', 'blockchain', 'crypto', 'bitcoin', 'ethereum',
    'coding', 'programming', 'python', 'javascript', 'developer', 'software',
    'app', 'startup', 'saas', 'cloud', 'cybersecurity', 'hack', 'data',
    'iphone', 'android', 'pixel', 'laptop', 'gpu', 'chip', 'processor',
    'spacex', 'tesla', 'neuralink', 'automation', 'tech', 'gadget',
    'vr', 'ar', 'headset', 'vision pro', 'wearable', 'smartwatch',
    'linux', 'windows', 'macos', 'open source', 'github', 'api',
    'model', 'training', 'inference', 'benchmark', 'performance',
    'drone', 'ev', 'electric vehicle', 'self-driving', 'autonomous',
    '5g', '6g', 'satellite', 'internet', 'wifi', 'networking',
    'streaming', 'gaming', 'console', 'playstation', 'xbox', 'steam',
}

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

    def _is_tech_topic(self, topic: str) -> bool:
        """Check if a trending topic is related to technology/AI."""
        topic_lower = topic.lower()
        return any(kw in topic_lower for kw in TECH_FILTER_KEYWORDS)

    def get_google_trends_topics(self) -> list:
        """Fetch trending topics from Google Trends, STRICTLY filtered for tech niche."""
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
                        raw_topic = title.text.strip()
                        if self._is_tech_topic(raw_topic):
                            topics.append(raw_topic)
                            logger.info(f"✅ Tech trend accepted: {raw_topic}")
                        else:
                            logger.debug(f"❌ Non-tech trend filtered: {raw_topic}")
        except Exception as e:
            logger.warning(f"Google Trends RSS: {e}")
        return topics

    def get_evergreen_keywords(self) -> list:
        """High-CPC, high-intent evergreen tech/AI seed topics."""
        seeds = [
            "Best Free AI Productivity Tools for Students and Professionals in 2026",
            "How to Use Open Source LLMs Locally for Coding and Research",
            "Top 7 Free Alternatives to Midjourney for Realistic AI Images",
            "How to Build Automated Python Workflows with Zero Coding Experience",
            "The Ultimate Guide to Starting a High-Traffic Blog with Zero Cost in 2026",
            "Top 5 Cloud Hosting Platforms That Are 100 Percent Free Forever",
            "How to Protect Your Online Privacy and Passwords in 2026",
            "Best Lightweight Laptops for Programming AI and Multitasking",
            "Step-by-Step Guide to Monetizing Websites with Google AdSense and Affiliates",
            "How Agentic AI Will Transform Remote Jobs and Freelancing",
            "Top 10 VS Code Extensions Every Developer Needs in 2026",
            "Complete Guide to Self-Hosting AI Models on a Budget PC",
            "Best Free Cybersecurity Tools to Protect Your Data Online",
            "How to Create Professional Websites Using Only Free AI Tools",
            "Top 8 Free AI Video Generators That Rival Sora and Runway",
            "Best Free AI Writing Tools That Replace ChatGPT Plus in 2026",
            "How to Automate Social Media Marketing Using Free AI Bots",
            "Top 5 Free Cloud GPU Platforms for AI Model Training",
            "Complete Beginners Guide to Prompt Engineering in 2026",
            "How to Build and Deploy a Full Stack App Using Only AI Assistants"
        ]
        return seeds

    def get_next_topic(self, custom_topic: str = None) -> str:
        if custom_topic:
            return custom_topic

        # First try tech-filtered Google Trends
        trends = self.get_google_trends_topics()
        for t in trends:
            candidate = f"Complete 2026 Guide: {t} — Everything You Need to Know"
            if candidate not in self.published_topics:
                logger.info(f"📌 Selected tech trending topic: {candidate}")
                return candidate

        # Fallback to curated evergreen tech seeds
        seeds = self.get_evergreen_keywords()
        random.shuffle(seeds)
        for t in seeds:
            if t not in self.published_topics:
                logger.info(f"📌 Selected evergreen tech topic: {t}")
                return t

        return f"Comprehensive Guide to {config.BLOG_NICHE} Trends & Best Practices (2026)"

topic_hunter = TopicHunter()
