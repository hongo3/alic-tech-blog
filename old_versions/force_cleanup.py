#!/usr/bin/env python3
"""
強制的に記事をクリーンアップして最新5件のみを保持
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

def force_cleanup():
    """記事を強制的にクリーンアップ"""
    posts_dir = Path("posts")
    docs_articles_dir = Path("docs/articles")
    
    # すべての記事を取得（タイムスタンプでソート）
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📊 現在の記事数: {len(md_files)}")
    
    # 最新5件を保持
    keep_files = md_files[:5]
    delete_files = md_files[5:]
    
    print(f"✅ 保持する記事: {len(keep_files)}件")
    for f in keep_files:
        print(f"   - {f.name}")
    
    print(f"\n🗑️  削除する記事: {len(delete_files)}件")
    
    # 削除実行
    for md_file in delete_files:
        print(f"   削除: {md_file.name}")
        md_file.unlink()
        
        # 対応するHTMLも削除
        html_file = docs_articles_dir / f"{md_file.stem}.html"
        if html_file.exists():
            html_file.unlink()
    
    print(f"\n✅ クリーンアップ完了！")
    
    # HTMLを再生成
    import subprocess
    print("\n📝 HTMLを再生成中...")
    subprocess.run(["python", "convert_articles.py"])
    
    # index.htmlを更新
    print("\n📝 index.htmlを更新中...")
    subprocess.run(["python", "update_to_modern_ui.py"])

if __name__ == "__main__":
    force_cleanup()