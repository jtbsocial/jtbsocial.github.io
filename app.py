import os
import sys
import json
import streamlit as st
from config import config
from topic_hunter import topic_hunter
from main import run_pipeline

st.set_page_config(
    page_title="AutoBlog AI Control Center",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #4F46E5; }
    .metric-card { background-color: #f8fafc; border-radius: 12px; padding: 15px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ AutoBlog AI — 100% Free Autonomous Blog System</h1>", unsafe_allow_html=True)
st.caption("Zero-Cost Auto-Blogging with Gemini AI, DuckDuckGo Research, Pollinations AI Images & GitHub Pages")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Google Gemini API Key (Free)",
        value=config.GEMINI_API_KEY,
        type="password",
        help="Get your 100% Free API key from https://aistudio.google.com"
    )
    if api_key != config.GEMINI_API_KEY:
        config.GEMINI_API_KEY = api_key
        os.environ["GEMINI_API_KEY"] = api_key

    st.markdown("---")
    st.subheader("📝 Blog Details")
    blog_name = st.text_input("Blog Name", value=config.BLOG_NAME)
    blog_tagline = st.text_input("Blog Tagline", value=config.BLOG_TAGLINE)
    blog_niche = st.selectbox(
        "Niche / Category",
        ["Artificial Intelligence & Tech", "Digital Marketing & SEO", "Personal Finance & Side Hustles", "Health & Fitness", "Gaming & Gadgets", "Custom"]
    )
    
    st.markdown("---")
    st.subheader("📢 Social Media Auto-Poster")
    tg_token = st.text_input("Telegram Bot Token", value=os.getenv("TELEGRAM_BOT_TOKEN", ""), type="password")
    tg_chat = st.text_input("Telegram Channel ID", value=os.getenv("TELEGRAM_CHAT_ID", ""), placeholder="@yourchannel")
    dc_hook = st.text_input("Discord Webhook URL", value=os.getenv("DISCORD_WEBHOOK_URL", ""), type="password")
    
    if tg_token:
        os.environ["TELEGRAM_BOT_TOKEN"] = tg_token
    if tg_chat:
        os.environ["TELEGRAM_CHAT_ID"] = tg_chat
    if dc_hook:
        os.environ["DISCORD_WEBHOOK_URL"] = dc_hook

    st.markdown("---")
    st.markdown("### 💰 AdSense Approval Checklist")
    st.checkbox("✅ Privacy Policy Page", value=True, disabled=True)
    st.checkbox("✅ Terms of Service Page", value=True, disabled=True)
    st.checkbox("✅ About & Contact Pages", value=True, disabled=True)
    st.checkbox("✅ Google Sitemap & RSS Feed", value=True, disabled=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚀 1-Click Content Generation")
    
    topic_mode = st.radio("Topic Source", ["Auto Hunter (Trending & High-CPC Seeds)", "Custom Topic"], horizontal=True)
    
    custom_topic = None
    if topic_mode == "Custom Topic":
        custom_topic = st.text_input("Enter Topic or Keyword", placeholder="e.g. 10 Best Free AI Video Generators in 2026")
    
    if st.button("✨ Generate & Publish Article Now", type="primary", use_container_width=True):
        with st.status("🚀 Running Autonomous Blogging Pipeline...", expanded=True) as status:
            st.write("1. 🎯 Sourcing topic and trends...")
            st.write("2. 🔍 Conducting live DuckDuckGo web research...")
            st.write("3. ✍️ Drafting 1,500+ words E-E-A-T article with Gemini...")
            st.write("4. 🎨 Generating 16:9 HD featured image with Pollinations AI...")
            st.write("5. 🌐 Compiling static HTML, sitemap.xml, and RSS feed...")
            
            result = run_pipeline(custom_topic)
            status.update(label="✅ Article Generated & Published Successfully!", state="complete", expanded=False)
            
        st.success(f"🎉 Published: **{result['title']}**")
        st.info(f"📂 Local File: `site/posts/{result['slug']}.html`")

with col2:
    st.subheader("📊 Blog Stats")
    articles_data_path = os.path.join(config.DATA_DIR, "articles.json")
    articles = []
    if os.path.exists(articles_data_path):
        try:
            with open(articles_data_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception:
            pass

    st.metric("Total Published Posts", len(articles))
    st.metric("Estimated Cost Spent", "$0.00 (100% Free)")
    
    st.markdown("---")
    st.markdown("### 🌐 Quick Preview")
    site_index = os.path.abspath(os.path.join(config.OUTPUT_DIR, "index.html"))
    if os.path.exists(site_index):
        st.markdown(f"[🔗 Open Blog in Browser](file:///{site_index.replace(chr(92), '/')})")

st.markdown("---")
st.subheader("📚 Recently Published Articles")

if articles:
    for art in articles[:6]:
        with st.expander(f"📌 {art.get('title')} ({art.get('date')})"):
            c1, c2 = st.columns([1, 3])
            with c1:
                img_path = os.path.join(config.OUTPUT_DIR, art.get('featured_image', ''))
                if os.path.exists(img_path):
                    st.image(img_path)
            with c2:
                st.write(f"**Category:** {art.get('category')} | **Read Time:** {art.get('read_time')} min")
                st.write(art.get('meta_description'))
                st.markdown(f"**Tags:** {', '.join(art.get('tags', []))}")
else:
    st.info("No articles published yet. Click the 'Generate & Publish Article Now' button above to create your first article!")
