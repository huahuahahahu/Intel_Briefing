"""
Reddit Sensor - 利用 Reddit RSS Feed 获取技术社区热点讨论
无需 API Key，替代 Grok 的 X/Twitter 社交扫描功能。

每个 subreddit 请求间隔 8 秒避免 429 限速。

数据源：r/MachineLearning, r/LocalLLaMA, r/artificial
"""

import sys
import time
import re
import httpx
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REDDIT_RSS = "https://www.reddit.com/r/{subreddit}/.rss"
USER_AGENT = "IntelBriefing/2.0"
REQUEST_DELAY = 8
ATOM_NS = "http://www.w3.org/2005/Atom"

SUBREDDITS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
]

# Sticky/meta post title patterns to skip
STICKY_PATTERNS = [
    r"(?i)self.promotion\s*thread",
    r"(?i)who.?s?\s*hiring",
    r"(?i)monthly\s+(thread|discussion)",
    r"(?i)weekly\s+(thread|discussion)",
    r"(?i)^\[D\]\s*(Self-Promotion|Hiring|Monthly|Weekly)",
]


def _is_sticky(title: str) -> bool:
    for pattern in STICKY_PATTERNS:
        if re.search(pattern, title):
            return True
    return False


def _fetch_subreddit(subreddit: str, limit: int = 5) -> list[dict]:
    """Fetch posts from a single subreddit via RSS."""
    url = REDDIT_RSS.format(subreddit=subreddit)
    headers = {"User-Agent": USER_AGENT}
    try:
        response = httpx.get(url, headers=headers, timeout=15)
        if response.status_code == 429:
            logger.warning(f"Reddit r/{subreddit} rate limited (429), skipping.")
            return []
        response.raise_for_status()
    except Exception as e:
        logger.warning(f"Reddit r/{subreddit} fetch failed: {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        logger.warning(f"Reddit r/{subreddit} RSS parse failed: {e}")
        return []

    posts = []
    entries = root.findall(f"{{{ATOM_NS}}}entry")

    for entry in entries:
        title_el = entry.find(f"{{{ATOM_NS}}}title")
        link_el = entry.find(f"{{{ATOM_NS}}}link")
        author_el = entry.find(f"{{{ATOM_NS}}}author")

        title = title_el.text if title_el is not None else ""
        if _is_sticky(title):
            continue

        link = link_el.get("href") if link_el is not None else ""
        author_name = ""
        if author_el is not None:
            name_el = author_el.find(f"{{{ATOM_NS}}}name")
            author_name = name_el.text if name_el is not None else ""

        posts.append({
            "title": title,
            "url": link,
            "author": f"u/{author_name}" if author_name else "unknown",
            "heat": f"r/{subreddit}",
            "subreddit": subreddit,
            "score": 0,
        })

        if len(posts) >= limit:
            break

    return posts


def fetch_reddit_hot(limit_per_sub: int = 3) -> list[dict]:
    """
    从多个技术 subreddit 抓取热门帖子。

    Args:
        limit_per_sub: 每个 subreddit 抓取数量
    """
    all_posts = []
    for sub in SUBREDDITS:
        posts = _fetch_subreddit(sub, limit=limit_per_sub)
        all_posts.extend(posts)
        print(f"  r/{sub}: {len(posts)} posts")
        time.sleep(REQUEST_DELAY)

    return all_posts
