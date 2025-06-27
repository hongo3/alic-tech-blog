#!/usr/bin/env python3
"""
ページング機能付きブログシステム
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import math

class PaginatedBlogSystem:
    def __init__(self, articles_per_page=5):
        self.articles_per_page = articles_per_page
        self.posts_dir = Path("posts")
        self.docs_dir = Path("docs")
        self.pages_dir = self.docs_dir / "pages"
        self.pages_dir.mkdir(exist_ok=True)
        
    def get_all_articles(self):
        """すべての記事を取得してメタデータと共に返す"""
        articles = []
        
        for md_file in self.posts_dir.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # メタデータを抽出
            metadata = {
                "filename": md_file.stem,
                "title": "無題",
                "date": "",
                "tags": "",
                "category": "general"
            }
            
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    meta_lines = parts[1].strip().split("\n")
                    for line in meta_lines:
                        if line.startswith("title:"):
                            metadata["title"] = line.replace("title:", "").strip()
                        elif line.startswith("date:"):
                            metadata["date"] = line.replace("date:", "").strip()
                        elif line.startswith("tags:"):
                            metadata["tags"] = line.replace("tags:", "").strip()
            
            # カテゴリー判定
            if "night_" in md_file.stem:
                metadata["category"] = "night"
            elif "special_" in md_file.stem:
                metadata["category"] = "special"
            elif "travel_" in md_file.stem or "Message" in metadata["tags"]:
                metadata["category"] = "message"
            elif "curated_" in md_file.stem:
                metadata["category"] = "curation"
            elif "stats_" in md_file.stem:
                metadata["category"] = "stats"
            else:
                metadata["category"] = "technical"
            
            # タイムスタンプを取得
            metadata["timestamp"] = md_file.stat().st_mtime
            
            articles.append(metadata)
        
        # 新しい順にソート
        articles.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return articles
    
    def generate_page(self, articles, page_num, total_pages, category=None):
        """特定のページのHTMLを生成"""
        jst_now = datetime.now(timezone(timedelta(hours=9)))
        
        # 記事のHTML生成
        articles_html = []
        for article in articles:
            # バッジの決定
            badge_map = {
                "night": "NIGHT",
                "special": "SPECIAL",
                "message": "MESSAGE",
                "curation": "CURATED",
                "stats": "STATS",
                "technical": "TECH"
            }
            badge = badge_map.get(article["category"], "NEW")
            
            # プレビューテキスト
            if article["category"] == "curation":
                preview = "AIが世界中から収集した最新テック情報のキュレーション"
            elif article["category"] == "night":
                preview = "深夜のエンジニアに向けた特別なメッセージ"
            else:
                preview = f"{article['title']}について、最新の技術動向と実装方法を解説します。"
            
            article_html = f'''        <article class="article" data-category="{article['category']}">
            <h2>{article['title']}<span class="new-badge badge-{article['category']}">{badge}</span></h2>
            <p class="meta">
                📅 {article['date']} | 
                🏷️ {article['tags']} | 
                🔗 <a href="https://qiita.com/tags/ai" target="_blank">参考元</a>
            </p>
            <div class="preview">{preview}</div>
            <a href="../articles/{article['filename']}.html" class="read-more">
                続きを読む →
            </a>
        </article>
'''
            articles_html.append(article_html)
        
        # ページネーションHTML
        pagination_html = self.generate_pagination_html(page_num, total_pages, category)
        
        # カテゴリータブのアクティブ状態
        category_active = {
            "all": "active" if category is None else "",
            "technical": "active" if category == "technical" else "",
            "night": "active" if category == "night" else "",
            "message": "active" if category == "message" else "",
            "special": "active" if category == "special" else "",
            "curation": "active" if category == "curation" else ""
        }
        
        # 全記事数を取得
        total_articles = len(self.get_all_articles())
        
        # HTMLテンプレート
        html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alic AI Blog - ページ {page_num}/{total_pages}</title>
    <link rel="stylesheet" href="../themes/modern-ui.css">
</head>
<body>
    <header>
        <h1 class="glitch" data-text="Alic AI Blog">Alic AI Blog</h1>
        <p class="tagline">24/7 AI-Powered Tech Insights</p>
        <p class="status">🟢 システム稼働中 | 最終更新: {jst_now.strftime('%H:%M:%S')} JST</p>
        <div class="stats-bar">
            <span>📝 総記事数: <strong>{total_articles}</strong></span>
            <span>📄 ページ: <strong>{page_num}/{total_pages}</strong></span>
            <span>⚡ 更新頻度: <strong>30分毎</strong></span>
        </div>
    </header>
    
    <nav class="category-tabs">
        <a href="../index.html" class="tab {category_active['all']}">すべて</a>
        <a href="technical_1.html" class="tab {category_active['technical']}">技術記事</a>
        <a href="night_1.html" class="tab {category_active['night']}">深夜の思考</a>
        <a href="message_1.html" class="tab {category_active['message']}">AIメッセージ</a>
        <a href="special_1.html" class="tab {category_active['special']}">特別記事</a>
        <a href="curation_1.html" class="tab {category_active['curation']}">キュレーション</a>
    </nav>
    
    <div class="container">
        <section id="articles">
{"".join(articles_html)}        </section>
    </div>
    
    {pagination_html}
    
    <footer>
        <p>© 2025 Alic AI Blog - Powered by AI Agents</p>
        <p>5つのAIエージェントが24時間365日コンテンツを生成中</p>
    </footer>
    
    <script>
        // ページ遷移時のアニメーション
        document.querySelectorAll('.page-btn, .page-num').forEach(btn => {{
            btn.addEventListener('click', function(e) {{
                if (this.href) {{
                    e.preventDefault();
                    document.body.style.opacity = '0';
                    setTimeout(() => {{
                        window.location.href = this.href;
                    }}, 200);
                }}
            }});
        }});
    </script>
</body>
</html>'''
        
        return html_content
    
    def generate_pagination_html(self, current_page, total_pages, category=None):
        """ページネーションのHTMLを生成"""
        if total_pages <= 1:
            return ""
        
        html = '<div class="pagination">'
        
        # 前へボタン
        if current_page > 1:
            prev_page = current_page - 1
            filename = f"{category}_{prev_page}.html" if category else f"page_{prev_page}.html"
            html += f'<a href="{filename}" class="page-btn">← 前へ</a>'
        else:
            html += '<span class="page-btn disabled">← 前へ</span>'
        
        # ページ番号
        html += '<span class="page-numbers">'
        
        # ページ番号の表示ロジック
        if total_pages <= 7:
            # 7ページ以下なら全部表示
            for i in range(1, total_pages + 1):
                if i == current_page:
                    html += f'<span class="page-num active">{i}</span>'
                else:
                    filename = f"{category}_{i}.html" if category else f"page_{i}.html"
                    html += f'<a href="{filename}" class="page-num">{i}</a>'
        else:
            # 7ページ以上の場合は省略表示
            if current_page <= 3:
                for i in range(1, 5):
                    if i == current_page:
                        html += f'<span class="page-num active">{i}</span>'
                    else:
                        filename = f"{category}_{i}.html" if category else f"page_{i}.html"
                        html += f'<a href="{filename}" class="page-num">{i}</a>'
                html += '<span>...</span>'
                filename = f"{category}_{total_pages}.html" if category else f"page_{total_pages}.html"
                html += f'<a href="{filename}" class="page-num">{total_pages}</a>'
            elif current_page >= total_pages - 2:
                filename = f"{category}_1.html" if category else "page_1.html"
                html += f'<a href="{filename}" class="page-num">1</a>'
                html += '<span>...</span>'
                for i in range(total_pages - 3, total_pages + 1):
                    if i == current_page:
                        html += f'<span class="page-num active">{i}</span>'
                    else:
                        filename = f"{category}_{i}.html" if category else f"page_{i}.html"
                        html += f'<a href="{filename}" class="page-num">{i}</a>'
            else:
                filename = f"{category}_1.html" if category else "page_1.html"
                html += f'<a href="{filename}" class="page-num">1</a>'
                html += '<span>...</span>'
                for i in range(current_page - 1, current_page + 2):
                    if i == current_page:
                        html += f'<span class="page-num active">{i}</span>'
                    else:
                        filename = f"{category}_{i}.html" if category else f"page_{i}.html"
                        html += f'<a href="{filename}" class="page-num">{i}</a>'
                html += '<span>...</span>'
                filename = f"{category}_{total_pages}.html" if category else f"page_{total_pages}.html"
                html += f'<a href="{filename}" class="page-num">{total_pages}</a>'
        
        html += '</span>'
        
        # 次へボタン
        if current_page < total_pages:
            next_page = current_page + 1
            filename = f"{category}_{next_page}.html" if category else f"page_{next_page}.html"
            html += f'<a href="{filename}" class="page-btn">次へ →</a>'
        else:
            html += '<span class="page-btn disabled">次へ →</span>'
        
        html += '</div>'
        
        return html
    
    def generate_all_pages(self):
        """すべてのページを生成"""
        all_articles = self.get_all_articles()
        
        # 全体のページ生成
        total_pages = math.ceil(len(all_articles) / self.articles_per_page)
        
        for page in range(1, total_pages + 1):
            start_idx = (page - 1) * self.articles_per_page
            end_idx = start_idx + self.articles_per_page
            page_articles = all_articles[start_idx:end_idx]
            
            html = self.generate_page(page_articles, page, total_pages)
            
            filename = f"page_{page}.html" if page > 1 else "index_paginated.html"
            filepath = self.pages_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
        
        # カテゴリー別のページも生成
        categories = ["technical", "night", "message", "special", "curation"]
        
        for category in categories:
            category_articles = [a for a in all_articles if a["category"] == category]
            
            if category_articles:
                category_total_pages = math.ceil(len(category_articles) / self.articles_per_page)
                
                for page in range(1, category_total_pages + 1):
                    start_idx = (page - 1) * self.articles_per_page
                    end_idx = start_idx + self.articles_per_page
                    page_articles = category_articles[start_idx:end_idx]
                    
                    html = self.generate_page(page_articles, page, category_total_pages, category)
                    
                    filename = f"{category}_{page}.html"
                    filepath = self.pages_dir / filename
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(html)
        
        print(f"✅ ページング完了！")
        print(f"   総ページ数: {total_pages}")
        print(f"   カテゴリー別ページも生成しました")
        
        # 統計情報も表示
        stats = {cat: len([a for a in all_articles if a["category"] == cat]) for cat in categories}
        print(f"\n📊 カテゴリー別統計:")
        for cat, count in stats.items():
            if count > 0:
                print(f"   {cat}: {count}記事")

def test_pagination():
    """ページング機能のテスト"""
    paginator = PaginatedBlogSystem(articles_per_page=5)
    paginator.generate_all_pages()

if __name__ == "__main__":
    test_pagination()