"""
Affiliate Engine — Injects high-converting recommendation CTA cards into articles.
Links only to VERIFIED cornerstone posts with full content.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Verified cornerstone articles with full 1500+ word content
AFFILIATE_OFFERS = {
    "ai": {
        "headline": "Supercharge Your Workflow with Top AI Tools",
        "description": "Explore the 10 best free AI productivity tools that are automating 90% of daily work for professionals in 2026.",
        "cta_text": "Explore Top AI Tools →",
        "url": "https://jtbsocial.github.io/latesttech/posts/top-10-free-ai-productivity-tools-that-will-automate-90-of-y.html",
        "badge": "🔥 STAFF PICK"
    },
    "coding": {
        "headline": "Free AI Coding Assistants That Beat GitHub Copilot",
        "description": "Discover 5 powerful free AI coding assistants with real benchmarks proving they outperform paid alternatives.",
        "cta_text": "View Full Comparison →",
        "url": "https://jtbsocial.github.io/latesttech/posts/5-free-ai-coding-assistants-that-outperform-github-copilot-i.html",
        "badge": "⚡ TRENDING"
    },
    "llm": {
        "headline": "Run Open-Source LLMs Locally for Free",
        "description": "The complete 2026 guide to 7 open-source LLMs you can run on your own hardware for coding, writing, and research.",
        "cta_text": "See the Full Guide →",
        "url": "https://jtbsocial.github.io/latesttech/posts/top-7-free-open-source-llms-you-can-run-locally-for-coding-i.html",
        "badge": "🌟 EDITOR'S CHOICE"
    }
}

# Keywords that trigger each offer type
CATEGORY_KEYWORDS = {
    "ai": ["ai", "artificial intelligence", "machine learning", "productivity", "automation", "tools", "technology"],
    "coding": ["coding", "programming", "developer", "software", "github", "code", "assistant"],
    "llm": ["llm", "language model", "open source", "local", "gpt", "model", "quantum"]
}

class AffiliateEngine:
    def inject_affiliate_boxes(self, html_content: str, category: str = "") -> str:
        """Inject a single high-converting affiliate recommendation after the 2nd heading."""
        if not html_content:
            return html_content

        # Determine best offer based on category keywords
        offer_key = "ai"  # default
        category_lower = category.lower() if category else ""
        for key, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in category_lower for kw in keywords):
                offer_key = key
                break

        offer = AFFILIATE_OFFERS[offer_key]
        
        affiliate_html = f"""
<div style="margin: 2.5rem 0; padding: 1.75rem; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 1rem; color: white; box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.3);">
    <div style="display: flex; align-items: flex-start; gap: 1rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px;">
            <span style="display: inline-block; padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.05em; margin-bottom: 0.75rem;">{offer['badge']}</span>
            <h4 style="font-size: 1.25rem; font-weight: 800; margin: 0 0 0.5rem 0; line-height: 1.3;">{offer['headline']}</h4>
            <p style="font-size: 0.9rem; opacity: 0.9; margin: 0 0 1rem 0; line-height: 1.6;">{offer['description']}</p>
            <a href="{offer['url']}" style="display: inline-block; padding: 0.75rem 1.5rem; background: white; color: #4f46e5; font-weight: 800; border-radius: 0.75rem; text-decoration: none; font-size: 0.9rem; transition: transform 0.2s;">{offer['cta_text']}</a>
        </div>
    </div>
</div>
"""
        # Insert after the second </h2> tag
        h2_positions = [m.end() for m in re.finditer(r'</h2>', html_content)]
        if len(h2_positions) >= 2:
            insert_pos = h2_positions[1]
            return html_content[:insert_pos] + affiliate_html + html_content[insert_pos:]
        elif len(h2_positions) >= 1:
            insert_pos = h2_positions[0]
            return html_content[:insert_pos] + affiliate_html + html_content[insert_pos:]

        return html_content

affiliate_engine = AffiliateEngine()
