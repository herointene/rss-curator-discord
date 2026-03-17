import os
import requests
from openai import OpenAI
import trafilatura

def extract_content(url):
    """提取网页正文"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            return text if text else ""
    except Exception as e:
        print(f"Content extraction error for {url}: {e}")
    return ""

def translate_article(article, env_vars):
    """使用 LLM 生成摘要并翻译"""
    api_key = env_vars.get("LLM_API_KEY")
    base_url = env_vars.get("LLM_BASE_URL")
    model = env_vars.get("LLM_MODEL")
    
    if not api_key:
        print("Warning: No LLM API key provided, skipping LLM processing")
        return article
        
    # 尝试抓取全文
    full_content = extract_content(article["link"])
    # 如果抓不到全文，使用 RSS description
    input_text = full_content if len(full_content) > 200 else article.get("summary", "")
    
    if not input_text:
        return article

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        prompt = f"""请将以下文章总结为 3 句重点，并直接用中文输出。
文章标题: {article['title']}
正文内容:
{input_text[:4000]}
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的新闻摘要助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        summary = response.choices[0].message.content.strip()
        article["summary_translated"] = summary
        
        # 生成點評（批判性、毒舌、不重複摘要）
        critique_prompt = f"""请针对以下新闻，用一句话给出批判性、毒舌的点评。
要求：
- 要有独立见解，不能只是重述新闻内容
- 语气可以犀利、讽刺，甚至刻薄
- 仅限一句话，50字以内

新闻标题: {article['title']}
新闻摘要: {summary}
"""
        
        critique_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个犀利、毒舌的新闻评论员，擅长一针见血地指出问题。"},
                {"role": "user", "content": critique_prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        article["critique"] = critique_response.choices[0].message.content.strip()
        
        # 同时翻译标题（如果不是中文）
        if article.get("source_lang") != "zh":
            title_response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": f"请将以下新闻标题翻译为中文，只要输出翻译结果：\n{article['title']}"}
                ],
                temperature=0.1
            )
            article["title_translated"] = title_response.choices[0].message.content.strip()
            
    except Exception as e:
        print(f"LLM processing error: {e}")
        
    return article
