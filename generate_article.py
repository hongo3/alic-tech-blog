#!/usr/bin/env python3
"""
GitHub Actions用の記事生成スクリプト
"""

import asyncio
from datetime import datetime
from pathlib import Path
import json
import time
import os
import random

async def generate_single_article():
    """1つの記事を生成"""
    
    blog_dir = Path(".")  # カレントディレクトリで動作
    
    topics = [
        "AIエージェントの最新動向",
        "プロンプトエンジニアリングの実践テクニック",
        "マルチモーダルAIの応用事例",
        "RAGシステムの構築ガイド",
        "LLMファインチューニングの手法",
        "AIセキュリティのベストプラクティス",
        "エッジAIの実装パターン",
        "自律型AIシステムの設計",
        "ベクトルデータベースの活用法",
        "AIオーケストレーションの技術"
    ]
    
    # ランダムにトピックを選択
    topic = random.choice(topics)
    article_id = f"auto_{int(time.time())}"
    
    content = f"""# {topic}

{topic}について、最新の技術動向と実装方法を解説します。

## はじめに

AIテクノロジーの急速な進化により、{topic}がますます重要になっています。
本記事では、実践的な観点から詳しく解説していきます。

## 技術的背景

この技術が注目される理由として、以下の点が挙げられます：

1. **効率性の向上**: 従来の手法と比較して大幅な効率化が可能
2. **スケーラビリティ**: 大規模なシステムにも適用可能
3. **実装の容易さ**: 既存のフレームワークとの統合が簡単

## 実装例

```python
# サンプルコード
def implement_ai_system():
    # AIシステムの実装例
    pass
```

## 実践的な応用

実際のプロジェクトでは、以下のような場面で活用されています：

- リアルタイムデータ処理
- 大規模な自動化システム
- インテリジェントな意思決定支援

## まとめ

{topic}は、今後のAI開発において重要な役割を果たすことが期待されます。
継続的な学習と実践を通じて、この技術を効果的に活用していきましょう。

---
*この記事はAIエージェントによって自動生成されました。*
*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
    
    # 記事を保存
    posts_dir = blog_dir / "posts"
    posts_dir.mkdir(exist_ok=True)
    
    article_path = posts_dir / f"{article_id}.md"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"---\\n")
        f.write(f"title: {topic}\\n")
        f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\\n")
        f.write(f"tags: AI, Technology, Tutorial\\n")
        f.write(f"source: https://qiita.com/tags/ai\\n")
        f.write(f"---\\n\\n")
        f.write(content)
    
    print(f"✅ Generated: {topic}")
    
    # HTMLに変換
    if Path("convert_articles.py").exists():
        os.system("python convert_articles.py")
    
    # index.htmlを更新
    await update_index_html(article_id, topic)
    
    return topic

async def update_index_html(article_id, title):
    """index.htmlに新記事を追加"""
    index_path = Path("docs/index.html")
    
    if not index_path.exists():
        print("❌ index.html not found")
        return
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 新記事のHTML
    new_html = f'''
            <article class="article">
                <h2>{title}<span class="new-badge">NEW</span></h2>
                <p class="meta">
                    📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
                    🏷️ AI, Technology, Tutorial | 
                    🔗 <a href="https://qiita.com/tags/ai" target="_blank">参考元</a>
                </p>
                <div class="preview">{title}について、最新の技術動向と実装方法を解説します。</div>
                <a href="articles/{article_id}.html" class="read-more">
                    続きを読む →
                </a>
            </article>
'''
    
    # 記事を挿入
    html = html.replace('<section id="articles">', f'<section id="articles">{new_html}')
    
    # 更新時刻を変更
    import re
    html = re.sub(
        r'最終更新: [0-9:]+',
        f'最終更新: {datetime.now().strftime("%H:%M:%S")}',
        html
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ Updated index.html")

async def main():
    """メイン処理"""
    print("🤖 GitHub Actions Article Generator")
    print("=" * 50)
    
    # 1つの記事を生成
    topic = await generate_single_article()
    
    print(f"\\n✅ Successfully generated article: {topic}")

if __name__ == "__main__":
    asyncio.run(main())