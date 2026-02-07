import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import load_sources, save_ratings

def calculate_scores(feedback_file):
    """计算各 RSS 源评分"""
    with open(feedback_file, 'r', encoding='utf-8') as f:
        feedback = json.load(f)
    
    source_stats = {}
    
    for msg in feedback.get("messages", []):
        source = msg.get("source")
        if not source:
            continue
        
        if source not in source_stats:
            source_stats[source] = {"likes": 0, "dislikes": 0, "total": 0}
        
        source_stats[source]["likes"] += msg.get("likes", 0)
        source_stats[source]["dislikes"] += msg.get("dislikes", 0)
        source_stats[source]["total"] += 1
    
    # 计算评分
    scores = {}
    for source, stats in source_stats.items():
        total_votes = stats["likes"] + stats["dislikes"]
        if total_votes > 0:
            score = stats["likes"] / total_votes
            scores[source] = {
                "score": round(score, 2),
                "likes": stats["likes"],
                "dislikes": stats["dislikes"],
                "total_votes": total_votes
            }
    
    return scores

def adjust_weights(sources_config, scores):
    """根据评分调整权重"""
    sources = sources_config.get("sources", [])
    changes = []
    
    for source in sources:
        name = source.get("name")
        old_weight = source.get("weight", 1.0)
        
        if name in scores:
            score = scores[name]["score"]
            
            if score > 0.7:
                # 高分：增加权重
                new_weight = old_weight * 1.2
                changes.append(f"{name}: {old_weight:.2f} → {new_weight:.2f} (高分 {score:.0%})")
            elif score < 0.4:
                # 低分：降低权重
                new_weight = old_weight * 0.6
                changes.append(f"{name}: {old_weight:.2f} → {new_weight:.2f} (低分 {score:.0%})")
            else:
                # 中等：略微降低
                new_weight = old_weight * 0.9
                changes.append(f"{name}: {old_weight:.2f} → {new_weight:.2f} (中等 {score:.0%})")
            
            source["weight"] = round(new_weight, 2)
        else:
            # 无反馈：略微降低
            new_weight = old_weight * 0.95
            source["weight"] = round(new_weight, 2)
            changes.append(f"{name}: {old_weight:.2f} → {new_weight:.2f} (无反馈)")
    
    return sources_config, changes

def main():
    """主入口"""
    print("=" * 60)
    print("RSS Curator - 每周优化")
    print("=" * 60)
    
    # 加载反馈数据
    feedback_file = Path(__file__).parent.parent / "data" / "feedback.json"
    if not feedback_file.exists():
        print("错误：未找到 feedback.json")
        return
    
    # 计算评分
    print("\n[1/3] 计算各源评分...")
    scores = calculate_scores(feedback_file)
    
    print("\n评分结果:")
    for source, data in scores.items():
        print(f"  • {source}: {data['score']:.0%} ({data['likes']}👍 / {data['dislikes']}👎)")
    
    # 加载源配置
    print("\n[2/3] 调整权重...")
    sources_config = load_sources()
    
    # 调整权重
    updated_config, changes = adjust_weights(sources_config, scores)
    
    print("\n权重调整:")
    for change in changes:
        print(f"  • {change}")
    
    # 保存更新后的配置
    print("\n[3/3] 保存配置...")
    config_file = Path(__file__).parent.parent / "config" / "sources.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(updated_config, f, ensure_ascii=False, indent=2)
    
    # 保存评分历史
    ratings_file = Path(__file__).parent.parent / "data" / "ratings.json"
    ratings = {}
    if ratings_file.exists():
        with open(ratings_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
    
    week = feedback_file.stat().st_mtime  # 使用文件修改时间
    ratings[f"week_{int(week)}"] = scores
    
    with open(ratings_file, 'w', encoding='utf-8') as f:
        json.dump(ratings, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("优化完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
