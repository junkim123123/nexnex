#!/bin/bash
# Bash 스크립트: .env 파일 생성
# 사용법: bash scripts/setup_env.sh

echo "🔐 NexSupply AI - Environment Variables Setup"
echo ""

# .env 파일 경로
ENV_FILE=".env"

# 기존 .env 파일 확인
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  기존 .env 파일이 발견되었습니다."
    read -p "덮어쓰시겠습니까? (yes/no): " overwrite
    if [ "$overwrite" != "yes" ]; then
        echo "취소되었습니다."
        exit 1
    fi
fi

# Gemini API 키 입력
echo "Gemini API 키를 입력하세요:"
read -s api_key
echo ""

# Supabase 설정 (선택적)
echo ""
echo "Supabase를 사용하시겠습니까? (선택적)"
read -p "yes/no (기본값: no): " use_supabase

supabase_url=""
supabase_key=""

if [ "$use_supabase" = "yes" ]; then
    echo "Supabase URL을 입력하세요:"
    read supabase_url
    
    echo "Supabase Key를 입력하세요:"
    read -s supabase_key
    echo ""
fi

# .env 파일 내용 생성
cat > "$ENV_FILE" << EOF
# NexSupply AI - Environment Variables
# ⚠️ 중요: 이 파일은 절대 Git에 커밋하지 마세요!

# Google Gemini API
GEMINI_API_KEY=$api_key
EOF

if [ "$use_supabase" = "yes" ]; then
    cat >> "$ENV_FILE" << EOF

# Supabase (선택적)
SUPABASE_URL=$supabase_url
SUPABASE_KEY=$supabase_key
EOF
fi

echo ""
echo "✅ .env 파일이 생성되었습니다!"
echo ""
echo "⚠️  중요 사항:"
echo "  1. .env 파일은 절대 Git에 커밋하지 마세요"
echo "  2. .gitignore에 .env가 포함되어 있는지 확인하세요"
echo "  3. 이 키를 코드나 문서에 직접 작성하지 마세요"
echo ""

# .gitignore 확인
if [ -f ".gitignore" ]; then
    if grep -q "\.env" ".gitignore"; then
        echo "✅ .gitignore에 .env가 포함되어 있습니다."
    else
        echo "⚠️  .gitignore에 .env가 없습니다. 추가해주세요!"
    fi
fi

