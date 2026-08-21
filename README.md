# ⚡ AutoBlog AI — 100% Free Autonomous Blog System

AutoBlog AI ek mukammal **100% Free / Zero-Cost** automated blogging system hai jo trending topics dhondta hai, live web research karta hai, 1500+ words ka human-like SEO article likhta hai, AI featured image generate karta hai, aur **GitHub Pages** par 24/7 cloud autopilot par publish karta hai!

---

## 🌟 Key Features (Khususiyaat)

1. **💸 100% Zero Cost ($0):**
   - AI Writer: **Google Gemini 2.0 / 1.5 Flash** (Free tier 1,500 articles/day)
   - Live Research: **DuckDuckGo Search Python** (Free, no API key needed)
   - AI Artwork: **Pollinations AI** (Free 16:9 HD images)
   - Hosting & 24/7 Cloud Automation: **GitHub Pages & GitHub Actions** (100% Free)
2. **📈 Google SEO & E-E-A-T Optimized:**
   - Real 2026 facts (no AI hallucinations)
   - Jump Table of Contents, Rich H2/H3s, Comparison Tables, Bullet Points
   - FAQ Section with JSON-LD Schema
   - Ultra-fast 100/100 Google PageSpeed score
3. **💰 Google AdSense Approval Ready:**
   - Pre-built **Privacy Policy, Terms of Service, About Us, Contact Us, Disclaimer** pages
   - Auto-generated `sitemap.xml` and `feed.xml` for instant Google indexing
   - Ready-made Ad slots (Header, In-article, Sidebar)
4. **☁️ 24/7 Cloud Autopilot (No PC Needed):**
   - GitHub Actions cloud me rozana scheduled time (e.g. har 6 ghantay baad) khud new articles generate karke live publish karta hai.

---

## 🚀 Quick Setup Guide (Step-by-Step)

### Step 1: Free Gemini API Key Hasil Karein
1. [https://aistudio.google.com/](https://aistudio.google.com/) par jayein.
2. Google account se login karke **"Get API key"** par click karein.
3. API key copy karein (ye 100% free hai).

### Step 2: Local Test Run Karein
Terminal ya PowerShell me yeh commands chalayein:

```powershell
# Dependencies install karein
pip install -r requirements.txt

# 1 Test Article Generate & Publish karein
python main.py --count 1
```

### Step 3: Web Control Center (Dashboard) Kholein
```powershell
streamlit run app.py
```

---

## ☁️ 24/7 Cloud Autopilot Kaise Setup Karein (GitHub Pages)?

Aapko apna computer on rakhne ki bilkul zaroorat nahi hai:

1. **GitHub par new repository banayein:**
   - GitHub.com par new repo banayein (e.g., `my-auto-blog`).
2. **Apna code GitHub par push karein:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/my-auto-blog.git
   git push -u origin main
   ```
3. **GitHub Secrets me Gemini API Key dalein:**
   - Repo me jayein -> **Settings** -> **Secrets and variables** -> **Actions**.
   - Click **"New repository secret"**.
   - Name: `GEMINI_API_KEY`, Secret: `Apki Gemini API key`.
4. **GitHub Pages On Karein:**
   - **Settings** -> **Pages** -> Source me **"Deploy from a branch"** select karein aur branch `gh-pages` select karein.

🎉 **Bas kaam hogaya!** Ab GitHub Actions 24/7 cloud par khud naye articles likhega aur live site par publish karta rahega!
