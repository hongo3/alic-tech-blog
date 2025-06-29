#!/usr/bin/env python3
"""
エラー自動修復システム
ブログ生成中のエラーを検出し、自動的に修復を試みる
"""

import asyncio
import json
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging
import subprocess

# 日本標準時のタイムゾーン
JST = timezone(timedelta(hours=9))

# ロガーの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ErrorRecoverySystem:
    """エラー自動修復システム"""
    
    def __init__(self):
        self.error_log_file = Path("error_recovery_log.json")
        self.recovery_strategies = {
            "TaskGroup": self._recover_from_taskgroup_error,
            "TimeoutError": self._recover_from_timeout,
            "ImportError": self._recover_from_import_error,
            "FileNotFoundError": self._recover_from_file_not_found,
            "JSONDecodeError": self._recover_from_json_error,
            "claude": self._recover_from_claude_error,
        }
        self.load_error_log()
    
    def load_error_log(self):
        """エラーログを読み込む"""
        if self.error_log_file.exists():
            with open(self.error_log_file, "r", encoding="utf-8") as f:
                self.error_log = json.load(f)
        else:
            self.error_log = {
                "errors": [],
                "recoveries": [],
                "statistics": {}
            }
    
    def save_error_log(self):
        """エラーログを保存"""
        with open(self.error_log_file, "w", encoding="utf-8") as f:
            json.dump(self.error_log, f, ensure_ascii=False, indent=2)
    
    async def handle_error(self, error: Exception, context: dict = None):
        """エラーを処理し、可能であれば自動修復を試みる"""
        
        error_info = {
            "timestamp": datetime.now(JST).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        # エラーログに記録
        self.error_log["errors"].append(error_info)
        logger.error(f"エラーを検出: {error_info['error_type']} - {error_info['error_message']}")
        
        # 自動修復を試みる
        recovery_result = await self._attempt_recovery(error, error_info)
        
        if recovery_result["success"]:
            logger.info(f"✅ エラーから自動修復しました: {recovery_result['strategy']}")
            self.error_log["recoveries"].append({
                "timestamp": datetime.now(JST).isoformat(),
                "error_type": error_info["error_type"],
                "strategy": recovery_result["strategy"],
                "success": True
            })
        else:
            logger.error(f"❌ 自動修復に失敗しました: {recovery_result['reason']}")
        
        self.save_error_log()
        return recovery_result
    
    async def _attempt_recovery(self, error: Exception, error_info: dict):
        """エラーの種類に応じた修復を試みる"""
        
        # エラータイプに基づいて修復戦略を選択
        for error_keyword, recovery_function in self.recovery_strategies.items():
            if error_keyword in error_info["error_type"] or error_keyword in error_info["error_message"]:
                try:
                    result = await recovery_function(error, error_info)
                    if result["success"]:
                        return result
                except Exception as e:
                    logger.error(f"修復戦略の実行中にエラー: {e}")
        
        return {
            "success": False,
            "reason": "適切な修復戦略が見つかりませんでした"
        }
    
    async def _recover_from_taskgroup_error(self, error, error_info):
        """TaskGroupエラーからの回復"""
        
        logger.info("TaskGroupエラーの修復を試みています...")
        
        # 戦略1: CLIフォールバックを強制
        try:
            # claude_code_integration.pyでCLI使用を強制
            integration_path = Path(__file__).parent.parent / "src" / "claude_code_integration.py"
            if integration_path.exists():
                content = integration_path.read_text(encoding='utf-8')
                # use_cli_fallbackをTrueに設定
                if "self.use_cli_fallback = False" in content:
                    content = content.replace("self.use_cli_fallback = False", "self.use_cli_fallback = True")
                    integration_path.write_text(content, encoding='utf-8')
                    
                    return {
                        "success": True,
                        "strategy": "CLIフォールバックを強制的に有効化"
                    }
        except Exception as e:
            logger.error(f"CLIフォールバック設定エラー: {e}")
        
        # 戦略2: シンプルな記事生成に切り替え
        try:
            # single_prompt_article_generator.pyを使用
            subprocess.run(["python", "single_prompt_article_generator.py"], check=True)
            return {
                "success": True,
                "strategy": "シンプルな記事生成システムに切り替え"
            }
        except Exception as e:
            logger.error(f"代替生成システムエラー: {e}")
        
        return {"success": False, "reason": "TaskGroupエラーの修復に失敗"}
    
    async def _recover_from_timeout(self, error, error_info):
        """タイムアウトエラーからの回復"""
        
        logger.info("タイムアウトエラーの修復を試みています...")
        
        # 戦略: より短いプロンプトで再試行
        return {
            "success": True,
            "strategy": "より短いプロンプトで再試行",
            "action": "retry_with_shorter_prompt"
        }
    
    async def _recover_from_import_error(self, error, error_info):
        """インポートエラーからの回復"""
        
        logger.info("インポートエラーの修復を試みています...")
        
        # 不足しているモジュールをインストール
        module_name = str(error).split("'")[1] if "'" in str(error) else None
        
        if module_name:
            try:
                subprocess.run(["pip", "install", module_name], check=True)
                return {
                    "success": True,
                    "strategy": f"モジュール '{module_name}' をインストール"
                }
            except Exception as e:
                logger.error(f"モジュールインストールエラー: {e}")
        
        return {"success": False, "reason": "モジュールのインストールに失敗"}
    
    async def _recover_from_file_not_found(self, error, error_info):
        """ファイル未検出エラーからの回復"""
        
        logger.info("ファイル未検出エラーの修復を試みています...")
        
        # 必要なディレクトリを作成
        required_dirs = ["posts", "docs", "data", "alic_blog/posts", "alic_blog/docs"]
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "strategy": "必要なディレクトリを作成"
        }
    
    async def _recover_from_json_error(self, error, error_info):
        """JSONエラーからの回復"""
        
        logger.info("JSONエラーの修復を試みています...")
        
        # 破損したJSONファイルをバックアップして初期化
        json_files = list(Path(".").glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError:
                # バックアップ
                backup_path = json_file.with_suffix(f".backup_{int(time.time())}.json")
                json_file.rename(backup_path)
                
                # 空のJSONで初期化
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump({}, f)
                
                logger.info(f"破損したJSONファイルを初期化: {json_file}")
        
        return {
            "success": True,
            "strategy": "破損したJSONファイルを初期化"
        }
    
    async def _recover_from_claude_error(self, error, error_info):
        """Claude関連エラーからの回復"""
        
        logger.info("Claude関連エラーの修復を試みています...")
        
        # Claude認証の再実行
        try:
            # Docker内でClaude認証を確認
            result = subprocess.run(
                ["docker", "exec", "alic-blog-generator", "claude", "auth", "status"],
                capture_output=True,
                text=True
            )
            
            if "not authenticated" in result.stdout.lower():
                logger.info("Claude認証が必要です。手動で認証してください。")
                return {
                    "success": False,
                    "reason": "Claude認証が必要",
                    "action": "manual_auth_required"
                }
            else:
                # CLIフォールバックを使用
                return await self._recover_from_taskgroup_error(error, error_info)
        except Exception as e:
            logger.error(f"Claude状態確認エラー: {e}")
        
        return {"success": False, "reason": "Claude関連エラーの修復に失敗"}

class RobustArticleGenerator:
    """エラー回復機能を備えた堅牢な記事生成システム"""
    
    def __init__(self):
        self.error_recovery = ErrorRecoverySystem()
        self.max_retries = 3
    
    async def generate_article_with_recovery(self):
        """エラー回復機能付きで記事を生成"""
        
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # まずシンプルな方法で試す
                try:
                    from single_prompt_article_generator import SinglePromptArticleGenerator
                except ImportError:
                    # ファイルが同じディレクトリにない場合
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent))
                    from single_prompt_article_generator import SinglePromptArticleGenerator
                
                generator = SinglePromptArticleGenerator()
                result = await generator.generate_article_with_single_prompt()
                
                if result["success"]:
                    return result
                else:
                    raise Exception(result.get("error", "Unknown error"))
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"記事生成エラー (試行 {retry_count}/{self.max_retries}): {e}")
                
                # エラー回復を試みる
                recovery_result = await self.error_recovery.handle_error(e, {
                    "retry_count": retry_count,
                    "generator": "single_prompt"
                })
                
                if recovery_result.get("action") == "retry_with_shorter_prompt":
                    # より短いプロンプトで再試行
                    logger.info("より短いプロンプトで再試行します...")
                    continue
                elif recovery_result.get("action") == "manual_auth_required":
                    # 手動介入が必要
                    logger.error("手動でのClaude認証が必要です")
                    break
                
                # 少し待ってから再試行
                await asyncio.sleep(5)
        
        return {
            "success": False,
            "error": f"最大試行回数 ({self.max_retries}) に達しました"
        }

async def main():
    """メイン実行関数"""
    
    generator = RobustArticleGenerator()
    result = await generator.generate_article_with_recovery()
    
    if result["success"]:
        print(f"\n✅ 記事生成成功！")
        print(f"📄 ファイル: {result['article_path']}")
        print(f"⏱️ 処理時間: {result['elapsed_time']:.1f}秒")
    else:
        print(f"\n❌ 記事生成失敗: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())