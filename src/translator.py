import os
import requests
import json
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
    """使用 LLM 生成摘要、点评和翻译（合并为单次调用）"""
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
        
        # 合并为单次调用，使用 JSON 格式返回
        prompt = f"""请将以下文章处理为三个部分，用 JSON 格式返回：
1. summary: 用3句话总结文章重点（中文）
2. critique: 用一句话给出批判性、毒舌的点评（50字以内，犀利讽刺）
3. title_zh: 将标题翻译为中文（如果是中文标题则保持不变）

文章标题: {article['title']}
正文内容:
{input_text[:4000]}

返回格式必须是有效的 JSON: {{"summary": "...", "critique": "...", "title_zh": "..."}}"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的新闻摘要助手和犀利评论员。请严格返回 JSON 格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        
        # 尝试提取 JSON（处理可能的 markdown 代码块包裹）
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # 尝试解析 JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，用花括号匹配提取完整 JSON 对象
            import re
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end > start:
                try:
                    result = json.loads(content[start:end+1])
                except json.JSONDecodeError:
                    raise ValueError(f"Cannot parse JSON from response: {content[:200]}")
            else:
                raise ValueError(f"Cannot extract JSON from response: {content[:200]}")
        
        article["summary_translated"] = result.get("summary", "")
        article["critique"] = result.get("critique", "")
        article["title_translated"] = result.get("title_zh", article["title"])
        
    except Exception as e:
        print(f"LLM processing error: {e}")
        # 出错时保留原文
        
    return article
