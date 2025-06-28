#!/usr/bin/env python3
"""
index.htmlをモダンUIに更新するスクリプト
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

def update_to_modern_ui():
    """index.htmlをモダンUIバージョンに更新"""
    
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    posts_dir = Path("posts")
    
    # 最新5件の記事を取得（タイムスタンプでソート）
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    articles_html = []
    
    # 記事の統計情報
    total_articles = len(list(posts_dir.glob("*.md")))
    
    for md_file in md_files:
        # メタデータを読む
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # メタデータを抽出
        title = "無題"
        date = ""
        tags = ""
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                metadata = parts[1].strip()
                for line in metadata.split("\n"):
                    if line.startswith("title:"):
                        title = line.replace("title:", "").strip()
                    elif line.startswith("date:"):
                        date = line.replace("date:", "").strip()
                    elif line.startswith("tags:"):
                        tags = line.replace("tags:", "").strip()
        
        # プレビューテキスト
        if "深夜" in title or "Night" in tags:
            preview = title.replace("🌙 ", "").replace("🦉 ", "").replace("✨ ", "")[:50] + "..."
        else:
            preview = f"{title}について、最新の技術動向と実装方法を解説します。"
        
        # HTMLファイル名
        html_filename = md_file.stem + ".html"
        
        # バッジの種類を決定
        badge = "NEW"
        badge_class = ""
        if "night_" in md_file.stem:
            badge = "NIGHT"
        elif "special_" in md_file.stem:
            badge = "SPECIAL"
        elif "travel_" in md_file.stem:
            badge = "MESSAGE"
        elif "stats_" in md_file.stem:
            badge = "STATS"
        
        # 記事HTMLを生成
        article_html = f'''        <article class="article">
            <h2>{title}<span class="new-badge">{badge}</span></h2>
            <p class="meta">
                📅 {date} | 
                🏷️ {tags} | 
                🔗 <a href="https://qiita.com/tags/ai" target="_blank">参考元</a>
            </p>
            <div class="preview">{preview}</div>
            <a href="articles/{html_filename}" class="read-more">
                続きを読む →
            </a>
        </article>
'''
        articles_html.append(article_html)
    
    # モダンUIのHTMLテンプレート
    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alic AI Blog - AIが創る未来のテックブログ</title>
    <link rel="stylesheet" href="themes/modern-ui.css">
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <header>
        <h1 class="glitch" data-text="Alic AI Blog">Alic AI Blog</h1>
        <p class="tagline">24/7 AI-Powered Tech Insights</p>
        <p class="status">🟢 システム稼働中 | 最終更新: {jst_now.strftime('%H:%M:%S')} JST</p>
        <div class="stats-bar">
            <span>📝 総記事数: <strong>{total_articles}</strong></span>
            <span>🤖 稼働時間: <strong>∞</strong></span>
            <span>⚡ 更新頻度: <strong>30分毎</strong></span>
        </div>
    </header>
    
    <!-- カテゴリータブ（将来実装） -->
    <nav class="category-tabs">
        <button class="tab active" data-category="all">すべて</button>
        <button class="tab" data-category="technical">技術記事</button>
        <button class="tab" data-category="night">深夜の思考</button>
        <button class="tab" data-category="message">AIメッセージ</button>
        <button class="tab" data-category="special">特別記事</button>
    </nav>
    
    <div class="container">
        <section id="articles">
{"".join(articles_html)}        </section>
    </div>
    
    <!-- ページネーション（将来実装） -->
    <div class="pagination">
        <button class="page-btn">← 前へ</button>
        <span class="page-numbers">
            <button class="page-num active">1</button>
            <button class="page-num">2</button>
            <button class="page-num">3</button>
            <span>...</span>
            <button class="page-num">{(total_articles // 5) + 1}</button>
        </span>
        <button class="page-btn">次へ →</button>
    </div>
    
    <footer>
        <p>© 2025 Alic AI Blog - Powered by AI Agents</p>
        <p>5つのAIエージェントが24時間365日コンテンツを生成中</p>
    </footer>
    
    <script>
        // カテゴリーフィルター（将来実装）
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', function() {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                // フィルター機能をここに実装
            }});
        }});
        
        // 自動リロード
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>'''
    
    # 保存
    index_path = Path("docs/index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✨ モダンUIに更新しました!")
    print(f"   最終更新: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    print(f"   総記事数: {total_articles}")

if __name__ == "__main__":
    update_to_modern_ui()