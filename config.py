import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    
    BLOG_NAME = os.getenv("BLOG_NAME", "LatestTech Hub")
    BLOG_TAGLINE = os.getenv("BLOG_TAGLINE", "Latest Tech Insights, AI Tools & Smart Guides")
    BLOG_DESCRIPTION = os.getenv("BLOG_DESCRIPTION", "Discover in-depth reviews, emerging AI technologies, gadget guides, and actionable tutorials.")
    BLOG_URL = os.getenv("BLOG_URL", "https://jtbsocial.github.io/latesttech")
    BLOG_AUTHOR = os.getenv("BLOG_AUTHOR", "LatestTech Editorial Team")
    BLOG_NICHE = os.getenv("BLOG_NICHE", "Artificial Intelligence & Modern Technology")
    
    ADSENSE_CLIENT_ID = os.getenv("ADSENSE_CLIENT_ID", "")
    
    MIN_WORD_COUNT = int(os.getenv("MIN_WORD_COUNT", "1500"))
    LANGUAGE = os.getenv("LANGUAGE", "English")
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "site")
    POSTS_DIR = os.path.join(OUTPUT_DIR, "posts")
    ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")
    IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    
    @classmethod
    def ensure_dirs(cls):
        for path in [cls.OUTPUT_DIR, cls.POSTS_DIR, cls.ASSETS_DIR, cls.IMAGES_DIR, cls.DATA_DIR]:
            os.makedirs(path, exist_ok=True)

config = Config()
config.ensure_dirs()
