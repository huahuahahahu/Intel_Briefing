#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIT Technology Review Sensor
从 MIT Technology Review 官方 RSS 抓取深度科技分析文章

数据源: https://www.technologyreview.com/feed/
协议: RSS 2.0 (公开、免费、合法)
更新频率: 每日
"""

import re
import urllib.request
import xml.etree.ElementTree as ET
import ssl
from dataclasses import dataclass, field
from typing import List, Optional


RSS_URL = "https://www.technologyreview.com/feed/"
FETCH_TIMEOUT = 15


@dataclass
class MITArticle:
    """An MIT Technology Review article."""
    title: str
    url: str
    description: str
    author: str = ""
    pub_date: str = ""
    categories: List[str] = field(default_factory=list)

    @property
    def source_label(self) -> str:
        return "MIT Technology Review"


def _strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    clean = clean.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', clean).strip()


def _create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_mit_review(limit: int = 5) -> List[MITArticle]:
    """
    Fetch latest articles from MIT Technology Review RSS.

    Args:
        limit: Maximum number of articles to return

    Returns:
        List of MITArticle objects
    """
    print(f"  → Fetching MIT Technology Review RSS (top {limit})...")

    try:
        req = urllib.request.Request(RSS_URL, headers={
            "User-Agent": "Intel-Briefing-RSS-Reader/2.0"
        })
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT, context=_create_ssl_context()) as resp:
            xml_data = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    [ERROR] MIT TR RSS fetch failed: {e}")
        return []

    articles = []
    try:
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')

        for item in items[:limit]:
            title_el = item.find('title')
            link_el = item.find('link')
            desc_el = item.find('description')
            creator_el = item.find('{http://purl.org/dc/elements/1.1/}creator')
            pub_el = item.find('pubDate')
            cat_els = item.findall('category')

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            url = link_el.text.strip() if link_el is not None and link_el.text else ""
            description = _strip_html(desc_el.text) if desc_el is not None and desc_el.text else ""
            author = creator_el.text.strip() if creator_el is not None and creator_el.text else ""
            pub_date = pub_el.text[:16] if pub_el is not None and pub_el.text else ""
            categories = [c.text for c in cat_els if c.text]

            if title and url:
                articles.append(MITArticle(
                    title=title,
                    url=url,
                    description=description,
                    author=author,
                    pub_date=pub_date,
                    categories=categories
                ))
    except ET.ParseError as e:
        print(f"    [ERROR] MIT TR XML parse error: {e}")
    except Exception as e:
        print(f"    [ERROR] MIT TR parse error: {e}")

    print(f"    Fetched {len(articles)} articles from MIT Technology Review")
    return articles


# CLI test
if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    articles = fetch_mit_review(limit)
    print(f"\n{'='*60}")
    print(f"  🔬 MIT Technology Review Top {limit}")
    print(f"{'='*60}\n")
    for i, a in enumerate(articles, 1):
        print(f"{i}. {a.title}")
        print(f"   ✍️ {a.author} | 🏷️ {', '.join(a.categories[:3])}")
        print(f"   📝 {a.description[:120]}...")
        print(f"   🔗 {a.url}")
        print()
