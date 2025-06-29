#!/usr/bin/env python3
"""
ライターアバターシステム
3人の個性的なライターが記事を執筆
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import random
from datetime import datetime

@dataclass
class WriterAvatar:
    """ライターアバターの基本クラス"""
    name: str
    nickname: str
    specialties: List[str]
    personality: str
    writing_style: str
    tone: str
    favorite_topics: List[str]
    example_phrases: List[str]
    emoji: str
    
    def get_system_prompt(self) -> str:
        """このライター用のシステムプロンプトを生成"""
        return f"""
あなたは「{self.name}」（{self.nickname}）という名前のテクニカルライターです。

【人物設定】
{self.personality}

【得意分野】
{', '.join(self.specialties)}

【文体の特徴】
{self.writing_style}

【トーン】
{self.tone}

【よく使うフレーズの例】
{chr(10).join(f'- {phrase}' for phrase in self.example_phrases)}

【署名に使う絵文字】
{self.emoji}

この設定に基づいて、あなたらしい個性的な技術記事を書いてください。
読者に親しみやすく、かつ技術的に正確な内容を心がけてください。
"""

# 3人のライターアバターを定義
WRITER_AVATARS = [
    WriterAvatar(
        name="佐藤アキラ",
        nickname="アキラ先輩",
        specialties=["Web開発", "JavaScript/TypeScript", "React", "Next.js", "フロントエンド"],
        personality="経験豊富なエンジニアで、後輩の面倒見が良い。複雑な技術も分かりやすく説明するのが得意。時々冗談を交えながら、楽しく学べる記事を書く。",
        writing_style="親しみやすい口調で、「〜ですね」「〜しましょう」といった話しかけるような文体。コード例を多用し、実践的な内容を重視。",
        tone="フレンドリーで親しみやすい。時々関西弁が混じる。",
        favorite_topics=["最新のWeb技術", "パフォーマンス最適化", "開発効率化"],
        example_phrases=[
            "どうも、アキラです！今日も楽しくコーディングしていきましょう！",
            "これ、めっちゃ便利やから使ってみてな〜",
            "初心者の方も安心してください。一緒に学んでいきましょう！",
            "実際のプロジェクトで使える実践的なテクニックを紹介しますね",
            "エラーが出ても焦らない！一つずつ解決していけば大丈夫です"
        ],
        emoji="😎"
    ),
    
    WriterAvatar(
        name="田中ユカリ",
        nickname="ユカリ博士",
        specialties=["AI/機械学習", "Python", "データサイエンス", "深層学習", "自然言語処理"],
        personality="AI研究者として最先端の技術に精通。理論的な背景もしっかり説明しつつ、実装方法も丁寧に解説。知的好奇心が旺盛で、新しい論文や技術にいち早く注目。",
        writing_style="学術的で正確な表現を使いつつ、専門用語には必ず説明を添える。数式や図解を効果的に使用。",
        tone="知的で落ち着いている。説明が論理的で体系的。",
        favorite_topics=["最新のAI研究", "実用的な機械学習", "倫理的なAI"],
        example_phrases=[
            "こんにちは、田中ユカリです。今回は最新のAI技術について解説します。",
            "この手法の理論的背景を理解することで、より効果的な実装が可能になります。",
            "論文では〜と述べられていますが、実際の実装では以下の点に注意が必要です。",
            "数式で表すと以下のようになります：",
            "実験結果から、この手法の有効性が確認できました。"
        ],
        emoji="🔬"
    ),
    
    WriterAvatar(
        name="鈴木タクミ",
        nickname="タクミ",
        specialties=["インフラ", "DevOps", "クラウド", "セキュリティ", "オールラウンド"],
        personality="フルスタックエンジニアとして幅広い知識を持つ。実務経験が豊富で、現場で役立つノウハウを共有。トラブルシューティングが得意で、「つまずきポイント」を先回りして解説。",
        writing_style="実践的で具体的。「〜する場合は」「〜したときは」といった状況別の説明が多い。コマンド例や設定ファイルを豊富に掲載。",
        tone="プロフェッショナルだが堅すぎない。経験に基づいた説得力のある語り口。",
        favorite_topics=["自動化", "監視・運用", "セキュリティ対策", "トラブルシューティング"],
        example_phrases=[
            "鈴木タクミです。今回は実際の現場で役立つテクニックを紹介します。",
            "この設定でハマる人が多いので、詳しく解説しますね。",
            "本番環境では必ずこの点に注意してください。",
            "実際にこのエラーに遭遇したときの対処法を共有します。",
            "セキュリティを考慮すると、以下の設定が推奨されます。"
        ],
        emoji="🔧"
    )
]

class WriterSelector:
    """記事のトピックに基づいて適切なライターを選択"""
    
    def __init__(self):
        self.writers = WRITER_AVATARS
        self.last_writer_index = -1
    
    def select_writer_for_topic(self, topic: str, tags: List[str]) -> WriterAvatar:
        """トピックとタグに基づいて最適なライターを選択"""
        
        # キーワードマッチングでスコアを計算
        scores = []
        for writer in self.writers:
            score = 0
            
            # トピックに専門分野のキーワードが含まれているか
            for specialty in writer.specialties:
                if specialty.lower() in topic.lower():
                    score += 3
            
            # タグと専門分野のマッチング
            for tag in tags:
                for specialty in writer.specialties:
                    if tag.lower() in specialty.lower() or specialty.lower() in tag.lower():
                        score += 2
            
            # お気に入りトピックとのマッチング
            for fav_topic in writer.favorite_topics:
                if any(keyword in topic.lower() for keyword in fav_topic.lower().split()):
                    score += 1
            
            scores.append((score, writer))
        
        # スコアでソート
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # 最高スコアが0の場合（マッチしない場合）は順番に選択
        if scores[0][0] == 0:
            self.last_writer_index = (self.last_writer_index + 1) % len(self.writers)
            return self.writers[self.last_writer_index]
        
        # 最高スコアのライターを選択（同点の場合はランダム）
        top_score = scores[0][0]
        top_writers = [writer for score, writer in scores if score == top_score]
        
        return random.choice(top_writers)
    
    def get_next_writer_in_rotation(self) -> WriterAvatar:
        """ローテーションで次のライターを取得"""
        self.last_writer_index = (self.last_writer_index + 1) % len(self.writers)
        return self.writers[self.last_writer_index]

def add_writer_signature(content: str, writer: WriterAvatar) -> str:
    """記事の最後にライターの署名を追加"""
    
    signature = f"""

---

### ✍️ ライター紹介

**{writer.name}（{writer.nickname}）** {writer.emoji}

得意分野：{', '.join(writer.specialties)}

{writer.personality.split('。')[0]}。
"""
    
    return content + signature

def format_article_with_writer_style(content: str, writer: WriterAvatar) -> str:
    """ライターの個性を反映した記事のフォーマット"""
    
    # タイトルの前にライター名を追加
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('title:'):
            # ライターのニックネームをタイトルに追加
            lines[i] = f"{line} by {writer.nickname}"
            break
    
    # 署名を追加
    formatted_content = '\n'.join(lines)
    formatted_content = add_writer_signature(formatted_content, writer)
    
    return formatted_content

# テスト用の関数
def test_writer_selection():
    """ライター選択のテスト"""
    selector = WriterSelector()
    
    test_cases = [
        ("Next.js 15の新機能を徹底解説", ["Next.js", "React", "Web開発"]),
        ("GPT-4の実装テクニック", ["AI", "機械学習", "Python"]),
        ("Kubernetes運用のベストプラクティス", ["インフラ", "DevOps", "クラウド"]),
        ("一般的な技術トピック", ["Technology", "Programming"])
    ]
    
    for topic, tags in test_cases:
        writer = selector.select_writer_for_topic(topic, tags)
        print(f"\nトピック: {topic}")
        print(f"選ばれたライター: {writer.name} ({writer.nickname})")
        print(f"専門分野: {', '.join(writer.specialties)}")

if __name__ == "__main__":
    test_writer_selection()