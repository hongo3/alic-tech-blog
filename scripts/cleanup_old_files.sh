#!/bin/bash
# 古いバージョンのファイルを整理するスクリプト

echo "🧹 古いファイルの整理を開始します..."

# バックアップディレクトリを作成
mkdir -p old_versions

# 古いバージョンのファイルを移動
echo "📦 古いバージョンのファイルをバックアップ..."

# 記事生成スクリプトの古いバージョン
mv generate_article.py old_versions/ 2>/dev/null
mv generate_article_v2.py old_versions/ 2>/dev/null
mv generate_article_v2.py.bak old_versions/ 2>/dev/null
mv generate_article_enhanced.py old_versions/ 2>/dev/null
mv generate_article_v3.py old_versions/ 2>/dev/null

# 変換スクリプトの古いバージョン
mv convert_articles.py old_versions/ 2>/dev/null
mv convert_articles_v2.py old_versions/ 2>/dev/null

# UI更新スクリプトの古いバージョン
mv update_to_modern_ui.py old_versions/ 2>/dev/null
mv update_to_modern_ui_v2.py old_versions/ 2>/dev/null

# その他の古いテストファイル
mv test_cleanup.py old_versions/ 2>/dev/null
mv manual_cleanup.py old_versions/ 2>/dev/null
mv force_cleanup.py old_versions/ 2>/dev/null
mv fix_all_links.py old_versions/ 2>/dev/null
mv fix_index_issues.py old_versions/ 2>/dev/null
mv fix_metadata.py old_versions/ 2>/dev/null
mv create_test_article.py old_versions/ 2>/dev/null
mv paginated_blog_system.py old_versions/ 2>/dev/null
mv update_blog_index.py old_versions/ 2>/dev/null

echo "✅ 古いファイルをold_versionsディレクトリに移動しました"

# 現在の最新ファイル
echo ""
echo "📋 現在の最新ファイル:"
echo "  - generate_article_with_evaluation.py (自己評価機能付き)"
echo "  - convert_articles_v3.py (改善されたHTML変換)"
echo "  - update_to_modern_ui_v3.py (改善されたUI更新)"
echo "  - article_evaluator.py (評価システム)"
echo "  - BLOG_WRITING_RULES.md (記事作成ルール)"

echo ""
echo "✨ 整理完了！"