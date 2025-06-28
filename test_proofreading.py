#!/usr/bin/env python3
"""
校正システムのテスト
"""

import asyncio
from pathlib import Path
from article_proofreader import ArticleProofreader

async def test_proofreading():
    """校正システムをテスト"""
    
    # テスト用の記事を作成
    test_content = """---
title: テスト記事：React 17とPython 3.8の活用
date: 2025-06-28 21:00
category: Web技術
tags: React, Python, テスト
difficulty: 初級
reading_time: 5分
---

# テスト記事：React 17とPython 3.8の活用

## はじめに

この記事では、React 17とPython 3.8を使った開発について説明します。
最新の技術動向を踏まえて解説していきます。

## 古い技術の使用例

以下のコードはcomponentWillMountを使っています：

```javascript
class OldComponent extends React.Component {
    componentWillMount() {
        console.log("This is deprecated!");
    }
}
```

また、varを使った変数宣言も見られます：

```javascript
var oldVariable = "This should be const or let";
```

## 誤字脱字の例

こどもでも理解できるように説明します。
すくなくとも基本的な概念は理解してる必要があります。

## 長い文章の例

この文章は非常に長く、一文で多くの情報を伝えようとしているため、読者にとって理解しづらく、また文の構造も複雑になってしまっており、結果として伝えたい内容が不明確になってしまう可能性があります。

## まとめ

本記事では、古い技術について解説しました。
"""
    
    # テスト記事を保存
    test_file = Path("test_article.md")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("📝 テスト記事を作成しました")
    
    # 校正システムを実行
    proofreader = ArticleProofreader()
    result = await proofreader.proofread_article(test_file)
    
    print("\n📊 校正結果:")
    print(f"  - 元のスコア: {result['original_score']}")
    print(f"  - 検出された問題: {len(result['issues_found'])}件")
    print(f"  - 自動修正: {len(result['corrections'])}件")
    print(f"  - 最終スコア: {result['final_score']}")
    
    print("\n⚠️  検出された問題の詳細:")
    for issue in result['issues_found']:
        print(f"  [{issue['severity']}] {issue['type']}: {issue['original']} → {issue.get('suggestion', 'N/A')}")
    
    if result['corrections']:
        print("\n✅ 適用された修正:")
        for correction in result['corrections']:
            print(f"  - {correction['type']}: {correction['original']} → {correction['corrected']}")
    
    # テストファイルを削除
    test_file.unlink()
    print("\n🧹 テストファイルを削除しました")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_proofreading())