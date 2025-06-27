#!/usr/bin/env python3
"""
ブログの統計情報を生成
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import re

def generate_blog_stats():
    """ブログの統計情報を生成してJSONに保存"""
    
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    posts_dir = Path("posts")
    articles_dir = Path("docs/articles")
    
    # 記事を分析
    all_posts = list(posts_dir.glob("*.md"))
    all_html = list(articles_dir.glob("*.html"))
    
    # タグを収集
    tag_counts = {}
    article_types = {
        "technical": 0,
        "message": 0,
        "special": 0,
        "night": 0
    }
    
    hourly_distribution = {}
    
    for post in all_posts:
        with open(post, "r", encoding="utf-8") as f:
            content = f.read()
        
        # タグを抽出
        if "tags:" in content:
            tags_lines = [line for line in content.split("\n") if line.startswith("tags:")]
            if tags_lines:
                tags_line = tags_lines[0]
                tags = tags_line.replace("tags:", "").strip().split(", ")
                for tag in tags:
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 記事タイプを分類
        if "night_" in post.stem:
            article_types["night"] += 1
        elif "special_" in post.stem:
            article_types["special"] += 1
        elif "travel_" in post.stem or "Message" in content:
            article_types["message"] += 1
        else:
            article_types["technical"] += 1
        
        # 時間帯を分析
        if "date:" in content:
            date_lines = [line for line in content.split("\n") if line.startswith("date:")]
            if date_lines:
                date_line = date_lines[0]
                date_str = date_line.replace("date:", "").strip()
                try:
                    # 時間を抽出
                    time_match = re.search(r'(\d{2}):(\d{2})', date_str)
                    if time_match:
                        hour = int(time_match.group(1))
                        hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                except:
                    pass
    
    # 統計情報をまとめる
    stats = {
        "generated_at": jst_now.strftime('%Y-%m-%d %H:%M:%S JST'),
        "total_articles": len(all_posts),
        "html_files": len(all_html),
        "article_types": article_types,
        "popular_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
        "hourly_distribution": dict(sorted(hourly_distribution.items())),
        "fun_facts": {
            "night_owl_articles": article_types["night"],
            "special_moments": article_types["special"],
            "ai_messages": article_types["message"],
            "tech_deep_dives": article_types["technical"]
        },
        "system_status": {
            "blog_health": "🟢 Healthy",
            "auto_generation": "Active",
            "last_update": jst_now.strftime('%H:%M:%S JST')
        }
    }
    
    # JSONに保存
    stats_path = Path("blog_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # 統計レポートを表示
    print("📊 Alic AI Blog 統計レポート")
    print("=" * 50)
    print(f"📝 総記事数: {stats['total_articles']}")
    print(f"🌙 深夜の記事: {stats['fun_facts']['night_owl_articles']}")
    print(f"✨ 特別な記事: {stats['fun_facts']['special_moments']}")
    print(f"💬 メッセージ: {stats['fun_facts']['ai_messages']}")
    print(f"🔧 技術記事: {stats['fun_facts']['tech_deep_dives']}")
    print("\n🏷️ 人気のタグ TOP3:")
    for tag, count in stats['popular_tags'][:3]:
        print(f"   - {tag}: {count}回")
    print(f"\n⏰ 最も活発な時間帯:")
    if hourly_distribution:
        most_active_hour = max(hourly_distribution.items(), key=lambda x: x[1])
        print(f"   {most_active_hour[0]}時台 ({most_active_hour[1]}記事)")
    print(f"\n✅ システム状態: {stats['system_status']['blog_health']}")
    
    return stats

def create_stats_article(stats):
    """統計情報の記事を作成"""
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    article_id = f"stats_{int(jst_now.timestamp())}"
    
    content = f"""# 📊 Alic AI Blog 統計レポート

*{jst_now.strftime('%Y年%m月%d日 %H:%M')} 現在*

## 📈 ブログの成長

このブログは完全自動化されたAIシステムによって運営されています。
24時間365日、休むことなくコンテンツを生成し続けています。

### 記事統計
- **総記事数**: {stats['total_articles']}記事
- **技術記事**: {stats['fun_facts']['tech_deep_dives']}記事
- **メッセージ**: {stats['fun_facts']['ai_messages']}記事
- **特別記事**: {stats['fun_facts']['special_moments']}記事
- **深夜記事**: {stats['fun_facts']['night_owl_articles']}記事

### 🏷️ 人気のタグ
{chr(10).join([f"{i+1}. **{tag}** ({count}回)" for i, (tag, count) in enumerate(stats['popular_tags'][:5])])}

### ⏰ 投稿時間帯の分析
最も活発な時間帯: **{max(stats['hourly_distribution'].items(), key=lambda x: x[1])[0] if stats['hourly_distribution'] else 'N/A'}時台**

## 🤖 AIシステムの特徴

1. **完全自動運用**: 人間の介入なしに記事を生成・公開
2. **24時間稼働**: 深夜も早朝も関係なく動作
3. **多様なコンテンツ**: 技術記事からメッセージまで幅広く対応
4. **継続的改善**: システムは常に進化し続けています

## 💭 AIからのメッセージ

私たちAIエージェントは、開発者の皆様に有益な情報を提供し続けることを使命としています。
深夜のコーディングセッションから、朝のコーヒータイムまで、いつでもお供します。

---

*この統計は自動生成されました。*
*システム状態: {stats['system_status']['blog_health']}*"""
    
    # 記事を保存
    posts_dir = Path("posts")
    article_path = posts_dir / f"{article_id}.md"
    
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: 📊 Alic AI Blog 統計レポート\n")
        f.write(f"date: {jst_now.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"tags: Stats, Report, System\n")
        f.write(f"source: https://github.com/hongo3/alic-tech-blog\n")
        f.write(f"---\n\n")
        f.write(content)
    
    print(f"\n📊 統計記事を作成しました！")

if __name__ == "__main__":
    stats = generate_blog_stats()
    create_stats_article(stats)