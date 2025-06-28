#!/usr/bin/env python3
"""
記事クリーンアップ機能のテストスクリプト
"""

import asyncio
from pathlib import Path
import shutil
from datetime import datetime, timezone, timedelta

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

def backup_current_state():
    """現在の状態をバックアップ"""
    posts_dir = Path("posts")
    docs_dir = Path("docs")
    
    # バックアップディレクトリを作成
    backup_dir = Path("backup_test")
    backup_dir.mkdir(exist_ok=True)
    
    # postsディレクトリをバックアップ
    if posts_dir.exists():
        backup_posts = backup_dir / "posts"
        if backup_posts.exists():
            shutil.rmtree(backup_posts)
        shutil.copytree(posts_dir, backup_posts)
        print(f"✅ Backed up posts directory to {backup_posts}")
    
    # index.htmlをバックアップ
    index_path = docs_dir / "index.html"
    if index_path.exists():
        backup_index = backup_dir / "index.html"
        shutil.copy2(index_path, backup_index)
        print(f"✅ Backed up index.html to {backup_index}")
    
    return backup_dir

def show_current_status():
    """現在の記事の状態を表示"""
    posts_dir = Path("posts")
    docs_articles_dir = Path("docs/articles")
    
    print("\n📊 現在の状態:")
    print("=" * 50)
    
    # Markdownファイルの数
    md_files = list(posts_dir.glob("*.md"))
    print(f"Markdownファイル数: {len(md_files)}")
    
    # 最新5件のファイル名を表示
    recent_files = sorted(md_files, key=lambda x: x.name, reverse=True)[:5]
    print("\n最新5件のMarkdownファイル:")
    for i, f in enumerate(recent_files, 1):
        print(f"  {i}. {f.name}")
    
    # HTMLファイルの数
    if docs_articles_dir.exists():
        html_files = list(docs_articles_dir.glob("*.html"))
        print(f"\nHTMLファイル数: {len(html_files)}")

async def test_cleanup():
    """クリーンアップ機能をテスト"""
    print("🧪 記事クリーンアップ機能のテスト")
    print("=" * 50)
    
    jst_now = get_jst_now()
    print(f"⏰ 現在の日本時間: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    
    # 現在の状態を表示
    show_current_status()
    
    # ユーザーに確認
    response = input("\n⚠️  クリーンアップテストを実行しますか？ (y/n): ")
    if response.lower() != 'y':
        print("❌ テストをキャンセルしました")
        return
    
    # バックアップを作成
    backup_dir = backup_current_state()
    
    # generate_article.pyを実行
    print("\n🚀 generate_article.pyを実行中...")
    proc = await asyncio.create_subprocess_exec(
        'python', 'generate_article.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    print("\n--- 実行結果 ---")
    if stdout:
        print(stdout.decode('utf-8'))
    if stderr:
        print("エラー:", stderr.decode('utf-8'))
    
    # 実行後の状態を表示
    print("\n" + "=" * 50)
    show_current_status()
    
    # リストアの確認
    response = input(f"\n💾 バックアップから復元しますか？ (y/n): ")
    if response.lower() == 'y':
        # postsディレクトリを復元
        posts_dir = Path("posts")
        backup_posts = backup_dir / "posts"
        if backup_posts.exists():
            if posts_dir.exists():
                shutil.rmtree(posts_dir)
            shutil.copytree(backup_posts, posts_dir)
            print("✅ posts directory restored")
        
        # index.htmlを復元
        backup_index = backup_dir / "index.html"
        if backup_index.exists():
            shutil.copy2(backup_index, Path("docs/index.html"))
            print("✅ index.html restored")
        
        # バックアップディレクトリを削除
        shutil.rmtree(backup_dir)
        print("✅ Backup directory removed")
        
        # convert_articles.pyを実行して一貫性を保つ
        print("\n📄 HTMLファイルを再生成中...")
        import subprocess
        subprocess.run(['python', 'convert_articles.py'])
    
    print("\n✨ テスト完了!")

if __name__ == "__main__":
    asyncio.run(test_cleanup())