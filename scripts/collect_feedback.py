#!/usr/bin/env python3
"""
从 Discord 频道获取最近7天的消息反馈
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# 配置
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID")
DAYS_BACK = 7  # 只获取最近7天的消息

def fetch_discord_messages():
    """从 Discord 获取最近7天的消息"""
    if not DISCORD_BOT_TOKEN:
        print("错误：未设置 DISCORD_BOT_TOKEN 环境变量")
        print("请设置: export DISCORD_BOT_TOKEN='your_bot_token'")
        return None
    
    if not DISCORD_CHANNEL_ID:
        print("错误：未设置 DISCORD_CHANNEL_ID 环境变量")
        print("请设置: export DISCORD_CHANNEL_ID='your_channel_id'")
        return None
    
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 计算7天前的时间戳
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    cutoff_snowflake = int((cutoff_time.timestamp() - 1420070400) * 4194304)
    
    all_messages = []
    last_id = None
    
    print(f"[Discord] 获取最近 {DAYS_BACK} 天的消息...")
    print(f"[Discord] 截止时间: {cutoff_time.isoformat()}")
    
    while True:
        url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages?limit=100"
        if last_id:
            url += f"&before={last_id}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"错误：无法获取消息 - {response.status_code}: {response.text}")
            return None
        
        messages = response.json()
        if not messages:
            break
        
        # 过滤消息：只保留在7天内的消息
        for msg in messages:
            msg_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
            if msg_time >= cutoff_time:
                all_messages.append(msg)
            else:
                # 消息已超出7天范围，停止获取
                print(f"[Discord] 已获取 {len(all_messages)} 条消息（最近 {DAYS_BACK} 天）")
                return all_messages
        
        last_id = messages[-1]["id"]
        
        # 如果已经获取了超过1000条消息，停止
        if len(all_messages) >= 1000:
            print(f"[Discord] 已获取 {len(all_messages)} 条消息（达到上限）")
            break
    
    print(f"[Discord] 已获取 {len(all_messages)} 条消息")
    return all_messages

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

def extract_feedback(messages):
    """从消息中提取反馈数据"""
    feedback_list = []
    
    for msg in messages:
        content = msg.get("content", "")
        
        # 只处理 RSS 文章消息（包含 📰 前缀）
        if not content.startswith("📰"):
            continue
        
        source = parse_source_from_content(content)
        if not source:
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
    
    return feedback_list

def main():
    """主入口"""
    print("=" * 60)
    print("RSS Curator - 收集 Discord 反馈")
    print("=" * 60)
    print(f"时间范围: 最近 {DAYS_BACK} 天")
    print()
    
    # 获取消息
    messages = fetch_discord_messages()
    if messages is None:
        print("\n提示: 如果没有 Discord Bot Token，可以使用 message tool 手动获取最近消息")
        return 1
    
    # 提取反馈
    feedback_list = extract_feedback(messages)
    
    print(f"\n解析结果:")
    print(f"  - 总消息: {len(messages)}")
    print(f"  - RSS 文章: {len(feedback_list)}")
    
    # 按来源统计
    source_stats = {}
    for item in feedback_list:
        source = item["source"]
        if source not in source_stats:
            source_stats[source] = {"count": 0, "likes": 0, "dislikes": 0}
        source_stats[source]["count"] += 1
        source_stats[source]["likes"] += item["likes"]
        source_stats[source]["dislikes"] += item["dislikes"]
    
    print(f"\n各来源统计:")
    for source, stats in sorted(source_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"  - {source}: {stats['count']} 篇文章, {stats['likes']}👍 {stats['dislikes']}👎")
    
    # 保存 feedback.json
    feedback = {
        "week": datetime.now().strftime("%Y-%m-%d"),
        "days_back": DAYS_BACK,
        "message_count": len(feedback_list),
        "messages": feedback_list
    }
    
    project_root = Path(__file__).parent.parent
    feedback_file = project_root / "data" / "feedback.json"
    
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到: {feedback_file}")
    print(f"   包含 {len(feedback_list)} 条反馈（最近 {DAYS_BACK} 天）")
    
    return 0

if __name__ == "__main__":
    exit(main())
