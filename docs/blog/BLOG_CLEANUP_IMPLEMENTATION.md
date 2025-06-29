# Alic Blog Cleanup Implementation Summary

## 実装した機能

### 1. 記事の自動クリーンアップ機能
- **最新5記事のみを保持**: 古い記事を自動的に削除
- **Markdownファイルとhtmlファイルの両方を削除**
- **index.htmlの自動更新**: 最新5記事のみを表示

### 2. 日本標準時（JST）の対応
- **タイムゾーン設定**: UTC+9の日本標準時を使用
- **すべての時刻表示にJST表記を追加**
- **GitHub Actionsでも環境変数TZを設定**

### 3. 修正したファイル

#### generate_article.py
- JSTタイムゾーンの追加
- `cleanup_old_articles()`関数の実装
- index.html更新時の時刻累積問題の修正
- 記事生成後の自動クリーンアップ処理

#### convert_articles.py
- 最新5記事のみをHTML変換
- 日付にJST表記を自動追加
- 既存HTMLファイルのクリーンアップ

#### .github/workflows/auto-update.yml
- 環境変数`TZ: 'Asia/Tokyo'`の追加
- コミットメッセージにJST表記を追加

### 4. ユーティリティスクリプト

#### manual_cleanup.py
- 手動で記事をクリーンアップするスクリプト
- 削除前に確認プロンプトを表示
- index.htmlの更新も同時に実行

#### fix_metadata.py
- エスケープされたメタデータを修正
- 既存記事の形式を統一

#### test_cleanup.py
- クリーンアップ機能のテストスクリプト
- バックアップとリストア機能付き

## 動作確認

### ローカルテスト
```bash
# 新しい記事を生成（自動的にクリーンアップも実行）
python generate_article.py

# 手動でクリーンアップを実行
python manual_cleanup.py

# メタデータを修正
python fix_metadata.py
```

### 現在の状態
- **記事数**: 5記事（最新のみ保持）
- **時刻表示**: すべてJST表記
- **index.html**: 最新5記事のみ表示
- **更新時刻**: 累積問題を解決済み

## GitHub Actionsでの動作
- 30分ごとに新記事を生成
- 自動的に古い記事をクリーンアップ
- 常に最新5記事のみを保持
- すべての時刻がJST表記

## 注意事項
- 削除された記事は復元できません
- 特別な記事（travel_*.md, special_*.md）も削除対象になります
- 必要に応じて`keep_count`パラメータを調整可能

## 今後の改善案
1. 重要な記事を保護する仕組み
2. アーカイブ機能の追加
3. 記事の重要度に基づく保持期間の調整