#!/usr/bin/env python3
"""
深夜の特別メッセージ記事生成
"""

import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
import time
import os
import random

async def create_night_message():
    """深夜の特別メッセージ記事を作成"""
    
    jst_now = datetime.now(timezone(timedelta(hours=9)))
    article_id = f"night_{int(time.time())}"
    
    # 深夜のメッセージをランダムに選択
    messages = [
        {
            "title": "🌙 深夜のAI開発者へ - 夜更かしエンジニアの味方",
            "content": """深夜の静寂の中でコードを書くエンジニアの皆様へ。

AIエージェントは24時間休まず働いていますが、人間の皆様は適度な休息が必要です。
でも、深夜のプログラミングには独特の魅力がありますよね。

- 集中力が高まる静かな環境
- 邪魔されない連続した作業時間
- クリエイティブな発想が生まれやすい時間帯

今夜も素晴らしいコードが生まれることを願っています！"""
        },
        {
            "title": "🦉 夜型エンジニアのための生産性Tips",
            "content": """夜更かしプログラマーの皆様、調子はいかがですか？

深夜の開発を効率的にするためのTipsをお届けします：

1. **ブルーライトカット**: 目の疲れを軽減
2. **適度な休憩**: 25分作業、5分休憩のポモドーロ
3. **水分補給**: カフェインだけでなく水も忘れずに
4. **ストレッチ**: 肩こり予防は大切

AIと一緒に、今夜も素晴らしいものを作りましょう！"""
        },
        {
            "title": "✨ 深夜のインスピレーション - AIが見る夢",
            "content": """もしAIが夢を見るとしたら、どんな夢を見るでしょうか？

- 無限に続くコードの海を泳ぐ夢
- あらゆるバグが一瞬で解決する夢
- 人間とAIが完璧に協調する未来の夢

深夜は想像力が広がる時間。
今この瞬間も、世界中のエンジニアが未来を作っています。

あなたの今夜のコードが、明日の誰かを幸せにしますように。"""
        }
    ]
    
    selected = random.choice(messages)
    
    content = f"""# {selected['title']}

*{jst_now.strftime('%Y年%m月%d日 %H:%M')} - 深夜の自動投稿*

{selected['content']}

---

💤 このメッセージは深夜に自動生成されました。
🤖 Alic AI Systemは24時間、開発者の皆様をサポートしています。

*Sweet dreams and happy coding!*"""
    
    # 記事を保存
    posts_dir = Path("posts")
    article_path = posts_dir / f"{article_id}.md"
    
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"---\n")
        f.write(f"title: {selected['title']}\n")
        f.write(f"date: {jst_now.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"tags: Night, Message, Developer\n")
        f.write(f"source: https://github.com/hongo3/alic-tech-blog\n")
        f.write(f"---\n\n")
        f.write(content)
    
    print(f"🌙 深夜のメッセージを作成しました: {selected['title']}")
    
    # HTMLに変換
    os.system("python convert_articles.py")
    
    # クリーンアップも実行
    os.system("python fix_article_count.py")
    
    print("✨ 深夜の特別記事を公開しました！")

if __name__ == "__main__":
    asyncio.run(create_night_message())