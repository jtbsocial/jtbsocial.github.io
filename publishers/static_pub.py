import os
import json
import re
import markdown
import logging
from config import config
from publishers.base import BasePublisher

logger = logging.getLogger(__name__)

class StaticPublisher(BasePublisher):
    def __init__(self):
        self.output_dir = config.OUTPUT_DIR
        self.posts_dir = config.POSTS_DIR
        self.assets_dir = config.ASSETS_DIR
        self.data_file = os.path.join(config.DATA_DIR, "articles.json")
        self._ensure_static_assets()

    def _ensure_static_assets(self):
        os.makedirs(os.path.join(self.assets_dir, "css"), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, "js"), exist_ok=True)
        
        css_path = os.path.join(self.assets_dir, "css", "style.css")
        if not os.path.exists(css_path):
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(self._get_css())

        js_path = os.path.join(self.assets_dir, "js", "main.js")
        if not os.path.exists(js_path):
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(self._get_js())

        self._generate_policy_pages()

    def _load_all_articles(self) -> list:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading articles database: {e}")
        return []

    def _save_articles(self, articles: list):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving articles database: {e}")

    def publish(self, article_data: dict, featured_image_path: str) -> bool:
        logger.info(f"Publishing article '{article_data.get('title')}' to Static Blog...")
        
        # 1. Apply Automatic Internal Linking
        from internal_linker import internal_linker
        from affiliate_engine import affiliate_engine

        md_content = article_data.get("markdown_content", "")
        md_content_linked = internal_linker.insert_internal_links(md_content, article_data.get("slug", ""))
        md_body = re.sub(r'^#\s+.*?\n', '', md_content_linked).strip()
        
        html_body = markdown.markdown(
            md_body,
            extensions=['extra', 'tables', 'fenced_code', 'toc', 'nl2br']
        )

        # 2. Inject High-Converting Affiliate Banner Box
        html_body = affiliate_engine.inject_affiliate_boxes(html_body, article_data.get("category", ""))

        article_record = {
            "title": article_data.get("title"),
            "slug": article_data.get("slug"),
            "meta_description": article_data.get("meta_description"),
            "category": article_data.get("category", "Technology"),
            "tags": article_data.get("tags", []),
            "date": article_data.get("date"),
            "read_time": article_data.get("read_time_minutes", 5),
            "featured_image": featured_image_path,
            "markdown_content": md_content_linked,
            "faq_schema": article_data.get("faq_schema", {})
        }

        post_html = self._render_post_page(article_record, html_body)
        post_file = os.path.join(self.posts_dir, f"{article_record['slug']}.html")
        with open(post_file, "w", encoding="utf-8") as f:
            f.write(post_html)

        articles = self._load_all_articles()
        articles = [a for a in articles if a.get("slug") != article_record["slug"]]
        articles.insert(0, article_record)
        self._save_articles(articles)

        self.build_home_page(articles)
        self.build_sitemap(articles)
        self.build_rss_feed(articles)
        self.build_robots_txt()

        logger.info(f"Article published successfully at site/posts/{article_record['slug']}.html")
        return True

    def _render_header(self, title: str, meta_desc: str, canonical_url: str = "", og_image: str = "", schema_json: str = "") -> str:
        adsense_script = ""
        if config.ADSENSE_CLIENT_ID:
            adsense_script = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={config.ADSENSE_CLIENT_ID}" crossorigin="anonymous"></script>'

        return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {config.BLOG_NAME}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="author" content="{config.BLOG_AUTHOR}">
    <link rel="canonical" href="{canonical_url or config.BLOG_URL}">
    
    <!-- Open Graph / SEO -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:image" content="{og_image}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="p:domain_verify" content="cfb450e2c89091ff91473d4d9fb9c5d1"/>
    
    <!-- Google Fonts & Tailwind CDN -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        display: ['Outfit', 'sans-serif'],
                    }},
                    colors: {{
                        primary: {{ 50: '#eef2ff', 100: '#e0e7ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' }}
                    }}
                }}
            }}
        }}
    </script>
    <link rel="stylesheet" href="../assets/css/style.css">
    {adsense_script}
    {f'<script type="application/ld+json">{schema_json}</script>' if schema_json else ''}
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 min-h-screen flex flex-col font-sans transition-colors duration-200 antialiased">
    <!-- Navbar -->
    <header class="sticky top-0 z-50 backdrop-blur-md bg-white/90 dark:bg-slate-900/90 border-b border-slate-200/80 dark:border-slate-800/80 shadow-sm">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
            <a href="../index.html" class="flex items-center gap-2 text-2xl font-black font-display bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                ⚡ {config.BLOG_NAME}
            </a>
            <nav class="hidden md:flex items-center gap-8 text-sm font-bold text-slate-600 dark:text-slate-300">
                <a href="../index.html" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Home</a>
                <a href="../about.html" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">About</a>
                <a href="../contact.html" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Contact</a>
                <a href="../privacy-policy.html" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Privacy</a>
            </nav>
            <div class="flex items-center gap-3">
                <button id="themeToggle" class="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-colors" aria-label="Toggle Theme">
                    🌙
                </button>
            </div>
        </div>
    </header>
"""

    def _render_footer(self) -> str:
        return f"""
    <!-- Footer -->
    <footer class="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 py-12">
        <div class="max-w-5xl mx-auto px-4 sm:px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
            <div class="md:col-span-2">
                <h3 class="text-xl font-bold font-display text-indigo-600 dark:text-indigo-400 mb-2">⚡ {config.BLOG_NAME}</h3>
                <p class="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-4 leading-relaxed">{config.BLOG_DESCRIPTION}</p>
                <p class="text-xs text-slate-400">&copy; 2026 {config.BLOG_NAME}. All rights reserved.</p>
            </div>
            <div>
                <h4 class="text-sm font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3 font-display">Navigation</h4>
                <ul class="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li><a href="../index.html" class="hover:underline">Home</a></li>
                    <li><a href="../about.html" class="hover:underline">About Us</a></li>
                    <li><a href="../contact.html" class="hover:underline">Contact</a></li>
                    <li><a href="../sitemap.xml" class="hover:underline">Sitemap</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-sm font-bold uppercase tracking-wider text-slate-900 dark:text-white mb-3 font-display">Compliance</h4>
                <ul class="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li><a href="../privacy-policy.html" class="hover:underline">Privacy Policy</a></li>
                    <li><a href="../terms.html" class="hover:underline">Terms of Service</a></li>
                    <li><a href="../disclaimer.html" class="hover:underline">Disclaimer</a></li>
                </ul>
            </div>
        </div>
    </footer>
    <script src="../assets/js/main.js"></script>
</body>
</html>
"""

    def _build_toc(self, content_html: str) -> str:
        """Extract H2 headings from HTML and build a clickable Table of Contents."""
        import re as _re
        headings = _re.findall(r'<h2[^>]*>(.*?)</h2>', content_html, _re.DOTALL)
        if not headings:
            return ""
        
        toc_items = ""
        for i, h in enumerate(headings):
            clean = _re.sub(r'<[^>]+>', '', h).strip()
            anchor_id = _re.sub(r'[^a-z0-9]+', '-', clean.lower()).strip('-')
            toc_items += f'<li><a href="#toc-{i}" class="block py-1.5 px-3 text-sm text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 rounded-lg transition-colors truncate">{clean}</a></li>\n'
        
        return f"""
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 class="text-sm font-black uppercase tracking-wider text-slate-900 dark:text-white mb-3 font-display flex items-center gap-2">
                📑 Table of Contents
            </h3>
            <ul class="space-y-0.5">{toc_items}</ul>
        </div>
        """

    def _add_heading_ids(self, content_html: str) -> str:
        """Add anchor IDs to H2 headings for ToC linking."""
        import re as _re
        counter = [0]
        def replacer(match):
            idx = counter[0]
            counter[0] += 1
            tag_content = match.group(0)
            return tag_content.replace('<h2', f'<h2 id="toc-{idx}"', 1)
        return _re.sub(r'<h2[^>]*>', replacer, content_html)

    def _build_related_posts(self, current_slug: str) -> str:
        """Build Related Posts sidebar widget."""
        articles = self._load_all_articles()
        related = [a for a in articles if a.get("slug") != current_slug][:4]
        if not related:
            return ""
        
        items = ""
        for art in related:
            items += f"""
            <a href="{art['slug']}.html" class="flex gap-3 p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors group">
                <img src="../{art['featured_image']}" alt="{art['title']}" class="w-16 h-16 rounded-xl object-cover flex-shrink-0 border border-slate-200 dark:border-slate-700">
                <div class="min-w-0">
                    <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-2 leading-tight">{art['title']}</h4>
                    <span class="text-xs text-slate-400 mt-1 block">⏱️ {art.get('read_time', 5)} min</span>
                </div>
            </a>
            """
        
        return f"""
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h3 class="text-sm font-black uppercase tracking-wider text-slate-900 dark:text-white mb-4 font-display flex items-center gap-2">
                🔥 Popular Guides
            </h3>
            <div class="space-y-1">{items}</div>
        </div>
        """

    def _render_post_page(self, article: dict, content_html: str) -> str:
        schema_json = json.dumps(article.get("faq_schema", {})) if article.get("faq_schema") else ""
        header = self._render_header(
            title=article["title"],
            meta_desc=article["meta_description"],
            canonical_url=f"{config.BLOG_URL}/posts/{article['slug']}.html",
            og_image=f"{config.BLOG_URL}/{article['featured_image']}",
            schema_json=schema_json
        )

        tags_html = "".join([f'<span class="px-3.5 py-1.5 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-xl text-xs font-bold border border-indigo-100 dark:border-indigo-900/40">#{t}</span>' for t in article.get("tags", [])])

        adsense_box = """
        <div class="my-10 p-6 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl text-center bg-slate-50/50 dark:bg-slate-900/40 text-xs font-semibold text-slate-400">
            <span>SPONSORED ADVERTISEMENT</span>
            <div class="min-h-[100px] flex items-center justify-center font-mono text-slate-300 dark:text-slate-600 mt-2">
                <!-- Google AdSense Responsive Slot -->
            </div>
        </div>
        """

        # Add anchor IDs to headings for ToC
        content_html = self._add_heading_ids(content_html)
        
        # Build sidebar widgets
        toc_html = self._build_toc(content_html)
        related_html = self._build_related_posts(article.get("slug", ""))
        
        share_url = f"{config.BLOG_URL}/posts/{article['slug']}.html"
        share_title = article['title'].replace(' ', '+')

        body = f"""
    <div id="progressBar" class="fixed top-0 left-0 h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 z-50 transition-all duration-150" style="width: 0%"></div>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-grow">
        <!-- Breadcrumb -->
        <nav class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-8 font-semibold uppercase tracking-wider">
            <a href="../index.html" class="hover:text-indigo-600">Home</a> &rsaquo;
            <span class="text-indigo-600 dark:text-indigo-400">{article['category']}</span> &rsaquo;
            <span class="truncate max-w-[200px] text-slate-400">{article['title']}</span>
        </nav>

        <!-- Two-Column Layout: Article + Sidebar -->
        <div class="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-10 items-start">
            
            <!-- LEFT: Main Article -->
            <article class="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-10 lg:p-12 shadow-sm border border-slate-100 dark:border-slate-800">
                <div class="flex items-center gap-3 mb-6">
                    <span class="px-3.5 py-1.5 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase tracking-wider shadow-sm">{article['category']}</span>
                    <span class="text-xs font-semibold text-slate-400">&bull; {article['date']}</span>
                    <span class="text-xs font-semibold text-slate-400">&bull; ⏱️ {article['read_time']} min read</span>
                </div>

                <h1 class="text-3xl sm:text-4xl font-black font-display leading-[1.15] text-slate-900 dark:text-white mb-6">
                    {article['title']}
                </h1>

                <p class="text-lg text-slate-600 dark:text-slate-300 mb-8 leading-relaxed font-medium">
                    {article['meta_description']}
                </p>

                <div class="mb-10 rounded-2xl overflow-hidden shadow-xl border border-slate-100 dark:border-slate-800 aspect-video">
                    <img src="../{article['featured_image']}" alt="{article['title']}" class="w-full h-full object-cover" loading="lazy">
                </div>

                {adsense_box}

                <!-- Rendered Article Body -->
                <div class="article-body">
                    {content_html}
                </div>

                {adsense_box}

                <!-- Tags -->
                <div class="mt-14 pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-wrap gap-2.5 items-center">
                    <span class="text-xs font-black text-slate-400 uppercase mr-2 tracking-wider">Tags:</span>
                    {tags_html}
                </div>

                <!-- Author Box for E-E-A-T -->
                <div class="mt-10 p-6 sm:p-8 bg-slate-50 dark:bg-slate-800/50 rounded-2xl flex flex-col sm:flex-row items-center gap-5 border border-slate-200/80 dark:border-slate-700/80">
                    <div class="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center text-white font-black text-2xl flex-shrink-0 shadow-lg shadow-indigo-500/20">
                        ⚡
                    </div>
                    <div class="text-center sm:text-left">
                        <h4 class="font-bold text-slate-900 dark:text-white font-display text-lg">{config.BLOG_AUTHOR}</h4>
                        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                            Researched, verified, and curated by the {config.BLOG_NAME} editorial team. Dedicated to bringing actionable insights, deep benchmarks, and practical tech guides.
                        </p>
                    </div>
                </div>
            </article>

            <!-- RIGHT: Sticky Sidebar -->
            <aside class="hidden lg:flex flex-col gap-6 sticky top-24">
                
                <!-- Table of Contents -->
                {toc_html}

                <!-- Share This Article -->
                <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <h3 class="text-sm font-black uppercase tracking-wider text-slate-900 dark:text-white mb-4 font-display">
                        📤 Share This Guide
                    </h3>
                    <div class="flex flex-wrap gap-2">
                        <a href="https://twitter.com/intent/tweet?url={share_url}&text={share_title}" target="_blank" rel="noopener"
                           class="flex-1 py-2.5 px-3 bg-slate-900 dark:bg-slate-800 text-white text-xs font-bold rounded-xl text-center hover:bg-slate-700 transition-colors">
                            𝕏 Tweet
                        </a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" target="_blank" rel="noopener"
                           class="flex-1 py-2.5 px-3 bg-blue-700 text-white text-xs font-bold rounded-xl text-center hover:bg-blue-600 transition-colors">
                            in LinkedIn
                        </a>
                        <a href="https://pinterest.com/pin/create/button/?url={share_url}&description={share_title}" target="_blank" rel="noopener"
                           class="flex-1 py-2.5 px-3 bg-red-600 text-white text-xs font-bold rounded-xl text-center hover:bg-red-500 transition-colors">
                            📌 Pin
                        </a>
                    </div>
                </div>

                <!-- Sidebar Ad Slot -->
                <div class="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
                    <div class="text-center text-xs font-semibold text-slate-400 mb-2">ADVERTISEMENT</div>
                    <div class="min-h-[250px] flex items-center justify-center border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl text-slate-300 dark:text-slate-600 text-xs">
                        <!-- Google AdSense Sidebar Slot -->
                    </div>
                </div>

                <!-- Related Posts -->
                {related_html}

                <!-- Newsletter Signup -->
                <div class="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-2xl p-6 text-white shadow-lg">
                    <h3 class="text-sm font-black uppercase tracking-wider mb-2 font-display">📬 Stay Updated</h3>
                    <p class="text-xs opacity-90 mb-4 leading-relaxed">Get the latest AI tools, coding guides, and tech insights delivered weekly.</p>
                    <a href="../index.html" class="block w-full py-3 bg-white text-indigo-700 font-black text-sm rounded-xl text-center hover:bg-indigo-50 transition-colors shadow-sm">
                        Browse All Guides →
                    </a>
                </div>

            </aside>
        </div>
    </main>
"""
        return header + body + self._render_footer()

    def _get_category_badge(self, cat: str) -> str:
        cat_low = cat.lower()
        if "gaming" in cat_low or "game" in cat_low:
            return "bg-purple-600 text-white"
        elif "gadget" in cat_low or "hardware" in cat_low or "phone" in cat_low or "laptop" in cat_low:
            return "bg-emerald-600 text-white"
        elif "movie" in cat_low or "entertainment" in cat_low or "sci-fi" in cat_low:
            return "bg-rose-600 text-white"
        elif "ai" in cat_low or "llm" in cat_low or "gpt" in cat_low:
            return "bg-indigo-600 text-white"
        else:
            return "bg-slate-700 text-white"

    def build_home_page(self, articles: list):
        featured = articles[0] if articles else None
        grid_articles = articles[1:] if len(articles) > 1 else []

        cards_html = ""
        for art in grid_articles:
            cat = art.get('category', 'Tech Trends')
            badge_class = self._get_category_badge(cat)
            cards_html += f"""
            <article data-category="{cat}" class="article-card bg-white dark:bg-slate-900 rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-slate-800 flex flex-col group">
                <a href="posts/{art['slug']}.html" class="block overflow-hidden aspect-video relative">
                    <img src="{art['featured_image']}" alt="{art['title']}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy">
                    <span class="absolute top-4 left-4 px-3 py-1 {badge_class} rounded-xl text-xs font-black uppercase tracking-wider shadow-lg">
                        {cat}
                    </span>
                </a>
                <div class="p-6 flex flex-col flex-grow">
                    <div class="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-3">
                        <span>📅 {art['date']}</span> &bull; <span>⏱️ {art['read_time']} min read</span>
                    </div>
                    <h3 class="text-xl font-bold font-display text-slate-900 dark:text-white mb-3 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-2 leading-tight">
                        <a href="posts/{art['slug']}.html">{art['title']}</a>
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400 line-clamp-3 mb-6 flex-grow leading-relaxed">
                        {art['meta_description']}
                    </p>
                    <div class="flex items-center justify-between text-xs text-slate-400 pt-4 border-t border-slate-100 dark:border-slate-800">
                        <span class="font-bold text-slate-500 dark:text-slate-400">{config.BLOG_NAME}</span>
                        <a href="posts/{art['slug']}.html" class="font-black text-indigo-600 dark:text-indigo-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">Read Full Guide &rarr;</a>
                    </div>
                </div>
            </article>
            """

        hero_html = ""
        if featured:
            f_cat = featured.get('category', 'Tech Trends')
            f_badge = self._get_category_badge(f_cat)
            hero_html = f"""
            <div class="mb-14 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 sm:p-10 text-white shadow-2xl relative overflow-hidden border border-indigo-500/20">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                    <div>
                        <div class="flex items-center gap-2 mb-4">
                            <span class="px-3.5 py-1.5 {f_badge} rounded-xl text-xs font-black uppercase tracking-wider shadow-lg">🌟 Featured Story</span>
                            <span class="text-xs text-slate-400">&bull; {featured['date']}</span>
                        </div>
                        <h2 class="text-2xl sm:text-4xl font-black font-display leading-[1.15] mb-4 hover:text-indigo-300 transition-colors">
                            <a href="posts/{featured['slug']}.html">{featured['title']}</a>
                        </h2>
                        <p class="text-sm sm:text-base text-slate-300 mb-8 line-clamp-3 leading-relaxed font-medium">
                            {featured['meta_description']}
                        </p>
                        <div class="flex items-center gap-4">
                            <a href="posts/{featured['slug']}.html" class="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-black rounded-xl text-sm transition-colors shadow-lg shadow-indigo-600/30">Read Full Story &rarr;</a>
                            <span class="text-xs text-slate-400 font-semibold">⏱️ {featured['read_time']} min read</span>
                        </div>
                    </div>
                    <div class="rounded-2xl overflow-hidden shadow-2xl border border-white/10 aspect-video">
                        <img src="{featured['featured_image']}" alt="{featured['title']}" class="w-full h-full object-cover">
                    </div>
                </div>
            </div>
            """

        index_content = f"""
    <main class="max-w-6xl mx-auto px-4 sm:px-6 py-10 flex-grow">
        <div class="text-center max-w-3xl mx-auto mb-12">
            <span class="px-4 py-1.5 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-full text-xs font-black uppercase tracking-wider inline-block mb-4 border border-indigo-100 dark:border-indigo-900/40">
                ⚡ Real-Time Tech, Gaming & AI Radar
            </span>
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black font-display tracking-tight text-slate-900 dark:text-white mb-4">
                {config.BLOG_TAGLINE}
            </h1>
            <p class="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                {config.BLOG_DESCRIPTION}
            </p>
        </div>

        {hero_html}

        <!-- Interactive Category Filter Tabs -->
        <div class="mb-10 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
            <div class="flex flex-wrap items-center gap-2" id="categoryTabs">
                <button onclick="filterCategory('all')" class="cat-btn active px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white transition-all shadow-sm">
                    🌟 All Trending
                </button>
                <button onclick="filterCategory('gaming')" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-all">
                    🎮 Gaming & Esports
                </button>
                <button onclick="filterCategory('ai')" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-all">
                    🤖 AI & Breakthroughs
                </button>
                <button onclick="filterCategory('gadget')" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-all">
                    📱 Gadgets & Hardware
                </button>
                <button onclick="filterCategory('entertainment')" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition-all">
                    🎬 Movies & Sci-Fi
                </button>
            </div>
            <span class="text-xs font-bold text-slate-400" id="articleCount">{len(articles)} Guides Published</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" id="articlesGrid">
            {cards_html if cards_html else '<p class="col-span-3 text-center text-slate-400 py-12">Generating first articles... Please check back in a few moments.</p>'}
        </div>
    </main>

    <script>
    function filterCategory(cat) {{
        document.querySelectorAll('.cat-btn').forEach(btn => {{
            btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-sm');
            btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
        }});
        event.currentTarget.classList.add('bg-indigo-600', 'text-white', 'shadow-sm');
        event.currentTarget.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');

        const cards = document.querySelectorAll('.article-card');
        let visibleCount = 0;
        cards.forEach(card => {{
            const cardCat = (card.getAttribute('data-category') || '').toLowerCase();
            if (cat === 'all' || cardCat.includes(cat)) {{
                card.style.display = 'flex';
                visibleCount++;
            }} else {{
                card.style.display = 'none';
            }}
        }});
        document.getElementById('articleCount').innerText = visibleCount + ' Guides Displayed';
    }}
    </script>
        """
        
        full_html = self._render_header(
            title=config.BLOG_NAME,
            meta_desc=config.BLOG_DESCRIPTION
        ).replace("../", "") + index_content.replace("../", "") + self._render_footer().replace("../", "")

        index_file = os.path.join(self.output_dir, "index.html")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(full_html)

    def build_sitemap(self, articles: list):
        xml_items = []
        xml_items.append(f"""  <url>
    <loc>{config.BLOG_URL}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")
        for a in articles:
            xml_items.append(f"""  <url>
    <loc>{config.BLOG_URL}/posts/{a['slug']}.html</loc>
    <lastmod>{a['date']}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

        sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(xml_items)}
</urlset>"""
        with open(os.path.join(self.output_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(sitemap_xml)

    def build_rss_feed(self, articles: list):
        items = []
        for a in articles[:20]:
            items.append(f"""    <item>
      <title><![CDATA[{a['title']}]]></title>
      <link>{config.BLOG_URL}/posts/{a['slug']}.html</link>
      <guid>{config.BLOG_URL}/posts/{a['slug']}.html</guid>
      <description><![CDATA[{a['meta_description']}]]></description>
      <pubDate>{a['date']}</pubDate>
    </item>""")

        rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>{config.BLOG_NAME}</title>
    <link>{config.BLOG_URL}</link>
    <description>{config.BLOG_DESCRIPTION}</description>
{chr(10).join(items)}
  </channel>
</rss>"""
        with open(os.path.join(self.output_dir, "feed.xml"), "w", encoding="utf-8") as f:
            f.write(rss_xml)

    def build_robots_txt(self):
        robots = f"""User-agent: *
Allow: /
Sitemap: {config.BLOG_URL}/sitemap.xml
"""
        with open(os.path.join(self.output_dir, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(robots)

    def _generate_policy_pages(self):
        pages = {
            "about.html": ("About Us", f"Welcome to {config.BLOG_NAME}, your primary resource for insightful, well-researched guides on {config.BLOG_NICHE}."),
            "privacy-policy.html": ("Privacy Policy", f"At {config.BLOG_NAME}, we respect your privacy. We use cookies and third-party advertising partners like Google AdSense to serve relevant ads."),
            "terms.html": ("Terms of Service", f"By accessing {config.BLOG_NAME}, you agree to our standard terms of service."),
            "contact.html": ("Contact Us", f"Have questions or feedback? Reach out to the editorial team at contact@{config.BLOG_NAME.lower().replace(' ', '')}.com."),
            "disclaimer.html": ("Disclaimer", f"All content on {config.BLOG_NAME} is for educational and informational purposes.")
        }
        for filename, (title, content) in pages.items():
            filepath = os.path.join(self.output_dir, filename)
            if not os.path.exists(filepath):
                body = f"""
                <main class="max-w-4xl mx-auto px-4 py-12 flex-grow">
                    <div class="bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-12 shadow-sm border border-slate-100 dark:border-slate-800">
                        <h1 class="text-3xl sm:text-4xl font-extrabold font-display text-slate-900 dark:text-white mb-6">{title}</h1>
                        <div class="prose prose-slate dark:prose-invert leading-relaxed">
                            <p class="text-lg text-slate-600 dark:text-slate-300">{content}</p>
                        </div>
                    </div>
                </main>
                """
                full = self._render_header(title, title).replace("../", "") + body + self._render_footer().replace("../", "")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full)

    def _get_css(self) -> str:
        return """
        html { scroll-behavior: smooth; }
        .prose a { text-decoration: none; font-weight: 600; }
        .prose a:hover { text-decoration: underline; }
        .prose table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.95rem; }
        .prose th { background-color: #f1f5f9; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; text-align: left; font-weight: 700; }
        .dark .prose th { background-color: #1e293b; border-color: #334155; }
        .prose td { padding: 0.75rem 1rem; border: 1px solid #e2e8f0; }
        .dark .prose td { border-color: #334155; }
        """

    def _get_js(self) -> str:
        return """
        const themeBtn = document.getElementById('themeToggle');
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }

        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                document.documentElement.classList.toggle('dark');
                if (document.documentElement.classList.contains('dark')) {
                    localStorage.theme = 'dark';
                } else {
                    localStorage.theme = 'light';
                }
            });
        }

        window.addEventListener('scroll', () => {
            const bar = document.getElementById('progressBar');
            if (bar) {
                const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
                const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrolled = (winScroll / height) * 100;
                bar.style.width = scrolled + '%';
            }
        });
        """

static_publisher = StaticPublisher()
