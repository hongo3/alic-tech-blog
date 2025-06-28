#!/usr/bin/env python3
"""
記事評価と自己改善システム
前回の記事とルールを評価し、継続的に品質を向上させる
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
import asyncio

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

class ArticleEvaluator:
    """記事の評価を行うクラス"""
    
    def __init__(self):
        self.evaluation_history_file = Path("evaluation_history.json")
        self.rules_file = Path("BLOG_WRITING_RULES.md")
        self.load_history()
        
    def load_history(self):
        """評価履歴を読み込む"""
        if self.evaluation_history_file.exists():
            with open(self.evaluation_history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = {
                "evaluations": [],
                "rule_updates": [],
                "quality_trends": {}
            }
    
    def save_history(self):
        """評価履歴を保存"""
        with open(self.evaluation_history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    async def evaluate_article(self, article_path: Path) -> Dict[str, Any]:
        """記事を評価する"""
        
        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # メタデータを抽出
        metadata = self._extract_metadata(content)
        
        # 評価スコアを計算
        scores = {
            "technical_accuracy": await self._evaluate_technical_accuracy(content, metadata),
            "readability": await self._evaluate_readability(content, metadata),
            "practicality": await self._evaluate_practicality(content, metadata),
            "originality": await self._evaluate_originality(content, metadata)
        }
        
        # 詳細な評価結果
        evaluation = {
            "article_path": str(article_path),
            "timestamp": datetime.now(JST).isoformat(),
            "metadata": metadata,
            "scores": scores,
            "total_score": sum(scores.values()),
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }
        
        # 強みと弱みを分析
        evaluation.update(self._analyze_strengths_weaknesses(content, scores))
        
        return evaluation
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """記事からメタデータを抽出"""
        metadata = {}
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                meta_section = parts[1].strip()
                for line in meta_section.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
        
        return metadata
    
    async def _evaluate_technical_accuracy(self, content: str, metadata: Dict[str, str]) -> float:
        """技術的正確性を評価（25点満点）"""
        score = 25.0
        
        # コードブロックの存在と品質をチェック
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        
        if len(code_blocks) == 0:
            score -= 10  # コードがない
        else:
            # コードの品質をチェック
            for code in code_blocks:
                # エラーハンドリングの有無
                if 'try:' in code or 'except' in code or 'error' in code.lower():
                    score -= 0  # 良い
                else:
                    score -= 0.5  # エラーハンドリングなし
                
                # コメントの有無
                if '#' in code and not code.strip().startswith('#'):
                    score -= 0  # コメントあり
                else:
                    score -= 0.5  # コメントなし
        
        # 技術用語の適切な使用
        tech_terms = ["API", "async", "await", "class", "function", "database", "cache"]
        term_count = sum(1 for term in tech_terms if term.lower() in content.lower())
        if term_count < 5:
            score -= 2  # 技術用語が少ない
        
        # 最新性のチェック（2025年の記述があるか）
        if "2025" in content or "最新" in content:
            score -= 0  # 最新性あり
        else:
            score -= 1
        
        return max(0, score)
    
    async def _evaluate_readability(self, content: str, metadata: Dict[str, str]) -> float:
        """読みやすさを評価（25点満点）"""
        score = 25.0
        
        # 文章構造のチェック
        sections = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
        if len(sections) < 5:
            score -= 3  # セクションが少ない
        
        # 段落の長さをチェック
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500 and not p.startswith('```')]
        if len(long_paragraphs) > 3:
            score -= 2  # 長すぎる段落が多い
        
        # 箇条書きの使用
        bullet_points = content.count('\n- ') + content.count('\n* ') + content.count('\n1. ')
        if bullet_points < 5:
            score -= 2  # 箇条書きが少ない
        
        # 専門用語の説明
        if "とは" in content or "について" in content or "の概要" in content:
            score -= 0  # 説明あり
        else:
            score -= 3  # 説明不足
        
        # AIの思考プロセスセクションの存在
        if "なぜこの記事を書こうと思ったのか" in content or "AIの思考プロセス" in content:
            score -= 0
        else:
            score -= 5  # 必須セクションがない
        
        return max(0, score)
    
    async def _evaluate_practicality(self, content: str, metadata: Dict[str, str]) -> float:
        """実用性を評価（25点満点）"""
        score = 25.0
        
        # 実装例の存在
        if "実装例" in content or "使用例" in content or "サンプルコード" in content:
            score -= 0
        else:
            score -= 5
        
        # ステップバイステップガイドの存在
        if "Step 1" in content or "ステップ1" in content or "手順" in content:
            score -= 0
        else:
            score -= 3
        
        # トラブルシューティングセクション
        if "トラブルシューティング" in content or "よくある問題" in content or "エラー" in content:
            score -= 0
        else:
            score -= 2
        
        # インストール/セットアップ手順
        if "pip install" in content or "npm install" in content or "インストール" in content:
            score -= 0
        else:
            score -= 2
        
        # 実行可能なコード例の数
        executable_patterns = ["if __name__", "async def main", "def main(", "asyncio.run("]
        executable_count = sum(1 for pattern in executable_patterns if pattern in content)
        if executable_count < 2:
            score -= 3
        
        return max(0, score)
    
    async def _evaluate_originality(self, content: str, metadata: Dict[str, str]) -> float:
        """独自性を評価（25点満点）"""
        score = 25.0
        
        # 複数技術の組み合わせ
        tech_combinations = 0
        if "との連携" in content or "を組み合わせ" in content or "統合" in content:
            tech_combinations += 1
        if tech_combinations == 0:
            score -= 3
        
        # AIならではの視点
        if "AIの視点" in content or "自動化" in content or "機械学習" in content:
            score -= 0
        else:
            score -= 3
        
        # 詳細な実装説明
        detailed_explanations = content.count("詳しく") + content.count("詳細に") + content.count("深く")
        if detailed_explanations < 3:
            score -= 2
        
        # パフォーマンス最適化の言及
        if "最適化" in content or "パフォーマンス" in content or "高速化" in content:
            score -= 0
        else:
            score -= 2
        
        # 文章量（独自の詳細な説明があるか）
        word_count = len(content.replace(" ", "").replace("\n", ""))
        if word_count < 5000:
            score -= 5  # 文章が短すぎる
        
        return max(0, score)
    
    def _analyze_strengths_weaknesses(self, content: str, scores: Dict[str, float]) -> Dict[str, List[str]]:
        """強みと弱みを分析"""
        result = {
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": []
        }
        
        # スコアに基づく分析
        for category, score in scores.items():
            if score >= 20:
                result["strengths"].append(f"{category}: 優秀なスコア ({score:.1f}/25)")
            elif score < 15:
                result["weaknesses"].append(f"{category}: 改善が必要 ({score:.1f}/25)")
        
        # コンテンツ分析
        if len(re.findall(r'```[\w]*\n', content)) > 5:
            result["strengths"].append("豊富なコード例")
        else:
            result["improvement_suggestions"].append("より多くのコード例を追加")
        
        if "なぜこの記事を書こうと思ったのか" in content:
            result["strengths"].append("AIの思考プロセスが明確")
        else:
            result["weaknesses"].append("AIの思考プロセスセクションが不足")
            result["improvement_suggestions"].append("記事冒頭にAIの思考プロセスを追加")
        
        # 文章とコードのバランス
        code_ratio = len(re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)) / max(1, content.count('\n\n'))
        if 0.2 <= code_ratio <= 0.4:
            result["strengths"].append("文章とコードの良好なバランス")
        else:
            result["improvement_suggestions"].append("文章とコードのバランスを調整（目標: 70:30）")
        
        return result

class RuleEvaluator:
    """ルール自体を評価し、更新するクラス"""
    
    def __init__(self):
        self.rules_file = Path("BLOG_WRITING_RULES.md")
        self.rules_history_file = Path("rules_history.json")
        self.load_rules_history()
    
    def load_rules_history(self):
        """ルール更新履歴を読み込む"""
        if self.rules_history_file.exists():
            with open(self.rules_history_file, "r", encoding="utf-8") as f:
                self.rules_history = json.load(f)
        else:
            self.rules_history = {
                "versions": [],
                "update_reasons": []
            }
    
    def save_rules_history(self):
        """ルール更新履歴を保存"""
        with open(self.rules_history_file, "w", encoding="utf-8") as f:
            json.dump(self.rules_history, f, ensure_ascii=False, indent=2)
    
    async def evaluate_rules(self, recent_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最近の評価結果に基づいてルールを評価"""
        
        rule_evaluation = {
            "timestamp": datetime.now(JST).isoformat(),
            "current_effectiveness": 0,
            "suggested_updates": [],
            "rationale": []
        }
        
        if not recent_evaluations:
            return rule_evaluation
        
        # 最近の記事の平均スコアを計算
        avg_scores = {
            "technical_accuracy": 0,
            "readability": 0,
            "practicality": 0,
            "originality": 0
        }
        
        for eval in recent_evaluations:
            for key in avg_scores:
                avg_scores[key] += eval["scores"][key]
        
        for key in avg_scores:
            avg_scores[key] /= len(recent_evaluations)
        
        total_avg = sum(avg_scores.values())
        rule_evaluation["current_effectiveness"] = total_avg
        
        # ルール更新の提案
        if avg_scores["readability"] < 18:
            rule_evaluation["suggested_updates"].append({
                "rule": "読みやすさの基準を強化",
                "action": "セクション間のマージンを増やし、説明をより詳細に",
                "priority": "high"
            })
            rule_evaluation["rationale"].append("最近の記事で読みやすさスコアが低い")
        
        if avg_scores["originality"] < 18:
            rule_evaluation["suggested_updates"].append({
                "rule": "独自性の要件を更新",
                "action": "複数技術の組み合わせを必須に、より深い分析を要求",
                "priority": "medium"
            })
            rule_evaluation["rationale"].append("独自性スコアが目標を下回っている")
        
        # 同じ問題が繰り返されているかチェック
        common_weaknesses = {}
        for eval in recent_evaluations:
            for weakness in eval.get("weaknesses", []):
                common_weaknesses[weakness] = common_weaknesses.get(weakness, 0) + 1
        
        for weakness, count in common_weaknesses.items():
            if count >= 3:  # 3記事以上で同じ問題
                rule_evaluation["suggested_updates"].append({
                    "rule": f"{weakness}に対するルール追加",
                    "action": "明確な基準とチェックリストを追加",
                    "priority": "high"
                })
                rule_evaluation["rationale"].append(f"{weakness}が{count}記事で発生")
        
        return rule_evaluation
    
    async def update_rules(self, rule_evaluation: Dict[str, Any]) -> bool:
        """ルールを更新する"""
        
        if not rule_evaluation["suggested_updates"]:
            return False
        
        # 高優先度の更新のみを適用
        high_priority_updates = [
            update for update in rule_evaluation["suggested_updates"] 
            if update["priority"] == "high"
        ]
        
        if not high_priority_updates:
            return False
        
        # 現在のルールを読み込む
        with open(self.rules_file, "r", encoding="utf-8") as f:
            current_rules = f.read()
        
        # バージョン情報を更新
        version_match = re.search(r'### v([\d.]+)', current_rules)
        if version_match:
            current_version = version_match.group(1)
            new_version = self._increment_version(current_version)
        else:
            new_version = "1.1"
        
        # 更新内容を追加
        update_date = datetime.now(JST).strftime('%Y-%m-%d')
        update_section = f"\n### v{new_version} ({update_date})\n"
        
        for update in high_priority_updates:
            update_section += f"- {update['rule']}: {update['action']}\n"
        
        # ルールファイルを更新
        updated_rules = re.sub(
            r'(### 今後の更新予定)',
            update_section + r'\n\1',
            current_rules
        )
        
        # バージョン番号を更新
        updated_rules = re.sub(
            r'\*バージョン: [\d.]+\*',
            f'*バージョン: {new_version}*',
            updated_rules
        )
        
        # ファイルに書き込む
        with open(self.rules_file, "w", encoding="utf-8") as f:
            f.write(updated_rules)
        
        # 履歴を更新
        self.rules_history["versions"].append({
            "version": new_version,
            "date": update_date,
            "updates": high_priority_updates,
            "rationale": rule_evaluation["rationale"]
        })
        self.save_rules_history()
        
        return True
    
    def _increment_version(self, version: str) -> str:
        """バージョン番号をインクリメント"""
        parts = version.split('.')
        if len(parts) == 2:
            major, minor = parts
            return f"{major}.{int(minor) + 1}"
        return "1.1"

class SelfImprovingBlogSystem:
    """自己改善型ブログシステムのメインクラス"""
    
    def __init__(self):
        self.article_evaluator = ArticleEvaluator()
        self.rule_evaluator = RuleEvaluator()
    
    async def evaluate_and_improve(self) -> Dict[str, Any]:
        """評価と改善のメインプロセス"""
        
        # 最新の記事を評価
        posts_dir = Path("posts")
        recent_articles = sorted(
            posts_dir.glob("*.md"), 
            key=lambda x: x.stat().st_mtime, 
            reverse=True
        )[:5]  # 最新5記事
        
        evaluations = []
        for article in recent_articles:
            evaluation = await self.article_evaluator.evaluate_article(article)
            evaluations.append(evaluation)
            
            # 評価履歴に追加
            self.article_evaluator.history["evaluations"].append(evaluation)
        
        # 履歴を保存
        self.article_evaluator.save_history()
        
        # ルールを評価
        rule_evaluation = await self.rule_evaluator.evaluate_rules(evaluations)
        
        # ルールを更新
        rules_updated = await self.rule_evaluator.update_rules(rule_evaluation)
        
        # 改善レポートを生成
        improvement_report = {
            "timestamp": datetime.now(JST).isoformat(),
            "articles_evaluated": len(evaluations),
            "average_score": sum(e["total_score"] for e in evaluations) / len(evaluations) if evaluations else 0,
            "rules_updated": rules_updated,
            "rule_evaluation": rule_evaluation,
            "recent_evaluations": evaluations[-3:],  # 最新3件の評価
            "improvement_trends": self._analyze_trends()
        }
        
        # レポートを保存
        report_file = Path(f"improvement_report_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(improvement_report, f, ensure_ascii=False, indent=2)
        
        return improvement_report
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """品質トレンドを分析"""
        evaluations = self.article_evaluator.history.get("evaluations", [])
        
        if len(evaluations) < 2:
            return {"trend": "insufficient_data"}
        
        # 最新10件と過去10件を比較
        recent = evaluations[-10:]
        older = evaluations[-20:-10] if len(evaluations) >= 20 else evaluations[:len(evaluations)//2]
        
        recent_avg = sum(e["total_score"] for e in recent) / len(recent)
        older_avg = sum(e["total_score"] for e in older) / len(older) if older else recent_avg
        
        improvement = recent_avg - older_avg
        
        return {
            "trend": "improving" if improvement > 0 else "declining",
            "improvement_rate": improvement,
            "recent_average": recent_avg,
            "historical_average": older_avg,
            "evaluation_count": len(evaluations)
        }

async def main():
    """メイン実行関数"""
    print("🔄 自己改善型ブログシステム - 評価と改善プロセス開始")
    print("=" * 60)
    
    system = SelfImprovingBlogSystem()
    
    # 評価と改善を実行
    report = await system.evaluate_and_improve()
    
    print(f"\n📊 評価完了:")
    print(f"  - 評価記事数: {report['articles_evaluated']}")
    print(f"  - 平均スコア: {report['average_score']:.1f}/100")
    print(f"  - ルール更新: {'実施' if report['rules_updated'] else '不要'}")
    
    if report["improvement_trends"]["trend"] != "insufficient_data":
        print(f"\n📈 品質トレンド: {report['improvement_trends']['trend']}")
        print(f"  - 改善率: {report['improvement_trends']['improvement_rate']:.1f}ポイント")
    
    print("\n✅ 評価と改善プロセス完了")
    print(f"📄 詳細レポート: improvement_report_*.json")

if __name__ == "__main__":
    asyncio.run(main())