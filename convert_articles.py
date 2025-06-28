#!/usr/bin/env python3
"""
Markdown記事をHTMLに変換
- 最新5記事のみを変換
- 日本標準時（JST）の表示に対応
"""

import os
from pathlib import Path
import re

def convert_md_to_html(md_file_path):
    """MarkdownファイルをHTMLに変換"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # メタデータとコンテンツを分離
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata = parts[1].strip()
            markdown_content = parts[2].strip()
            
            # メタデータをパース
            meta_dict = {}
            for line in metadata.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    meta_dict[key.strip()] = value.strip()
        else:
            meta_dict = {}
            markdown_content = content
    else:
        meta_dict = {}
        markdown_content = content
    
    # 簡単なMarkdown→HTML変換
    html_content = markdown_content
    
    # 見出し
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    
    # 太字
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # リスト
    html_content = re.sub(r'^- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\n\1</ul>\n', html_content)
    
    # 番号付きリスト
    html_content = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    
    # リンク
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
    
    # コードブロック
    html_content = re.sub(r'```[^\n]*\n(.*?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
    
    # インラインコード
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
    
    # 段落
    paragraphs = html_content.split('\n\n')
    html_content = '\n'.join(f'<p>{p}</p>' if not p.strip().startswith('<') else p for p in paragraphs if p.strip())
    
    # 日付にJST表記を追加（まだ付いていない場合）
    date_str = meta_dict.get('date', '')
    if date_str and 'JST' not in date_str:
        date_str += ' JST'
    
    # HTMLテンプレート
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_dict.get('title', 'Alic Blog Article')}</title>
    <link rel="stylesheet" href="../themes/article-style.css">
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, system-ui, sans-serif;
            line-height: 1.7;
            color: #1f2937;
        }}
        .article-header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #e5e7eb;
            margin-bottom: 40px;
        }}
        .article-meta {{
            color: #64748b;
            font-size: 0.9em;
            margin: 20px 0;
        }}
        .article-content {{
            font-size: 1.1em;
        }}
        .article-content h1, .article-content h2, .article-content h3 {{
            margin-top: 2em;
            margin-bottom: 1em;
            color: #2563eb;
        }}
        .article-content code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .article-content pre {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        .article-content pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 40px;
            padding: 10px 20px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }}
        .back-link:hover {{
            background: #1d4ed8;
        }}
    </style>
</head>
<body>
    <div class="article-header">
        <h1>{meta_dict.get('title', 'Untitled')}</h1>
        <div class="article-meta">
            📅 {date_str} | 
            🏷️ {meta_dict.get('tags', '')} | 
            🔗 <a href="{meta_dict.get('source', '#')}" target="_blank">参考元</a>
        </div>
    </div>
    
    <div class="article-content">
        {html_content}
    </div>
    
    <a href="../index.html" class="back-link">← ブログトップに戻る</a>
</body>
</html>"""
    
    return html_template

def main():
    """すべてのMarkdown記事をHTMLに変換（最新5件のみ）"""
    posts_dir = Path("posts")
    docs_dir = Path("docs/articles")
    
    # articlesディレクトリを作成
    docs_dir.mkdir(exist_ok=True)
    
    # すべてのMarkdownファイルを取得して、新しい順にソート（タイムスタンプで）
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    # 最新5件のみを変換
    files_to_convert = md_files[:5]
    
    print(f"📝 {len(files_to_convert)}個の記事をHTMLに変換します...")
    
    # 既存のHTMLファイルをすべて削除（クリーンアップ）
    for html_file in docs_dir.glob("*.html"):
        html_file.unlink()
    
    for md_file in files_to_convert:
        html_content = convert_md_to_html(md_file)
        
        # HTMLファイルとして保存
        html_filename = md_file.stem + ".html"
        html_path = docs_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ {md_file.name} → {html_filename}")
    
    print(f"\n✨ 完了！{len(files_to_convert)}個の記事をHTMLに変換しました。")

if __name__ == "__main__":
    main()