import os
import sys
import argparse
import logging
from config import config
from topic_hunter import topic_hunter
from researcher import researcher
from generator import generator
from image_engine import image_engine
from publishers.static_pub import static_publisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AutoBlogCore")

def run_pipeline(custom_topic: str = None) -> dict:
    logger.info("=" * 60)
    logger.info("🚀 STARTING AUTO BLOG GENERATION PIPELINE")
    logger.info("=" * 60)

    # 1. Topic Hunter
    topic = topic_hunter.get_next_topic(custom_topic)
    logger.info(f"📌 Selected Target Topic: {topic}")

    # 2. Live Web Research
    logger.info("🔍 Fetching live 2026 facts & context via DuckDuckGo...")
    research_data = researcher.search_topic(topic)
    research_summary = research_data.get("research_summary", "")

    # 3. AI Generation
    logger.info("✍️ Generating human-grade SEO article with Gemini...")
    article = generator.generate_article(topic, research_summary)
    
    # 4. Free AI Image Engine
    logger.info("🎨 Generating 16:9 featured artwork via Pollinations AI...")
    img_path = image_engine.generate_featured_image(topic, article["slug"])

    # 5. Static Publisher
    logger.info("🌐 Publishing article and updating static website...")
    static_publisher.publish(article, img_path)

    # 6. Instant Search Engine Indexing Ping
    from indexer import search_indexer
    search_indexer.ping_search_engines(f"{config.BLOG_URL}/posts/{article['slug']}.html")

    # 7. Mark Published
    topic_hunter.mark_published(topic)
    logger.info(f"✅ Topic '{topic}' marked as published!")
    logger.info("=" * 60)
    logger.info(f"🎉 SUCCESS: Post published at site/posts/{article['slug']}.html")
    logger.info("=" * 60)

    return {
        "title": article["title"],
        "slug": article["slug"],
        "url": f"{config.BLOG_URL}/posts/{article['slug']}.html",
        "featured_image": img_path
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero-Cost Auto Blog Automation Engine")
    parser.add_argument("--topic", type=str, help="Specific topic to generate", default=None)
    parser.add_argument("--count", type=int, help="Number of articles to generate", default=1)
    args = parser.parse_args()

    for i in range(args.count):
        run_pipeline(args.topic)
