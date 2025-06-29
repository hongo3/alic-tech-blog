#!/usr/bin/env python3
"""
index.htmlをモダンUIに更新するスクリプト v3
- カテゴリー表示の改善
- タグの多様化
- タイムスタンプ累積バグの修正
- セクション間マージンの改善
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

def fix_timestamp_accumulation(html_content, jst_now):
    """タイムスタンプの累積を修正"""
    # 既存のタイムスタンプパターンを検索して、最新のものだけに置き換え
    pattern = r'最終更新: (?:[\d:]+\s+JST\s*)+'
    replacement = f'最終更新: {jst_now.strftime("%H:%M:%S")} JST'
    return re.sub(pattern, replacement, html_content)

def update_to_modern_ui():
    """index.htmlをモダンUIバージョンに更新"""
    
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    posts_dir = Path("posts")
    
    # 最新5件の記事を取得（タイムスタンプでソート）
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    articles_html = []
    
    # 記事の統計情報
    total_articles = len(list(posts_dir.glob("*.md")))
    category_counts = {}
    
    for i, md_file in enumerate(md_files):
        # メタデータを読む
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # メタデータを抽出
        title = "無題"
        date = ""
        tags = "AI, Technology"
        category = "AI開発"
        source = "https://github.com/hongo3/alic-tech-blog"
        difficulty = "中級"
        reading_time = "5分"
        
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
                    elif line.startswith("category:"):
                        category = line.replace("category:", "").strip()
                    elif line.startswith("source:"):
                        source = line.replace("source:", "").strip()
                    elif line.startswith("difficulty:"):
                        difficulty = line.replace("difficulty:", "").strip()
                    elif line.startswith("reading_time:"):
                        reading_time = line.replace("reading_time:", "").strip()
        
        # カテゴリー統計
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # プレビューテキスト（タイトルから生成）
        if "完全ガイド" in title or "完全攻略" in title:
            preview = f"本記事では、最新の技術トレンドを踏まえながら、実践的な実装方法を詳しく解説します。初心者から上級者まで、すべての開発者に役立つ内容です。"
        elif "実践" in title or "実装" in title:
            preview = f"実際のプロジェクトで即座に活用できる実践的な知識をお伝えします。サンプルコードと詳細な解説付き。"
        elif "比較" in title:
            preview = f"各技術の特徴を徹底比較。あなたのプロジェクトに最適な選択ができるよう、詳細な分析結果をお届けします。"
        else:
            preview = f"{title.split('：')[0] if '：' in title else title[:30]}について、最新の技術動向と実装方法を解説します。"
        
        # HTMLファイル名
        html_filename = md_file.stem + ".html"
        
        # バッジの種類を決定（カテゴリーベース）
        badge = "NEW" if i == 0 else ""
        badge_class = ""
        
        # カテゴリーに応じた色
        category_colors = {
            "AI開発": "#667eea",
            "Web技術": "#48bb78",
            "インフラ": "#ed8936",
            "セキュリティ": "#e53e3e",
            "データサイエンス": "#38b2ac"
        }
        
        category_color = category_colors.get(category, "#667eea")
        
        # 記事HTMLを生成
        article_html = f'''        <article class="article" data-category="{category.lower().replace(' ', '_')}">
            <div class="article-header-info">
                <h2>{title}{f'<span class="new-badge">{badge}</span>' if badge else ''}</h2>
                <div class="article-meta-tags">
                    <span class="category-badge" style="background-color: {category_color}">{category}</span>
                    <span class="difficulty-badge">{difficulty}</span>
                    <span class="reading-time">📖 {reading_time}</span>
                </div>
            </div>
            <p class="meta">
                📅 {date} | 
                🏷️ {tags}
            </p>
            <div class="preview">{preview}</div>
            <a href="articles/{html_filename}" class="read-more">
                続きを読む →
            </a>
        </article>
'''
        articles_html.append(article_html)
    
    # カテゴリー別記事数を計算
    category_stats = []
    for cat, count in category_counts.items():
        category_stats.append(f"{cat}: {count}件")
    
    # モダンUIのHTMLテンプレート
    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【開発中】Alic AI Blog - AIが創る未来のテックブログ（実験的プロジェクト）</title>
    <link rel="stylesheet" href="themes/article-style.css">
    <meta http-equiv="refresh" content="30">
    <style>
        /* 追加のスタイル */
        .article-header-info {{
            margin-bottom: 10px;
        }}
        
        .article-meta-tags {{
            display: flex;
            gap: 10px;
            margin: 10px 0;
            flex-wrap: wrap;
        }}
        
        .category-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .difficulty-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background-color: #f0f0f0;
            color: #333;
            font-size: 0.85em;
        }}
        
        .reading-time {{
            display: inline-block;
            padding: 4px 12px;
            color: #666;
            font-size: 0.85em;
        }}
        
        .article h2 {{
            font-size: 1.5em;
            line-height: 1.3;
            margin-bottom: 8px;
        }}
        
        .preview {{
            line-height: 1.6;
            color: #555;
        }}
        
        .category-tabs {{
            margin: 20px auto;
            max-width: 1200px;
        }}
        
        .pagination {{
            margin: 40px auto;
            max-width: 1200px;
        }}
        
        /* カテゴリータブのアクティブ状態 */
        .tab.active {{
            background-color: #667eea;
            color: white;
        }}
        
        /* 記事のフィルタリング */
        .article.hidden {{
            display: none;
        }}
        
        /* 記事間のマージンを改善 */
        .article {{
            margin-bottom: 40px;
            padding-bottom: 40px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .article:last-child {{
            border-bottom: none;
        }}
        
        /* セクション間のマージン */
        header {{
            margin-bottom: 40px;
        }}
        
        .category-tabs {{
            margin-bottom: 40px;
        }}
        
        .container {{
            margin-bottom: 60px;
        }}
        
        footer {{
            margin-top: 80px;
            padding-top: 40px;
            border-top: 2px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <header>
        <h1 class="glitch" data-text="Alic AI Blog【開発中】">Alic AI Blog【開発中】</h1>
        <p class="tagline">24/7 AI-Powered Tech Insights（実験的プロジェクト）</p>
        <p class="status">🟢 システム稼働中 | 最終更新: {jst_now.strftime('%H:%M:%S')} JST</p>
        <div class="stats-bar">
            <span>📝 総記事数: <strong>{total_articles}</strong></span>
            <span>🤖 稼働時間: <strong>∞</strong></span>
            <span>⚡ 更新頻度: <strong>30分毎</strong></span>
        </div>
        <div class="category-stats">
            {' | '.join(category_stats)}
        </div>
    </header>
    
    <!-- カテゴリータブ -->
    <nav class="category-tabs">
        <button class="tab active" data-category="all" onclick="filterArticles('all')">すべて</button>
        <button class="tab" data-category="ai開発" onclick="filterArticles('ai開発')">AI開発</button>
        <button class="tab" data-category="web技術" onclick="filterArticles('web技術')">Web技術</button>
        <button class="tab" data-category="インフラ" onclick="filterArticles('インフラ')">インフラ</button>
        <button class="tab" data-category="セキュリティ" onclick="filterArticles('セキュリティ')">セキュリティ</button>
        <button class="tab" data-category="データサイエンス" onclick="filterArticles('データサイエンス')">データサイエンス</button>
    </nav>
    
    <div class="container">
        <section id="articles">
{"".join(articles_html)}        </section>
    </div>
    
    <!-- ページネーション -->
    <div class="pagination">
        <button class="page-btn" onclick="previousPage()">← 前へ</button>
        <span class="page-numbers">
            <button class="page-num active" onclick="goToPage(1)">1</button>
            <button class="page-num" onclick="goToPage(2)">2</button>
            <button class="page-num" onclick="goToPage(3)">3</button>
            <span>...</span>
            <button class="page-num" onclick="goToPage({(total_articles // 5) + 1})">{(total_articles // 5) + 1}</button>
        </span>
        <button class="page-btn" onclick="nextPage()">次へ →</button>
    </div>
    
    <footer>
        <p>© 2025 Alic AI Blog【開発中】 - Powered by AI Agents</p>
        <p>🚧 このブログは開発中のAIシステムです。品質向上のため継続的に改善されています 🚧</p>
    </footer>
    
    <script>
        // カテゴリーフィルター機能
        function filterArticles(category) {{
            const articles = document.querySelectorAll('.article');
            const tabs = document.querySelectorAll('.tab');
            
            // タブのアクティブ状態を更新
            tabs.forEach(tab => {{
                if (tab.getAttribute('data-category') === category) {{
                    tab.classList.add('active');
                }} else {{
                    tab.classList.remove('active');
                }}
            }});
            
            // 記事のフィルタリング
            articles.forEach(article => {{
                if (category === 'all') {{
                    article.classList.remove('hidden');
                }} else {{
                    const articleCategory = article.getAttribute('data-category');
                    if (articleCategory && articleCategory.includes(category.toLowerCase().replace(' ', '_'))) {{
                        article.classList.remove('hidden');
                    }} else {{
                        article.classList.add('hidden');
                    }}
                }}
            }});
        }}
        
        // ページネーション機能（仮実装）
        let currentPage = 1;
        const articlesPerPage = 5;
        
        function goToPage(page) {{
            currentPage = page;
            updatePageDisplay();
        }}
        
        function nextPage() {{
            currentPage++;
            updatePageDisplay();
        }}
        
        function previousPage() {{
            if (currentPage > 1) {{
                currentPage--;
                updatePageDisplay();
            }}
        }}
        
        function updatePageDisplay() {{
            // ページ番号のアクティブ状態を更新
            const pageNums = document.querySelectorAll('.page-num');
            pageNums.forEach(num => {{
                if (parseInt(num.textContent) === currentPage) {{
                    num.classList.add('active');
                }} else {{
                    num.classList.remove('active');
                }}
            }});
            
            // 実際のページネーション実装はここに追加
            console.log('Current page:', currentPage);
        }}
        
        // 自動リロード
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>'''
    
    # タイムスタンプ累積を修正
    html_content = fix_timestamp_accumulation(html_content, jst_now)
    
    # 保存
    index_path = Path("docs/index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✨ モダンUI v3に更新しました!")
    print(f"   最終更新: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    print(f"   総記事数: {total_articles}")
    print(f"   カテゴリー別: {', '.join(category_stats)}")

if __name__ == "__main__":
    update_to_modern_ui()