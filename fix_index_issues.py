#!/usr/bin/env python3
"""
index.htmlの問題を修正
- CSSパスを修正
- 記事リンクを修正
- タイムスタンプの累積を修正
"""

from pathlib import Path
import re

def fix_index_issues():
    """index.htmlの問題を修正"""
    index_path = Path("docs/index.html")
    
    if not index_path.exists():
        print("❌ index.html not found")
        return
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # CSSパスを修正（既に修正済みの場合はスキップ）
    if 'href="../themes/modern-ui.css"' in html:
        html = html.replace('href="../themes/modern-ui.css"', 'href="themes/modern-ui.css"')
        print("✅ CSSパスを修正しました")
    
    # 記事リンクを修正（../posts/*.md → articles/*.html）
    # 新しいパターン
    html = re.sub(
        r'<a href="../posts/([^"]+)\.md"',
        r'<a href="articles/\1.html"',
        html
    )
    
    # 累積したタイムスタンプを修正
    # 複数のタイムスタンプがある場合、最初のものだけを残す
    html = re.sub(
        r'最終更新: ([\d:]+) JST(?: [\d:]+ JST)*',
        r'最終更新: \1 JST',
        html
    )
    
    # 保存
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ index.htmlの問題を修正しました")
    print("   - CSSパス: themes/modern-ui.css")
    print("   - 記事リンク: articles/*.html")
    print("   - タイムスタンプ: 最新のみ表示")

if __name__ == "__main__":
    fix_index_issues()