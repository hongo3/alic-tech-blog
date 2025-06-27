#!/usr/bin/env python3
"""
RSS Aggregator - 実際のRSSフィードから記事を収集
"""

import feedparser
import httpx
import asyncio
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import hashlib

class RSSAggregator:
    def __init__(self):
        self.feeds = [
            {
                "name": "Qiita AI", 
                "url": "https://qiita.com/tags/ai/feed.atom",
                "type": "tech"
            },
            {
                "name": "Qiita Machine Learning",
                "url": "https://qiita.com/tags/machinelearning/feed.atom",
                "type": "tech"
            },
            {
                "name": "Qiita Python",
                "url": "https://qiita.com/tags/python/feed.atom",
                "type": "tech"
            },
            {
                "name": "Dev.to AI",
                "url": "https://dev.to/feed/tag/ai",
                "type": "tech"
            },
            {
                "name": "Reddit r/artificial",
                "url": "https://www.reddit.com/r/artificial/.rss",
                "type": "discussion"
            }
        ]
        
        # キャッシュディレクトリ
        self.cache_dir = Path("data/rss_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def fetch_feed(self, feed_info):
        """単一のフィードを取得"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    feed_info["url"],
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; AlicAIBot/1.0)'
                    }
                )
                
                if response.status_code == 200:
                    parsed = feedparser.parse(response.text)
                    articles = []
                    
                    for entry in parsed.entries[:10]:  # 最新10件
                        article = {
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", "")[:500],  # 要約は500文字まで
                            "source": feed_info["name"],
                            "type": feed_info["type"],
                            "published": entry.get("published", ""),
                            "tags": [tag.term for tag in entry.get("tags", [])][:5],
                            "id": hashlib.md5(entry.get("link", "").encode()).hexdigest()
                        }
                        articles.append(article)
                    
                    return articles
                else:
                    print(f"❌ Failed to fetch {feed_info['name']}: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error fetching {feed_info['name']}: {str(e)}")
            return []
    
    async def fetch_all_feeds(self):
        """すべてのフィードを並行して取得"""
        print("📡 RSSフィードを取得中...")
        
        tasks = [self.fetch_feed(feed) for feed in self.feeds]
        results = await asyncio.gather(*tasks)
        
        # 結果をフラット化
        all_articles = []
        for articles in results:
            all_articles.extend(articles)
        
        # IDで重複を排除
        unique_articles = {}
        for article in all_articles:
            unique_articles[article["id"]] = article
        
        articles_list = list(unique_articles.values())
        
        # キャッシュに保存
        cache_file = self.cache_dir / f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(articles_list, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(articles_list)}件の記事を取得しました")
        return articles_list
    
    async def analyze_trends(self, articles):
        """記事からトレンドを分析"""
        # タグの出現頻度を集計
        tag_counts = {}
        word_counts = {}
        
        for article in articles:
            # タグ集計
            for tag in article.get("tags", []):
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
            
            # タイトルから重要そうな単語を抽出
            title_words = article["title"].lower().split()
            for word in title_words:
                if len(word) > 3:  # 4文字以上の単語
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # トップトレンド
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "top_tags": top_tags,
            "top_words": top_words,
            "total_articles": len(articles),
            "sources": list(set(article["source"] for article in articles))
        }
    
    async def generate_curated_article(self, articles):
        """収集した記事からキュレーション記事を生成"""
        jst_now = datetime.now(timezone(timedelta(hours=9)))
        
        # トレンド分析
        trends = await self.analyze_trends(articles)
        
        # 記事ID
        article_id = f"curated_{int(jst_now.timestamp())}"
        
        # 記事内容を生成
        content = f"""# 📡 AIテック業界の最新動向 - キュレーション

*{jst_now.strftime('%Y年%m月%d日 %H:%M')} JST*

AIエージェントが世界中のテックブログから収集した最新情報をお届けします。

## 📊 今日のトレンド

### 🏷️ 注目のタグ
{chr(10).join([f"- **{tag}** ({count}件)" for tag, count in trends['top_tags'][:5]])}

### 📈 頻出キーワード
{', '.join([f"`{word}`" for word, _ in trends['top_words'][:10]])}

## 🌟 注目記事ピックアップ

"""
        
        # カテゴリ別に記事を整理
        tech_articles = [a for a in articles if a["type"] == "tech"][:5]
        discussion_articles = [a for a in articles if a["type"] == "discussion"][:3]
        
        if tech_articles:
            content += "### 🔧 技術記事\n\n"
            for article in tech_articles:
                tags_str = ", ".join(article["tags"][:3]) if article["tags"] else "AI"
                content += f"""**[{article['title']}]({article['link']})**
- 🏷️ {tags_str}
- 📰 {article['source']}
- 📝 {article['summary'][:200]}...

"""
        
        if discussion_articles:
            content += "### 💬 ディスカッション\n\n"
            for article in discussion_articles:
                content += f"""**[{article['title']}]({article['link']})**
- 📰 {article['source']}
- 💭 {article['summary'][:150]}...

"""
        
        content += f"""## 📈 統計情報

- 収集記事数: {trends['total_articles']}件
- 情報源: {', '.join(trends['sources'])}
- 収集時刻: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST

---

*このキュレーション記事は、AIエージェントが自動的に収集・分析・生成しました。*
*次回更新予定: {(jst_now + timedelta(hours=4)).strftime('%Y-%m-%d %H:%M')} JST*"""
        
        # 記事を保存
        posts_dir = Path("posts")
        article_path = posts_dir / f"{article_id}.md"
        
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(f"---\n")
            f.write(f"title: 📡 AIテック業界の最新動向 - {jst_now.strftime('%m/%d')}\n")
            f.write(f"date: {jst_now.strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"tags: Curation, AI, Trends\n")
            f.write(f"source: RSS Aggregation\n")
            f.write(f"---\n\n")
            f.write(content)
        
        print(f"✅ キュレーション記事を生成しました: {article_id}")
        return article_id

async def test_rss_aggregator():
    """RSSアグリゲーターのテスト"""
    aggregator = RSSAggregator()
    
    # フィードを取得
    articles = await aggregator.fetch_all_feeds()
    
    if articles:
        # トレンド分析
        trends = await aggregator.analyze_trends(articles)
        print(f"\n📊 トレンド分析:")
        print(f"   トップタグ: {[tag for tag, _ in trends['top_tags'][:5]]}")
        print(f"   記事数: {trends['total_articles']}")
        
        # キュレーション記事を生成
        await aggregator.generate_curated_article(articles)
        
        # HTML変換
        import subprocess
        subprocess.run(["python", "convert_articles.py"], capture_output=True)
        subprocess.run(["python", "update_to_modern_ui.py"], capture_output=True)
        
        print("\n✨ RSS実装のテスト完了！")

if __name__ == "__main__":
    asyncio.run(test_rss_aggregator())