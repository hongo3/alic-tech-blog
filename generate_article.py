#!/usr/bin/env python3
"""
GitHub Actions用の記事生成スクリプト
- 最新5記事のみを保持
- 日本標準時（JST）を使用
"""

import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import time
import os
import random
import re

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

def cleanup_old_articles(keep_count=5):
    """古い記事を削除して最新N件のみを保持"""
    print(f"\n🧹 記事のクリーンアップを開始します（最新{keep_count}件を保持）")
    
    # posts ディレクトリの記事を取得
    posts_dir = Path("posts")
    if not posts_dir.exists():
        return
    
    # すべての記事ファイルを取得して、更新時刻でソート（新しい順）
    md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if len(md_files) <= keep_count:
        print(f"  現在の記事数: {len(md_files)}件 - クリーンアップ不要")
        return
    
    # 削除対象の記事
    files_to_delete = md_files[keep_count:]
    print(f"  削除対象: {len(files_to_delete)}件の古い記事")
    
    # Markdownファイルを削除
    for md_file in files_to_delete:
        print(f"  🗑️  削除: {md_file.name}")
        md_file.unlink()
        
        # 対応するHTMLファイルも削除
        html_file = Path("docs/articles") / f"{md_file.stem}.html"
        if html_file.exists():
            html_file.unlink()
    
    print(f"  ✅ {len(files_to_delete)}件の記事を削除しました")

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
        "AIオーケストレーションの技術",
        "機械学習パイプラインの最適化",
        "AIモデルのデプロイメント戦略",
        "自然言語処理の実践応用",
        "コンピュータビジョンの最新技術",
        "強化学習の産業応用"
    ]
    
    # ランダムにトピックを選択
    topic = random.choice(topics)
    jst_now = get_jst_now()
    article_id = f"auto_{int(jst_now.timestamp())}"
    
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
    model = load_pretrained_model()
    results = model.predict(data)
    return results
```

## 実践的な応用

実際のプロジェクトでは、以下のような場面で活用されています：

- リアルタイムデータ処理
- 大規模な自動化システム
- インテリジェントな意思決定支援

## 今後の展望

{topic}の分野では、以下のような発展が期待されています：

1. **性能の向上**: より高速で正確な処理が可能に
2. **適用範囲の拡大**: 新たな業界や用途への展開
3. **標準化の進展**: 業界標準の確立と普及

## まとめ

{topic}は、今後のAI開発において重要な役割を果たすことが期待されます。
継続的な学習と実践を通じて、この技術を効果的に活用していきましょう。

---
*この記事はAIエージェントによって自動生成されました。*
*Generated at {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST*"""
    
    # 記事を保存
    posts_dir = blog_dir / "posts"
    posts_dir.mkdir(exist_ok=True)
    
    article_path = posts_dir / f"{article_id}.md"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: {topic}\n")
        f.write(f"date: {jst_now.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"tags: AI, Technology, Tutorial\n")
        f.write(f"source: https://qiita.com/tags/ai\n")
        f.write(f"---\n\n")
        f.write(content)
    
    print(f"✅ Generated: {topic}")
    print(f"   時刻: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    
    # HTMLに変換（確実に実行）
    if Path("convert_articles.py").exists():
        import subprocess
        print("📝 HTMLに変換中...")
        result = subprocess.run(
            ["python", "convert_articles.py"], 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"❌ HTML変換エラー: {result.stderr}")
        else:
            print("✅ HTML変換完了")
            print(result.stdout)
    
    # update_to_modern_ui.pyを使ってindex.htmlを更新
    if Path("update_to_modern_ui.py").exists():
        import subprocess
        print("📝 index.htmlを更新中...")
        subprocess.run(["python", "update_to_modern_ui.py"])
    
    return topic

async def update_index_html(article_id, title, jst_now):
    """index.htmlを更新して最新5記事のみを表示"""
    index_path = Path("docs/index.html")
    
    if not index_path.exists():
        print("❌ index.html not found")
        return
    
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    # 既存の記事セクションを取得
    articles_match = re.search(r'<section id="articles">(.*?)</section>', html, re.DOTALL)
    if not articles_match:
        print("❌ Articles section not found")
        return
    
    articles_html = articles_match.group(1)
    
    # 新記事のHTML
    new_article_html = f'''
            <article class="article">
                <h2>{title}<span class="new-badge">NEW</span></h2>
                <p class="meta">
                    📅 {jst_now.strftime('%Y-%m-%d %H:%M')} JST | 
                    🏷️ AI, Technology, Tutorial | 
                    🔗 <a href="https://qiita.com/tags/ai" target="_blank">参考元</a>
                </p>
                <div class="preview">{title}について、最新の技術動向と実装方法を解説します。</div>
                <a href="articles/{article_id}.html" class="read-more">
                    続きを読む →
                </a>
            </article>'''
    
    # 既存の記事を解析
    existing_articles = re.findall(r'<article class="article">.*?</article>', articles_html, re.DOTALL)
    
    # 新しい記事を先頭に追加
    all_articles = [new_article_html.strip()] + existing_articles
    
    # 最新5件のみを保持
    kept_articles = all_articles[:5]
    
    # NEW バッジを最新記事のみに付ける
    for i, article in enumerate(kept_articles):
        if i > 0:  # 最新記事以外
            # NEW バッジを削除
            article = re.sub(r'<span class="new-badge">NEW</span>', '', article)
            kept_articles[i] = article
    
    # 記事セクションを再構築
    new_articles_section = f'<section id="articles">\n{"".join(kept_articles)}\n        </section>'
    
    # HTMLを更新
    html = re.sub(r'<section id="articles">.*?</section>', new_articles_section, html, flags=re.DOTALL)
    
    # 更新時刻を変更（JST表記を追加）
    # 複数の時刻が連結されている場合も考慮
    html = re.sub(
        r'最終更新: [0-9: JST]+',
        f'最終更新: {jst_now.strftime("%H:%M:%S")} JST',
        html
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ Updated index.html (最新5記事のみ表示)")

async def main():
    """メイン処理"""
    print("🤖 GitHub Actions Article Generator")
    print("=" * 50)
    
    # 現在の日本時間を表示
    jst_now = get_jst_now()
    print(f"⏰ 現在の日本時間: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    
    # 1つの記事を生成
    topic = await generate_single_article()
    
    # 古い記事をクリーンアップ
    cleanup_old_articles(keep_count=5)
    
    # HTMLを再生成（クリーンアップ後）
    if Path("convert_articles.py").exists():
        print("\n📄 HTMLファイルを再生成しています...")
        os.system("python convert_articles.py")
    
    # index.htmlを更新
    if Path("update_to_modern_ui.py").exists():
        print("📝 index.htmlを最終更新中...")
        os.system("python update_to_modern_ui.py")
    
    print(f"\n✅ Successfully generated article: {topic}")
    print(f"✅ クリーンアップ完了 - 最新5記事を保持")

if __name__ == "__main__":
    asyncio.run(main())