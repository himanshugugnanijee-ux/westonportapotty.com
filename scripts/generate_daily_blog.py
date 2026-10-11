#!/usr/bin/env python3
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TODAY = dt.date.today().isoformat()


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def request_article():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        fail("OPENAI_API_KEY GitHub secret is required")
    prompt = f"""Create one original local SEO blog article for RapidClean Portable Toilet Rental Works in Weston, Florida, serving Weston and Broward County. Publication date: {TODAY}. Cover a practical porta-potty planning topic that is different from existing articles. Do not make unsupported claims, do not invent awards or customer reviews, and do not mention being AI-generated. Return valid JSON only with these keys: title (55-70 characters), slug (lowercase hyphenated, no date), description (145-160 characters), category (2-4 words), read_time (for example '7 min read'), and body_html. body_html must be 900-1200 words of accessible HTML using only h2, h3, p, ul, ol, li, and strong. Include useful Weston/Broward references naturally, a clear quote CTA, and an FAQ section with 3 h3 questions and answers. The article should be helpful first and not keyword stuffed."""
    payload = {"model": MODEL, "temperature": 0.7, "response_format": {"type": "json_object"}, "messages": [
        {"role": "system", "content": "You write accurate, conversion-focused local service content."},
        {"role": "user", "content": prompt},
    ]}
    request = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)
    except Exception as exc:
        fail(f"OpenAI request failed: {exc}")
    try:
        article = json.loads(result["choices"][0]["message"]["content"])
        required = ["title", "slug", "description", "category", "read_time", "body_html"]
        if any(not article.get(key) for key in required):
            fail("AI response omitted a required article field")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", article["slug"]):
            fail("AI returned an invalid slug")
        if re.search(r"<script|<style|on[a-z]+=", article["body_html"], re.I):
            fail("AI response contained unsafe HTML")
        return article
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        fail(f"Could not parse article response: {exc}")


def render_page(article):
    template = (ROOT / "how-many-portable-toilets-do-i-need.html").read_text()
    title = html.escape(article["title"])
    description = html.escape(article["description"])
    slug = article["slug"]
    url = f"https://westonportapotty.com/{slug}.html"
    page = re.sub(r"<title>.*?</title>", f"<title>{title} | Weston, FL Portable Toilet Rental</title>", template, count=1)
    page = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{description}">', page, count=1)
    page = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{url}">', page, count=1)
    page = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{title}">', page, count=1)
    page = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{description}">', page, count=1)
    page = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{url}">', page, count=1)
    page = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{title}">', page, count=1)
    page = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{description}">', page, count=1)
    page = re.sub(r'"headline":\s*".*?"', f'"headline": {json.dumps(article["title"])}', page, count=1)
    page = re.sub(r'"description":\s*".*?"', f'"description": {json.dumps(article["description"])}', page, count=1)
    page = re.sub(r'"datePublished":\s*".*?"', f'"datePublished": {json.dumps(TODAY)}', page, count=1)
    page = re.sub(r'(<main[\s\S]*?<div class="article-layout">)[\s\S]*?(</div>\s*</main>)', lambda m: m.group(1) + f'\n<div class="article-layout"><article class="article-body"><div class="eyebrow">{html.escape(article["category"])} · {html.escape(article["read_time"])}</div><h1>{title}</h1><p class="article-intro">{description}</p>{article["body_html"]}</article></div>\n' + m.group(2), page, count=1)
    return page


def update_blog(article):
    path = ROOT / "blog.html"
    page = path.read_text()
    slug = article["slug"]
    card = f'''  <article class="blog-card">\n    <a href="{slug}.html" class="blog-card-img" tabindex="-1" aria-hidden="true">\n      <img src="images/event-hero.jpg" alt="" loading="lazy" width="900" height="600">\n    </a>\n    <div class="blog-card-body">\n      <div class="blog-meta"><span>{html.escape(article["category"])}</span><span>{dt.date.today().strftime("%B %Y")}</span><span>{html.escape(article["read_time"])}</span></div>\n      <h3><a href="{slug}.html">{html.escape(article["title"])}</a></h3>\n      <p>{html.escape(article["description"])}</p>\n      <a href="{slug}.html" class="btn btn-blue">Read The Guide</a>\n    </div>\n  </article>\n'''
    marker = '  </div>\n  </div>\n  </section>'
    if marker not in page:
        fail("Could not find blog card container")
    page = page.replace(marker, card + marker, 1)
    path.write_text(page)


def update_sitemap(article):
    path = ROOT / "sitemap.xml"
    content = path.read_text()
    url = f"https://westonportapotty.com/{article['slug']}.html"
    if url not in content:
        entry = f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
        content = content.replace("</urlset>", entry + "</urlset>")
        path.write_text(content)


def main():
    article = request_article()
    target = ROOT / f"{article['slug']}.html"
    if target.exists():
        fail(f"article already exists: {target.name}")
    target.write_text(render_page(article))
    update_blog(article)
    update_sitemap(article)
    print(f"Published {target.name}")


if __name__ == "__main__":
    main()
  
