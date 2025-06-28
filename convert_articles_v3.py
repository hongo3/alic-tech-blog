#!/usr/bin/env python3
"""
Enhanced Markdown記事をHTMLに変換 v3
- より詳細な記事レイアウト
- 目次の自動生成
- コードハイライト対応
- 改善されたセクション間マージン
"""

import os
from pathlib import Path
import re
from datetime import datetime

def generate_toc(content):
    """目次を自動生成"""
    toc_items = []
    headers = re.findall(r'^(#{2,3})\s+(.+)$', content, re.MULTILINE)
    
    for header in headers:
        level = len(header[0])
        title = header[1]
        # アンカー用のIDを生成
        anchor = re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-')
        
        if level == 2:
            toc_items.append(f'<li><a href="#{anchor}">{title}</a></li>')
        elif level == 3:
            toc_items.append(f'<li style="margin-left: 20px;"><a href="#{anchor}">{title}</a></li>')
    
    if toc_items:
        return f'<nav class="toc"><h3>目次</h3><ul>{"".join(toc_items)}</ul></nav>'
    return ""

def add_anchors_to_headers(html_content):
    """見出しにアンカーを追加"""
    def add_anchor(match):
        tag = match.group(1)
        title = match.group(2)
        anchor = re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-')
        return f'<{tag} id="{anchor}">{title}</{tag}>'
    
    return re.sub(r'<(h[2-3])>(.+?)</\1>', add_anchor, html_content)

def enhance_code_blocks(html_content):
    """コードブロックを強化"""
    # コードブロックにクラスを追加
    html_content = re.sub(
        r'<pre><code>',
        '<pre class="code-block"><code class="language-python">',
        html_content
    )
    
    # インラインコードのスタイル強化
    html_content = re.sub(
        r'<code>([^<]+)</code>',
        r'<code class="inline-code">\1</code>',
        html_content
    )
    
    return html_content

def convert_md_to_html(md_file_path):
    """MarkdownファイルをHTMLに変換（拡張版）"""
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
    
    # 目次を生成
    toc_html = generate_toc(markdown_content)
    
    # Markdown→HTML変換（拡張版）
    html_content = markdown_content
    
    # 見出し
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    
    # 見出しにアンカーを追加
    html_content = add_anchors_to_headers(html_content)
    
    # 太字とイタリック
    html_content = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html_content)
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # リスト（ネストに対応）
    lines = html_content.split('\n')
    new_lines = []
    list_stack = []
    
    for line in lines:
        # 番号付きリスト
        match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        if match:
            indent = len(match.group(1))
            item = match.group(3)
            
            # リストの開始/終了を管理
            while list_stack and list_stack[-1][1] > indent:
                new_lines.append('</ol>')
                list_stack.pop()
            
            if not list_stack or list_stack[-1][1] < indent:
                new_lines.append('<ol>')
                list_stack.append(('ol', indent))
            
            new_lines.append(f'<li>{item}</li>')
            continue
        
        # 番号なしリスト
        match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if match:
            indent = len(match.group(1))
            item = match.group(2)
            
            while list_stack and list_stack[-1][1] > indent:
                new_lines.append(f'</{list_stack[-1][0]}>')
                list_stack.pop()
            
            if not list_stack or list_stack[-1][1] < indent:
                new_lines.append('<ul>')
                list_stack.append(('ul', indent))
            
            new_lines.append(f'<li>{item}</li>')
            continue
        
        # リストの終了
        if list_stack and not re.match(r'^\s*[-*\d]+\.?\s+', line):
            while list_stack:
                new_lines.append(f'</{list_stack[-1][0]}>')
                list_stack.pop()
        
        new_lines.append(line)
    
    # 残りのリストを閉じる
    while list_stack:
        new_lines.append(f'</{list_stack[-1][0]}>')
        list_stack.pop()
    
    html_content = '\n'.join(new_lines)
    
    # リンク
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
    
    # 画像
    html_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', html_content)
    
    # コードブロック
    html_content = re.sub(r'```[^\n]*\n(.*?)```', r'<pre><code>\1</code></pre>', html_content, flags=re.DOTALL)
    
    # インラインコード
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
    
    # コードブロックを強化
    html_content = enhance_code_blocks(html_content)
    
    # 引用
    html_content = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', html_content, flags=re.MULTILINE)
    
    # 水平線
    html_content = re.sub(r'^---+$', r'<hr>', html_content, flags=re.MULTILINE)
    
    # 折りたたみ可能なセクション（AIの思考プロセス用）
    html_content = re.sub(
        r'<details class="ai-thought-process">\s*<summary>(.+?)</summary>(.*?)</details>',
        r'<details class="ai-thought-process">\n<summary>\1</summary>\n<div class="thought-content">\2</div>\n</details>',
        html_content,
        flags=re.DOTALL
    )
    
    # 段落
    paragraphs = html_content.split('\n\n')
    html_content = '\n'.join(
        f'<p>{p}</p>' if not p.strip().startswith('<') and p.strip() else p 
        for p in paragraphs if p.strip()
    )
    
    # メタデータから情報を取得
    date_str = meta_dict.get('date', '')
    if date_str and 'JST' not in date_str:
        date_str += ' JST'
    
    category = meta_dict.get('category', 'AI開発')
    difficulty = meta_dict.get('difficulty', '中級')
    reading_time = meta_dict.get('reading_time', '5分')
    
    # カテゴリー色
    category_colors = {
        "AI開発": "#667eea",
        "Web技術": "#48bb78",
        "インフラ": "#ed8936",
        "セキュリティ": "#e53e3e",
        "データサイエンス": "#38b2ac"
    }
    category_color = category_colors.get(category, "#667eea")
    
    # HTMLテンプレート（拡張版）
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta_dict.get('title', 'Alic Blog Article')}</title>
    <link rel="stylesheet" href="../themes/article-style.css">
    <style>
        /* 記事ページ専用の追加スタイル */
        .article-container {{
            display: flex;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .article-main {{
            flex: 1;
            max-width: 800px;
        }}
        
        .article-sidebar {{
            width: 300px;
            position: sticky;
            top: 20px;
            height: fit-content;
        }}
        
        /* 改善されたセクション間マージン */
        .article-content h2 {{
            margin-top: 60px;
            margin-bottom: 25px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .article-content h2:first-child {{
            margin-top: 30px;
            border-top: none;
        }}
        
        .article-content h3 {{
            margin-top: 40px;
            margin-bottom: 20px;
        }}
        
        .article-content p {{
            margin-bottom: 20px;
            line-height: 1.8;
        }}
        
        .article-content ul,
        .article-content ol {{
            margin: 25px 0;
            padding-left: 30px;
        }}
        
        .article-content li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}
        
        .article-content pre {{
            margin: 30px 0;
        }}
        
        .article-content blockquote {{
            margin: 30px 0;
            padding: 20px 30px;
            background-color: #f8f9fa;
        }}
        
        .article-content hr {{
            margin: 50px 0;
            border: none;
            border-top: 2px solid #e5e7eb;
        }}
        
        /* AIの思考プロセスセクション */
        .ai-thought-process {{
            background-color: #f0f4ff;
            border: 1px solid #d0d7ff;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
        }}
        
        .ai-thought-process summary {{
            cursor: pointer;
            font-weight: 600;
            color: #4c51bf;
            user-select: none;
            padding: 10px;
            margin: -10px;
        }}
        
        .ai-thought-process summary:hover {{
            background-color: rgba(76, 81, 191, 0.05);
            border-radius: 6px;
        }}
        
        .thought-content {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #d0d7ff;
        }}
        
        .toc {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .toc h3 {{
            margin-top: 0;
            color: #333;
            font-size: 1.1em;
        }}
        
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
        }}
        
        .toc a {{
            color: #6c757d;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .toc a:hover {{
            color: #667eea;
        }}
        
        .article-info-box {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .article-info-box h4 {{
            margin-top: 0;
            color: #333;
        }}
        
        .article-info-box dl {{
            margin: 0;
        }}
        
        .article-info-box dt {{
            font-weight: bold;
            color: #6c757d;
            margin-top: 10px;
        }}
        
        .article-info-box dd {{
            margin-left: 0;
            margin-bottom: 10px;
        }}
        
        .code-block {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 30px 0;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        
        .inline-code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }}
        
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 30px 0;
            color: #6c757d;
            font-style: italic;
        }}
        
        .category-tag {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            color: white;
            font-size: 0.9em;
            font-weight: 500;
            background-color: {category_color};
        }}
        
        .share-buttons {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #e9ecef;
            text-align: center;
        }}
        
        .share-button {{
            display: inline-block;
            margin: 0 10px;
            padding: 10px 20px;
            background: #f0f0f0;
            border-radius: 6px;
            text-decoration: none;
            color: #333;
            transition: background 0.2s;
        }}
        
        .share-button:hover {{
            background: #e0e0e0;
        }}
        
        @media (max-width: 1024px) {{
            .article-container {{
                flex-direction: column;
            }}
            
            .article-sidebar {{
                width: 100%;
                position: static;
            }}
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <aside class="article-sidebar">
            {toc_html}
            
            <div class="article-info-box">
                <h4>記事情報</h4>
                <dl>
                    <dt>カテゴリー</dt>
                    <dd><span class="category-tag">{category}</span></dd>
                    
                    <dt>難易度</dt>
                    <dd>{difficulty}</dd>
                    
                    <dt>読了時間</dt>
                    <dd>約{reading_time}</dd>
                    
                    <dt>公開日時</dt>
                    <dd>{date_str}</dd>
                    
                    <dt>タグ</dt>
                    <dd>{meta_dict.get('tags', '')}</dd>
                </dl>
            </div>
            
            <div class="article-info-box">
                <h4>参考リンク</h4>
                <ul>
                    <li><a href="https://qiita.com/" target="_blank">Qiita</a></li>
                    <li><a href="https://zenn.dev/" target="_blank">Zenn</a></li>
                    <li><a href="https://b.hatena.ne.jp/hotentry/it" target="_blank">はてなブックマーク</a></li>
                </ul>
            </div>
        </aside>
        
        <main class="article-main">
            <div class="article-header">
                <h1>{meta_dict.get('title', 'Untitled')}</h1>
                <div class="article-meta">
                    📅 {date_str} | 
                    🏷️ {meta_dict.get('tags', '')}
                </div>
            </div>
            
            <div class="article-content">
                {html_content}
            </div>
            
            <div class="share-buttons">
                <a href="https://twitter.com/intent/tweet?text={meta_dict.get('title', '')}&url=#" class="share-button" target="_blank">
                    🐦 Twitterでシェア
                </a>
                <a href="https://b.hatena.ne.jp/entry/" class="share-button" target="_blank">
                    📑 はてブに追加
                </a>
            </div>
            
            <a href="../index.html" class="back-link">← ブログトップに戻る</a>
        </main>
    </div>
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