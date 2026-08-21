import re
import json
import os
import logging
from config import config

logger = logging.getLogger(__name__)

class AffiliateEngine:
    """
    Automatically injects stylish, high-converting Affiliate Callout Boxes
    and product recommendation cards into blog posts based on content keywords.
    """
    def __init__(self):
        self.offers = [
            {
                "keywords": ["ai", "prompt", "llm", "productivity", "writing", "chatgpt", "gemini", "claude"],
                "badge": "🔥 Editor's Choice 2026",
                "title": "Supercharge Your Workflow with Top AI Tools",
                "desc": "Automate 90% of your repetitive tasks, writing, and coding with next-gen AI platforms.",
                "cta_text": "Explore Top Rated AI Deals →",
                "link": "https://jtbsocial.github.io/latesttech/posts/top-10-free-ai-tools-that-automate-90-percent-of-daily-work-.html"
            },
            {
                "keywords": ["coding", "python", "developer", "software", "copilot", "github"],
                "badge": "⚡ Best Developer Pick",
                "title": "Top Free AI Coding Extensions for VS Code",
                "desc": "Boost coding speed by 3x with intelligent context-aware autocomplete and agentic refactoring.",
                "cta_text": "See Free AI Assistants →",
                "link": "https://jtbsocial.github.io/latesttech/posts/5-free-ai-coding-assistants-that-outperform-github-copilot-i.html"
            }
        ]

    def inject_affiliate_boxes(self, html_content: str, category: str = "") -> str:
        """Injects responsive affiliate CTA banner into article body"""
        offer = self.offers[0]
        if "coding" in category.lower() or "developer" in category.lower():
            offer = self.offers[1]

        banner_html = f"""
        <div class="my-10 p-6 rounded-2xl bg-gradient-to-r from-indigo-900 to-violet-900 text-white shadow-xl border border-indigo-500/30 flex flex-col sm:flex-row items-center justify-between gap-6 not-prose">
            <div class="space-y-2 text-center sm:text-left">
                <span class="px-3 py-1 bg-amber-400 text-slate-900 rounded-full text-xs font-black uppercase tracking-wider">{offer['badge']}</span>
                <h4 class="text-xl font-bold font-display text-white">{offer['title']}</h4>
                <p class="text-sm text-indigo-200">{offer['desc']}</p>
            </div>
            <a href="{offer['link']}" class="px-6 py-3 bg-amber-400 hover:bg-amber-300 text-slate-950 font-black rounded-xl text-sm transition-all shadow-lg whitespace-nowrap hover:scale-105">
                {offer['cta_text']}
            </a>
        </div>
        """
        
        # Insert after 2nd H2 heading if present
        h2_split = html_content.split("</h2>", 2)
        if len(h2_split) >= 3:
            return h2_split[0] + "</h2>" + h2_split[1] + "</h2>" + banner_html + h2_split[2]
        
        return html_content + banner_html

affiliate_engine = AffiliateEngine()
