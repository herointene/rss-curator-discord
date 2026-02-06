import feedparser
import random
from datetime import datetime, timedelta

def fetch_feed(url):
    """抓取 RSS feed"""
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def select_articles(sources_config, count=5):
    """按权重选择文章"""
    sources = sources_config.get("sources", [])
    all_articles = []
    
    # 获取所有文章
    for source in sources:
        entries = fetch_feed(source["url"])
        for entry in entries[:10]:  # 每个源取前10条
            article = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", entry.get("description", ""))[:500],
                "published": entry.get("published", ""),
                "source_name": source["name"],
                "source_lang": source.get("lang", "en"),
                "weight": source.get("weight", 1.0)
            }
            all_articles.append(article)
    
    # 按权重加权随机选择
    if not all_articles:
        return []
    
    # 去重
    seen_links = set()
    unique_articles = []
    for article in all_articles:
        if article["link"] not in seen_links:
            seen_links.add(article["link"])
            unique_articles.append(article)
    
    # 加权随机选择
    weights = [a["weight"] for a in unique_articles]
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0] * len(unique_articles)
    
    selected = random.choices(unique_articles, weights=weights, k=min(count, len(unique_articles)))
    return selected
