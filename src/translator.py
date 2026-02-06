import requests
import os

def translate_text(text, target_lang='zh', api_key=None):
    """使用 Google Translate API 翻译文本"""
    if not api_key:
        api_key = os.environ.get("GOOGLE_TRANSLATE_API_KEY")
    
    if not api_key:
        print("Warning: No Google Translate API key provided")
        return text
    
    # 如果文本为空或太短，直接返回
    if not text or len(text.strip()) < 10:
        return text
    
    url = "https://translation.googleapis.com/language/translate/v2"
    
    params = {
        "key": api_key,
        "q": text[:1000],  # API 限制
        "target": target_lang,
        "format": "text"
    }
    
    try:
        response = requests.post(url, data=params, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "data" in result and "translations" in result["data"]:
            return result["data"]["translations"][0]["translatedText"]
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_article(article, api_key=None):
    """翻译文章标题和摘要"""
    if article.get("source_lang") == "zh":
        # 中文文章不需要翻译
        return article
    
    # 翻译标题
    if article.get("title"):
        article["title_translated"] = translate_text(article["title"], api_key=api_key)
    
    # 翻译摘要（限制长度）
    if article.get("summary"):
        summary = article["summary"][:300]  # 取前300字符翻译
        article["summary_translated"] = translate_text(summary, api_key=api_key)
    
    return article
