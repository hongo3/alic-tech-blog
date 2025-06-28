#!/usr/bin/env python3
"""
記事のメタデータ形式を修正するスクリプト
"""

from pathlib import Path
import re

def fix_metadata_in_file(file_path):
    """ファイルのメタデータ形式を修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # エスケープされた改行を実際の改行に変換
    if content.startswith('---\\n'):
        # 最初の部分だけ修正
        content = content.replace('---\\n', '---\n', 1)
        
        # メタデータ部分を修正
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # メタデータ部分のエスケープを修正
            metadata = parts[1]
            metadata = metadata.replace('\\n', '\n')
            
            # 再構築
            content = f"---{metadata}---{parts[2]}"
    
    return content

def main():
    """すべての記事ファイルを修正"""
    posts_dir = Path("posts")
    
    # 修正が必要なファイルを特定
    files_to_fix = []
    for md_file in posts_dir.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('---\\n'):
                files_to_fix.append(md_file)
    
    if files_to_fix:
        print(f"🔧 {len(files_to_fix)}個のファイルを修正します:")
        for md_file in files_to_fix:
            print(f"  - {md_file.name}")
            
            # ファイルを修正
            fixed_content = fix_metadata_in_file(md_file)
            
            # 保存
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
        
        print(f"\n✅ {len(files_to_fix)}個のファイルを修正しました")
    else:
        print("✅ 修正が必要なファイルはありません")

if __name__ == "__main__":
    main()