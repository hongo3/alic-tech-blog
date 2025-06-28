#!/usr/bin/env python3
"""
記事校正システム
プロのライター視点で記事を校正し、正確性と品質を向上させる
"""

import json
import re
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
import httpx
from urllib.parse import urlparse

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

class ArticleProofreader:
    """記事の校正を行うクラス"""
    
    def __init__(self):
        self.proofreading_rules_file = Path("BLOG_PROOFREADING_RULES.md")
        self.proofreading_log_file = Path("proofreading_log.json")
        self.load_proofreading_log()
        
    def load_proofreading_log(self):
        """校正ログを読み込む"""
        if self.proofreading_log_file.exists():
            with open(self.proofreading_log_file, "r", encoding="utf-8") as f:
                self.proofreading_log = json.load(f)
        else:
            self.proofreading_log = {
                "logs": [],
                "common_issues": {},
                "improvement_patterns": []
            }
    
    def save_proofreading_log(self):
        """校正ログを保存"""
        with open(self.proofreading_log_file, "w", encoding="utf-8") as f:
            json.dump(self.proofreading_log, f, ensure_ascii=False, indent=2)
    
    async def proofread_article(self, article_path: Path) -> Dict[str, Any]:
        """記事を校正する"""
        
        with open(article_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # メタデータを抽出
        metadata = self._extract_metadata(content)
        
        # 校正結果を初期化
        proofreading_result = {
            "article_id": article_path.stem,
            "timestamp": datetime.now(JST).isoformat(),
            "original_score": 100,  # 減点方式
            "issues_found": [],
            "corrections": [],
            "final_score": 100
        }
        
        # 各項目をチェック
        technical_issues = await self._check_technical_accuracy(content, metadata)
        timeliness_issues = await self._check_timeliness(content, metadata)
        quality_issues = self._check_writing_quality(content)
        practicality_issues = self._check_practicality(content)
        
        # すべての問題を統合
        all_issues = technical_issues + timeliness_issues + quality_issues + practicality_issues
        proofreading_result["issues_found"] = all_issues
        
        # スコアを計算
        for issue in all_issues:
            if issue["severity"] == "high":
                proofreading_result["original_score"] -= 10
            elif issue["severity"] == "medium":
                proofreading_result["original_score"] -= 5
            else:
                proofreading_result["original_score"] -= 2
        
        # 自動修正を適用
        corrected_content = content
        for issue in all_issues:
            if issue.get("auto_correctable", False):
                corrected_content, correction = self._apply_correction(
                    corrected_content, issue
                )
                if correction:
                    proofreading_result["corrections"].append(correction)
        
        # 最終スコアを計算
        proofreading_result["final_score"] = min(
            100,
            proofreading_result["original_score"] + len(proofreading_result["corrections"]) * 3
        )
        
        # 修正が必要な場合は記事を更新
        if proofreading_result["corrections"]:
            proofreading_result["corrected_content"] = corrected_content
            proofreading_result["auto_corrected"] = True
        else:
            proofreading_result["auto_corrected"] = False
        
        return proofreading_result
    
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
    
    async def _check_technical_accuracy(self, content: str, metadata: Dict[str, str]) -> List[Dict[str, Any]]:
        """技術的正確性をチェック"""
        issues = []
        
        # バージョン情報をチェック
        version_patterns = [
            (r'Python (\d+\.\d+(?:\.\d+)?)', 'Python', '3.11'),
            (r'Node\.js (\d+(?:\.\d+)?)', 'Node.js', '20'),
            (r'React (\d+(?:\.\d+)?)', 'React', '18.2'),
            (r'Next\.js (\d+(?:\.\d+)?)', 'Next.js', '15'),
            (r'Vue (\d+(?:\.\d+)?)', 'Vue', '3.4'),
        ]
        
        for pattern, tech, latest in version_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self._is_version_outdated(match, latest):
                    issues.append({
                        "type": "version_outdated",
                        "severity": "medium",
                        "location": f"{tech} {match}",
                        "original": match,
                        "suggestion": latest,
                        "auto_correctable": True,
                        "pattern": f"{tech} {match}",
                        "replacement": f"{tech} {latest}"
                    })
        
        # 非推奨の用語や手法をチェック
        deprecated_terms = {
            "componentWillMount": "useEffect",
            "componentWillReceiveProps": "useEffect or getDerivedStateFromProps",
            "findDOMNode": "ref",
            "React.createClass": "class components or function components",
            "var ": "let or const",
        }
        
        for deprecated, replacement in deprecated_terms.items():
            if deprecated in content:
                issues.append({
                    "type": "deprecated_usage",
                    "severity": "high",
                    "location": f"Usage of {deprecated}",
                    "original": deprecated,
                    "suggestion": replacement,
                    "auto_correctable": deprecated == "var ",
                    "pattern": deprecated,
                    "replacement": "const " if deprecated == "var " else None
                })
        
        # コードブロックの文法をチェック
        code_blocks = re.findall(r'```(?:python|javascript|typescript)?\n(.*?)\n```', content, re.DOTALL)
        for i, code in enumerate(code_blocks):
            syntax_issues = self._check_code_syntax(code)
            for issue in syntax_issues:
                issue["location"] = f"Code block {i+1}"
                issues.append(issue)
        
        # URLの有効性をチェック（簡易版）
        urls = re.findall(r'https?://[^\s\)]+', content)
        for url in urls[:5]:  # 最初の5個のみチェック（パフォーマンスのため）
            if not await self._is_url_valid(url):
                issues.append({
                    "type": "invalid_url",
                    "severity": "low",
                    "location": url,
                    "original": url,
                    "suggestion": "Check URL validity",
                    "auto_correctable": False
                })
        
        return issues
    
    async def _check_timeliness(self, content: str, metadata: Dict[str, str]) -> List[Dict[str, Any]]:
        """時流との整合性をチェック"""
        issues = []
        
        # 古い年号の参照をチェック
        current_year = datetime.now().year
        old_year_pattern = r'\b(20[0-9]{2})年'
        year_matches = re.findall(old_year_pattern, content)
        
        for year in year_matches:
            if int(year) < current_year - 2:  # 2年以上前
                issues.append({
                    "type": "outdated_reference",
                    "severity": "low",
                    "location": f"{year}年",
                    "original": year,
                    "suggestion": "Consider updating to more recent information",
                    "auto_correctable": False
                })
        
        # 「最新」という表現の妥当性をチェック
        if "最新" in content:
            # 記事の日付を確認
            article_date = metadata.get("date", "")
            if article_date:
                try:
                    # 日付をパース（YYYY-MM-DD HH:MM形式を想定）
                    article_datetime = datetime.strptime(article_date, "%Y-%m-%d %H:%M")
                    # 現在時刻との差が1ヶ月以上なら警告
                    if (datetime.now() - article_datetime).days > 30:
                        issues.append({
                            "type": "stale_latest_claim",
                            "severity": "medium",
                            "location": "「最新」という表現",
                            "original": "最新",
                            "suggestion": "具体的な日付や時期を明記",
                            "auto_correctable": False
                        })
                except:
                    pass
        
        return issues
    
    def _check_writing_quality(self, content: str) -> List[Dict[str, Any]]:
        """文章品質をチェック"""
        issues = []
        
        # 基本的な誤字脱字パターン
        typo_patterns = [
            ("こども", "子ども"),
            ("いづれ", "いずれ"),
            ("すくなくとも", "少なくとも"),
            ("もとづ", "基づ"),
            ("おこな", "行な"),
            ("してる", "している"),
            ("してない", "していない"),
        ]
        
        for wrong, correct in typo_patterns:
            if wrong in content:
                issues.append({
                    "type": "typo",
                    "severity": "low",
                    "location": wrong,
                    "original": wrong,
                    "suggestion": correct,
                    "auto_correctable": True,
                    "pattern": wrong,
                    "replacement": correct
                })
        
        # 一文の長さをチェック
        sentences = re.split(r'[。！？]', content)
        for i, sentence in enumerate(sentences):
            if len(sentence) > 100:  # 100文字以上
                issues.append({
                    "type": "long_sentence",
                    "severity": "low",
                    "location": f"Sentence {i+1}",
                    "original": sentence[:50] + "...",
                    "suggestion": "文を分割して読みやすくする",
                    "auto_correctable": False
                })
        
        # 受動態の過度な使用をチェック
        passive_count = len(re.findall(r'れる|られる', content))
        if passive_count > 20:  # 記事全体で20回以上
            issues.append({
                "type": "excessive_passive_voice",
                "severity": "low",
                "location": "全体",
                "original": f"受動態が{passive_count}回使用",
                "suggestion": "能動態を使って文章を活発にする",
                "auto_correctable": False
            })
        
        # 専門用語の説明不足をチェック
        technical_terms = [
            "Docker", "Kubernetes", "CI/CD", "DevOps", "マイクロサービス",
            "レイテンシ", "スループット", "冪等性", "非同期処理"
        ]
        
        content_lower = content.lower()
        for term in technical_terms:
            if term.lower() in content_lower:
                # 用語の説明があるかチェック
                explanation_patterns = [
                    f"{term}とは",
                    f"{term}は",
                    f"{term}（",
                    f"{term} \\("
                ]
                has_explanation = any(
                    pattern.lower() in content_lower 
                    for pattern in explanation_patterns
                )
                
                if not has_explanation:
                    issues.append({
                        "type": "missing_term_explanation",
                        "severity": "medium",
                        "location": term,
                        "original": term,
                        "suggestion": f"{term}の説明を追加",
                        "auto_correctable": False
                    })
        
        return issues
    
    def _check_practicality(self, content: str) -> List[Dict[str, Any]]:
        """実用性をチェック"""
        issues = []
        
        # コード例の数をチェック
        code_blocks = re.findall(r'```[^\n]*\n', content)
        if len(code_blocks) < 3:
            issues.append({
                "type": "insufficient_code_examples",
                "severity": "medium",
                "location": "全体",
                "original": f"コード例が{len(code_blocks)}個",
                "suggestion": "より多くの実装例を追加",
                "auto_correctable": False
            })
        
        # インストール手順の有無をチェック
        has_install = any(
            keyword in content 
            for keyword in ["pip install", "npm install", "yarn add", "インストール"]
        )
        
        if not has_install and any(
            tech in content 
            for tech in ["ライブラリ", "パッケージ", "フレームワーク"]
        ):
            issues.append({
                "type": "missing_installation_guide",
                "severity": "medium",
                "location": "セットアップセクション",
                "original": "インストール手順なし",
                "suggestion": "インストール手順を追加",
                "auto_correctable": False
            })
        
        # エラーハンドリングの言及をチェック
        has_error_handling = any(
            keyword in content 
            for keyword in ["try", "except", "catch", "エラー", "例外", "トラブルシューティング"]
        )
        
        if not has_error_handling:
            issues.append({
                "type": "missing_error_handling",
                "severity": "low",
                "location": "全体",
                "original": "エラーハンドリングの言及なし",
                "suggestion": "エラーハンドリングやトラブルシューティングを追加",
                "auto_correctable": False
            })
        
        return issues
    
    def _check_code_syntax(self, code: str) -> List[Dict[str, Any]]:
        """コードの文法をチェック（簡易版）"""
        issues = []
        
        # 基本的な文法エラーパターン
        if "import" in code and "from" in code:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("from") and " import " in line:
                    # import文の順序をチェック
                    if i > 0 and not lines[i-1].strip().startswith(("from", "import", "")):
                        issues.append({
                            "type": "import_order",
                            "severity": "low",
                            "location": f"Line {i+1}",
                            "original": line.strip(),
                            "suggestion": "Import文を先頭にまとめる",
                            "auto_correctable": False
                        })
        
        # 未使用の変数をチェック（簡易版）
        variable_pattern = r'^(\s*)(\w+)\s*='
        variables = re.findall(variable_pattern, code, re.MULTILINE)
        for indent, var_name in variables:
            if var_name not in ["_", "__"] and code.count(var_name) == 1:
                issues.append({
                    "type": "unused_variable",
                    "severity": "low",
                    "location": var_name,
                    "original": var_name,
                    "suggestion": f"未使用の変数 {var_name}",
                    "auto_correctable": False
                })
        
        return issues
    
    def _is_version_outdated(self, version: str, latest: str) -> bool:
        """バージョンが古いかチェック"""
        try:
            current_parts = [int(x) for x in version.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # メジャーバージョンで比較
            if current_parts[0] < latest_parts[0]:
                return True
            
            # マイナーバージョンで比較（メジャーが同じ場合）
            if current_parts[0] == latest_parts[0] and len(current_parts) > 1 and len(latest_parts) > 1:
                if current_parts[1] < latest_parts[1]:
                    return True
            
            return False
        except:
            return False
    
    async def _is_url_valid(self, url: str) -> bool:
        """URLが有効かチェック（簡易版）"""
        try:
            # GitHubのURLは常に有効とみなす
            parsed = urlparse(url)
            if parsed.netloc in ["github.com", "githubusercontent.com"]:
                return True
            
            # その他のURLは簡単なフォーマットチェックのみ
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def _apply_correction(self, content: str, issue: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """修正を適用"""
        if not issue.get("auto_correctable", False):
            return content, None
        
        pattern = issue.get("pattern")
        replacement = issue.get("replacement")
        
        if pattern and replacement is not None:
            corrected_content = content.replace(pattern, replacement)
            if corrected_content != content:
                correction = {
                    "type": issue["type"],
                    "original": pattern,
                    "corrected": replacement,
                    "location": issue.get("location", "")
                }
                return corrected_content, correction
        
        return content, None

class ProofreadingRuleManager:
    """校正ルールを管理・更新するクラス"""
    
    def __init__(self):
        self.rules_file = Path("BLOG_PROOFREADING_RULES.md")
        self.rules_history_file = Path("proofreading_rules_history.json")
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
    
    async def evaluate_proofreading_rules(self, recent_proofreadings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """最近の校正結果に基づいてルールを評価"""
        
        rule_evaluation = {
            "timestamp": datetime.now(JST).isoformat(),
            "effectiveness": 0,
            "suggested_updates": [],
            "common_issues": {}
        }
        
        if not recent_proofreadings:
            return rule_evaluation
        
        # 共通の問題パターンを分析
        issue_counts = {}
        total_issues = 0
        
        for proofreading in recent_proofreadings:
            for issue in proofreading.get("issues_found", []):
                issue_type = issue["type"]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
                total_issues += 1
        
        rule_evaluation["common_issues"] = issue_counts
        
        # ルールの有効性を評価
        avg_final_score = sum(p["final_score"] for p in recent_proofreadings) / len(recent_proofreadings)
        rule_evaluation["effectiveness"] = avg_final_score
        
        # ルール更新の提案
        for issue_type, count in issue_counts.items():
            if count >= 3:  # 3回以上発生
                if issue_type == "version_outdated":
                    rule_evaluation["suggested_updates"].append({
                        "rule": "バージョン情報の自動更新強化",
                        "action": "最新バージョン情報の取得方法を改善",
                        "priority": "high"
                    })
                elif issue_type == "missing_term_explanation":
                    rule_evaluation["suggested_updates"].append({
                        "rule": "専門用語の説明チェック強化",
                        "action": "用語集を作成し、自動的に説明を挿入",
                        "priority": "medium"
                    })
                elif issue_type == "typo":
                    rule_evaluation["suggested_updates"].append({
                        "rule": "誤字脱字パターンの拡充",
                        "action": "よくある誤字パターンをルールに追加",
                        "priority": "low"
                    })
        
        return rule_evaluation

class ImprovedArticleWithProofreading:
    """校正機能を組み込んだ記事生成システム"""
    
    def __init__(self):
        self.proofreader = ArticleProofreader()
        self.rule_manager = ProofreadingRuleManager()
    
    async def generate_and_proofread(self, article_path: Path) -> Dict[str, Any]:
        """記事を生成して校正する"""
        
        print("📝 記事の校正を開始...")
        
        # 記事を校正
        proofreading_result = await self.proofreader.proofread_article(article_path)
        
        print(f"📊 校正結果:")
        print(f"  - 元のスコア: {proofreading_result['original_score']}")
        print(f"  - 検出された問題: {len(proofreading_result['issues_found'])}件")
        print(f"  - 自動修正: {len(proofreading_result['corrections'])}件")
        print(f"  - 最終スコア: {proofreading_result['final_score']}")
        
        # 問題の詳細を表示
        if proofreading_result['issues_found']:
            print("\n⚠️  検出された問題:")
            for issue in proofreading_result['issues_found'][:5]:  # 最初の5件
                print(f"  - [{issue['severity']}] {issue['type']}: {issue['original'][:50]}...")
        
        # 自動修正を適用
        if proofreading_result.get('auto_corrected', False):
            print("\n✅ 自動修正を適用しました:")
            for correction in proofreading_result['corrections']:
                print(f"  - {correction['type']}: {correction['original']} → {correction['corrected']}")
            
            # 修正された内容を保存
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(proofreading_result['corrected_content'])
            
            print(f"\n📝 記事を更新しました: {article_path}")
        
        # 校正ログを保存
        self.proofreader.proofreading_log["logs"].append(proofreading_result)
        self.proofreader.save_proofreading_log()
        
        # ルールの評価（最新10件の校正結果を使用）
        recent_logs = self.proofreader.proofreading_log["logs"][-10:]
        rule_evaluation = await self.rule_manager.evaluate_proofreading_rules(recent_logs)
        
        if rule_evaluation["suggested_updates"]:
            print("\n💡 校正ルールの改善提案:")
            for update in rule_evaluation["suggested_updates"]:
                print(f"  - {update['rule']}: {update['action']}")
        
        return {
            "proofreading_result": proofreading_result,
            "rule_evaluation": rule_evaluation
        }

async def main():
    """テスト実行"""
    print("🔍 記事校正システム - テスト実行")
    print("=" * 60)
    
    # 最新の記事を取得
    posts_dir = Path("posts")
    latest_article = sorted(
        posts_dir.glob("*.md"), 
        key=lambda x: x.stat().st_mtime, 
        reverse=True
    )[0]
    
    print(f"\n📄 対象記事: {latest_article.name}")
    
    # 校正システムを実行
    system = ImprovedArticleWithProofreading()
    result = await system.generate_and_proofread(latest_article)
    
    print("\n✅ 校正完了！")
    
    if result["proofreading_result"]["final_score"] >= 90:
        print("  → 高品質な記事です！")
    elif result["proofreading_result"]["final_score"] >= 80:
        print("  → 良好な品質ですが、改善の余地があります。")
    else:
        print("  → 品質向上のため、さらなる修正が必要です。")

if __name__ == "__main__":
    asyncio.run(main())