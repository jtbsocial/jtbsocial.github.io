import os
import re
import urllib.parse
import requests
import logging
from config import config

logger = logging.getLogger(__name__)

class ImageEngine:
    def __init__(self):
        self.images_dir = config.IMAGES_DIR
        os.makedirs(self.images_dir, exist_ok=True)

    def generate_featured_image(self, topic: str, slug: str) -> str:
        """
        Generates a 100% free high-quality 16:9 featured image using Pollinations AI.
        Saves the image locally and returns the relative image path.
        """
        logger.info(f"Generating featured image for topic: '{topic}'...")
        filename = f"{slug}-featured.jpg"
        file_path = os.path.join(self.images_dir, filename)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            logger.info(f"Image already exists: {filename}")
            return f"assets/images/{filename}"

        clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
        image_prompt = f"Modern aesthetic conceptual 3d illustration representing {clean_topic}, high quality digital art, 8k wallpaper, sleek minimal tech style, cinematic lighting, 16:9 aspect ratio"
        encoded_prompt = urllib.parse.quote(image_prompt)
        
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=675&nologo=true&enhance=true"

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            }
            response = requests.get(image_url, headers=headers, timeout=25)
            if response.status_code == 200 and len(response.content) > 2000:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Successfully generated and saved featured image: {filename}")
                return f"assets/images/{filename}"
        except Exception as e:
            logger.warning(f"Failed to fetch image via Pollinations: {e}")

        # Fallback to direct placeholder
        return image_url

image_engine = ImageEngine()
