from config import load_sources, get_env_vars
from rss_fetcher import select_articles
from translator import translate_article
from discord_sender import send_articles

def main():
    """主入口：抓取、翻译、推送"""
    print("Starting RSS Curator...")
    
    # 加载配置
    sources_config = load_sources()
    env_vars = get_env_vars()
    
    print(f"Loaded {len(sources_config.get('sources', []))} sources")
    
    # 选择文章
    articles = select_articles(sources_config, count=5)
    print(f"Selected {len(articles)} articles")
    
    # 翻译
    api_key = env_vars.get("GOOGLE_TRANSLATE_API_KEY")
    translated_articles = []
    for article in articles:
        translated = translate_article(article, api_key=api_key)
        translated_articles.append(translated)
    print(f"Translated {len(translated_articles)} articles")
    
    # 推送到 Discord
    webhook_url = env_vars.get("DISCORD_WEBHOOK_URL")
    send_articles(translated_articles, webhook_url=webhook_url)
    
    print("Done!")

if __name__ == "__main__":
    main()
