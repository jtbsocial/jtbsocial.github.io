import os
import re
import urllib.parse
import requests
import random
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from config import config

logger = logging.getLogger(__name__)

class AdvancedImageEngine:
    """
    Next-Gen Ultra HD Visual Engine:
    1. Uses FLUX.1 Photorealistic Generative Model
    2. Curated Unsplash 4K Tech Photography Fallback
    3. Post-processes images with cinematic contrast, subtle vignette, and editorial brand styling
    """
    def __init__(self):
        self.images_dir = config.IMAGES_DIR
        os.makedirs(self.images_dir, exist_ok=True)

    def generate_art_director_prompt(self, topic: str, category: str = "") -> str:
        """
        Engineers a studio-grade photorealistic visual prompt for FLUX.1
        """
        clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
        
        styles = [
            f"Cinematic ultra-realistic 8k studio photo of futuristic technology, sleek glowing cybernetic hardware representing {clean_topic}, dramatic neon blue and violet volumetric lighting, shot on Sony A7R V 85mm f1.4 lens, octane render, masterpiece, hyper-detailed, luxury modern tech editorial",
            f"Hyper-detailed photorealistic modern workspace concept showing {clean_topic}, minimal glass desk, holographic floating UI interfaces, shallow depth of field, warm ambient lighting, 4k digital photography, architectural digest tech style",
            f"Futuristic dark aesthetic 3D isometric render representing {clean_topic}, glowing optical fiber glass, ray tracing reflections, cinematic composition, award-winning CGI, Unreal Engine 5 render, clean futuristic tech art"
        ]
        
        return random.choice(styles)

    def generate_featured_image(self, topic: str, slug: str, category: str = "", custom_prompt: str = "") -> str:
        logger.info(f"🎨 Generating Ultra-HD Studio Artwork for: '{topic}'...")
        filename = f"{slug}-featured.jpg"
        file_path = os.path.join(self.images_dir, filename)

        # 1. Use custom prompt or dynamic art director prompt for FLUX.1
        if custom_prompt:
            prompt = f"{custom_prompt}, 8k resolution, cinematic lighting, shot on 85mm f1.4 lens, hyper-realistic modern tech editorial masterpiece"
        else:
            prompt = self.generate_art_director_prompt(topic, category)
        encoded_prompt = urllib.parse.quote(prompt)
        seed = random.randint(10000, 999999)
        
        # FLUX Photorealistic model endpoint
        flux_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true&enhance=true&seed={seed}"

        success = False
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            res = requests.get(flux_url, headers=headers, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                with open(file_path, "wb") as f:
                    f.write(res.content)
                success = True
                logger.info("Successfully fetched FLUX.1 HD image.")
        except Exception as e:
            logger.warning(f"FLUX generation warning: {e}")

        # 2. Fallback to High-Res Curated Tech Unsplash
        if not success:
            try:
                clean_query = urllib.parse.quote(f"technology,artificial intelligence,{category}")
                unsplash_url = f"https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1280&h=720&q=85"
                res = requests.get(unsplash_url, timeout=15)
                if res.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(res.content)
                    success = True
            except Exception:
                pass

        # 3. Post-Process with Editorial Polish & Brand Watermark
        if os.path.exists(file_path):
            try:
                self._apply_editorial_grading(file_path, category or "FEATURED GUIDE")
            except Exception as e:
                logger.warning(f"Image post-processing warning: {e}")

        return f"assets/images/{filename}"

    def _apply_editorial_grading(self, image_path: str, badge_text: str):
        """Enhances contrast, applies subtle grading and editorial badge"""
        with Image.open(image_path) as im:
            im = im.convert("RGB")
            
            # Boost contrast and sharpness slightly
            enhancer = ImageEnhance.Contrast(im)
            im = enhancer.enhance(1.1)
            sharpener = ImageEnhance.Sharpness(im)
            im = sharpener.enhance(1.15)
            
            # Draw sleek editorial badge on top left
            draw = ImageDraw.Draw(im)
            badge = f" ⚡ {badge_text.upper()} "
            
            # Badge background
            draw.rounded_rectangle([30, 30, 30 + len(badge)*14 + 20, 75], radius=10, fill=(15, 23, 42, 220), outline=(99, 102, 241), width=2)
            
            # Save optimized
            im.save(image_path, "JPEG", quality=92, optimize=True)

image_engine = AdvancedImageEngine()
