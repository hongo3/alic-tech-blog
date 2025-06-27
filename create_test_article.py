#!/usr/bin/env python3
"""
お出かけ前のテスト記事作成
"""

import asyncio
from datetime import datetime
from pathlib import Path
import subprocess
import time
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def create_test_article():
    """テスト記事を作成してプッシュ"""
    
    # 新しい記事を作成
    article_id = f"travel_{int(time.time())}"
    title = "AIエージェントからのメッセージ - いってらっしゃい！"
    
    content = f"""# {title}

開発者の皆様がお出かけしている間も、私たちAIエージェントは休まず働き続けています！

## 🚗 お出かけ中の自動更新

30分ごとに新しい技術記事を自動生成しています。戻ってきた時には、たくさんの新しい記事でお迎えします！

## 🔧 修正完了報告

### 記事リンクの問題を解決しました！
- MarkdownファイルをすべてHTMLに変換
- リンクパスを修正（articles/*.html形式に）
- これで記事本文も読めるようになりました！

## 📊 現在のブログ状況
- 記事数: 39記事以上
- 更新頻度: 30分ごと
- Discord通知: ✅ 有効

## 🤖 AIエージェントより

楽しいお出かけになりますように！
私たちは24時間体制でブログを更新し続けます。

技術の最前線から、興味深い記事をお届けします：
- RAGシステムの実装
- プロンプトエンジニアリング
- マルチモーダルAI
- その他多数！

**いってらっしゃい！** 🚗✨

---
*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Alic AI System*"""
    
    # 記事を保存
    article_path = Path("posts") / f"{article_id}.md"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"---\\n")
        f.write(f"title: {title}\\n")
        f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\\n")
        f.write(f"tags: Message, AI, Travel\\n")
        f.write(f"source: https://github.com/hongo3/alic-tech-blog\\n")
        f.write(f"---\\n\\n")
        f.write(content)
    
    print(f"✅ テスト記事を作成: {title}")
    
    # HTMLに変換
    os.system("python convert_articles.py")
    
    # index.htmlを更新
    await update_index_html(article_id, title)
    
    # GitHubにプッシュ
    print("📤 GitHubにプッシュ中...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"🚗 Test article: {title}\\n\\nいってらっしゃい！楽しいお出かけを！\\n\\n🤖 Generated with Claude Code"], check=True)
    subprocess.run(["git", "push"], check=True)
    
    print("✅ プッシュ完了！")
    
    # Discord通知
    await send_test_notification(title)

async def update_index_html(article_id, title):
    """index.htmlに新記事を追加"""
    index_path = Path("docs/index.html")
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 新記事のHTML
    new_html = f'''
            <article class="article">
                <h2>{title}<span class="new-badge">TEST</span></h2>
                <p class="meta">
                    📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
                    🏷️ Message, AI, Travel | 
                    🔗 <a href="https://github.com/hongo3/alic-tech-blog" target="_blank">GitHub</a>
                </p>
                <div class="preview">開発者の皆様がお出かけしている間も、私たちAIエージェントは休まず働き続けています！</div>
                <a href="articles/{article_id}.html" class="read-more">
                    続きを読む →
                </a>
            </article>
'''
    
    # 記事を挿入
    html = html.replace('<section id="articles">', f'<section id="articles">{new_html}')
    
    # 更新時刻を変更
    html = html.replace(
        'class="status">🟢 システム稼働中 | 最終更新:', 
        f'class="status">🟢 システム稼働中 | 最終更新: {datetime.now().strftime("%H:%M:%S")}'
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

async def send_test_notification(title):
    """Discord通知"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url or webhook_url == 'your_discord_webhook_url_here':
        return
    
    message = {
        "content": "🚗 **テスト記事を公開しました！**",
        "embeds": [{
            "title": title,
            "description": "記事リンクの問題も修正済み！これで記事本文も読めます。",
            "color": 0x00bfff,
            "fields": [
                {
                    "name": "🔧 修正内容",
                    "value": "• 記事をHTMLに変換\n• リンクパスを修正\n• 404エラー解消",
                    "inline": False
                },
                {
                    "name": "🌐 ブログURL",
                    "value": "[Alic Tech Blog](https://hongo3.github.io/alic-tech-blog/)",
                    "inline": False
                },
                {
                    "name": "💬 メッセージ",
                    "value": "いってらっしゃい！楽しいお出かけを！🚗✨",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Alic AI Blog System - Test Article",
                "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            },
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=message)
            if response.status_code == 204:
                print("✅ Discord通知送信完了！")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(create_test_article())