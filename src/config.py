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
    with open(DATA_DIR / "ratings.json", "w", encoding="utf-8") as f:
        json.dump(ratings, f, ensure_ascii=False, indent=2)

def get_env_vars():
    """获取环境变量"""
    return {
        "GOOGLE_TRANSLATE_API_KEY": os.environ.get("GOOGLE_TRANSLATE_API_KEY"),
        "DISCORD_WEBHOOK_URL": os.environ.get("DISCORD_WEBHOOK_URL")
    }
