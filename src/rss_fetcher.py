import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
import random
from datetime import datetime

def fetch_feed(url):
    """抓取 RSS feed"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            
        # 解析 XML
        root = ET.fromstring(data)
        
        # 处理 RSS 2.0 和 Atom 格式
        entries = []
        
        # RSS 2.0
        if root.tag == 'rss':
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item'):
                    entry = {
                        'title': item.findtext('title', ''),
                        'link': item.findtext('link', ''),
                        'description': item.findtext('description', ''),
                        'published': item.findtext('pubDate', ''),
                    }
                    entries.append(entry)
        
        # Atom
        elif root.tag.endswith('feed'):
            for entry_elem in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                entry = {
                    'title': entry_elem.findtext('{http://www.w3.org/2005/Atom}title', ''),
                    'link': '',
                    'description': entry_elem.findtext('{http://www.w3.org/2005/Atom}summary', ''),
                    'published': entry_elem.findtext('{http://www.w3.org/2005/Atom}updated', ''),
                }
                # 获取 link
                link_elem = entry_elem.find('{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    entry['link'] = link_elem.get('href', '')
                entries.append(entry)
        
        return entries
        
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
                "summary": entry.get("description", entry.get("summary", ""))[:500],
                "published": entry.get("published", ""),
                "source_name": source["name"],
                "source_lang": source.get("lang", "en"),
                "weight": source.get("weight", 1.0)
            }
            all_articles.append(article)
    
    # 去重
    seen_links = set()
    unique_articles = []
    for article in all_articles:
        if article["link"] not in seen_links:
            seen_links.add(article["link"])
            unique_articles.append(article)
    
    # 加权随机选择
    if not unique_articles:
        return []
    
    weights = [a["weight"] for a in unique_articles]
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0] * len(unique_articles)
    
    selected = random.choices(unique_articles, weights=weights, k=min(count, len(unique_articles)))
    return selected
