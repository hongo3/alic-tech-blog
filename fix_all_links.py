#!/usr/bin/env python3
"""
すべての記事リンクを修正
"""

import re
from pathlib import Path

def fix_links():
    index_path = Path("docs/index.html")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # ../posts/*.md を articles/*.html に置換
    html = re.sub(r'href="../posts/([^"]+)\.md"', r'href="articles/\1.html"', html)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ すべてのリンクを修正しました！")

if __name__ == "__main__":
    fix_links()