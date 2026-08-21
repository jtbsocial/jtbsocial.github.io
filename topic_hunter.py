"""
Advanced Multi-Category Trending Hunter
Captures real-time viral traffic across:
1. 🤖 AI & Future Software Launches
2. 🎮 Trending Video Games & Esports
3. 📱 Smartphone, Laptop & Hardware Gadgets
4. 🎬 Sci-Fi, Streaming & Tech-Entertainment
5. ⚡ Viral Productivity & Internet Trends
"""
import os
import json
import random
import logging
import requests
import xml.etree.ElementTree as ET
from config import config

logger = logging.getLogger(__name__)

# Category mapping keywords for automatic tagging
CATEGORY_RULES = {
    "Gaming & Esports": [
        "game", "gaming", "ps5", "xbox", "gta", "playstation", "nintendo", "steam",
        "esports", "fortnite", "roblox", "minecraft", "rpg", "fps", "unreal engine"
    ],
    "Gadgets & Hardware": [
        "iphone", "android", "samsung", "pixel", "laptop", "gpu", "nvidia", "rtx",
        "amd", "intel", "smartwatch", "vision pro", "vr", "headset", "drone", "camera"
    ],
    "Entertainment & Sci-Fi": [
        "movie", "film", "trailer", "netflix", "marvel", "disney", "series",
        "streaming", "cinema", "box office", "anime", "actor", "hollywood"
    ],
    "AI & Breakthroughs": [
        "ai", "chatgpt", "gemini", "claude", "openai", "copilot", "llm",
        "deep learning", "quantum", "robot", "tesla optimus", "neuralink", "automation"
    ]
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

    def detect_category(self, topic: str) -> str:
        t_low = topic.lower()
        for cat, keywords in CATEGORY_RULES.items():
            if any(k in t_low for k in keywords):
                return cat
        return "Tech Trends"

    def get_google_trends_topics(self) -> list:
        """Fetch live high-velocity search trends from Google Trends."""
        topics = []
        try:
            url = "https://trends.google.com/trending/rss?geo=US"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item"):
                    title = item.find("title")
                    if title is not None and title.text:
                        raw = title.text.strip()
                        topics.append(raw)
        except Exception as e:
            logger.warning(f"Google Trends fetch: {e}")
        return topics

    def get_viral_seed_catalog(self) -> list:
        """High-velocity viral seeds across Games, Movies, AI, and Gadgets."""
        return [
            # 🎮 Gaming Hits
            "GTA 6 Official Release Date, Map Leaks, and Gameplay Mechanics: Complete 2026 Breakdown",
            "Top 10 Most Anticipated Unreal Engine 5 Games Launching in 2026",
            "PS5 Pro vs High-End Gaming PC: Which One Should You Buy in 2026?",
            "The Best Free Open-World Games on Steam That Everyone Is Playing Right Now",
            "Steam Deck 2 Rumors, Hardware Specs, and Expected Price: What We Know",

            # 🤖 AI & Software Breakthroughs
            "OpenAI GPT-5 and Gemini 2.0 Ultra: The Next Giant Leap in AI Reasoning",
            "Top 10 Secret AI Websites That Feel Illegal to Know in 2026",
            "How to Build Autonomous AI Agents for Free Without Writing Code",
            "Best Free AI Video Generators That Rival Hollywood CGI in 2026",
            "Apple Intelligence 2.0 Features: Everything New Coming to Your iPhone",

            # 📱 Hardware & Next-Gen Gadgets
            "iPhone 17 Pro Max Leaks: Slim Design, 2nm Chip, and Under-Display Cameras",
            "Top 5 Budget Gaming Laptops Under 1000 Dollars That Crush Every 2026 Game",
            "Nvidia RTX 5090 vs RTX 4090: Massive Performance Benchmarks Breakdown",
            "Tesla Optimus Gen 3: How Humanoid Robots Are Entering Everyday Homes",
            "The Best Lightweight Ultrabooks for Students and Programmers in 2026",

            # 🎬 Sci-Fi & Pop Tech Entertainment
            "Top 10 Must-Watch Sci-Fi Movies and Series Coming to Netflix and Max in 2026",
            "How AI CGI and Deepfakes Are Quietly Revolutionizing Hollywood Movie Studios",
            "Avatar 3 and Beyond: The Groundbreaking Visual Tech Powering the Sequel"
        ]

    def get_next_topic(self, custom_topic: str = None) -> str:
        if custom_topic:
            return custom_topic

        # 1. Check Google Trends first
        trends = self.get_google_trends_topics()
        for t in trends:
            cat = self.detect_category(t)
            # Create high-converting click-worthy title
            candidate = f"Everything You Need to Know About {t}: In-Depth 2026 Guide"
            if candidate not in self.published_topics:
                logger.info(f"🔥 Found live trending topic: {candidate} [{cat}]")
                return candidate

        # 2. Pull from viral seeds
        seeds = self.get_viral_seed_catalog()
        random.shuffle(seeds)
        for s in seeds:
            if s not in self.published_topics:
                logger.info(f"🚀 Selected high-traffic viral seed: {s}")
                return s

        return f"Top Tech, Gaming & AI Trends Dominating 2026: Complete Guide"

topic_hunter = TopicHunter()
