#!/usr/bin/env python3
"""
ページネーション対応ブログ生成システム
全ての記事を削除せずに、ページごとに表示する機能を実装
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
import markdown
import math

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

class PaginatedBlogGenerator:
    """ページネーション対応ブログ生成クラス"""
    
    def __init__(self, posts_dir="posts", docs_dir="docs", articles_per_page=5):
        self.posts_dir = Path(posts_dir)
        self.docs_dir = Path(docs_dir)
        self.articles_per_page = articles_per_page
        
    def get_all_articles(self):
        """全ての記事を取得してメタデータでソート"""
        articles = []
        
        if not self.posts_dir.exists():
            return articles
            
        for md_file in self.posts_dir.glob("*.md"):
            try:
                article_data = self._parse_article(md_file)
                if article_data:
                    articles.append(article_data)
            except Exception as e:
                print(f"Error parsing {md_file}: {e}")
                
        # 日付順にソート（新しい順）
        articles.sort(key=lambda x: x['timestamp'], reverse=True)
        return articles
    
    def _parse_article(self, md_file):
        """記事ファイルを解析してメタデータを取得"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # メタデータ抽出
        metadata = {}
        content_body = content
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                metadata_text = parts[1]
                content_body = parts[2]
                
                # メタデータをパース
                for line in metadata_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        # プレビューテキストを生成
        preview = self._generate_preview(content_body)
        
        # タイムスタンプを生成
        timestamp = self._extract_timestamp(md_file.stem, metadata.get('date', ''))
        
        return {
            'filename': md_file.stem,
            'title': metadata.get('title', 'Untitled'),
            'date': metadata.get('date', ''),
            'category': metadata.get('category', 'general'),
            'tags': metadata.get('tags', ''),
            'difficulty': metadata.get('difficulty', '中級'),
            'reading_time': metadata.get('reading_time', '10分'),
            'source': metadata.get('source', ''),
            'preview': preview,
            'timestamp': timestamp
        }
    
    def _extract_timestamp(self, filename, date_str):
        """ファイル名から日付を抽出"""
        # ファイル名から日付を抽出（article_1751116762.md形式）
        match = re.search(r'article_(\d+)', filename)
        if match:
            return int(match.group(1))
        
        # 日付文字列から変換
        if date_str:
            try:
                # 2025-06-28 22:19 形式
                dt = datetime.strptime(date_str + ':00', '%Y-%m-%d %H:%M:%S')
                return int(dt.timestamp())
            except:
                pass
                
        return 0
    
    def _generate_preview(self, content):
        """記事のプレビューテキストを生成"""
        # Markdownから見出しとテキストを抽出
        lines = content.split('\n')
        preview_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```') and not line.startswith('<'):
                # HTMLタグやMarkdown記法を除去
                clean_line = re.sub(r'[*_`\[\]()]', '', line)
                if len(clean_line) > 20:  # 短すぎる行は除外
                    preview_lines.append(clean_line)
                    if len(' '.join(preview_lines)) > 100:
                        break
        
        preview = ' '.join(preview_lines)[:150]
        return preview + '...' if len(preview) == 150 else preview
    
    def generate_paginated_html(self):
        """ページネーション対応のHTMLを生成"""
        articles = self.get_all_articles()
        total_pages = math.ceil(len(articles) / self.articles_per_page)
        
        # メインページを生成
        self._generate_main_page(articles, total_pages)
        
        # 各ページを生成
        for page in range(1, total_pages + 1):
            self._generate_page(articles, page, total_pages)
    
    def _generate_main_page(self, articles, total_pages):
        """メインページ（1ページ目）を生成"""
        page_articles = articles[:self.articles_per_page]
        
        # カテゴリー統計を計算
        category_stats = self._calculate_category_stats(articles)
        
        html_content = self._generate_html_template(
            page_articles, 
            current_page=1, 
            total_pages=total_pages,
            total_articles=len(articles),
            category_stats=category_stats
        )
        
        # index.htmlに書き込み
        output_path = self.docs_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated main page: {output_path}")
    
    def _generate_page(self, articles, page_num, total_pages):
        """指定されたページのHTMLを生成"""
        start_idx = (page_num - 1) * self.articles_per_page
        end_idx = start_idx + self.articles_per_page
        page_articles = articles[start_idx:end_idx]
        
        if not page_articles:
            return
        
        # カテゴリー統計を計算
        category_stats = self._calculate_category_stats(articles)
        
        html_content = self._generate_html_template(
            page_articles, 
            current_page=page_num, 
            total_pages=total_pages,
            total_articles=len(articles),
            category_stats=category_stats
        )
        
        # ページファイルに書き込み
        output_path = self.docs_dir / f"page_{page_num}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Generated page {page_num}: {output_path}")
    
    def _calculate_category_stats(self, articles):
        """カテゴリー統計を計算"""
        stats = {}
        for article in articles:
            category = article['category']
            stats[category] = stats.get(category, 0) + 1
        return stats
    
    def _generate_html_template(self, articles, current_page, total_pages, total_articles, category_stats):
        """HTMLテンプレートを生成"""
        
        current_time = get_jst_now().strftime("%H:%M:%S JST")
        
        # 記事のHTMLを生成
        articles_html = ""
        for article in articles:
            category_color = self._get_category_color(article['category'])
            article_html = f'''
        <article class="article" data-category="{article['category'].lower().replace(' ', '_')}">
            <div class="article-header-info">
                <h2>{article['title']}</h2>
                <div class="article-meta-tags">
                    <span class="category-badge" style="background-color: {category_color}">{article['category']}</span>
                    <span class="difficulty-badge">{article['difficulty']}</span>
                    <span class="reading-time">📖 {article['reading_time']}</span>
                </div>
            </div>
            <p class="meta">
                📅 {article['date']} | 
                🏷️ {article['tags']}
            </p>
            <div class="preview">{article['preview']}</div>
            <a href="articles/{article['filename']}.html" class="read-more">
                続きを読む →
            </a>
        </article>'''
            articles_html += article_html
        
        # ページネーションのHTMLを生成
        pagination_html = self._generate_pagination_html(current_page, total_pages)
        
        # カテゴリー統計のHTMLを生成
        category_stats_html = " | ".join([f"{cat}: {count}件" for cat, count in category_stats.items()])
        
        return f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alic AI Blog - AIが創る未来のテックブログ</title>
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
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }}
        
        .page-btn {{
            padding: 8px 16px;
            background-color: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        
        .page-btn:hover {{
            background-color: #5a6fd8;
        }}
        
        .page-btn:disabled {{
            background-color: #ccc;
            cursor: not-allowed;
        }}
        
        .page-numbers {{
            display: flex;
            gap: 5px;
            align-items: center;
        }}
        
        .page-num {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            background-color: white;
            cursor: pointer;
            text-decoration: none;
            border-radius: 3px;
            color: #333;
        }}
        
        .page-num.active {{
            background-color: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .page-num:hover:not(.active) {{
            background-color: #f5f5f5;
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
        <h1 class="glitch" data-text="Alic AI Blog">Alic AI Blog</h1>
        <p class="tagline">24/7 AI-Powered Tech Insights</p>
        <p class="status">🟢 システム稼働中 | 最終更新: {current_time}</p>
        <div class="stats-bar">
            <span>📝 総記事数: <strong>{total_articles}</strong></span>
            <span>🤖 稼働時間: <strong>∞</strong></span>
            <span>⚡ 更新頻度: <strong>30分毎</strong></span>
            <span>📄 ページ: <strong>{current_page}/{total_pages}</strong></span>
        </div>
        <div class="category-stats">
            {category_stats_html}
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
        {articles_html}
        </section>
    </div>
    
    {pagination_html}
    
    <footer>
        <p>© 2025 Alic AI Blog - Powered by AI Agents</p>
        <p>自己改善型AIシステムが24時間365日、より良いコンテンツを生成中</p>
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
        
        // 自動リロード
        setInterval(() => {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>'''
    
    def _generate_pagination_html(self, current_page, total_pages):
        """ページネーションのHTMLを生成"""
        if total_pages <= 1:
            return ""
        
        pagination_html = '<div class="pagination">'
        
        # 前へボタン
        if current_page > 1:
            prev_page = 'index.html' if current_page == 2 else f'page_{current_page - 1}.html'
            pagination_html += f'<a href="{prev_page}" class="page-btn">← 前へ</a>'
        else:
            pagination_html += '<button class="page-btn" disabled>← 前へ</button>'
        
        # ページ番号
        pagination_html += '<span class="page-numbers">'
        
        # 最初のページ
        if current_page == 1:
            pagination_html += '<span class="page-num active">1</span>'
        else:
            pagination_html += '<a href="index.html" class="page-num">1</a>'
        
        # 中間のページ
        start_page = max(2, current_page - 2)
        end_page = min(total_pages, current_page + 2)
        
        if start_page > 2:
            pagination_html += '<span>...</span>'
        
        for page in range(start_page, end_page + 1):
            if page == total_pages and total_pages == 1:
                continue
                
            if page == current_page:
                pagination_html += f'<span class="page-num active">{page}</span>'
            else:
                if page == 1:
                    continue  # 既に処理済み
                page_file = 'index.html' if page == 1 else f'page_{page}.html'
                pagination_html += f'<a href="{page_file}" class="page-num">{page}</a>'
        
        if end_page < total_pages - 1:
            pagination_html += '<span>...</span>'
        
        # 最後のページ
        if total_pages > 1 and current_page != total_pages:
            pagination_html += f'<a href="page_{total_pages}.html" class="page-num">{total_pages}</a>'
        
        pagination_html += '</span>'
        
        # 次へボタン
        if current_page < total_pages:
            next_page = f'page_{current_page + 1}.html'
            pagination_html += f'<a href="{next_page}" class="page-btn">次へ →</a>'
        else:
            pagination_html += '<button class="page-btn" disabled>次へ →</button>'
        
        pagination_html += '</div>'
        return pagination_html
    
    def _get_category_color(self, category):
        """カテゴリーに対応する色を取得"""
        colors = {
            'AI開発': '#667eea',
            'Web技術': '#48bb78',
            'インフラ': '#ed8936',
            'セキュリティ': '#f56565',
            'データサイエンス': '#38b2ac',
            'general': '#718096'
        }
        return colors.get(category, '#718096')

def main():
    """メイン実行関数"""
    print("📄 ページネーション対応ブログ生成システム")
    print("=" * 60)
    
    generator = PaginatedBlogGenerator()
    generator.generate_paginated_html()
    
    print(f"✅ ページネーション対応ブログ生成完了")

if __name__ == "__main__":
    main()