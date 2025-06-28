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
from article_evaluator import SelfImprovingBlogSystem
from article_proofreader import ImprovedArticleWithProofreading
from generate_article_with_evaluation import ImprovedArticleGenerator

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

class FullReviewArticleSystem:
    """完全レビューシステムを統合した記事生成"""
    
    def __init__(self):
        self.evaluation_system = SelfImprovingBlogSystem()
        self.proofreading_system = ImprovedArticleWithProofreading()
        self.article_generator = ImprovedArticleGenerator()
        self.generation_log_file = Path("full_review_log.json")
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
        generation_result["phases"]["evaluation"] = {
            "average_score": improvement_report["average_score"],
            "rules_updated": improvement_report["rules_updated"],
            "improvement_suggestions": len(
                improvement_report["recent_evaluations"][0]["improvement_suggestions"]
                if improvement_report["recent_evaluations"] else 0
            )
        }
        
        print(f"  ✓ 平均スコア: {improvement_report['average_score']:.1f}/100")
        print(f"  ✓ ルール更新: {'実施' if improvement_report['rules_updated'] else '不要'}")
        
        # Phase 2: 改善を反映した新記事の生成
        print("\n✏️ Phase 2: 改善を反映した新記事の生成")
        print("-" * 50)
        
        article_data = await self.article_generator.generate_with_evaluation()
        generation_result["phases"]["generation"] = {
            "title": article_data["article_data"]["title"],
            "category": article_data["article_data"]["category"],
            "initial_score": article_data["evaluation"]["total_score"],
            "improvements_applied": len(article_data["improvements_applied"])
        }
        
        print(f"  ✓ 記事タイトル: {article_data['article_data']['title'][:50]}...")
        print(f"  ✓ 初期スコア: {article_data['evaluation']['total_score']:.1f}/100")
        
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
            await self._publish_article(latest_article)
        elif final_score >= 75:
            print("  ⚠️  判定: 良好 - 条件付きリリース")
            generation_result["published"] = True
            await self._publish_article(latest_article)
        else:
            print("  ❌ 判定: 要改善 - リリース保留")
            generation_result["published"] = False
            # 低品質の記事は削除
            latest_article.unlink()
            print("  → 品質基準を満たさないため、記事を削除しました")
        
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