import os
import logging
import requests
from config import config

logger = logging.getLogger(__name__)

class SocialMediaPoster:
    """
    Automates instant syndication across social platforms (Telegram, Discord, Twitter/X)
    to drive immediate viral traffic to newly published blog posts.
    """
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    def broadcast_new_post(self, article: dict, featured_image_path: str):
        """Broadcasts a newly published post to all configured social channels"""
        logger.info(f"📢 Initiating social broadcast for: '{article.get('title')}'...")

        post_url = f"{config.BLOG_URL}/posts/{article.get('slug')}.html"
        tags = " ".join([f"#{t.replace(' ', '')}" for t in article.get("tags", [])[:5]])

        # 1. Telegram Channel Broadcast
        if self.telegram_bot_token and self.telegram_chat_id:
            self._post_to_telegram(article, post_url, tags, featured_image_path)

        # 2. Discord Community Webhook
        if self.discord_webhook_url:
            self._post_to_discord(article, post_url, tags)

    def _post_to_telegram(self, article: dict, post_url: str, tags: str, image_path: str):
        try:
            logger.info("Posting article to Telegram Channel...")
            caption = (
                f"🔥 *NEW GUIDE:* {article.get('title')}\n\n"
                f"⏱️ *Read Time:* {article.get('read_time', 5)} mins | 📂 *Category:* {article.get('category')}\n\n"
                f"📝 *Summary:* {article.get('meta_description')}\n\n"
                f"🔗 *Read Full Article:* {post_url}\n\n"
                f"{tags}"
            )
            
            # Send photo with caption
            full_img_path = os.path.join(config.OUTPUT_DIR, image_path)
            if os.path.exists(full_img_path):
                with open(full_img_path, "rb") as photo:
                    url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                    res = requests.post(url, data={
                        "chat_id": self.telegram_chat_id,
                        "caption": caption,
                        "parse_mode": "Markdown"
                    }, files={"photo": photo}, timeout=15)
                    if res.status_code == 200:
                        logger.info("✅ Successfully broadcasted to Telegram Channel!")
                    else:
                        logger.warning(f"Telegram broadcast error: {res.text}")
            else:
                # Text fallback
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                requests.post(url, json={
                    "chat_id": self.telegram_chat_id,
                    "text": caption,
                    "parse_mode": "Markdown"
                }, timeout=15)
        except Exception as e:
            logger.warning(f"Telegram syndication failed: {e}")

    def _post_to_discord(self, article: dict, post_url: str, tags: str):
        try:
            logger.info("Posting article to Discord Webhook...")
            img_url = f"{config.BLOG_URL}/{article.get('featured_image', '')}"
            
            payload = {
                "embeds": [
                    {
                        "title": f"⚡ {article.get('title')}",
                        "url": post_url,
                        "description": f"{article.get('meta_description')}\n\n[👉 **Read Complete Guide Here**]({post_url})\n\n{tags}",
                        "color": 5174501,  # Indigo hex
                        "author": {
                            "name": config.BLOG_NAME,
                            "url": config.BLOG_URL
                        },
                        "image": {
                            "url": img_url
                        },
                        "footer": {
                            "text": f"⏱️ {article.get('read_time', 5)} min read • {article.get('category')}"
                        }
                    }
                ]
            }
            res = requests.post(self.discord_webhook_url, json=payload, timeout=10)
            if res.status_code in [200, 204]:
                logger.info("✅ Successfully broadcasted to Discord community!")
        except Exception as e:
            logger.warning(f"Discord broadcast failed: {e}")

social_poster = SocialMediaPoster()
