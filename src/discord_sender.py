import requests
import os

def send_article(article, webhook_url=None):
    """发送单篇文章到 Discord"""
    if not webhook_url:
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("Error: No Discord webhook URL provided")
        return False
    
    # 构建消息
    title = article.get("title_translated") or article.get("title", "")
    summary = article.get("summary_translated") or article.get("summary", "")[:150]
    link = article.get("link", "")
    source = article.get("source_name", "")
    
    # 标题做成超链接 [标题](链接)
    content = f"📰 [**{title}**]({link})\n\n"
    content += f"📝 {summary}\n\n"
    
    # 添加點評（如果有）
    critique = article.get("critique", "")
    if critique:
        content += f"【點評】{critique}\n\n"
    
    content += f"📡 来源: {source}\n"
    content += "👍 👎 （点击表情投票）"
    
    payload = {
        "content": content
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        print(f"Sent: {title[:50]}...")
        return True
    except Exception as e:
        # Mask webhook URL in error logs
        error_msg = str(e).replace(webhook_url, "******") if webhook_url else str(e)
        print(f"Error sending to Discord: {error_msg}")
        return False

def send_articles(articles, webhook_url=None):
    """发送多篇文章到 Discord"""
    success_count = 0
    for article in articles:
        if send_article(article, webhook_url):
            success_count += 1
    print(f"Sent {success_count}/{len(articles)} articles")
    return success_count
