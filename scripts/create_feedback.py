#!/usr/bin/env python3
"""
从 Discord 消息生成 feedback.json（只包含最近7天）
"""

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 配置
DAYS_BACK = 7  # 只处理最近7天的消息

def parse_source_from_content(content):
    """从消息内容解析 RSS 来源"""
    # 查找 "📡 来源: XXX" 格式
    match = re.search(r"📡\s*来源:\s*([^\n]+)", content)
    if match:
        return match.group(1).strip()
    return None

def parse_reactions(message):
    """解析消息的表情反应"""
    likes = 0
    dislikes = 0
    
    for reaction in message.get("reactions", []):
        emoji = reaction.get("emoji", {}).get("name", "")
        count = reaction.get("count", 0)
        
        if emoji == "👍":
            likes = count
        elif emoji == "👎":
            dislikes = count
    
    return likes, dislikes

def filter_recent_messages(messages, days_back=DAYS_BACK):
    """只保留最近 N 天的消息"""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    filtered = []
    for msg in messages:
        msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
        if msg_time >= cutoff_time:
            filtered.append(msg)
    
    return filtered

def main():
    """主入口"""
    print("=" * 60)
    print("RSS Curator - 创建 Feedback（最近7天）")
    print("=" * 60)
    print()
    
    # 注意：这里的数据应该由调用者传入
    # 这个脚本需要与 collect_feedback.py 配合使用
    print("请运行 collect_feedback.py 从 Discord 获取最近7天的消息")
    print("或者使用 message tool 获取消息后，手动创建 feedback.json")
    print()
    print("时间范围: 最近7天")
    print("消息格式: 需要包含 timestamp, content, reactions 字段")

if __name__ == "__main__":
    main()
