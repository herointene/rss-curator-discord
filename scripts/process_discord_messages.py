#!/usr/bin/env python3
"""
处理 Discord 消息并生成 feedback.json（只包含最近7天）
使用方式: python3 process_discord_messages.py < discord_messages.json
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 配置
DAYS_BACK = 7  # 只处理最近7天的消息

def parse_source_from_content(content):
    """从消息内容解析 RSS 来源"""
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

def process_messages(messages):
    """处理消息，只保留最近7天的 RSS 文章"""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    
    feedback_list = []
    skipped_count = 0
    
    for msg in messages:
        # 检查时间
        msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
        if msg_time < cutoff_time:
            skipped_count += 1
            continue
        
        content = msg.get("content", "")
        
        # 只处理 RSS 文章消息（包含 📰 前缀）
        if not content.startswith("📰"):
            skipped_count += 1
            continue
        
        source = parse_source_from_content(content)
        if not source:
            skipped_count += 1
            continue
        
        # 提取标题（从 [**标题**](链接) 格式）
        title_match = re.search(r"\[\*\*([^\]]+)\*\*\]", content)
        title = title_match.group(1) if title_match else "Unknown"
        
        # 解析表情反应
        likes, dislikes = parse_reactions(msg)
        
        feedback_list.append({
            "source": source,
            "title": title,
            "likes": likes,
            "dislikes": dislikes,
            "message_id": msg["id"],
            "timestamp": msg["timestamp"]
        })
    
    return feedback_list, skipped_count

def main():
    """主入口"""
    print("=" * 60)
    print("RSS Curator - 处理 Discord 消息")
    print("=" * 60)
    print(f"时间范围: 最近 {DAYS_BACK} 天")
    print()
    
    # 从标准输入读取 JSON
    try:
        data = json.load(sys.stdin)
        messages = data.get("messages", []) if isinstance(data, dict) else data
    except json.JSONDecodeError as e:
        print(f"错误: 无法解析 JSON - {e}")
        sys.exit(1)
    
    print(f"输入消息总数: {len(messages)}")
    
    # 处理消息
    feedback_list, skipped = process_messages(messages)
    
    print(f"跳过消息: {skipped} 条（超出时间范围或非 RSS 消息）")
    print(f"有效 RSS 消息: {len(feedback_list)} 条")
    
    # 按来源统计
    source_stats = {}
    for item in feedback_list:
        source = item["source"]
        if source not in source_stats:
            source_stats[source] = {"count": 0, "likes": 0, "dislikes": 0}
        source_stats[source]["count"] += 1
        source_stats[source]["likes"] += item["likes"]
        source_stats[source]["dislikes"] += item["dislikes"]
    
    print(f"\n各来源统计（最近{DAYS_BACK}天）:")
    for source, stats in sorted(source_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"  - {source}: {stats['count']} 篇文章, {stats['likes']}👍 {stats['dislikes']}👎")
    
    # 创建 feedback 数据
    feedback = {
        "week": datetime.now().strftime("%Y-%m-%d"),
        "days_back": DAYS_BACK,
        "message_count": len(feedback_list),
        "messages": feedback_list
    }
    
    # 保存到文件
    project_root = Path(__file__).parent.parent
    feedback_file = project_root / "data" / "feedback.json"
    
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到: {feedback_file}")
    print(f"   包含 {len(feedback_list)} 条反馈（最近 {DAYS_BACK} 天）")

if __name__ == "__main__":
    main()
