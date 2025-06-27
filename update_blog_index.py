#!/usr/bin/env python3
"""
ブログのindex.htmlを正しく更新
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta
import re

def update_blog_index():
    """index.htmlを最新の記事で更新"""
    
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    posts_dir = Path("posts")
    
    # 最新5件の記事を取得
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.name, reverse=True)[:5]
    
    articles_html = []
    
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
        if "night_" in md_file.stem:
            badge = "NIGHT"
        elif "special_" in md_file.stem:
            badge = "SPECIAL"
        elif "travel_" in md_file.stem:
            badge = "MESSAGE"
        
        # 記事HTMLを生成
        article_html = f'''            <article class="article">
                <h2>{title}<span class="new-badge">{badge}</span></h2>
                <p class="meta">
                    📅 {date} | 
                    🏷️ {tags} | 
                    🔗 <a href="https://github.com/hongo3/alic-tech-blog" target="_blank">参考元</a>
                </p>
                <div class="preview">{preview}</div>
                <a href="articles/{html_filename}" class="read-more">
                    続きを読む →
                </a>
            </article>
'''
        articles_html.append(article_html)
    
    # index.htmlを読む
    index_path = Path("docs/index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 記事セクションを置き換え
    articles_section = f'''        <section id="articles">
{"".join(articles_html)}        </section>'''
    
    # 既存の記事セクションを置き換え
    html = re.sub(
        r'<section id="articles">.*?</section>',
        articles_section,
        html,
        flags=re.DOTALL
    )
    
    # 最終更新時刻を修正（累積を防ぐ）
    html = re.sub(
        r'<p class="status">🟢 システム稼働中 \| 最終更新: .*?</p>',
        f'<p class="status">🟢 システム稼働中 | 最終更新: {jst_now.strftime("%H:%M:%S")} JST</p>',
        html
    )
    
    # 保存
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ index.htmlを更新しました")
    print(f"   最終更新: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    print(f"   記事数: {len(articles_html)}件")

if __name__ == "__main__":
    update_blog_index()