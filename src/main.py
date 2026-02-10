import time
from config import load_sources, get_env_vars, load_sent_urls, save_sent_urls
from rss_fetcher import select_articles
from translator import translate_article
from discord_sender import send_article

def main():
    """主入口：抓取、LLM总结、推送"""
    print("Starting RSS Curator (V2)...")
    
    # 1. 加载配置
    sources_config = load_sources()
    env_vars = get_env_vars()
    sent_urls = load_sent_urls()
    
    print(f"Loaded {len(sources_config.get('sources', []))} sources")
    
    # 2. 获取文章（一次抓 20 条用于筛选）
    raw_articles = select_articles(sources_config, count=20)
    
    # 3. 过滤已发送的 URL
    new_articles = [a for a in raw_articles if a["link"] not in sent_urls]
    print(f"Found {len(new_articles)} new articles after filtering")
    
    if not new_articles:
        print("No new articles to process. Done!")
        return

    # 4. 限制发送篇数 (环境变量控制)
    max_to_send = env_vars.get("MAX_ARTICLES", 1)
    to_process = new_articles[:max_to_send]
    
    # 5. 循环处理每一篇：提取 -> 总结 -> 发送
    webhook_url = env_vars.get("DISCORD_WEBHOOK_URL")
    delay = env_vars.get("POST_DELAY_SEC", 5)
    
    processed_count = 0
    for i, article in enumerate(to_process):
        print(f"Processing ({i+1}/{len(to_process)}): {article['title'][:50]}...")
        
        # AI 总结
        processed_article = translate_article(article, env_vars)
        
        # 推送
        if send_article(processed_article, webhook_url):
            sent_urls.append(article["link"])
            processed_count += 1
            
            # 记录进度（每篇都存，防止崩溃丢失）
            save_sent_urls(sent_urls)
            
            # 间隔（最后一篇不延时）
            if i < len(to_process) - 1:
                print(f"Waiting {delay}s for next article...")
                time.sleep(delay)
    
    print(f"Successfully sent {processed_count} articles. Done!")

if __name__ == "__main__":
    main()
