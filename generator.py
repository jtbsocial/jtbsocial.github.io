import os
import re
import json
import logging
import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from config import config
from researcher import researcher

logger = logging.getLogger(__name__)

class FAQItem(BaseModel):
    question: str
    answer: str

class ArticleSchema(BaseModel):
    title: str = Field(description="Catchy click-worthy H1 title")
    meta_description: str = Field(description="150-160 characters SEO meta description with target keywords")
    category: str = Field(description="Primary category name")
    tags: List[str] = Field(description="4 to 6 relevant SEO tags")
    read_time_minutes: int = Field(description="Estimated reading time in minutes")
    markdown_content: str = Field(description="Complete 1500+ words detailed article in rich Markdown including Table of Contents, H2/H3s, tables, and takeaways")
    image_prompt: str = Field(description="Vivid, photorealistic 30-word visual description of a futuristic high-tech scene for 8K studio photography")
    faqs: List[FAQItem] = Field(description="4 to 5 high-intent FAQ questions and answers")

class ContentGenerator:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model_name = config.GEMINI_MODEL

    def _get_client(self):
        api_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        
        try:
            from google import genai
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.warning(f"Generative AI initialization error: {e}")
            return None

    def create_slug(self, title: str) -> str:
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug).strip('-')
        return slug[:60]

    def generate_article(self, topic: str, custom_research: str = None) -> dict:
        logger.info(f"Generating full article for topic: '{topic}'...")

        if not custom_research:
            research_data = researcher.search_topic(topic)
            research_summary = research_data.get("research_summary", "")
        else:
            research_summary = custom_research

        prompt = f"""
You are an elite SEO Content Strategist, Senior Tech Journalist, and Google E-E-A-T specialist.
Your goal is to write a comprehensive, deeply engaging, 100% human-sounding article that outperforms all existing competitor blogs on Google search.

TARGET TOPIC: {topic}
LIVE 2026 WEB RESEARCH & BENCHMARKS:
{research_summary}

WRITING & SEO GUIDELINES:
1. Tone: Conversational, expert, authoritative, engaging, and clear. Avoid robotic AI clichés.
2. Word Count: 1,500 - 2,200 words. Comprehensive and highly practical with exact examples, step-by-step walkthroughs, and comparisons.
3. Structure:
   - Catchy H1 title.
   - Quick "Key Takeaways" summary box.
   - Jump Table of Contents (#section-id).
   - Rich H2 and H3 sections with deep explanations.
   - At least 1-2 Markdown comparison tables with clear data columns.
   - Step-by-step tutorial or implementation framework.
   - 4-5 high-intent FAQs.
"""

        client = self._get_client()
        
        if not client:
            logger.warning("No Gemini API key set. Generating structured demo article.")
            return self._generate_fallback(topic, research_summary)

        try:
            from google.genai import types
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ArticleSchema,
                    temperature=0.7
                )
            )
            
            data = json.loads(response.text)
            
            # Format schema.org FAQ
            faqs = data.get("faqs", [])
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f.get("question", ""),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f.get("answer", "")
                        }
                    }
                    for f in faqs
                ]
            }
            
            data["slug"] = self.create_slug(data.get("title", topic))
            data["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
            data["faq_schema"] = faq_schema
            logger.info("Successfully generated structured E-E-A-T article via Gemini!")
            return data
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}. Falling back to clean template.")
            return self._generate_fallback(topic, research_summary)

    def _generate_fallback(self, topic: str, research: str) -> dict:
        slug = self.create_slug(topic)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        content = f"""# {topic}

> **Quick Summary:** In this comprehensive guide, we explore everything you need to know about {topic}. Learn practical strategies, key comparisons, and step-by-step best practices for 2026.

---

## Table of Contents
1. [Introduction to {topic}](#introduction)
2. [Key Benefits & Why It Matters](#benefits)
3. [Feature & Performance Comparison](#comparison)
4. [Step-by-Step Implementation Guide](#guide)
5. [Common Mistakes to Avoid](#mistakes)
6. [Frequently Asked Questions](#faq)

---

## 1. Introduction to {topic} <a id="introduction"></a>
The landscape of modern technology is evolving at an unprecedented pace. Understanding **{topic}** has become essential for anyone looking to optimize their workflow and achieve sustainable digital growth in 2026.

---

## 2. Key Benefits & Why It Matters <a id="benefits"></a>
- **Maximized Productivity:** Streamline complex operations into automated, reliable routines.
- **Cost Reduction:** Eliminate repetitive manual overhead with modern zero-cost tools.
- **Future-Proof Scalability:** Stay ahead of market shifts with intelligent architectures.

---

## 3. Feature & Performance Comparison <a id="comparison"></a>

| Feature | Standard Approach | Next-Gen Automated Solution |
| :--- | :--- | :--- |
| **Speed / Turnaround** | Hours / Days | Minutes |
| **Operational Cost** | High Recurring Fees | $0 (Free-tier friendly) |
| **Reliability** | Prone to human fatigue | 24/7 Autopilot |
| **SEO Optimization** | Manual & Inconsistent | Automated E-E-A-T & Schema |

---

## 4. Step-by-Step Implementation Guide <a id="guide"></a>

### Step 1: Initial Setup
Prepare your environment with the correct configuration and lightweight open-source dependencies.

### Step 2: Configure Your Automation Pipeline
Set up real-time search triggers to feed fresh context into your generative workflow.

### Step 3: Publish & Monitor
Deploy your static output to cloud endpoints like GitHub Pages or custom domains for instant global availability.

---

## 5. Frequently Asked Questions <a id="faq"></a>

### Q: Is this suitable for beginners?
**A:** Yes! The entire workflow is designed to be plug-and-play with simple configuration options.

### Q: What is the cost involved?
**A:** With free tiers from Google AI Studio, DuckDuckGo, and GitHub Pages, total operating cost is **$0**.
"""
        return {
            "title": topic,
            "slug": slug,
            "meta_description": f"Complete guide to {topic}. Discover actionable tips, feature comparisons, and best practices in our in-depth 2026 review.",
            "category": "Technology & AI",
            "tags": ["AI Tools", "Tech Guide", "Automation", "2026 Trends"],
            "read_time_minutes": 6,
            "date": date_str,
            "markdown_content": content,
            "faq_schema": {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"What are the main advantages of {topic}?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Key advantages include maximum efficiency, zero ongoing costs, and high scalability."
                        }
                    }
                ]
            }
        }

generator = ContentGenerator()
