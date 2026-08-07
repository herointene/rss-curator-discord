import os
import requests
import json
import re
from openai import OpenAI
import trafilatura


def extract_content(url):
    """提取网页正文"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_precision=True,
            )
            return text if text else ""
    except Exception as e:
        print(f"Content extraction error for {url}: {e}")
    return ""


def _call_llm(client, model, system_prompt, user_prompt):
    """调用 LLM 并返回原始 content 字符串"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()


def _parse_json_from_text(text):
    """从 LLM 回复中提取 JSON 对象，容忍 markdown 包裹和多余文字"""
    # 先去掉 markdown 代码块
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # 直接尝试解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 花括号匹配
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


def _build_input_text(article):
    """构建送入 LLM 的文本，中文源优先用全文"""
    is_zh = article.get("source_lang", "en") == "zh"
    rss_summary = article.get("summary", "")
    full_content = extract_content(article["link"])

    if is_zh:
        # 中文源：如果全文抓得到且有意义，用全文；否则用 RSS 描述
        if full_content and len(full_content) > 100:
            return full_content[:6000], "full"
        elif rss_summary and len(rss_summary) > 30:
            return rss_summary, "rss"
        else:
            # 两者都不行，再试一次全文（可能 trafilatura 第一次失败了）
            return full_content[:6000] if full_content else rss_summary, "retry"
    else:
        # 英文源：全文优先，RSS 作兜底
        if full_content and len(full_content) > 200:
            return full_content[:6000], "full"
        return rss_summary[:2000], "rss"


def translate_article(article, env_vars):
    """使用 LLM 生成摘要、点评和翻译（合并为单次调用）"""
    api_key = env_vars.get("LLM_API_KEY")
    base_url = env_vars.get("LLM_BASE_URL", "https://api.moonshot.cn/v1")
    model = env_vars.get("LLM_MODEL", "moonshot-v1-8k")

    if not api_key:
        print("Warning: No LLM API key provided, skipping LLM processing")
        return article

    # 构建输入文本
    input_text, source_type = _build_input_text(article)

    if not input_text or len(input_text) < 10:
        print(f"Warning: No usable content for {article['title'][:40]}")
        return article

    title = article.get("title", "")
    source_lang = article.get("source_lang", "en")

    # 根据源语言构建不同的 prompt
    if source_lang == "zh":
        system_prompt = (
            "你是专业的中文科技新闻编辑。你收到的文章已经是中文，"
            "你需要提炼精华、去粗取精，用高质量的中文输出。"
            "严格返回 JSON 格式，不要包含任何其他文字。"
        )
        user_prompt = f"""请将以下中文文章处理为三个部分，用 JSON 格式返回：
1. summary: 用3句话总结文章核心信息（中文，要精炼、有信息量，不要重复原文废话）
2. critique: 用一句话给出犀利、有趣的点评（50字以内，带点毒舌）
3. title_zh: 保持原标题不变

文章标题: {title}
来源: {article.get("source_name", "")}

文章内容:
{input_text[:5000]}

返回格式必须是有效的 JSON: {{"summary": "...", "critique": "...", "title_zh": "..."}}"""
    else:
        system_prompt = (
            "You are a professional Chinese tech news editor. "
            "Summarize the English article in fluent, natural Chinese. "
            "Return only valid JSON, nothing else."
        )
        user_prompt = f"""请将以下英文文章处理为三个部分，用 JSON 格式返回：
1. summary: 用3句话总结文章核心信息（中文，翻译要自然流畅，像原生中文科技报道）
2. critique: 用一句话给出犀利、有趣的中文点评（50字以内，带点毒舌）
3. title_zh: 将标题翻译为自然的中文

文章标题: {title}

文章内容:
{input_text[:5000]}

返回格式必须是有效的 JSON: {{"summary": "...", "critique": "...", "title_zh": "..."}}"""

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)

        # 最多重试 2 次
        result = None
        for attempt in range(3):
            raw = _call_llm(client, model, system_prompt, user_prompt)
            result = _parse_json_from_text(raw)
            if result and result.get("summary"):
                break
            print(f"  Attempt {attempt + 1}: JSON parse failed, retrying...")

        if not result or not result.get("summary"):
            print(f"  LLM failed to produce valid output for: {title[:50]}")
            return article

        article["summary_translated"] = result["summary"].strip()
        article["critique"] = result.get("critique", "").strip()
        article["title_translated"] = result.get("title_zh", title).strip()

    except Exception as e:
        print(f"LLM processing error: {e}")

    return article
