import os, json
from config import config

# 1. Load articles database
data_file = os.path.join(config.DATA_DIR, 'articles.json')
with open(data_file, 'r', encoding='utf-8') as f:
    articles = json.load(f)

# 2. Find and remove articles with no real content
empty_slugs = []
good_articles = []
for art in articles:
    md = art.get('markdown_content', '')
    slug = art.get('slug', 'unknown')
    if md and len(md) > 500:
        good_articles.append(art)
        print("  KEEP: {} ({} chars)".format(slug, len(md)))
    else:
        empty_slugs.append(slug)
        print("  REMOVE (empty): {} ({} chars)".format(slug, len(md)))

# 3. Save cleaned articles database
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(good_articles, f, indent=2, ensure_ascii=False)

# 4. Delete empty HTML post files
for slug in empty_slugs:
    post_file = os.path.join(config.POSTS_DIR, slug + '.html')
    if os.path.exists(post_file):
        os.remove(post_file)
        print("  Deleted: " + post_file)

# 5. Delete stale policy pages (to be regenerated with correct branding)
for page in ['about.html', 'privacy-policy.html', 'terms.html', 'contact.html', 'disclaimer.html']:
    filepath = os.path.join(config.OUTPUT_DIR, page)
    if os.path.exists(filepath):
        os.remove(filepath)
        print("  Deleted stale policy page: " + page)

print("\nCleaned: {} good articles kept, {} empty removed".format(len(good_articles), len(empty_slugs)))
