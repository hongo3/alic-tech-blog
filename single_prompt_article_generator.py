#!/usr/bin/env python3
"""
Claude Codeに一つのプロンプトで記事生成全体を任せる新アプローチ
処理時間を10分以内に短縮することを目標とする
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_code_integration import ClaudeCodeSDKIntegration
from writer_avatars import WriterSelector, format_article_with_writer_style
import logging

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SinglePromptArticleGenerator:
    """一つのプロンプトで記事生成全体を処理"""
    
    def __init__(self):
        self.claude_integration = ClaudeCodeSDKIntegration()
        self.writer_selector = WriterSelector()
        self.start_time = None
        
    async def generate_article_with_single_prompt(self, topic=None):
        """一つのプロンプトで記事生成全体を処理"""
        
        self.start_time = time.time()
        jst_now = datetime.now(JST)
        
        print(f"\n🚀 高速記事生成システム (Single Prompt Approach)")
        print(f"📅 開始時刻: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
        print("=" * 60)
        
        # トピックが指定されていない場合はランダムに選択
        if not topic:
            topic = self._get_random_topic()
        
        # ライターを選択
        writer = self.writer_selector.select_writer_for_topic(topic["title"], topic["tags"])
        print(f"\n✍️ 選ばれたライター: {writer.name}（{writer.nickname}）{writer.emoji}")
        
        # 記事生成プロンプトを作成
        prompt = self._create_comprehensive_prompt(topic, writer)
        
        try:
            # Claude Codeに記事生成を依頼
            print("\n📝 Claude Codeによる記事生成を開始...")
            messages = await self.claude_integration.query_with_sdk(prompt, max_turns=1)
            
            # 結果を処理
            if messages and len(messages) > 0:
                result = messages[-1].get("result", "")
                
                # 記事を保存
                article_path = self._save_article(result, writer)
                
                elapsed_time = time.time() - self.start_time
                print(f"\n✅ 記事生成完了！")
                print(f"⏱️ 処理時間: {elapsed_time:.1f}秒")
                print(f"📄 保存先: {article_path}")
                
                return {
                    "success": True,
                    "article_path": str(article_path),
                    "writer": writer.name,
                    "elapsed_time": elapsed_time
                }
            else:
                logger.error("No response from Claude Code")
                return {"success": False, "error": "No response from Claude Code"}
                
        except Exception as e:
            logger.error(f"記事生成エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_random_topic(self):
        """ランダムなトピックを選択"""
        import random
        
        topics = [
            {
                "title": "Next.js 15の革新的な新機能とパフォーマンス最適化テクニック",
                "tags": ["Next.js", "React", "Web開発", "パフォーマンス"],
                "category": "frontend"
            },
            {
                "title": "Claude 3.5とGPT-4の実践的な使い分けガイド",
                "tags": ["AI", "Claude", "GPT-4", "機械学習"],
                "category": "ai"
            },
            {
                "title": "Kubernetes運用の落とし穴と本番環境でのベストプラクティス",
                "tags": ["Kubernetes", "DevOps", "インフラ", "運用"],
                "category": "infrastructure"
            },
            {
                "title": "TypeScriptの型システム完全攻略：上級者向けテクニック集",
                "tags": ["TypeScript", "JavaScript", "型システム", "プログラミング"],
                "category": "programming"
            },
            {
                "title": "サーバーレスアーキテクチャで実現する高可用性システム",
                "tags": ["サーバーレス", "AWS", "クラウド", "アーキテクチャ"],
                "category": "cloud"
            }
        ]
        
        return random.choice(topics)
    
    def _create_comprehensive_prompt(self, topic, writer):
        """包括的な記事生成プロンプト"""
        
        return f"""
あなたは技術ブログの記事を書くAIライターです。以下の指示に従って、高品質な技術記事を一つ作成してください。

## ライター設定
{writer.get_system_prompt()}

## 記事のトピック
タイトル: {topic['title']}
タグ: {', '.join(topic['tags'])}
カテゴリ: {topic['category']}

## 記事の要件
1. **文字数**: 10,000文字以上の詳細な技術記事
2. **構成**: 
   - 導入部分（なぜこのトピックが重要か）
   - 技術的な背景と理論
   - 実装例（動作するコードサンプル付き）
   - ベストプラクティス
   - トラブルシューティング
   - まとめと今後の展望

3. **品質基準**:
   - 技術的に正確であること
   - 実践的で役立つ内容であること
   - コード例は実際に動作すること
   - 読みやすく、論理的な構成であること

4. **フォーマット**:
   - Markdown形式で記述
   - 以下のメタデータを含める：
     ```
     ---
     title: [記事タイトル]
     date: {datetime.now(JST).strftime('%Y-%m-%d')}
     tags: {', '.join(topic['tags'])}
     author: {writer.name}
     author_nickname: {writer.nickname}
     author_emoji: {writer.emoji}
     ---
     ```

5. **ライターの個性を反映**:
   - あなた（{writer.nickname}）らしい文体で書く
   - 得意分野の知識を活かす
   - よく使うフレーズを適度に含める

## 追加の指示
- 最新の技術トレンドを反映させる
- 具体的な数値やベンチマーク結果を含める（可能な場合）
- 読者が実際に試せるような実践的な内容にする
- エラーハンドリングやセキュリティの観点も含める

さあ、あなたの個性を活かして素晴らしい技術記事を書いてください！
"""
    
    def _save_article(self, content, writer):
        """記事を保存"""
        
        # 記事にライターの署名を追加
        content_with_signature = format_article_with_writer_style(content, writer)
        
        # ファイル名を生成
        timestamp = int(time.time())
        filename = f"article_{timestamp}.md"
        
        # 保存先ディレクトリ
        posts_dir = Path("posts")
        posts_dir.mkdir(exist_ok=True)
        
        # ファイルパス
        article_path = posts_dir / filename
        
        # 保存
        article_path.write_text(content_with_signature, encoding='utf-8')
        
        return article_path

class ArticleQualityChecker:
    """記事の品質を自動チェック"""
    
    @staticmethod
    def check_article_quality(article_path):
        """記事の品質をチェック"""
        
        content = Path(article_path).read_text(encoding='utf-8')
        
        checks = {
            "has_metadata": "---" in content[:100],
            "min_length": len(content) > 10000,
            "has_code_examples": "```" in content,
            "has_headings": "##" in content,
            "has_conclusion": "まとめ" in content or "結論" in content,
        }
        
        score = sum(1 for check in checks.values() if check) * 20
        
        return {
            "score": score,
            "checks": checks,
            "issues": [name for name, passed in checks.items() if not passed]
        }

async def main():
    """メイン実行関数"""
    
    generator = SinglePromptArticleGenerator()
    
    # 記事を生成
    result = await generator.generate_article_with_single_prompt()
    
    if result["success"]:
        # 品質チェック
        quality = ArticleQualityChecker.check_article_quality(result["article_path"])
        
        print(f"\n📊 品質チェック結果:")
        print(f"  スコア: {quality['score']}/100")
        
        if quality['issues']:
            print(f"  問題点: {', '.join(quality['issues'])}")
        else:
            print("  ✅ 全ての品質基準を満たしています")
    else:
        print(f"\n❌ エラー: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())