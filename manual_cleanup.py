#!/usr/bin/env python3
"""
既存の記事を手動でクリーンアップするスクリプト
最新5記事のみを保持し、index.htmlも更新
"""

from pathlib import Path
import shutil
from datetime import datetime, timezone, timedelta
import re
import subprocess

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

def cleanup_articles(keep_count=5):
    """記事をクリーンアップして最新N件のみを保持"""
    posts_dir = Path("posts")
    docs_articles_dir = Path("docs/articles")
    
    if not posts_dir.exists():
        print("❌ posts directory not found")
        return
    
    # 現在の状態を表示
    all_md_files = list(posts_dir.glob("*.md"))
    print(f"\n📊 現在の記事数: {len(all_md_files)}")
    
    # ファイル名でソート（新しい順）
    sorted_files = sorted(all_md_files, key=lambda x: x.name, reverse=True)
    
    # 保持する記事と削除する記事を分ける
    keep_files = sorted_files[:keep_count]
    delete_files = sorted_files[keep_count:]
    
    print(f"\n✅ 保持する記事: {len(keep_files)}件")
    for f in keep_files[:5]:  # 最初の5件を表示
        print(f"   - {f.name}")
    
    if delete_files:
        print(f"\n🗑️  削除する記事: {len(delete_files)}件")
        print(f"   最も古い記事: {delete_files[-1].name}")
        print(f"   最も新しい削除対象: {delete_files[0].name}")
        
        # 確認
        response = input(f"\n⚠️  {len(delete_files)}件の記事を削除しますか？ (y/n): ")
        if response.lower() != 'y':
            print("❌ キャンセルしました")
            return
        
        # 削除実行
        for md_file in delete_files:
            md_file.unlink()
            
            # 対応するHTMLファイルも削除
            html_file = docs_articles_dir / f"{md_file.stem}.html"
            if html_file.exists():
                html_file.unlink()
        
        print(f"✅ {len(delete_files)}件の記事を削除しました")
    else:
        print("\n✅ 削除対象の記事はありません")

def rebuild_html():
    """HTMLファイルを再生成"""
    print("\n📄 HTMLファイルを再生成中...")
    
    # convert_articles.pyを実行
    result = subprocess.run(['python', 'convert_articles.py'], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("エラー:", result.stderr)

def update_index_html():
    """index.htmlを更新して最新5記事のみを表示"""
    print("\n📝 index.htmlを更新中...")
    
    posts_dir = Path("posts")
    index_path = Path("docs/index.html")
    
    if not index_path.exists():
        print("❌ index.html not found")
        return
    
    # 最新5件の記事を取得
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.name, reverse=True)[:5]
    
    # 各記事のメタデータを読み込む
    articles_html = []
    for i, md_file in enumerate(md_files):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # メタデータを抽出
        meta_dict = {}
        if content.startswith('---'):
            # 特殊な形式の処理（---\n...の場合）
            content = content.replace('---\\n', '---\n')
            parts = content.split('---', 2)
            if len(parts) >= 3:
                metadata = parts[1].strip()
                for line in metadata.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        meta_dict[key.strip()] = value.strip()
        
        # 日付にJSTを追加
        date_str = meta_dict.get('date', '')
        if date_str and 'JST' not in date_str:
            date_str += ' JST'
        
        # NEWバッジは最新記事のみ
        new_badge = '<span class="new-badge">NEW</span>' if i == 0 else ''
        
        article_html = f'''
            <article class="article">
                <h2>{meta_dict.get('title', 'Untitled')}{new_badge}</h2>
                <p class="meta">
                    📅 {date_str} | 
                    🏷️ {meta_dict.get('tags', '')} | 
                    🔗 <a href="{meta_dict.get('source', '#')}" target="_blank">参考元</a>
                </p>
                <div class="preview">{meta_dict.get('title', '')}について、最新の技術動向と実装方法を解説します。</div>
                <a href="articles/{md_file.stem}.html" class="read-more">
                    続きを読む →
                </a>
            </article>'''
        
        articles_html.append(article_html)
    
    # index.htmlを読み込む
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 記事セクションを更新
    articles_section = f'<section id="articles">{"".join(articles_html)}\n        </section>'
    html = re.sub(r'<section id="articles">.*?</section>', articles_section, html, flags=re.DOTALL)
    
    # 更新時刻を変更
    jst_now = get_jst_now()
    html = re.sub(
        r'最終更新: [0-9:]+( JST)?',
        f'最終更新: {jst_now.strftime("%H:%M:%S")} JST',
        html
    )
    
    # 保存
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ index.htmlを更新しました")

def main():
    """メイン処理"""
    print("🧹 記事クリーンアップツール")
    print("=" * 50)
    
    jst_now = get_jst_now()
    print(f"⏰ 現在の日本時間: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    
    # クリーンアップ実行
    cleanup_articles(keep_count=5)
    
    # HTMLを再生成
    rebuild_html()
    
    # index.htmlを更新
    update_index_html()
    
    print("\n✨ クリーンアップ完了!")

if __name__ == "__main__":
    main()