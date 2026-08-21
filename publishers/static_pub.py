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
    
    <!-- Google Fonts & Tailwind CDN -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        display: ['Space Grotesk', 'sans-serif'],
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
<body class="bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 min-h-screen flex flex-col font-sans transition-colors duration-200">
    <!-- Navbar -->
    <header class="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
            <a href="../index.html" class="flex items-center gap-2 text-2xl font-extrabold font-display bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                ⚡ {config.BLOG_NAME}
            </a>
            <nav class="hidden md:flex items-center gap-6 text-sm font-semibold">
                <a href="../index.html" class="hover:text-indigo-600 dark:hover:text-indigo-400">Home</a>
                <a href="../about.html" class="hover:text-indigo-600 dark:hover:text-indigo-400">About</a>
                <a href="../contact.html" class="hover:text-indigo-600 dark:hover:text-indigo-400">Contact</a>
                <a href="../privacy-policy.html" class="hover:text-indigo-600 dark:hover:text-indigo-400">Privacy</a>
            </nav>
            <div class="flex items-center gap-3">
                <button id="themeToggle" class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200" aria-label="Toggle Theme">
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
        <div class="max-w-6xl mx-auto px-4 sm:px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
            <div class="md:col-span-2">
                <h3 class="text-xl font-bold font-display text-indigo-600 dark:text-indigo-400 mb-2">⚡ {config.BLOG_NAME}</h3>
                <p class="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-4">{config.BLOG_DESCRIPTION}</p>
                <p class="text-xs text-slate-400">&copy; 2026 {config.BLOG_NAME}. All rights reserved.</p>
            </div>
            <div>
                <h4 class="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-white mb-3">Quick Links</h4>
                <ul class="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                    <li><a href="../index.html" class="hover:underline">Home</a></li>
                    <li><a href="../about.html" class="hover:underline">About Us</a></li>
                    <li><a href="../contact.html" class="hover:underline">Contact</a></li>
                    <li><a href="../sitemap.xml" class="hover:underline">Sitemap</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-white mb-3">Legal & Compliance</h4>
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

    def _render_post_page(self, article: dict, content_html: str) -> str:
        schema_json = json.dumps(article.get("faq_schema", {})) if article.get("faq_schema") else ""
        header = self._render_header(
            title=article["title"],
            meta_desc=article["meta_description"],
            canonical_url=f"{config.BLOG_URL}/posts/{article['slug']}.html",
            og_image=f"{config.BLOG_URL}/{article['featured_image']}",
            schema_json=schema_json
        )

        tags_html = "".join([f'<span class="px-3 py-1 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-full text-xs font-semibold">#{t}</span>' for t in article.get("tags", [])])

        adsense_box = """
        <div class="my-8 p-4 border border-dashed border-slate-300 dark:border-slate-700 rounded-xl text-center bg-slate-50 dark:bg-slate-800/40 text-xs text-slate-400">
            <span>Advertisement</span>
            <div class="min-h-[100px] flex items-center justify-center font-mono">
                <!-- Google AdSense Ad Slot Auto -->
            </div>
        </div>
        """

        body = f"""
    <div id="progressBar" class="fixed top-0 left-0 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 z-50 transition-all duration-150" style="width: 0%"></div>

    <main class="max-w-4xl mx-auto px-4 sm:px-6 py-10 flex-grow">
        <nav class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-6 font-medium">
            <a href="../index.html" class="hover:underline">Home</a> &rsaquo;
            <span>{article['category']}</span> &rsaquo;
            <span class="truncate max-w-[200px]">{article['title']}</span>
        </nav>

        <article class="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-10 shadow-sm border border-slate-100 dark:border-slate-800">
            <div class="flex items-center gap-3 mb-4">
                <span class="px-3 py-1 bg-indigo-600 text-white rounded-lg text-xs font-bold uppercase tracking-wider">{article['category']}</span>
                <span class="text-xs text-slate-400">&bull; {article['date']}</span>
                <span class="text-xs text-slate-400">&bull; ⏱️ {article['read_time']} min read</span>
            </div>

            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-display leading-tight text-slate-900 dark:text-white mb-6">
                {article['title']}
            </h1>

            <p class="text-lg text-slate-600 dark:text-slate-300 mb-8 leading-relaxed font-medium">
                {article['meta_description']}
            </p>

            <div class="mb-10 rounded-2xl overflow-hidden shadow-lg border border-slate-100 dark:border-slate-800">
                <img src="../{article['featured_image']}" alt="{article['title']}" class="w-full h-auto object-cover max-h-[480px]" loading="lazy">
            </div>

            {adsense_box}

            <div class="prose prose-slate dark:prose-invert max-w-none prose-headings:font-display prose-headings:font-bold prose-h2:text-2xl sm:prose-h2:text-3xl prose-h2:mt-10 prose-h2:mb-4 prose-h3:text-xl prose-p:leading-relaxed prose-a:text-indigo-600 dark:prose-a:text-indigo-400 prose-img:rounded-2xl prose-table:border prose-table:shadow-sm">
                {content_html}
            </div>

            {adsense_box}

            <div class="mt-12 pt-6 border-t border-slate-200 dark:border-slate-800 flex flex-wrap gap-2 items-center">
                <span class="text-xs font-bold text-slate-400 uppercase mr-2">Tags:</span>
                {tags_html}
            </div>

            <div class="mt-10 p-6 bg-slate-50 dark:bg-slate-800/60 rounded-2xl flex items-center gap-4 border border-slate-200 dark:border-slate-700">
                <div class="w-14 h-14 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
                    ✍️
                </div>
                <div>
                    <h4 class="font-bold text-slate-900 dark:text-white">{config.BLOG_AUTHOR}</h4>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        Researched, verified, and curated by the {config.BLOG_NAME} tech editorial team.
                    </p>
                </div>
            </div>
        </article>
    </main>
"""
        return header + body + self._render_footer()

    def build_home_page(self, articles: list):
        featured = articles[0] if articles else None
        grid_articles = articles[1:] if len(articles) > 1 else []

        cards_html = ""
        for art in grid_articles:
            cards_html += f"""
            <article class="bg-white dark:bg-slate-900 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow border border-slate-100 dark:border-slate-800 flex flex-col">
                <a href="posts/{art['slug']}.html" class="block overflow-hidden aspect-video">
                    <img src="{art['featured_image']}" alt="{art['title']}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-300" loading="lazy">
                </a>
                <div class="p-6 flex flex-col flex-grow">
                    <div class="flex items-center gap-2 text-xs font-semibold text-indigo-600 dark:text-indigo-400 mb-2">
                        <span>{art['category']}</span> &bull; <span>{art['date']}</span>
                    </div>
                    <h3 class="text-xl font-bold font-display text-slate-900 dark:text-white mb-3 hover:text-indigo-600 transition-colors line-clamp-2">
                        <a href="posts/{art['slug']}.html">{art['title']}</a>
                    </h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400 line-clamp-3 mb-4 flex-grow">
                        {art['meta_description']}
                    </p>
                    <div class="flex items-center justify-between text-xs text-slate-400 pt-4 border-t border-slate-100 dark:border-slate-800">
                        <span>⏱️ {art['read_time']} min read</span>
                        <a href="posts/{art['slug']}.html" class="font-bold text-indigo-600 dark:text-indigo-400 hover:underline">Read Guide &rarr;</a>
                    </div>
                </div>
            </article>
            """

        hero_html = ""
        if featured:
            hero_html = f"""
            <div class="mb-14 bg-gradient-to-br from-indigo-900 to-slate-900 rounded-3xl p-6 sm:p-10 text-white shadow-xl relative overflow-hidden border border-indigo-700/30">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                    <div>
                        <span class="px-3 py-1 bg-indigo-500/30 text-indigo-200 border border-indigo-400/30 rounded-full text-xs font-bold uppercase tracking-wider mb-4 inline-block">🌟 Featured Guide</span>
                        <h2 class="text-2xl sm:text-4xl font-extrabold font-display leading-tight mb-4 hover:text-indigo-300 transition-colors">
                            <a href="posts/{featured['slug']}.html">{featured['title']}</a>
                        </h2>
                        <p class="text-sm sm:text-base text-slate-300 mb-6 line-clamp-3 leading-relaxed">
                            {featured['meta_description']}
                        </p>
                        <div class="flex items-center gap-4">
                            <a href="posts/{featured['slug']}.html" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm transition-colors shadow-lg">Read Complete Article</a>
                            <span class="text-xs text-slate-400">⏱️ {featured['read_time']} min read</span>
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
        <div class="text-center max-w-2xl mx-auto mb-12">
            <h1 class="text-4xl sm:text-5xl font-extrabold font-display tracking-tight text-slate-900 dark:text-white mb-4">
                {config.BLOG_TAGLINE}
            </h1>
            <p class="text-base sm:text-lg text-slate-600 dark:text-slate-300">
                {config.BLOG_DESCRIPTION}
            </p>
        </div>

        {hero_html}

        <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl font-bold font-display text-slate-900 dark:text-white">Latest Articles</h2>
            <span class="text-xs font-semibold px-3 py-1 bg-slate-200 dark:bg-slate-800 rounded-full text-slate-600 dark:text-slate-400">{len(articles)} Guides Published</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {cards_html if cards_html else '<p class="col-span-3 text-center text-slate-400 py-12">Generating first articles... Please check back in a few moments.</p>'}
        </div>
    </main>
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
