#!/bin/bash
# Git History에서 노출된 API 키 완전히 제거하는 스크립트
# 
# 사용법:
# 1. git filter-repo 설치: pip install git-filter-repo
# 2. 이 스크립트 실행: bash scripts/remove_leaked_key.sh
# 3. 강제 푸시: git push origin --force --all

set -e

echo "⚠️  WARNING: This script will rewrite git history!"
echo "⚠️  Make sure you have a backup of your repository!"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# 노출된 키
LEAKED_KEY="AIzaSyBgMc5wI9HpbgfQKcZykcYpItmDiDaR9r4"

# git filter-repo로 키 제거
echo "Removing leaked key from git history..."
git filter-repo --replace-text <(echo "$LEAKED_KEY==>REMOVED_LEAKED_KEY")

echo ""
echo "✅ Done! The leaked key has been removed from git history."
echo ""
echo "⚠️  IMPORTANT: You must force push to update remote repository:"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "⚠️  WARNING: This will rewrite history. Make sure all team members"
echo "   are aware and have pulled the latest changes before force pushing."

