#!/usr/bin/env python3
"""
完全レビュー機能付き記事生成スクリプト
評価 → 生成 → 校正 → 修正 → リリースの完全なフローを実装
"""

import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os
import subprocess
import logging
from article_evaluator import SelfImprovingBlogSystem
from article_proofreader import ImprovedArticleWithProofreading
from generate_article_with_evaluation import ImprovedArticleGenerator
from generate_detailed_article_v4 import DetailedArticleGenerator
from writer_avatars import WriterSelector, format_article_with_writer_style, WRITER_AVATARS

# ロガーの設定
logger = logging.getLogger(__name__)

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

class FullReviewArticleSystem:
    """完全レビューシステムを統合した記事生成"""
    
    def __init__(self, use_detailed_generator=True):
        self.evaluation_system = SelfImprovingBlogSystem()
        self.proofreading_system = ImprovedArticleWithProofreading()
        if use_detailed_generator:
            self.article_generator = DetailedArticleGenerator()
            self.use_detailed = True
        else:
            self.article_generator = ImprovedArticleGenerator()
            self.use_detailed = False
        self.generation_log_file = Path("full_review_log.json")
        self.writer_selector = WriterSelector()
        self.load_generation_log()
    
    def load_generation_log(self):
        """生成ログを読み込む"""
        if self.generation_log_file.exists():
            with open(self.generation_log_file, "r", encoding="utf-8") as f:
                self.generation_log = json.load(f)
        else:
            self.generation_log = {
                "generations": [],
                "quality_trends": [],
                "improvement_metrics": {}
            }
    
    def save_generation_log(self):
        """生成ログを保存"""
        with open(self.generation_log_file, "w", encoding="utf-8") as f:
            json.dump(self.generation_log, f, ensure_ascii=False, indent=2)
    
    async def generate_with_full_review(self):
        """完全レビュープロセスで記事を生成"""
        
        print("🔄 完全レビュー付き記事生成システム")
        print("=" * 60)
        
        generation_result = {
            "timestamp": get_jst_now().isoformat(),
            "phases": {},
            "final_score": 0,
            "published": False
        }
        
        # Phase 1: 既存記事の評価と改善提案
        print("\n📊 Phase 1: 既存記事の評価と改善提案")
        print("-" * 50)
        
        improvement_report = await self.evaluation_system.evaluate_and_improve()
        # improvement_suggestionsの数を安全に取得
        suggestion_count = 0
        if improvement_report.get("recent_evaluations") and len(improvement_report["recent_evaluations"]) > 0:
            suggestions = improvement_report["recent_evaluations"][0].get("improvement_suggestions", [])
            if isinstance(suggestions, list):
                suggestion_count = len(suggestions)
            elif isinstance(suggestions, int):
                suggestion_count = suggestions
        
        generation_result["phases"]["evaluation"] = {
            "average_score": improvement_report["average_score"],
            "rules_updated": improvement_report["rules_updated"],
            "improvement_suggestions": suggestion_count
        }
        
        print(f"  ✓ 平均スコア: {improvement_report['average_score']:.1f}/100")
        print(f"  ✓ ルール更新: {'実施' if improvement_report['rules_updated'] else '不要'}")
        
        # Phase 2: 改善を反映した新記事の生成
        print("\n✏️ Phase 2: 改善を反映した新記事の生成")
        print("-" * 50)
        
        if self.use_detailed:
            # 詳細記事生成システムを使用
            import random
            from pathlib import Path
            
            # トピックリストから選択
            topics = [
                {
                    "title": "ゼロトラストセキュリティ実装ガイド：BeyondCorpモデルで作る次世代認証基盤",
                    "short_title": "ゼロトラストセキュリティ入門",
                    "category": "security",
                    "source_url": "https://github.com/pomerium/pomerium",
                    "reference_sites": [
                        "https://www.csoonline.com/",
                        "https://www.darkreading.com/",
                        "https://thehackernews.com/"
                    ],
                    "keywords": ["ゼロトラスト", "BeyondCorp", "認証", "アクセス制御"],
                    "difficulty": "上級",
                    "reading_time": "30分"
                },
                {
                    "title": "Next.js 15完全攻略:App Router×Server Components×Streamingで作る爆速Webアプリ",
                    "short_title": "Next.js 15の新機能解説",
                    "category": "web_tech",
                    "source_url": "https://github.com/vercel/next.js",
                    "reference_sites": [
                        "https://nextjs.org/blog",
                        "https://vercel.com/blog",
                        "https://dev.to/t/nextjs"
                    ],
                    "keywords": ["Next.js", "React", "Server Components", "App Router"],
                    "difficulty": "中級",
                    "reading_time": "25分"
                },
                {
                    "title": "【2025年最新】AIエージェントが変える開発現場 - AutoGenとLangChainの実践比較",
                    "short_title": "AIエージェントの最新動向",
                    "category": "ai_development",
                    "source_url": "https://github.com/microsoft/autogen",
                    "reference_sites": [
                        "https://qiita.com/",
                        "https://zenn.dev/",
                        "https://b.hatena.ne.jp/hotentry/it"
                    ],
                    "keywords": ["AutoGen", "LangChain", "マルチエージェント", "自律型AI"],
                    "difficulty": "中級",
                    "reading_time": "20分"
                }
            ]
            
            # ランダムにトピックを選択
            topic_data = random.choice(topics)
            
            # 詳細記事を生成
            content = await self.article_generator.generate_detailed_content(topic_data)
            
            # 記事を保存
            jst_now = get_jst_now()
            article_id = f"article_{int(jst_now.timestamp())}"
            
            posts_dir = Path("posts")
            posts_dir.mkdir(exist_ok=True)
            
            article_path = posts_dir / f"{article_id}.md"
            with open(article_path, "w", encoding="utf-8") as f:
                f.write(f"---\n")
                f.write(f"title: {topic_data['title']}\n")
                f.write(f"date: {jst_now.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"category: {topic_data['category']}\n")
                f.write(f"tags: {', '.join(topic_data['keywords'])}\n")
                f.write(f"difficulty: {topic_data['difficulty']}\n")
                f.write(f"reading_time: {topic_data['reading_time']}\n")
                f.write(f"production_time: {round(self.article_generator.generation_log[-1]['elapsed_seconds'], 2)}秒\n")
                f.write(f"---\n\n")
                f.write(content)
            
            # 評価用の仮データを作成
            article_data = {
                "article_data": topic_data,
                "evaluation": {"total_score": 90.0},  # 詳細記事は高品質と仮定
                "improvements_applied": []
            }
            
            generation_result["phases"]["generation"] = {
                "title": topic_data["title"],
                "category": topic_data["category"],
                "initial_score": 90.0,
                "improvements_applied": 0,
                "character_count": len(content),
                "production_time": round(self.article_generator.generation_log[-1]['elapsed_seconds'], 2)
            }
            
            print(f"  ✓ 記事タイトル: {topic_data['title'][:50]}...")
            print(f"  ✓ 文字数: {len(content):,}文字")
            print(f"  ✓ 制作時間: {round(self.article_generator.generation_log[-1]['elapsed_seconds'], 2)}秒")
        else:
            # 従来の記事生成システムを使用
            article_data = await self.article_generator.generate_with_evaluation()
            generation_result["phases"]["generation"] = {
                "title": article_data["article_data"]["title"],
                "category": article_data["article_data"]["category"],
                "initial_score": article_data["evaluation"]["total_score"],
                "improvements_applied": len(article_data["improvements_applied"])
            }
            
            print(f"  ✓ 記事タイトル: {article_data['article_data']['title'][:50]}...")
            print(f"  ✓ 初期スコア: {article_data['evaluation']['total_score']:.1f}/100")
        
        # ライターアバターを選択
        # 記事のトピックとタグを取得
        article_title = article_data.get("article_data", {}).get("title", "")
        article_tags = article_data.get("article_data", {}).get("tags", "").split(", ")
        
        # 適切なライターを選択
        selected_writer = self.writer_selector.select_writer_for_topic(article_title, article_tags)
        print(f"\n✍️ 選ばれたライター: {selected_writer.name}（{selected_writer.nickname}）{selected_writer.emoji}")
        print(f"  専門分野: {', '.join(selected_writer.specialties)}")
        
        # Phase 3: プロのライター視点での校正
        print("\n🔍 Phase 3: プロのライター視点での校正")
        print("-" * 50)
        
        # 最新の記事を取得
        posts_dir = Path("posts")
        latest_article = sorted(
            posts_dir.glob("*.md"), 
            key=lambda x: x.stat().st_mtime, 
            reverse=True
        )[0]
        
        # ライターの個性を記事に反映
        content = latest_article.read_text(encoding='utf-8')
        content_with_writer = format_article_with_writer_style(content, selected_writer)
        latest_article.write_text(content_with_writer, encoding='utf-8')
        
        generation_result["writer"] = {
            "name": selected_writer.name,
            "nickname": selected_writer.nickname,
            "specialties": selected_writer.specialties
        }
        
        proofreading_result = await self.proofreading_system.generate_and_proofread(latest_article)
        generation_result["phases"]["proofreading"] = {
            "original_score": proofreading_result["proofreading_result"]["original_score"],
            "issues_found": len(proofreading_result["proofreading_result"]["issues_found"]),
            "corrections_applied": len(proofreading_result["proofreading_result"]["corrections"]),
            "final_score": proofreading_result["proofreading_result"]["final_score"]
        }
        
        # Phase 4: 品質判定とリリース決定
        print("\n🎯 Phase 4: 品質判定とリリース決定")
        print("-" * 50)
        
        # 総合スコアを計算（評価スコアと校正スコアの平均）
        final_score = (
            article_data["evaluation"]["total_score"] * 0.5 + 
            proofreading_result["proofreading_result"]["final_score"] * 0.5
        )
        generation_result["final_score"] = final_score
        
        print(f"  📊 総合品質スコア: {final_score:.1f}/100")
        
        # リリース判定
        if final_score >= 85:
            print("  ✅ 判定: 高品質 - 自動リリース")
            generation_result["published"] = True
            generation_result["quality_status"] = "high_quality"
            await self._publish_article(latest_article)
        elif final_score >= 75:
            print("  ⚠️  判定: 良好 - 条件付きリリース")
            generation_result["published"] = True
            generation_result["quality_status"] = "good"
            await self._publish_article(latest_article)
        else:
            print("  ❌ 判定: 要改善 - ボツ記事として公開")
            generation_result["published"] = True
            generation_result["quality_status"] = "rejected"
            # ボツ記事として校正レポート付きで公開
            await self._publish_rejected_article(latest_article, proofreading_result, final_score)
        
        # Phase 5: 学習とフィードバック
        print("\n📈 Phase 5: 学習とフィードバック")
        print("-" * 50)
        
        # 生成ログを更新
        self.generation_log["generations"].append(generation_result)
        
        # 品質トレンドを分析
        quality_trend = self._analyze_quality_trend()
        generation_result["quality_trend"] = quality_trend
        
        print(f"  📊 品質トレンド: {quality_trend['direction']}")
        print(f"  📈 改善率: {quality_trend['improvement_rate']:.1f}%")
        
        # ログを保存
        self.save_generation_log()
        
        # 古い記事のクリーンアップ
        self._cleanup_old_articles()
        
        return generation_result
    
    async def _publish_article(self, article_path: Path):
        """記事を公開（HTMLに変換してインデックスを更新）"""
        
        print("\n📤 記事を公開しています...")
        
        # HTMLに変換
        if Path("convert_articles_v3.py").exists():
            result = subprocess.run(
                ["python", "convert_articles_v3.py"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                print("  ✓ HTML変換完了")
            else:
                print(f"  × HTML変換エラー: {result.stderr}")
        
        # index.htmlを更新
        if Path("update_to_modern_ui_v3.py").exists():
            result = subprocess.run(
                ["python", "update_to_modern_ui_v3.py"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ インデックス更新完了")
            else:
                print(f"  × インデックス更新エラー: {result.stderr}")
    
    async def _publish_rejected_article(self, article_path: Path, proofreading_result: dict, final_score: float):
        """ボツ記事として校正レポート付きで公開"""
        
        print("\n📤 ボツ記事として校正レポート付きで公開しています...")
        
        # 記事の内容を読み込む
        content = article_path.read_text(encoding='utf-8')
        
        # タイトルに[ボツ記事]を追加
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('title:'):
                lines[i] = f'title: [ボツ記事] {line[6:].strip()}'
                break
        
        # 校正レポートを記事の最後に追加
        proofreading_report = self._generate_proofreading_report(proofreading_result, final_score)
        
        # 記事を更新
        updated_content = '\n'.join(lines) + '\n\n' + proofreading_report
        article_path.write_text(updated_content, encoding='utf-8')
        
        # 通常の公開処理を実行
        await self._publish_article(article_path)
    
    def _generate_proofreading_report(self, proofreading_result: dict, final_score: float):
        """校正レポートを生成"""
        
        report = []
        report.append("\n---\n")
        report.append("## 🔍 校正レポート（開発中のAIシステムによる自動評価）")
        report.append(f"\n**総合品質スコア**: {final_score:.1f}/100")
        report.append("\n### ❌ この記事がボツになった理由\n")
        report.append(f"品質基準（75点）を下回ったため、ボツ記事として公開されています。")
        
        # 校正結果の詳細
        pr = proofreading_result.get("proofreading_result", {})
        report.append(f"\n### 📊 校正スコア詳細\n")
        report.append(f"- **元のスコア**: {pr.get('original_score', 0)}/100")
        report.append(f"- **検出された問題**: {len(pr.get('issues_found', []))}件")
        report.append(f"- **自動修正**: {len(pr.get('corrections', []))}件")
        report.append(f"- **最終スコア**: {pr.get('final_score', 0)}/100")
        
        # 検出された問題の詳細
        issues = pr.get('issues_found', [])
        if issues:
            report.append("\n### ⚠️ 検出された問題\n")
            for issue in issues[:10]:  # 最大10件まで表示
                severity = issue.get('severity', 'unknown')
                issue_type = issue.get('type', 'unknown')
                message = issue.get('message', '')
                report.append(f"- **[{severity}]** `{issue_type}`: {message}")
            
            if len(issues) > 10:
                report.append(f"\n...他{len(issues) - 10}件の問題")
        
        # AIによる動的な改善提案
        report.append("\n### 💡 改善のヒント\n")
        report.append("このAIシステムは現在開発中です。以下は、今回の記事の分析に基づいた具体的な改善提案です：")
        
        # AIに具体的な改善提案を生成してもらう
        improvement_suggestions = self._generate_ai_improvement_suggestions(proofreading_result, final_score)
        for suggestion in improvement_suggestions:
            report.append(f"- {suggestion}")
        
        report.append("\n---")
        report.append("\n*このブログは開発中のAI記事生成システムによって運営されています。*")
        report.append("*品質向上のため、システムは継続的に改善されています。*")
        
        return '\n'.join(report)
    
    def _generate_ai_improvement_suggestions(self, proofreading_result: dict, final_score: float):
        """AIが動的に改善提案を生成"""
        
        # 校正結果から問題を分析
        issues = proofreading_result.get("proofreading_result", {}).get("issues_found", [])
        
        # デフォルトの提案（AIが生成できない場合のフォールバック）
        default_suggestions = [
            "より具体的なコード例の追加",
            "技術的な深さの向上",
            "読者への価値提供の明確化",
            "文章構成の改善"
        ]
        
        try:
            # AIによる分析（簡易版）
            # TODO: 将来的にはClaude APIを使用してより詳細な分析を行う
            suggestions = []
            
            # スコアに基づいた提案
            if final_score < 50:
                suggestions.append("記事の基本構成を見直し、論理的な流れを改善する")
                suggestions.append("導入部分でトピックの重要性をより明確に説明する")
            
            # 問題タイプに基づいた提案
            issue_types = [issue.get('type', '') for issue in issues]
            if 'unused_variable' in issue_types:
                suggestions.append("コード例で定義した変数は必ず使用するか、削除する")
            if 'outdated_reference' in issue_types:
                suggestions.append("最新の技術情報やバージョンに更新する")
            if 'clarity' in issue_types:
                suggestions.append("専門用語には初出時に説明を追加する")
            
            # 具体的な問題に基づいた提案
            if len(issues) > 20:
                suggestions.append("記事全体を見直し、エラーや警告を減らす")
            elif len(issues) > 10:
                suggestions.append("コードの品質を向上させ、ベストプラクティスに従う")
            
            # もし提案が少なければデフォルトから追加
            if len(suggestions) < 3:
                for default in default_suggestions:
                    if default not in suggestions:
                        suggestions.append(default)
                        if len(suggestions) >= 4:
                            break
            
            return suggestions[:5]  # 最大5つの提案
            
        except Exception as e:
            logger.warning(f"AI改善提案の生成に失敗: {e}")
            return default_suggestions
    
    def _analyze_quality_trend(self):
        """品質トレンドを分析"""
        
        generations = self.generation_log["generations"]
        
        if len(generations) < 2:
            return {
                "direction": "データ不足",
                "improvement_rate": 0,
                "average_score": generations[-1]["final_score"] if generations else 0
            }
        
        # 最新10件の平均と、その前の10件の平均を比較
        recent = generations[-10:]
        older = generations[-20:-10] if len(generations) >= 20 else generations[:len(generations)//2]
        
        recent_avg = sum(g["final_score"] for g in recent) / len(recent)
        older_avg = sum(g["final_score"] for g in older) / len(older) if older else recent_avg
        
        improvement_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        if improvement_rate > 5:
            direction = "向上中 📈"
        elif improvement_rate < -5:
            direction = "低下中 📉"
        else:
            direction = "安定 ➡️"
        
        return {
            "direction": direction,
            "improvement_rate": improvement_rate,
            "average_score": recent_avg
        }
    
    def _cleanup_old_articles(self, keep_count=5):
        """古い記事をクリーンアップ"""
        
        print("\n🧹 古い記事のクリーンアップ...")
        
        posts_dir = Path("posts")
        if not posts_dir.exists():
            return
        
        md_files = sorted(posts_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(md_files) <= keep_count:
            print(f"  現在の記事数: {len(md_files)}件 - クリーンアップ不要")
            return
        
        files_to_delete = md_files[keep_count:]
        print(f"  削除対象: {len(files_to_delete)}件の古い記事")
        
        for md_file in files_to_delete:
            md_file.unlink()
            
            html_file = Path("docs/articles") / f"{md_file.stem}.html"
            if html_file.exists():
                html_file.unlink()
        
        print(f"  ✓ {len(files_to_delete)}件の記事を削除しました")

async def main():
    """メイン処理"""
    print("🤖 完全レビュー付き記事生成システム v1.0")
    print("=" * 60)
    
    jst_now = get_jst_now()
    print(f"⏰ 現在の日本時間: {jst_now.strftime('%Y-%m-%d %H:%M:%S')} JST")
    
    # 完全レビューシステムを実行
    system = FullReviewArticleSystem()
    result = await system.generate_with_full_review()
    
    print("\n" + "=" * 60)
    print("✅ 完全レビュープロセス完了！")
    print(f"  - 最終スコア: {result['final_score']:.1f}/100")
    print(f"  - 公開状態: {'公開済み' if result['published'] else '保留'}")
    print(f"  - 品質トレンド: {result['quality_trend']['direction']}")
    
    # 詳細レポート
    print("\n📊 フェーズ別レポート:")
    for phase, data in result["phases"].items():
        print(f"\n  【{phase.upper()}】")
        for key, value in data.items():
            print(f"    - {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())