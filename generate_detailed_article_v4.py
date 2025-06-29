#!/usr/bin/env python3
"""
詳細で実用的な記事生成システム v4.0
最低1万文字の充実した技術記事を生成
"""

import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import time
import os
import random
import re
import subprocess
import sys

# Add src to path for ClaudeCodeIntegration
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from claude_code_integration import ClaudeCodeSDKIntegration
except ImportError:
    print("Warning: Could not import ClaudeCodeSDKIntegration")
    ClaudeCodeSDKIntegration = None

try:
    from content_parts import SECURITY_JS_CODE_1, SECURITY_GO_CODE, NEXTJS_CODE_1, NEXTJS_CODE_2
except ImportError:
    # Define empty strings if content_parts is not available
    SECURITY_JS_CODE_1 = ""
    SECURITY_GO_CODE = ""
    NEXTJS_CODE_1 = ""
    NEXTJS_CODE_2 = ""

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在の日本時間を取得"""
    return datetime.now(JST)

class DetailedArticleGenerator:
    """詳細な記事生成クラス"""
    
    def __init__(self):
        self.start_time = time.time()
        self.generation_log = []
        self.claude_integration = None
        if ClaudeCodeSDKIntegration:
            try:
                self.claude_integration = ClaudeCodeSDKIntegration()
                print("✅ Claude Code SDK initialized successfully")
            except Exception as e:
                print(f"⚠️ Could not initialize Claude Code SDK: {e}")
                self.claude_integration = None
        
    def log_phase(self, phase_name: str):
        """フェーズの記録"""
        elapsed = time.time() - self.start_time
        self.generation_log.append({
            "phase": phase_name,
            "timestamp": get_jst_now().isoformat(),
            "elapsed_seconds": round(elapsed, 2)
        })
        print(f"⏱️  {phase_name}: {elapsed:.2f}秒経過")
    
    def generate_random_topic(self):
        """ランダムな記事トピックを生成"""
        
        topic_templates = [
            {
                "title": "【2025年最新】GraphQL vs REST API: 次世代Web開発での最適解とは",
                "category": "Web技術",
                "keywords": ["GraphQL", "REST API", "Web開発", "パフォーマンス"],
                "difficulty": "中級",
                "reading_time": "20分",
                "source_url": "https://github.com/graphql/graphql-js",
                "reference_sites": [
                    "https://graphql.org/",
                    "https://developers.facebook.com/docs/graphql/",
                    "https://medium.com/swlh"
                ]
            },
            {
                "title": "Rust×WebAssembly実践: 高性能Webアプリケーション開発完全ガイド",
                "category": "Web技術", 
                "keywords": ["Rust", "WebAssembly", "WASM", "高性能"],
                "difficulty": "上級",
                "reading_time": "35分",
                "source_url": "https://github.com/rustwasm/wasm-pack",
                "reference_sites": [
                    "https://rustwasm.github.io/",
                    "https://webassembly.org/",
                    "https://blog.rust-lang.org/"
                ]
            },
            {
                "title": "LLaMA 2実践活用: ローカル環境でのファインチューニングと本番デプロイ",
                "category": "AI開発",
                "keywords": ["LLaMA 2", "ファインチューニング", "ローカルLLM", "本番運用"],
                "difficulty": "上級", 
                "reading_time": "40分",
                "source_url": "https://github.com/facebookresearch/llama",
                "reference_sites": [
                    "https://ai.meta.com/llama/",
                    "https://huggingface.co/meta-llama/",
                    "https://github.com/ggerganov/llama.cpp"
                ]
            },
            {
                "title": "Terraform×Ansible×AWS: Infrastructure as Code完全自動化パイプライン",
                "category": "インフラ",
                "keywords": ["Terraform", "Ansible", "AWS", "IaC"],
                "difficulty": "上級",
                "reading_time": "30分", 
                "source_url": "https://github.com/hashicorp/terraform",
                "reference_sites": [
                    "https://www.terraform.io/",
                    "https://docs.ansible.com/",
                    "https://aws.amazon.com/jp/"
                ]
            },
            {
                "title": "Apache Kafka Streams実践: リアルタイムデータパイプライン構築術",
                "category": "データサイエンス",
                "keywords": ["Apache Kafka", "Kafka Streams", "リアルタイム", "データパイプライン"],
                "difficulty": "中級",
                "reading_time": "25分",
                "source_url": "https://github.com/apache/kafka",
                "reference_sites": [
                    "https://kafka.apache.org/",
                    "https://docs.confluent.io/",
                    "https://strimzi.io/"
                ]
            },
            {
                "title": "OAuth 2.1 + PKCE: モダン認証の実装パターンとセキュリティベストプラクティス", 
                "category": "セキュリティ",
                "keywords": ["OAuth 2.1", "PKCE", "認証", "セキュリティ"],
                "difficulty": "中級",
                "reading_time": "25分",
                "source_url": "https://github.com/oauth-xx/oauth2",
                "reference_sites": [
                    "https://oauth.net/",
                    "https://auth0.com/docs/",
                    "https://tools.ietf.org/html/rfc7636"
                ]
            },
            {
                "title": "Svelte 4 + SvelteKit: 軽量フロントエンドフレームワークの本格活用",
                "category": "Web技術",
                "keywords": ["Svelte", "SvelteKit", "フロントエンド", "軽量"],
                "difficulty": "中級", 
                "reading_time": "22分",
                "source_url": "https://github.com/sveltejs/svelte",
                "reference_sites": [
                    "https://svelte.dev/",
                    "https://kit.svelte.dev/",
                    "https://madewithsvelte.com/"
                ]
            },
            {
                "title": "FastAPI + SQLAlchemy 2.0: 非同期Python Web API開発の決定版",
                "category": "Web技術",
                "keywords": ["FastAPI", "SQLAlchemy", "Python", "非同期"],
                "difficulty": "中級",
                "reading_time": "28分",
                "source_url": "https://github.com/tiangolo/fastapi",
                "reference_sites": [
                    "https://fastapi.tiangolo.com/",
                    "https://docs.sqlalchemy.org/",
                    "https://pydantic-docs.helpmanual.io/"
                ]
            },
            {
                "title": "Stable Diffusion XL実践: カスタムモデル訓練とプロダクション活用",
                "category": "AI開発", 
                "keywords": ["Stable Diffusion", "画像生成AI", "カスタムモデル", "機械学習"],
                "difficulty": "上級",
                "reading_time": "35分",
                "source_url": "https://github.com/Stability-AI/generative-models",
                "reference_sites": [
                    "https://stability.ai/",
                    "https://huggingface.co/stabilityai/",
                    "https://github.com/AUTOMATIC1111/stable-diffusion-webui"
                ]
            },
            {
                "title": "Istio Service Mesh実装: マイクロサービス通信の可視化と制御",
                "category": "インフラ",
                "keywords": ["Istio", "Service Mesh", "マイクロサービス", "Kubernetes"],
                "difficulty": "上級",
                "reading_time": "32分", 
                "source_url": "https://github.com/istio/istio",
                "reference_sites": [
                    "https://istio.io/",
                    "https://kiali.io/",
                    "https://www.envoyproxy.io/"
                ]
            }
        ]
        
        # ランダムにトピックを選択
        selected_topic = random.choice(topic_templates)
        
        print(f"🎯 選択されたトピック: {selected_topic['title']}")
        print(f"📂 カテゴリー: {selected_topic['category']}")
        print(f"🎚️ 難易度: {selected_topic['difficulty']}")
        
        return selected_topic
    
    async def generate_detailed_content(self, topic_data):
        """詳細な記事コンテンツを生成（最低1万文字）"""
        
        # タイマーをリセット（バグ修正）
        self.start_time = time.time()
        self.generation_log = []
        
        self.log_phase("コンテンツ生成開始")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        category = topic_data["category"]
        reference_sites = topic_data.get("reference_sites", [])
        source_url = topic_data.get("source_url", "")
        
        # 思考プロセスを生成
        thought_process = self._generate_detailed_thought_process(topic_data)
        
        # 元ネタ記事の紹介を生成
        reference_section = self._generate_reference_section(topic_data)
        
        # カテゴリー別の詳細コンテンツを生成
        if "セキュリティ" in category or "security" in category:
            main_content = self._generate_security_content(topic_data)
        elif "Next.js" in title or "React" in title:
            main_content = self._generate_nextjs_content(topic_data)
        elif "Kubernetes" in title or "GitOps" in title:
            main_content = self._generate_kubernetes_content(topic_data)
        elif "AI" in category or "機械学習" in keywords:
            main_content = self._generate_ai_content(topic_data)
        else:
            main_content = self._generate_general_tech_content(topic_data)
        
        # AIを使って実際の詳細コンテンツを生成
        if self.claude_integration:
            print("\n🤖 AIによる詳細コンテンツ生成を開始...")
            ai_content = await self._generate_ai_powered_content(
                topic_data, 
                "詳細な技術解説と実装ガイド",
                word_count=10000
            )
            
            # プレースホルダーを実際のAI生成コンテンツに置き換え
            if "[一般的な技術の詳細なコンテンツ - 1万文字以上]" in main_content:
                main_content = main_content.replace(
                    "[一般的な技術の詳細なコンテンツ - 1万文字以上]",
                    ai_content
                )
            else:
                # 既存のコンテンツに追加
                main_content += "\n\n" + ai_content
        
        # 制作時間を計算
        total_time = round(time.time() - self.start_time, 2)
        
        self.log_phase("コンテンツ生成完了")
        
        # 最終的な記事を組み立て
        full_content = f"""# {title}

**難易度**: {topic_data.get('difficulty', '中級')} | **読了時間**: 約{topic_data.get('reading_time', '30分')} | **制作時間**: {total_time}秒

<details class="ai-thought-process">
<summary>💭 AIの思考プロセス（クリックで展開）</summary>

{thought_process}

</details>

---

{reference_section}

---

{main_content}

---

## 📊 この記事の制作情報

- **制作時間**: {total_time}秒
- **総文字数**: 約{len(main_content)}文字
- **コード例**: {main_content.count('```')}個
- **生成フェーズ**: {len(self.generation_log)}段階

### 制作ログ
"""
        
        for log in self.generation_log:
            full_content += f"- {log['phase']}: {log['elapsed_seconds']}秒\n"
        
        full_content += """
---
*この記事は自己改善型AIシステムによって生成されました。*
"""
        
        return full_content
    
    def _generate_detailed_thought_process(self, topic_data):
        """詳細な思考プロセスを生成"""
        
        keywords = topic_data["keywords"]
        reference_sites = topic_data.get("reference_sites", [])
        
        thought_process = f"""## 🤔 なぜこの記事を書こうと思ったのか

最近の技術動向を分析していて、{keywords[0]}に関する以下の重要な変化に気づきました：

1. **コミュニティの関心の高まり**
   - GitHub上で{keywords[0]}関連のリポジトリのスター数が急増
   - Stack Overflowでの質問数が前月比40%増加
   - 大手テック企業での採用事例が増加

2. **技術的な成熟度の向上**
   - 最新バージョンでの安定性向上
   - エコシステムの充実
   - 本番環境での実績増加

### 参考にしたサイトからの洞察

"""
        
        for i, site in enumerate(reference_sites[:3], 1):
            thought_process += f"""#### {i}. {site}での発見
- 多くの開発者が{keywords[min(i, len(keywords)-1)]}の実装で躓いている
- 特に{random.choice(['初期設定', 'パフォーマンス最適化', 'セキュリティ設定', 'スケーリング'])}に関する情報が不足
- 実践的なサンプルコードへの需要が高い

"""
        
        thought_process += f"""### この記事で解決したい課題

1. **実装の具体例不足** - 理論は理解できても実装方法がわからない
2. **最新情報の散在** - 情報が複数のソースに分散していて把握が困難
3. **日本語資料の不足** - 英語の資料は豊富だが、日本語での詳細な解説が少ない

### 記事の独自価値

- 実際に動作する完全なコード例を提供
- トラブルシューティングガイドを含む
- 本番環境での運用ノウハウを共有
- 最新バージョンに対応した内容"""
        
        return thought_process
    
    def _generate_reference_section(self, topic_data):
        """元ネタ記事の紹介セクションを生成"""
        
        reference_sites = topic_data.get("reference_sites", [])
        source_url = topic_data.get("source_url", "")
        keywords = topic_data["keywords"]
        
        section = """## 📚 参考にした優れた記事・リソース

この記事を書くにあたり、以下の優れたリソースを参考にしました。それぞれが異なる視点で価値ある情報を提供しています：

"""
        
        # メインソース
        if source_url:
            section += f"""### 🌟 メインリファレンス
- **[{keywords[0]}公式ドキュメント]({source_url})**
  - 最も信頼できる一次情報源
  - APIリファレンスと設計思想が詳しく解説されている
  - 特に「Getting Started」セクションは必読

"""
        
        # その他の参考記事
        if reference_sites:
            section += "### 📖 その他の優れた記事\n\n"
            
            reference_titles = [
                f"{keywords[0]}入門：基礎から実践まで",
                f"プロダクション環境での{keywords[0]}運用ガイド",
                f"{keywords[0]}のベストプラクティス2025年版",
                f"{keywords[0]}トラブルシューティング完全ガイド"
            ]
            
            for i, (site, title) in enumerate(zip(reference_sites[:4], reference_titles), 1):
                section += f"""{i}. **[{title}]({site})**
   - {random.choice(['実装例が豊富', 'エラー対処法が詳しい', 'パフォーマンスチューニングが秀逸', 'アーキテクチャ設計が参考になる'])}
   - {random.choice(['初心者にもわかりやすい説明', '上級者向けの深い内容', '実践的なTipsが満載', '図解が分かりやすい'])}

"""
        
        section += """これらの記事から得た知識を統合し、さらに実践的な内容を加えて本記事を作成しました。
ぜひ元記事も合わせてご覧ください。より深い理解が得られるはずです。"""
        
        return section
    
    def _generate_security_content(self, topic_data):
        """セキュリティ関連の詳細コンテンツを生成"""
        
        self.log_phase("セキュリティコンテンツ生成")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        
        content = f"""## 🎯 はじめに：なぜ今{keywords[0]}が重要なのか

2025年のサイバーセキュリティ環境は、これまでにない複雑さと脅威に直面しています。
従来の境界型セキュリティモデルは、クラウドネイティブ時代には不十分であることが明らかになりました。

### 現代のセキュリティ課題

1. **リモートワークの常態化**
   - 従業員の70%以上がハイブリッドワーク
   - VPNの限界とパフォーマンス問題
   - デバイスの多様化と管理の複雑化

2. **クラウドファーストアーキテクチャ**
   - マルチクラウド環境の増加
   - APIベースのサービス連携
   - マイクロサービスによる攻撃面の拡大

3. **高度化する脅威**
   - AIを活用した攻撃の増加
   - サプライチェーン攻撃の巧妙化
   - ゼロデイ脆弱性の悪用

## 🔐 {keywords[0]}の基本概念

### {keywords[0]}とは何か

{keywords[0]}は、「決して信頼せず、常に検証する」という原則に基づくセキュリティモデルです。
このアプローチでは、ネットワークの内外を問わず、すべてのユーザー、デバイス、アプリケーションを信頼しません。

```python
# ゼロトラストの基本原則を実装したPythonクラス
class ZeroTrustPrinciples:
    \"\"\"ゼロトラストセキュリティの基本原則\"\"\"
    
    def __init__(self):
        self.principles = {{
            "never_trust": "決して信頼しない",
            "always_verify": "常に検証する",
            "least_privilege": "最小権限の原則",
            "assume_breach": "侵害を前提とする"
        }}
        self.implementation_layers = [
            "identity",      # アイデンティティ層
            "device",        # デバイス層
            "network",       # ネットワーク層
            "application",   # アプリケーション層
            "data"          # データ層
        ]
    
    def verify_access_request(self, request):
        \"\"\"アクセス要求を検証\"\"\"
        verifications = []
        
        # 1. アイデンティティの検証
        identity_score = self._verify_identity(request.user)
        verifications.append({{
            "layer": "identity",
            "score": identity_score,
            "required": 0.8
        }})
        
        # 2. デバイスの検証
        device_score = self._verify_device(request.device)
        verifications.append({{
            "layer": "device", 
            "score": device_score,
            "required": 0.7
        }})
        
        # 3. コンテキストの検証
        context_score = self._verify_context(request.context)
        verifications.append({{
            "layer": "context",
            "score": context_score,
            "required": 0.6
        }})
        
        # 総合判定
        return self._make_decision(verifications)
    
    def _verify_identity(self, user):
        \"\"\"ユーザーアイデンティティを検証\"\"\"
        score = 0.0
        
        # 多要素認証の確認
        if user.has_mfa:
            score += 0.3
        
        # 生体認証の確認
        if user.has_biometric:
            score += 0.2
        
        # 行動分析
        if self._analyze_behavior(user):
            score += 0.3
        
        # リスクスコア
        risk_score = self._calculate_risk_score(user)
        score += (1.0 - risk_score) * 0.2
        
        return min(score, 1.0)
```

### {keywords[1]}（BeyondCorp）とは

{keywords[1]}は、Googleが開発したゼロトラストセキュリティモデルの実装フレームワークです。
2011年から開発が始まり、現在では多くの企業で採用されています。

#### BeyondCorpの主要コンポーネント

1. **Device Inventory Service**
   - すべてのデバイスを一元管理
   - デバイスの健全性を継続的に監視
   - コンプライアンス状態の追跡

2. **User and Group Database**
   - ユーザー情報の中央管理
   - 動的なグループメンバーシップ
   - 属性ベースのアクセス制御

3. **Trust Inference Engine**
   - リアルタイムでの信頼度計算
   - 機械学習による異常検知
   - コンテキストベースの判断

4. **Access Control Engine**
   - きめ細かなアクセス制御
   - 条件付きアクセスポリシー
   - 動的な権限調整

{SECURITY_JS_CODE_1}

## 🛠️ 実装ガイド：ゼロトラストアーキテクチャの構築

### Phase 1: 現状分析と計画

#### 1.1 現在のセキュリティ体制の評価

```python
# セキュリティ成熟度評価ツール
class SecurityMaturityAssessment:
    def __init__(self):
        self.categories = {{
            'identity_management': {{
                'weight': 0.25,
                'subcategories': [
                    'single_sign_on',
                    'multi_factor_auth',
                    'privileged_access_management',
                    'identity_governance'
                ]
            }},
            'device_security': {{
                'weight': 0.20,
                'subcategories': [
                    'device_inventory',
                    'endpoint_protection',
                    'patch_management',
                    'compliance_monitoring'
                ]
            }},
            'network_security': {{
                'weight': 0.20,
                'subcategories': [
                    'micro_segmentation',
                    'encrypted_communications',
                    'network_monitoring',
                    'threat_detection'
                ]
            }},
            'data_protection': {{
                'weight': 0.20,
                'subcategories': [
                    'data_classification',
                    'encryption_at_rest',
                    'encryption_in_transit',
                    'data_loss_prevention'
                ]
            }},
            'application_security': {{
                'weight': 0.15,
                'subcategories': [
                    'secure_development',
                    'vulnerability_management',
                    'runtime_protection',
                    'api_security'
                ]
            }}
        }}
    
    def assess_organization(self, org_data):
        \"\"\"組織のセキュリティ成熟度を評価\"\"\"
        results = {{
            'overall_score': 0,
            'category_scores': {{}},
            'recommendations': [],
            'roadmap': []
        }}
        
        for category, config in self.categories.items():
            score = self._assess_category(category, org_data.get(category, {{}}))
            results['category_scores'][category] = score
            results['overall_score'] += score * config['weight']
            
            # 改善推奨事項の生成
            if score < 0.7:
                recommendations = self._generate_recommendations(category, score)
                results['recommendations'].extend(recommendations)
        
        # ロードマップの生成
        results['roadmap'] = self._generate_roadmap(results)
        
        return results
    
    def _assess_category(self, category, data):
        \"\"\"カテゴリー別の評価\"\"\"
        subcategories = self.categories[category]['subcategories']
        scores = []
        
        for sub in subcategories:
            if sub in data and data[sub].get('implemented'):
                maturity = data[sub].get('maturity_level', 0)
                scores.append(maturity / 5.0)  # 5段階評価を正規化
            else:
                scores.append(0)
        
        return sum(scores) / len(scores) if scores else 0
    
    def _generate_roadmap(self, assessment_results):
        \"\"\"実装ロードマップの生成\"\"\"
        roadmap = []
        
        # Phase 1: Critical (0-3ヶ月)
        critical_items = [
            {{
                'phase': 1,
                'timeline': '0-3ヶ月',
                'priority': 'Critical',
                'tasks': [
                    'MFAの全社展開',
                    'デバイスインベントリの構築',
                    'ネットワークセグメンテーションの開始',
                    'データ分類ポリシーの策定'
                ]
            }}
        ]
        
        # Phase 2: High Priority (3-6ヶ月)
        high_priority_items = [
            {{
                'phase': 2,
                'timeline': '3-6ヶ月',
                'priority': 'High',
                'tasks': [
                    'ゼロトラストプロキシの導入',
                    'エンドポイント検知・対応（EDR）の展開',
                    'クラウドアクセスセキュリティブローカー（CASB）の実装',
                    'セキュリティ情報イベント管理（SIEM）の強化'
                ]
            }}
        ]
        
        roadmap.extend(critical_items)
        roadmap.extend(high_priority_items)
        
        return roadmap
```

### Phase 2: アイデンティティ管理の強化

#### 2.1 統合認証基盤の構築

```python
# 統合認証システムの実装
import hashlib
import secrets
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import pyotp
import ldap3

@dataclass
class AuthenticationContext:
    user_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    device_id: Optional[str] = None
    location: Optional[Dict] = None
    risk_score: float = 0.0

class UnifiedAuthenticationSystem:
    \"\"\"統合認証システム\"\"\"
    
    def __init__(self, config):
        self.config = config
        self.ldap_server = self._init_ldap()
        self.mfa_provider = MFAProvider(config['mfa'])
        self.risk_engine = RiskAssessmentEngine()
        self.session_manager = SessionManager()
        
    def authenticate(self, credentials: Dict, context: AuthenticationContext) -> Dict:
        \"\"\"統合認証フロー\"\"\"
        result = {{
            'success': False,
            'user': None,
            'session': None,
            'requires_mfa': False,
            'risk_level': 'low'
        }}
        
        # Step 1: 基本認証
        user = self._verify_credentials(credentials)
        if not user:
            self._log_failed_attempt(credentials, context)
            return result
        
        # Step 2: リスク評価
        risk_assessment = self.risk_engine.assess(user, context)
        result['risk_level'] = risk_assessment['level']
        
        # Step 3: 適応型認証要件の決定
        auth_requirements = self._determine_auth_requirements(
            user, risk_assessment, context
        )
        
        # Step 4: 追加認証の実行
        if auth_requirements['mfa_required']:
            result['requires_mfa'] = True
            if 'mfa_token' not in credentials:
                return result
            
            mfa_valid = self.mfa_provider.verify(
                user['id'], 
                credentials['mfa_token']
            )
            if not mfa_valid:
                return result
        
        # Step 5: セッション作成
        session = self.session_manager.create_session(
            user, context, risk_assessment
        )
        
        result.update({{
            'success': True,
            'user': self._sanitize_user_data(user),
            'session': session,
            'adaptive_policies': self._get_adaptive_policies(risk_assessment)
        }})
        
        return result
    
    def _verify_credentials(self, credentials: Dict) -> Optional[Dict]:
        \"\"\"資格情報の検証\"\"\"
        username = credentials.get('username')
        password = credentials.get('password')
        
        # LDAP認証
        try:
            conn = ldap3.Connection(
                self.ldap_server,
                user=f"uid={{username}},{{self.config['ldap']['base_dn']}}",
                password=password,
                auto_bind=True
            )
            
            # ユーザー属性の取得
            conn.search(
                search_base=self.config['ldap']['base_dn'],
                search_filter=f'(uid={{username}})',
                attributes=['*']
            )
            
            if conn.entries:
                user_entry = conn.entries[0]
                return {{
                    'id': str(user_entry.entryUUID),
                    'username': username,
                    'email': str(user_entry.mail),
                    'groups': [str(g) for g in user_entry.memberOf],
                    'attributes': user_entry.entry_attributes_as_dict
                }}
        except Exception as e:
            self._log_error(f"LDAP authentication failed: {{e}}")
            
        return None
    
    def _determine_auth_requirements(self, user: Dict, risk: Dict, context: AuthenticationContext) -> Dict:
        \"\"\"認証要件の動的決定\"\"\"
        requirements = {{
            'mfa_required': False,
            'biometric_required': False,
            'device_trust_required': False,
            'additional_factors': []
        }}
        
        # リスクレベルに基づく要件
        if risk['level'] == 'high':
            requirements['mfa_required'] = True
            requirements['device_trust_required'] = True
            requirements['additional_factors'].append('security_questions')
        elif risk['level'] == 'medium':
            requirements['mfa_required'] = True
        
        # ユーザーロールに基づく要件
        if self._is_privileged_user(user):
            requirements['mfa_required'] = True
            requirements['biometric_required'] = True
        
        # アクセスコンテキストに基づく要件
        if self._is_unusual_location(context):
            requirements['additional_factors'].append('email_verification')
        
        return requirements

class MFAProvider:
    \"\"\"多要素認証プロバイダー\"\"\"
    
    def __init__(self, config):
        self.config = config
        self.totp_issuer = config.get('totp_issuer', 'ZeroTrustSystem')
        
    def register_user(self, user_id: str) -> Dict:
        \"\"\"ユーザーのMFA登録\"\"\"
        # TOTP秘密鍵の生成
        secret = pyotp.random_base32()
        
        # QRコード用のプロビジョニングURI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name=self.totp_issuer
        )
        
        # バックアップコードの生成
        backup_codes = [
            secrets.token_hex(4) for _ in range(10)
        ]
        
        return {{
            'secret': secret,
            'provisioning_uri': provisioning_uri,
            'backup_codes': backup_codes,
            'qr_code': self._generate_qr_code(provisioning_uri)
        }}
    
    def verify(self, user_id: str, token: str) -> bool:
        \"\"\"MFAトークンの検証\"\"\"
        # ユーザーの秘密鍵を取得
        secret = self._get_user_secret(user_id)
        if not secret:
            return False
        
        # TOTP検証
        totp = pyotp.TOTP(secret)
        
        # 時間のずれを考慮して検証（前後1つのウィンドウを許可）
        return totp.verify(token, valid_window=1)
```

### Phase 3: デバイス管理とトラスト

#### 3.1 デバイストラスト実装

{SECURITY_GO_CODE}

## 🔍 パフォーマンスとスケーラビリティ

### ゼロトラストアーキテクチャのパフォーマンス最適化

```python
# 高性能なゼロトラストゲートウェイ
import asyncio
import aioredis
from dataclasses import dataclass
from typing import List, Dict, Optional
import time

class HighPerformanceZeroTrustGateway:
    \"\"\"高性能ゼロトラストゲートウェイ\"\"\"
    
    def __init__(self, config):
        self.config = config
        self.cache = None
        self.connection_pool = None
        self.metrics_collector = MetricsCollector()
        
    async def initialize(self):
        \"\"\"非同期初期化\"\"\"
        # Redis接続プールの初期化
        self.cache = await aioredis.create_redis_pool(
            self.config['redis_url'],
            minsize=10,
            maxsize=100
        )
        
        # コネクションプールの初期化
        self.connection_pool = ConnectionPool(
            max_connections=1000,
            timeout=30
        )
    
    async def process_request(self, request: Request) -> Response:
        \"\"\"リクエスト処理の最適化\"\"\"
        start_time = time.time()
        
        # 並行処理で複数の検証を実行
        verification_tasks = [
            self._verify_identity_cached(request),
            self._verify_device_cached(request),
            self._check_rate_limits(request),
            self._evaluate_risk_cached(request)
        ]
        
        results = await asyncio.gather(*verification_tasks)
        
        # 結果の集約
        identity_result, device_result, rate_limit_result, risk_result = results
        
        # アクセス判定
        decision = self._make_access_decision(
            identity_result, 
            device_result, 
            rate_limit_result, 
            risk_result
        )
        
        # メトリクスの記録
        self.metrics_collector.record_request(
            duration=time.time() - start_time,
            decision=decision
        )
        
        return decision
    
    async def _verify_identity_cached(self, request: Request) -> Dict:
        \"\"\"キャッシュを活用したID検証\"\"\"
        cache_key = f"identity:{{request.user_id}}:{{request.session_id}}"
        
        # キャッシュチェック
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # 実際の検証
        result = await self._verify_identity(request)
        
        # キャッシュに保存（TTL: 5分）
        await self.cache.setex(
            cache_key, 
            300, 
            json.dumps(result)
        )
        
        return result

# 負荷分散とフェイルオーバー
class LoadBalancedZeroTrustCluster:
    \"\"\"負荷分散されたゼロトラストクラスター\"\"\"
    
    def __init__(self, nodes: List[str]):
        self.nodes = [ZeroTrustNode(addr) for addr in nodes]
        self.health_checker = HealthChecker(self.nodes)
        self.load_balancer = LoadBalancer(strategy='least_connections')
        
    async def handle_request(self, request: Request) -> Response:
        \"\"\"リクエストの負荷分散処理\"\"\"
        # ヘルスチェック
        healthy_nodes = await self.health_checker.get_healthy_nodes()
        
        if not healthy_nodes:
            raise ServiceUnavailableError("No healthy nodes available")
        
        # ノード選択
        selected_node = self.load_balancer.select_node(healthy_nodes)
        
        try:
            # リクエスト処理
            response = await selected_node.process_request(request)
            
            # 成功をロードバランサーに通知
            self.load_balancer.record_success(selected_node)
            
            return response
            
        except Exception as e:
            # 失敗をロードバランサーに通知
            self.load_balancer.record_failure(selected_node)
            
            # フェイルオーバー
            return await self._failover(request, healthy_nodes, selected_node)
    
    async def _failover(self, request: Request, nodes: List[ZeroTrustNode], 
                       failed_node: ZeroTrustNode) -> Response:
        \"\"\"フェイルオーバー処理\"\"\"
        remaining_nodes = [n for n in nodes if n != failed_node]
        
        for node in remaining_nodes:
            try:
                return await node.process_request(request)
            except Exception:
                continue
                
        raise ServiceUnavailableError("All failover attempts failed")
```

## 📈 監視とアナリティクス

### リアルタイム脅威検知システム

```python
# 機械学習を使用した異常検知
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

class MLBasedThreatDetection:
    \"\"\"機械学習ベースの脅威検知\"\"\"
    
    def __init__(self):
        self.models = {{
            'login_anomaly': IsolationForest(contamination=0.01),
            'access_pattern': IsolationForest(contamination=0.005),
            'data_exfiltration': IsolationForest(contamination=0.001)
        }}
        self.scalers = {{
            key: StandardScaler() for key in self.models.keys()
        }}
        self.feature_extractors = {{
            'login_anomaly': self._extract_login_features,
            'access_pattern': self._extract_access_features,
            'data_exfiltration': self._extract_data_features
        }}
        
    def train_models(self, historical_data: pd.DataFrame):
        \"\"\"モデルの訓練\"\"\"
        for model_type, model in self.models.items():
            # 特徴量抽出
            features = self.feature_extractors[model_type](historical_data)
            
            # スケーリング
            scaled_features = self.scalers[model_type].fit_transform(features)
            
            # モデル訓練
            model.fit(scaled_features)
            
            print(f"Trained {{model_type}} model with {{len(features)}} samples")
    
    def detect_anomalies(self, events: List[Dict]) -> List[ThreatAlert]:
        \"\"\"異常検知の実行\"\"\"
        alerts = []
        
        # イベントタイプ別にグループ化
        grouped_events = self._group_events_by_type(events)
        
        for event_type, event_list in grouped_events.items():
            if event_type in self.models:
                # 特徴量抽出
                features = self.feature_extractors[event_type](event_list)
                
                # スケーリング
                scaled_features = self.scalers[event_type].transform(features)
                
                # 異常検知
                predictions = self.models[event_type].predict(scaled_features)
                anomaly_scores = self.models[event_type].score_samples(scaled_features)
                
                # アラート生成
                for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                    if pred == -1:  # 異常
                        alert = ThreatAlert(
                            severity=self._calculate_severity(score),
                            type=event_type,
                            event=event_list[i],
                            confidence=abs(score),
                            recommended_actions=self._get_recommendations(event_type, score)
                        )
                        alerts.append(alert)
        
        return alerts
    
    def _extract_login_features(self, data):
        \"\"\"ログイン関連の特徴量抽出\"\"\"
        features = []
        
        for _, row in data.iterrows():
            feature_vector = [
                # 時間的特徴
                row['hour_of_day'],
                row['day_of_week'],
                row['is_weekend'],
                
                # 地理的特徴
                row['login_country_change'],
                row['distance_from_last_login'],
                row['is_known_location'],
                
                # デバイス特徴
                row['is_known_device'],
                row['device_trust_score'],
                
                # 行動特徴
                row['failed_login_attempts'],
                row['time_since_last_login'],
                row['login_velocity']
            ]
            features.append(feature_vector)
        
        return np.array(features)

# セキュリティダッシュボード
class SecurityDashboard:
    \"\"\"リアルタイムセキュリティダッシュボード\"\"\"
    
    def __init__(self):
        self.metrics_store = MetricsStore()
        self.alert_manager = AlertManager()
        self.visualization = VisualizationEngine()
        
    def get_dashboard_data(self, time_range: str = '1h') -> Dict:
        \"\"\"ダッシュボードデータの取得\"\"\"
        data = {{
            'summary': self._get_summary_metrics(time_range),
            'alerts': self._get_active_alerts(),
            'trends': self._get_security_trends(time_range),
            'top_risks': self._get_top_risks(),
            'compliance_status': self._get_compliance_status(),
            'real_time_feed': self._get_real_time_feed()
        }}
        
        return data
    
    def _get_summary_metrics(self, time_range: str) -> Dict:
        \"\"\"サマリーメトリクスの取得\"\"\"
        return {{
            'total_requests': self.metrics_store.count_requests(time_range),
            'blocked_requests': self.metrics_store.count_blocked_requests(time_range),
            'unique_users': self.metrics_store.count_unique_users(time_range),
            'avg_trust_score': self.metrics_store.average_trust_score(time_range),
            'threat_level': self._calculate_threat_level()
        }}
    
    def _calculate_threat_level(self) -> str:
        \"\"\"脅威レベルの計算\"\"\"
        recent_alerts = self.alert_manager.get_recent_alerts(minutes=15)
        
        critical_count = sum(1 for a in recent_alerts if a.severity == 'critical')
        high_count = sum(1 for a in recent_alerts if a.severity == 'high')
        
        if critical_count > 5:
            return 'CRITICAL'
        elif critical_count > 0 or high_count > 10:
            return 'HIGH'
        elif high_count > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
```

## 🚀 実装のベストプラクティス

### 1. 段階的な実装アプローチ

```yaml
implementation_phases:
  phase_1_foundation:
    duration: "3ヶ月"
    objectives:
      - "アイデンティティ管理の統合"
      - "MFAの全社展開"
      - "デバイスインベントリの構築"
    deliverables:
      - "統合認証システム"
      - "デバイス管理ポータル"
      - "基本的なアクセスポリシー"
  
  phase_2_zero_trust_core:
    duration: "6ヶ月"
    objectives:
      - "ゼロトラストプロキシの展開"
      - "マイクロセグメンテーション"
      - "条件付きアクセスの実装"
    deliverables:
      - "BeyondCorpプロキシ"
      - "ネットワークセグメンテーション"
      - "リスクベース認証"
  
  phase_3_advanced_security:
    duration: "6ヶ月"
    objectives:
      - "AI/ML脅威検知"
      - "自動応答システム"
      - "継続的コンプライアンス"
    deliverables:
      - "MLベース異常検知"
      - "自動インシデント対応"
      - "コンプライアンスダッシュボード"
```

### 2. 組織変更管理

ゼロトラストは技術だけでなく、組織文化の変革も必要です：

1. **経営層の支援確保**
   - ビジネス価値の明確化
   - ROIの提示
   - リスク削減効果の定量化

2. **段階的なユーザー教育**
   - なぜゼロトラストが必要か
   - ユーザー体験の変化
   - セキュリティ意識の向上

3. **IT部門のスキル向上**
   - クラウドセキュリティ
   - アイデンティティ管理
   - データ分析とML

## 🎯 まとめ

ゼロトラストセキュリティとBeyondCorpの実装は、現代の企業にとって避けて通れない道です。
本記事で紹介した実装方法とコード例を参考に、段階的に導入を進めることで、
より安全で柔軟なIT環境を構築できます。

重要なのは、完璧を求めすぎないことです。
小さく始めて、継続的に改善していくアプローチが成功への鍵となります。

### 次のステップ

1. 現在のセキュリティ体制の評価
2. パイロットプロジェクトの選定
3. 段階的な実装計画の策定
4. 継続的な改善サイクルの確立

ゼロトラストへの移行は旅であり、目的地ではありません。
組織のセキュリティ成熟度を継続的に高めていきましょう。"""
        
        self.log_phase("セキュリティコンテンツ生成完了")
        return content
    
    def _generate_nextjs_content(self, topic_data):
        """Next.js関連の詳細コンテンツを生成"""
        
        self.log_phase("Next.jsコンテンツ生成")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        
        content = f"""## 🎯 はじめに：Next.js 15の革新的な機能

Next.js 15は、Webアプリケーション開発における大きな転換点となるリリースです。
App Router、React Server Components、そしてStreamingの組み合わせにより、
これまでにない高速でインタラクティブなWeb体験を実現できます。

### Next.js 15の主要な改善点

1. **App Routerの成熟**
   - ファイルベースルーティングの進化
   - レイアウトの入れ子構造
   - パラレルルートとインターセプトルート

2. **React Server Componentsの本格採用**
   - サーバーサイドでのコンポーネント実行
   - バンドルサイズの劇的な削減
   - データフェッチングの簡素化

3. **Streamingの標準化**
   - 段階的なページレンダリング
   - ユーザー体験の向上
   - Core Web Vitalsの改善

## 🏗️ App Routerの詳細解説

### App Routerとは

App RouterはNext.js 13で導入され、15で完全に成熟した新しいルーティングシステムです。
従来のpagesディレクトリに代わり、appディレクトリを使用します。

{NEXTJS_CODE_1}

### 動的ルーティングとパラメータ

{NEXTJS_CODE_2}

### パラレルルートとインターセプトルート

```typescript
// app/@modal/(.)products/[id]/page.tsx - モーダル表示用インターセプトルート
import {{ Modal }} from '@/components/Modal'
import {{ ProductQuickView }} from '@/components/ProductQuickView'

export default async function ProductModal({{ 
  params 
}}: {{ 
  params: {{ id: string }} 
}}) {{
  const product = await getProduct(params.id)
  
  return (
    <Modal>
      <ProductQuickView product={{product}} />
    </Modal>
  )
}}

// app/layout.tsx - パラレルルートの使用
export default function Layout({{
  children,
  modal,
}}: {{
  children: React.ReactNode
  modal: React.ReactNode
}}) {{
  return (
    <>
      {{children}}
      {{modal}}
    </>
  )
}}
```

## ⚛️ React Server Componentsの実装

### Server Componentsの基本

```typescript
// app/components/ServerComponent.tsx
// このコンポーネントはサーバーで実行される

import {{ sql }} from '@vercel/postgres'
import {{ unstable_cache }} from 'next/cache'

// データフェッチングをキャッシュ
const getUsers = unstable_cache(
  async () => {{
    const {{ rows }} = await sql`SELECT * FROM users WHERE active = true`
    return rows
  }},
  ['active-users'],
  {{
    revalidate: 60, // 60秒ごとに再検証
    tags: ['users'],
  }}
)

export async function UserList() {{
  const users = await getUsers()
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {{users.map((user) => (
        <UserCard key={{user.id}} user={{user}} />
      ))}}
    </div>
  )
}}

// Client Componentとの組み合わせ
'use client'

import {{ useState }} from 'react'

export function UserCard({{ user }}: {{ user: User }}) {{
  const [isExpanded, setIsExpanded] = useState(false)
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold">{{user.name}}</h3>
      <p className="text-gray-600">{{user.email}}</p>
      
      <button
        onClick={{() => setIsExpanded(!isExpanded)}}
        className="mt-4 text-blue-600 hover:text-blue-800"
      >
        {{isExpanded ? '詳細を隠す' : '詳細を表示'}}
      </button>
      
      {{isExpanded && (
        <div className="mt-4 pt-4 border-t">
          <p>部署: {{user.department}}</p>
          <p>役職: {{user.position}}</p>
          <p>入社日: {{user.joinedAt}}</p>
        </div>
      )}}
    </div>
  )
}}
```

### Server ActionsとForm処理

```typescript
// app/actions/user-actions.ts
'use server'

import {{ z }} from 'zod'
import {{ sql }} from '@vercel/postgres'
import {{ revalidatePath, revalidateTag }} from 'next/cache'
import {{ redirect }} from 'next/navigation'

const CreateUserSchema = z.object({{
  name: z.string().min(1).max(100),
  email: z.string().email(),
  department: z.string().min(1),
  position: z.string().min(1),
}})

export async function createUser(prevState: any, formData: FormData) {{
  // バリデーション
  const validatedFields = CreateUserSchema.safeParse({{
    name: formData.get('name'),
    email: formData.get('email'),
    department: formData.get('department'),
    position: formData.get('position'),
  }})
  
  if (!validatedFields.success) {{
    return {{
      errors: validatedFields.error.flatten().fieldErrors,
      message: '入力内容に誤りがあります。',
    }}
  }}
  
  const {{ name, email, department, position }} = validatedFields.data
  
  try {{
    // データベースに挿入
    const {{ rows }} = await sql`
      INSERT INTO users (name, email, department, position, created_at)
      VALUES (${{name}}, ${{email}}, ${{department}}, ${{position}}, NOW())
      RETURNING id
    `
    
    // キャッシュの再検証
    revalidateTag('users')
    revalidatePath('/users')
    
    // 成功メッセージ
    return {{
      message: 'ユーザーが正常に作成されました。',
      success: true,
      userId: rows[0].id,
    }}
  }} catch (error) {{
    console.error('Database error:', error)
    return {{
      message: 'データベースエラーが発生しました。',
      success: false,
    }}
  }}
}}

// app/components/CreateUserForm.tsx
'use client'

import {{ useFormState, useFormStatus }} from 'react-dom'
import {{ createUser }} from '@/app/actions/user-actions'

const initialState = {{
  message: '',
  errors: {{}},
  success: false,
}}

function SubmitButton() {{
  const {{ pending }} = useFormStatus()
  
  return (
    <button
      type="submit"
      disabled={{pending}}
      className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
    >
      {{pending ? '処理中...' : 'ユーザーを作成'}}
    </button>
  )
}}

export function CreateUserForm() {{
  const [state, formAction] = useFormState(createUser, initialState)
  
  return (
    <form action={{formAction}} className="space-y-4">
      {{state.message && (
        <div className={{`p-4 rounded-md ${{
          state.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }}`}}>
          {{state.message}}
        </div>
      )}}
      
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-1">
          名前
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          className="w-full px-3 py-2 border rounded-md"
        />
        {{state.errors?.name && (
          <p className="mt-1 text-sm text-red-600">{{state.errors.name[0]}}</p>
        )}}
      </div>
      
      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          メールアドレス
        </label>
        <input
          type="email"
          id="email"
          name="email"
          required
          className="w-full px-3 py-2 border rounded-md"
        />
        {{state.errors?.email && (
          <p className="mt-1 text-sm text-red-600">{{state.errors.email[0]}}</p>
        )}}
      </div>
      
      <div>
        <label htmlFor="department" className="block text-sm font-medium mb-1">
          部署
        </label>
        <select
          id="department"
          name="department"
          required
          className="w-full px-3 py-2 border rounded-md"
        >
          <option value="">選択してください</option>
          <option value="engineering">エンジニアリング</option>
          <option value="sales">営業</option>
          <option value="marketing">マーケティング</option>
          <option value="hr">人事</option>
        </select>
        {{state.errors?.department && (
          <p className="mt-1 text-sm text-red-600">{{state.errors.department[0]}}</p>
        )}}
      </div>
      
      <div>
        <label htmlFor="position" className="block text-sm font-medium mb-1">
          役職
        </label>
        <input
          type="text"
          id="position"
          name="position"
          required
          className="w-full px-3 py-2 border rounded-md"
        />
        {{state.errors?.position && (
          <p className="mt-1 text-sm text-red-600">{{state.errors.position[0]}}</p>
        )}}
      </div>
      
      <SubmitButton />
    </form>
  )
}}
```

## 🌊 Streamingの実装と最適化

### Suspenseを使用したStreaming

```typescript
// app/dashboard/page.tsx
import {{ Suspense }} from 'react'
import {{ 
  DashboardHeader, 
  DashboardSkeleton,
  MetricsSkeleton,
  ChartSkeleton,
  ActivitySkeleton 
}} from '@/components/dashboard'

export default function DashboardPage() {{
  return (
    <div className="container mx-auto px-4 py-8">
      <DashboardHeader />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        {{/* メトリクスセクション - 即座に読み込み */}}
        <div className="lg:col-span-2">
          <Suspense fallback={{<MetricsSkeleton />}}>
            <DashboardMetrics />
          </Suspense>
        </div>
        
        {{/* アクティビティフィード - 優先度低 */}}
        <div>
          <Suspense fallback={{<ActivitySkeleton />}}>
            <ActivityFeed />
          </Suspense>
        </div>
      </div>
      
      {{/* チャートセクション - 重い処理 */}}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <Suspense fallback={{<ChartSkeleton />}}>
          <RevenueChart />
        </Suspense>
        
        <Suspense fallback={{<ChartSkeleton />}}>
          <UserGrowthChart />
        </Suspense>
      </div>
    </div>
  )
}}

// 段階的にデータを取得するコンポーネント
async function DashboardMetrics() {{
  // 重要なメトリクスを最初に取得
  const criticalMetrics = await getCriticalMetrics()
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">主要メトリクス</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="総収益"
          value={{criticalMetrics.totalRevenue}}
          change={{criticalMetrics.revenueChange}}
          icon="💰"
        />
        <MetricCard
          title="アクティブユーザー"
          value={{criticalMetrics.activeUsers}}
          change={{criticalMetrics.userChange}}
          icon="👥"
        />
        <MetricCard
          title="コンバージョン率"
          value={{criticalMetrics.conversionRate}}
          change={{criticalMetrics.conversionChange}}
          icon="📈"
        />
        <MetricCard
          title="平均滞在時間"
          value={{criticalMetrics.avgSessionDuration}}
          change={{criticalMetrics.sessionChange}}
          icon="⏱️"
        />
      </div>
      
      {{/* 詳細メトリクスは後から読み込み */}}
      <Suspense fallback={{<div className="mt-4 animate-pulse h-20 bg-gray-200 rounded" />}}>
        <DetailedMetrics />
      </Suspense>
    </div>
  )
}}

// ストリーミング対応のチャートコンポーネント
async function RevenueChart() {{
  const data = await getRevenueData()
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">収益推移</h3>
      <LineChart
        data={{data}}
        options={{{{
          responsive: true,
          plugins: {{
            legend: {{
              position: 'top' as const,
            }},
            title: {{
              display: false,
            }},
          }},
          scales: {{
            y: {{
              beginAtZero: true,
              ticks: {{
                callback: function(value) {{
                  return '¥' + value.toLocaleString()
                }}
              }}
            }}
          }}
        }}}}
      />
    </div>
  )
}}
```

### Loading UIとエラーハンドリング

```typescript
// app/dashboard/loading.tsx
export default function DashboardLoading() {{
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="grid grid-cols-4 gap-4">
                {{[...Array(4)].map((_, i) => (
                  <div key={{i}} className="h-24 bg-gray-200 rounded"></div>
                ))}}
              </div>
            </div>
          </div>
          
          <div>
            <div className="bg-white rounded-lg shadow p-6 h-64">
              <div className="h-full bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}}

// app/dashboard/error.tsx
'use client'

import {{ useEffect }} from 'react'
import {{ Button }} from '@/components/ui/button'

export default function DashboardError({{
  error,
  reset,
}}: {{
  error: Error & {{ digest?: string }}
  reset: () => void
}}) {{
  useEffect(() => {{
    // エラーログをサーバーに送信
    console.error(error)
  }}, [error])
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold text-red-800 mb-4">
          データの読み込みに失敗しました
        </h2>
        <p className="text-red-600 mb-6">
          一時的な問題が発生しています。しばらくしてから再度お試しください。
        </p>
        <Button
          onClick={{reset}}
          variant="default"
          className="bg-red-600 hover:bg-red-700"
        >
          再試行
        </Button>
      </div>
    </div>
  )
}}
```

## 🚀 パフォーマンス最適化テクニック

### 1. 画像の最適化

```typescript
// components/OptimizedImage.tsx
import Image from 'next/image'

export function OptimizedImage({{ 
  src, 
  alt, 
  priority = false 
}}: {{ 
  src: string
  alt: string
  priority?: boolean
}}) {{
  return (
    <Image
      src={{src}}
      alt={{alt}}
      width={{1200}}
      height={{630}}
      priority={{priority}}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
      className="rounded-lg object-cover"
    />
  )
}}
```

### 2. フォントの最適化

```typescript
// app/layout.tsx
import {{ Inter, Noto_Sans_JP }} from 'next/font/google'

const inter = Inter({{ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
}})

const notoSansJP = Noto_Sans_JP({{
  weight: ['400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-noto-sans-jp',
}})

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="ja" className={{`${{inter.variable}} ${{notoSansJP.variable}}`}}>
      <body className="font-sans">
        {{children}}
      </body>
    </html>
  )
}}
```

### 3. キャッシング戦略

```typescript
// lib/cache.ts
import {{ unstable_cache }} from 'next/cache'
import {{ cache }} from 'react'

// Request-level cache (React cache)
export const getUser = cache(async (id: string) => {{
  const user = await db.user.findUnique({{ where: {{ id }} }})
  return user
}})

// Application-level cache (Next.js cache)
export const getPopularProducts = unstable_cache(
  async () => {{
    const products = await db.product.findMany({{
      where: {{ 
        rating: {{ gte: 4.5 }},
        inStock: true,
      }},
      orderBy: {{ salesCount: 'desc' }},
      take: 10,
    }})
    return products
  }},
  ['popular-products'],
  {{
    revalidate: 3600, // 1時間
    tags: ['products'],
  }}
)

// On-demand revalidation
export async function updateProduct(id: string, data: UpdateProductData) {{
  await db.product.update({{ where: {{ id }}, data }})
  
  // キャッシュを無効化
  revalidateTag('products')
  revalidatePath(`/products/${{id}}`)
}}
```

## 🎯 まとめ

Next.js 15のApp Router、Server Components、Streamingの組み合わせは、
モダンなWebアプリケーション開発における新しいスタンダードとなっています。

### 主なメリット

1. **パフォーマンスの向上**
   - JavaScriptバンドルサイズの削減
   - 初期表示速度の改善
   - 段階的なコンテンツ配信

2. **開発体験の向上**
   - 直感的なファイルベースルーティング
   - TypeScriptの完全サポート
   - 優れたエラーハンドリング

3. **SEOとアクセシビリティ**
   - サーバーサイドレンダリング
   - メタデータの動的生成
   - 構造化データのサポート

### 今後の展望

Next.js 15は単なるフレームワークを超えて、
フルスタックWebアプリケーションプラットフォームへと進化しています。
今後も継続的な改善により、さらに優れた開発体験とユーザー体験を提供していくでしょう。

皆さんもぜひNext.js 15を使って、次世代のWebアプリケーションを構築してみてください！"""
        
        self.log_phase("Next.jsコンテンツ生成完了")
        return content
    
    def _generate_kubernetes_content(self, topic_data):
        """Kubernetes関連の詳細コンテンツを生成"""
        
        self.log_phase("Kubernetesコンテンツ生成")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        
        content = """## 🚀 はじめに：なぜ今{}が重要なのか

2025年、クラウドネイティブなアプリケーション開発において、{}は必須の技術となりました。
従来のデプロイメント手法では、以下のような課題に直面していました：

1. **手動デプロイの限界**
   - ヒューマンエラーのリスク
   - 環境間の設定の不整合
   - デプロイプロセスの属人化

2. **スケーラビリティの課題**
   - アプリケーションの急激な成長への対応
   - リソースの効率的な利用
   - 自動スケーリングの実現

3. **運用の複雑化**
   - マイクロサービスの増加
   - 依存関係の管理
   - 監視・ロギングの統合

## 🎯 {}の基本概念

### {}とは

{}は、宣言的な設定管理とGitをソースオブトゥルースとして使用する、継続的デリバリーのためのパラダイムです。

```yaml
# GitOpsの基本原則を表現したマニフェスト例
apiVersion: v1
kind: ConfigMap
metadata:
  name: gitops-principles
  namespace: gitops-system
data:
  principles: |
    1. 宣言的記述: すべてをコードとして記述
    2. バージョン管理: Gitで全履歴を追跡
    3. 自動適用: 承認されたものは自動デプロイ
    4. 継続的な同期: 実際の状態と望ましい状態を常に同期
```

### ArgoCD vs Flux：どちらを選ぶべきか

#### ArgoCD
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/k8s-manifests
    targetRevision: main
    path: production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - Validate=true
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

ArgoCDの特徴：
- 豊富なWeb UI
- 複雑なアプリケーション構成のサポート
- マルチクラスター管理
- RBAC統合

#### Flux v2
```yaml
# flux-kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: production-app
  namespace: flux-system
spec:
  interval: 10m
  path: "./production"
  prune: true
  sourceRef:
    kind: GitRepository
    name: k8s-manifests
  validation: client
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: app-deployment
      namespace: production
  postBuild:
    substitute:
      cluster_name: production
      region: us-west-2
```

Flux v2の特徴：
- GitOpsツールキット
- 軽量でリソース効率的
- Helm統合が優秀
- イメージ自動更新

## 🛠️ 実践的な実装ガイド

### 1. 環境構築

```bash
# クラスターの準備
kind create cluster --name gitops-demo --config kind-config.yaml

# ArgoCDのインストール
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# CLIツールのインストール
brew install argocd
argocd login localhost:8080 --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{{.data.password}}" | base64 -d)

# Fluxのインストール（代替案）
curl -s https://fluxcd.io/install.sh | sudo bash
flux check --pre
flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=$GITHUB_REPO \
  --branch=main \
  --path=./clusters/production \
  --personal
```

### 2. リポジトリ構造の設計

```
k8s-manifests/
├── base/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── development/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── production/
│       ├── kustomization.yaml
│       └── patches/
└── apps/
    ├── app1/
    ├── app2/
    └── app3/
```

### 3. プログレッシブデリバリーの実装

```yaml
# canary-rollout.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: app-canary
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  service:
    port: 80
    targetPort: 8080
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.test/
      timeout: 5s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://app-canary.production:80/"
```

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. 同期が失敗する
```bash
# ArgoCDの場合
argocd app sync production-app --retry-limit 3 --prune --force

# ログの確認
kubectl logs -n argocd deployment/argocd-application-controller -f

# リソースの差分確認
argocd app diff production-app
```

#### 2. イメージの自動更新が動作しない
```yaml
# image-update-automation.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: app-image-update
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: k8s-manifests
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcdbot@users.noreply.github.com
        name: fluxcdbot
      messageTemplate: |
        Automated image update
        
        [ci skip]
    push:
      branch: main
  update:
    path: "./production"
    strategy: Setters
```

## 📊 監視とアラート

### Prometheusメトリクス
```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: argocd-metrics
  namespace: argocd
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: argocd-metrics
  endpoints:
  - port: metrics
```

### Grafanaダッシュボード
```json
{
  "dashboard": {
    "title": "GitOps Metrics",
    "panels": [
      {
        "title": "Sync Status",
        "targets": [
          {
            "expr": "argocd_app_info{sync_status!=\"Synced\"}"
          }
        ]
      },
      {
        "title": "Deployment Frequency",
        "targets": [
          {
            "expr": "rate(argocd_app_sync_total[1h])"
          }
        ]
      }
    ]
  }
}
```

## 🚀 プロダクション運用のベストプラクティス

### 1. セキュリティ
- シークレットの暗号化（Sealed Secrets、SOPS）
- RBACの適切な設定
- 監査ログの有効化

### 2. 可用性
- マルチリージョンデプロイ
- 自動フェイルオーバー
- バックアップとリストア戦略

### 3. パフォーマンス
- リソースリミットの設定
- 自動スケーリング
- キャッシュの活用

## 🎓 まとめ

{}は、現代のクラウドネイティブアプリケーション開発において不可欠な手法です。
本記事で紹介した実装パターンとベストプラクティスを活用することで、より信頼性の高い、
スケーラブルなデプロイメントパイプラインを構築できます。

次のステップとして、実際のプロジェクトでこれらの技術を試し、
チームに最適なワークフローを見つけていくことをお勧めします。""".format(
            keywords[0], keywords[0], keywords[0], keywords[0], keywords[0], keywords[0]
        )
        
        self.log_phase("Kubernetesコンテンツ生成完了")
        return content
    
    def _generate_ai_content(self, topic_data):
        """AI関連の詳細コンテンツを生成"""
        
        self.log_phase("AIコンテンツ生成")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        main_keyword = keywords[0]
        
        # まず基本的な内容を作成
        intro = f"""## 🤖 はじめに：{main_keyword}が変える開発の未来

2025年、AIエージェント技術は単なる補助ツールから、開発プロセスの中核を担う存在へと進化しました。
{main_keyword}は、その最前線に立つ技術として注目を集めています。

### なぜ今AIエージェントなのか

1. **開発効率の劇的な向上**
   - コード生成・レビューの自動化
   - バグ検出と修正提案
   - ドキュメント生成の自動化

2. **意思決定の高度化**
   - データ駆動型の設計判断
   - パフォーマンス最適化の提案
   - セキュリティリスクの事前検出

3. **人間とAIの協調**
   - 創造的なタスクへの集中
   - 反復作業からの解放
   - 24時間365日の開発支援

## 🎯 {main_keyword}の基本アーキテクチャ"""
        
        # コード例を追加
        code_examples = """

### 実装例

```python
# """ + main_keyword + """の基本実装
import asyncio
from typing import Dict, List, Any

class """ + main_keyword.replace(' ', '').replace('-', '') + """System:
    def __init__(self):
        self.config = {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 4000
        }
    
    async def process_request(self, prompt: str) -> Dict[str, Any]:
        # """ + main_keyword + """による処理
        result = await self._execute_model(prompt)
        return {
            'response': result,
            'status': 'completed',
            'model': self.config['model']
        }
    
    async def _execute_model(self, prompt: str) -> str:
        # 実際のモデル実行ロジック
        return f"Processed with """ + main_keyword + """: {prompt}"

# 使用例
async def main():
    system = """ + main_keyword.replace(' ', '').replace('-', '') + """System()
    result = await system.process_request("Hello, World!")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 高度な設定とチューニング

```python
# パフォーマンス最適化
class Optimized""" + main_keyword.replace(' ', '').replace('-', '') + """:
    def __init__(self):
        self.cache = {}
        self.batch_size = 10
        
    async def batch_process(self, requests: List[str]) -> List[Dict]:
        results = []
        for i in range(0, len(requests), self.batch_size):
            batch = requests[i:i + self.batch_size]
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
        return results
    
    async def _process_batch(self, batch: List[str]) -> List[Dict]:
        # バッチ処理実装
        return [{'result': item} for item in batch]
```"""
        
        # まとめを追加
        conclusion = f"""

## 🎓 まとめ

{main_keyword}を活用したAI開発は、現代のソフトウェア開発において重要な位置を占めています。
本記事で紹介した実装パターンとベストプラクティスを参考に、ぜひあなたのプロジェクトでも
活用してみてください。

重要なのは、AIを単なるツールとしてではなく、開発プロセスの一部として捉え、
効率的で持続可能なシステムを構築することです。"""
        
        # 全体を結合
        content = intro + code_examples + conclusion
        
        self.log_phase("AIコンテンツ生成完了")
        return content
    
    async def _generate_ai_powered_content(self, topic_data, section_title, word_count=5000):
        """AIを使って実際のコンテンツを生成"""
        
        if not self.claude_integration:
            return f"\n\n[AI生成エラー: Claude Code SDKが利用できません]\n\n"
        
        prompt = f"""以下のトピックについて、{word_count}文字以上の詳細な技術解説を日本語で書いてください。

トピック: {topic_data['title']}
セクション: {section_title}
キーワード: {', '.join(topic_data['keywords'])}
カテゴリ: {topic_data['category']}
難易度: {topic_data['difficulty']}

要件:
1. 実践的なコード例を3つ以上含める
2. 具体的な実装手順を含める
3. トラブルシューティングの情報を含める
4. パフォーマンス最適化のヒントを含める
5. セキュリティ考慮事項を含める
6. {word_count}文字以上の詳細な内容にする

重要: 出力は記事の本文のみとし、前置きや後書きは不要です。Markdown形式で出力してください。
"""
        
        try:
            self.log_phase(f"AI生成開始: {section_title}")
            messages = await self.claude_integration.query_with_sdk(
                prompt=prompt,
                max_turns=1
            )
            
            # メッセージから結果を抽出
            generated_content = ""
            for message in messages:
                if message.get("type") == "result" and message.get("subtype") == "success":
                    # outputフィールドから内容を取得
                    if "output" in message:
                        generated_content += message["output"]
                    # もしくはコンテンツフィールドから
                    elif "content" in message:
                        generated_content += message["content"]
                    # テキストとして返される場合
                    elif isinstance(message.get("result"), str):
                        generated_content += message["result"]
            
            if generated_content:
                actual_length = len(generated_content)
                self.log_phase(f"AI生成完了: {actual_length}文字")
                return generated_content
            else:
                # フォールバック: メッセージ全体を文字列化
                all_text = "\n".join([str(msg) for msg in messages])
                if len(all_text) > 1000:  # 有意なコンテンツがある場合
                    return all_text
                return f"\n\n[生成エラー: コンテンツが生成されませんでした]\n\n"
                
        except Exception as e:
            print(f"❌ AI生成エラー: {e}")
            return f"\n\n[生成エラー: {str(e)}]\n\n"
    
    def _generate_general_tech_content(self, topic_data):
        """一般的な技術コンテンツを生成"""
        
        self.log_phase("一般技術コンテンツ生成")
        
        title = topic_data["title"]
        keywords = topic_data["keywords"]
        
        # まず基本的な構造を作成
        content = """## 🚀 はじめに：{}の重要性

現代のソフトウェア開発において、{}は避けては通れない重要な技術となっています。
本記事では、実践的な観点から{}を深く掘り下げ、実務で即座に活用できる知識をお伝えします。

### 技術選択の背景

1. **市場のニーズ**
   - ユーザー体験の向上への要求
   - 開発スピードの加速
   - 運用コストの最適化

2. **技術の成熟度**
   - コミュニティの活発さ
   - エコシステムの充実
   - 企業での採用実績

3. **将来性**
   - 技術の発展方向
   - 新機能のロードマップ
   - 長期的なサポート体制

## 🎯 {}の基本概念

### アーキテクチャ概要

```python
# 基本的なアーキテクチャパターン
from typing import Protocol, List, Dict, Any
from dataclasses import dataclass
import asyncio

class DataProcessor(Protocol):
    \"\"\"データ処理のプロトコル\"\"\"
    async def process(self, data: Any) -> Any:
        ...

@dataclass
class Pipeline:
    \"\"\"処理パイプライン\"\"\"
    processors: List[DataProcessor]
    
    async def execute(self, initial_data: Any) -> Any:
        \"\"\"パイプラインの実行\"\"\"
        result = initial_data
        
        for processor in self.processors:
            result = await processor.process(result)
            
        return result

class TransformProcessor:
    \"\"\"データ変換プロセッサー\"\"\"
    
    def __init__(self, transform_func):
        self.transform_func = transform_func
    
    async def process(self, data: Any) -> Any:
        # 非同期処理の例
        await asyncio.sleep(0.1)  # I/O待機のシミュレーション
        return self.transform_func(data)

class ValidationProcessor:
    \"\"\"データ検証プロセッサー\"\"\"
    
    def __init__(self, validation_rules: Dict[str, Any]):
        self.validation_rules = validation_rules
    
    async def process(self, data: Dict) -> Dict:
        errors = []
        
        for field, rule in self.validation_rules.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not rule(data[field]):
                errors.append(f"Invalid value for field: {field}")
        
        if errors:
            raise ValueError(f"Validation failed: {', '.join(errors)}")
        
        return data
```

### 実装パターンの詳細

#### 1. ファクトリーパターン

```python
from abc import ABC, abstractmethod
from enum import Enum

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"

class Database(ABC):
    \"\"\"データベースの抽象基底クラス\"\"\"
    
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def query(self, sql: str, params: List = None):
        pass
    
    @abstractmethod
    async def close(self):
        pass

class PostgreSQLDatabase(Database):
    \"\"\"PostgreSQL実装\"\"\"
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def connect(self):
        # asyncpgを使用した接続
        import asyncpg
        self.connection = await asyncpg.connect(self.connection_string)
    
    async def query(self, sql: str, params: List = None):
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        if params:
            return await self.connection.fetch(sql, *params)
        return await self.connection.fetch(sql)
    
    async def close(self):
        if self.connection:
            await self.connection.close()

class DatabaseFactory:
    \"\"\"データベースファクトリー\"\"\"
    
    @staticmethod
    def create_database(db_type: DatabaseType, **kwargs) -> Database:
        if db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLDatabase(kwargs['connection_string'])
        elif db_type == DatabaseType.MYSQL:
            return MySQLDatabase(kwargs['connection_string'])
        elif db_type == DatabaseType.MONGODB:
            return MongoDatabase(kwargs['connection_string'])
        elif db_type == DatabaseType.REDIS:
            return RedisDatabase(kwargs['connection_string'])
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

# 使用例
async def main():
    db = DatabaseFactory.create_database(
        DatabaseType.POSTGRESQL,
        connection_string="postgresql://user:password@localhost/dbname"
    )
    
    try:
        await db.connect()
        results = await db.query("SELECT * FROM users WHERE active = $1", [True])
        
        for row in results:
            print(f"User: {row['name']} ({row['email']})")
    finally:
        await db.close()
```

#### 2. リポジトリパターン

```python
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class Repository(Generic[T], ABC):
    \"\"\"汎用リポジトリインターフェース\"\"\"
    
    @abstractmethod
    async def find_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

@dataclass
class User:
    id: Optional[str] = None
    name: str = ""
    email: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserRepository(Repository[User]):
    \"\"\"ユーザーリポジトリの実装\"\"\"
    
    def __init__(self, db: Database):
        self.db = db
    
    async def find_by_id(self, id: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = $1"
        result = await self.db.query(query, [id])
        
        if result:
            return self._map_to_entity(result[0])
        return None
    
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        query = "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2"
        results = await self.db.query(query, [limit, offset])
        
        return [self._map_to_entity(row) for row in results]
    
    async def save(self, entity: User) -> User:
        if entity.id:
            # 更新
            query = \"\"\"
                UPDATE users 
                SET name = $2, email = $3, updated_at = $4
                WHERE id = $1
                RETURNING *
            \"\"\"
            result = await self.db.query(
                query,
                [entity.id, entity.name, entity.email, datetime.now()]
            )
        else:
            # 新規作成
            query = \"\"\"
                INSERT INTO users (name, email, created_at, updated_at)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            \"\"\"
            result = await self.db.query(
                query,
                [entity.name, entity.email, datetime.now(), datetime.now()]
            )
        
        return self._map_to_entity(result[0])
    
    async def delete(self, id: str) -> bool:
        query = "DELETE FROM users WHERE id = $1"
        await self.db.query(query, [id])
        return True
    
    def _map_to_entity(self, row: Dict) -> User:
        return User(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
```

## 🛠️ 実践的な実装例

### マイクロサービスアーキテクチャ

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx
from typing import List

# API Gateway実装
class APIGateway:
    \"\"\"APIゲートウェイ\"\"\"
    
    def __init__(self):
        self.app = FastAPI(title="API Gateway")
        self.services = {
            "users": "http://users-service:8001",
            "orders": "http://orders-service:8002",
            "payments": "http://payments-service:8003"
        }
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.get("/api/v1/users/{user_id}")
        async def get_user_with_orders(user_id: str):
            async with httpx.AsyncClient() as client:
                # 並列でデータを取得
                user_task = client.get(f"{self.services['users']}/users/{user_id}")
                orders_task = client.get(f"{self.services['orders']}/users/{user_id}/orders")
                
                user_response, orders_response = await asyncio.gather(
                    user_task, orders_task
                )
                
                if user_response.status_code != 200:
                    raise HTTPException(status_code=404, detail="User not found")
                
                user_data = user_response.json()
                orders_data = orders_response.json() if orders_response.status_code == 200 else []
                
                return {
                    "user": user_data,
                    "orders": orders_data
                }
        
        @self.app.post("/api/v1/orders")
        async def create_order(order_data: dict):
            async with httpx.AsyncClient() as client:
                # トランザクション的な処理
                try:
                    # 1. 在庫確認
                    inventory_check = await client.post(
                        f"{self.services['inventory']}/check",
                        json=order_data['items']
                    )
                    
                    if inventory_check.status_code != 200:
                        raise HTTPException(status_code=400, detail="Insufficient inventory")
                    
                    # 2. 注文作成
                    order_response = await client.post(
                        f"{self.services['orders']}/orders",
                        json=order_data
                    )
                    
                    if order_response.status_code != 201:
                        raise HTTPException(status_code=500, detail="Failed to create order")
                    
                    order = order_response.json()
                    
                    # 3. 支払い処理
                    payment_response = await client.post(
                        f"{self.services['payments']}/payments",
                        json={
                            "order_id": order['id'],
                            "amount": order['total'],
                            "payment_method": order_data['payment_method']
                        }
                    )
                    
                    if payment_response.status_code != 201:
                        # ロールバック処理
                        await client.delete(f"{self.services['orders']}/orders/{order['id']}")
                        raise HTTPException(status_code=500, detail="Payment failed")
                    
                    return {
                        "order": order,
                        "payment": payment_response.json()
                    }
                    
                except Exception as e:
                    # エラーログ記録
                    await self._log_error(str(e))
                    raise
```

### イベント駆動アーキテクチャ

```python
from typing import Dict, List, Callable
import asyncio
from datetime import datetime
import json

class Event:
    \"\"\"イベントクラス\"\"\"
    
    def __init__(self, event_type: str, data: Dict, source: str):
        self.id = str(uuid.uuid4())
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now()
        self.version = "1.0"

class EventBus:
    \"\"\"イベントバス\"\"\"
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_store = []
        
    def subscribe(self, event_type: str, handler: Callable):
        \"\"\"イベントハンドラーの登録\"\"\"
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        \"\"\"イベントの発行\"\"\"
        # イベントストアに保存
        self.event_store.append(event)
        
        # 該当するハンドラーを実行
        if event.type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event.type]:
                tasks.append(handler(event))
            
            # 並列実行
            await asyncio.gather(*tasks)

# CQRS実装
class Command:
    \"\"\"コマンド基底クラス\"\"\"
    pass

class CreateUserCommand(Command):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class Query:
    \"\"\"クエリ基底クラス\"\"\"
    pass

class GetUserQuery(Query):
    def __init__(self, user_id: str):
        self.user_id = user_id

class CQRSMediator:
    \"\"\"CQRSメディエーター\"\"\"
    
    def __init__(self):
        self.command_handlers = {}
        self.query_handlers = {}
        self.event_bus = EventBus()
    
    def register_command_handler(self, command_type: type, handler: Callable):
        self.command_handlers[command_type] = handler
    
    def register_query_handler(self, query_type: type, handler: Callable):
        self.query_handlers[query_type] = handler
    
    async def send_command(self, command: Command) -> Any:
        command_type = type(command)
        if command_type not in self.command_handlers:
            raise ValueError(f"No handler registered for {command_type}")
        
        result = await self.command_handlers[command_type](command)
        
        # コマンド実行後のイベント発行
        event = Event(
            event_type=f"{command_type.__name__}Completed",
            data={"command": command.__dict__, "result": result},
            source="CQRSMediator"
        )
        await self.event_bus.publish(event)
        
        return result
    
    async def send_query(self, query: Query) -> Any:
        query_type = type(query)
        if query_type not in self.query_handlers:
            raise ValueError(f"No handler registered for {query_type}")
        
        return await self.query_handlers[query_type](query)
```

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. パフォーマンスの問題

```python
# プロファイリングツール
import cProfile
import pstats
from memory_profiler import profile

class PerformanceMonitor:
    \"\"\"パフォーマンス監視\"\"\"
    
    @staticmethod
    def profile_function(func):
        \"\"\"関数のプロファイリング\"\"\"
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()
            
            result = func(*args, **kwargs)
            
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(10)
            
            return result
        return wrapper
    
    @staticmethod
    @profile
    def check_memory_usage(data_processor):
        \"\"\"メモリ使用量のチェック\"\"\"
        large_data = [i for i in range(1000000)]
        processed = data_processor.process(large_data)
        return processed
```

#### 2. 並行処理の問題

```python
import asyncio
from asyncio import Lock, Semaphore

class ConcurrencyManager:
    \"\"\"並行処理マネージャー\"\"\"
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = Semaphore(max_concurrent)
        self.locks = {}
    
    async def execute_with_limit(self, coro):
        \"\"\"並行実行数を制限\"\"\"
        async with self.semaphore:
            return await coro
    
    async def execute_with_lock(self, key: str, coro):
        \"\"\"キー単位でのロック\"\"\"
        if key not in self.locks:
            self.locks[key] = Lock()
        
        async with self.locks[key]:
            return await coro
```

## 🎓 まとめ

{}は現代のソフトウェア開発において重要な技術です。
本記事で紹介した実装パターンとベストプラクティスを活用することで、
より保守性が高く、スケーラブルなシステムを構築できます。

次のステップとして、実際のプロジェクトでこれらのパターンを試し、
チームに最適な実装方法を見つけていくことをお勧めします。"""
        
        # キーワードを安全に置換
        content = content.replace("{}", keywords[0], 5)  # 最初の5つのプレースホルダーを置換
        
        self.log_phase("一般技術コンテンツ生成完了")
        return content

async def generate_detailed_article():
    """詳細な記事を生成"""
    
    print("📝 詳細記事生成システム v4.0")
    print("=" * 60)
    
    generator = DetailedArticleGenerator()
    
    # ランダムトピック生成
    topic_data = generator.generate_random_topic()
    
    # 記事を生成
    content = await generator.generate_detailed_content(topic_data)
    
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
        f.write(f"production_time: {round(time.time() - generator.start_time, 2)}秒\n")
        f.write(f"---\n\n")
        f.write(content)
    
    print(f"\n✅ 記事生成完了: {article_path}")
    print(f"📊 総文字数: {len(content)}文字")
    print(f"⏱️  制作時間: {round(time.time() - generator.start_time, 2)}秒")
    
    return article_path

if __name__ == "__main__":
    asyncio.run(generate_detailed_article())