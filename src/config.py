import json
import os
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
DATA_DIR = Path(__file__).parent.parent / "data"

def load_sources():
    """加载 RSS 源配置"""
    with open(CONFIG_DIR / "sources.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_candidates():
    """加载候选源配置"""
    with open(CONFIG_DIR / "candidates.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_ratings():
    """加载评分数据"""
    ratings_file = DATA_DIR / "ratings.json"
    if ratings_file.exists():
        with open(ratings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_ratings(ratings):
    """保存评分数据"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "ratings.json", "w", encoding="utf-8") as f:
        json.dump(ratings, f, ensure_ascii=False, indent=2)

def load_sent_urls():
    """加载已发送的 URL 列表"""
    sent_file = DATA_DIR / "sent_urls.json"
    if sent_file.exists():
        try:
            with open(sent_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_sent_urls(urls):
    """保存已发送的 URL 列表（保留最近 1000 条）"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "sent_urls.json", "w", encoding="utf-8") as f:
        json.dump(urls[-1000:], f, ensure_ascii=False, indent=2)

def get_env_vars():
    """获取环境变量"""
    return {
        "LLM_API_KEY": os.environ.get("LLM_API_KEY"),
        "LLM_BASE_URL": os.environ.get("LLM_BASE_URL", "https://api.moonshot.cn/v1"),
        "LLM_MODEL": os.environ.get("LLM_MODEL", "moonshot-v1-8k"),
        "DISCORD_WEBHOOK_URL": os.environ.get("DISCORD_WEBHOOK_URL"),
        "MAX_ARTICLES": int(os.environ.get("MAX_ARTICLES", "1")),
        "POST_DELAY_SEC": int(os.environ.get("POST_DELAY_SEC", "5"))
    }
