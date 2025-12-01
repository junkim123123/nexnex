# PowerShell 스크립트: .env 파일 생성
# 사용법: .\scripts\setup_env.ps1

Write-Host "🔐 NexSupply AI - Environment Variables Setup" -ForegroundColor Cyan
Write-Host ""

# .env 파일 경로
$envFile = ".env"

# 기존 .env 파일 확인
if (Test-Path $envFile) {
    Write-Host "⚠️  기존 .env 파일이 발견되었습니다." -ForegroundColor Yellow
    $overwrite = Read-Host "덮어쓰시겠습니까? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "취소되었습니다." -ForegroundColor Red
        exit
    }
}

Write-Host "Gemini API 키를 입력하세요:" -ForegroundColor Green
Write-Host "(입력한 키는 화면에 표시되지 않습니다)" -ForegroundColor Gray
$apiKey = Read-Host -AsSecureString
$apiKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
)

# Supabase 설정 (선택적)
Write-Host ""
Write-Host "Supabase를 사용하시겠습니까? (선택적)" -ForegroundColor Green
$useSupabase = Read-Host "yes/no (기본값: no)"
$supabaseUrl = ""
$supabaseKey = ""

if ($useSupabase -eq "yes") {
    Write-Host "Supabase URL을 입력하세요:" -ForegroundColor Green
    $supabaseUrl = Read-Host
    
    Write-Host "Supabase Key를 입력하세요:" -ForegroundColor Green
    $supabaseKeySecure = Read-Host -AsSecureString
    $supabaseKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($supabaseKeySecure)
    )
}

# .env 파일 내용 생성
$envContent = @"
# NexSupply AI - Environment Variables
# ⚠️ 중요: 이 파일은 절대 Git에 커밋하지 마세요!

# Google Gemini API
GEMINI_API_KEY=$apiKeyPlain
"@

if ($useSupabase -eq "yes") {
    $envContent += @"

# Supabase (선택적)
SUPABASE_URL=$supabaseUrl
SUPABASE_KEY=$supabaseKey
"@
}

# .env 파일 저장
$envContent | Out-File -FilePath $envFile -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "✅ .env 파일이 생성되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  중요 사항:" -ForegroundColor Yellow
Write-Host "  1. .env 파일은 절대 Git에 커밋하지 마세요"
Write-Host "  2. .gitignore에 .env가 포함되어 있는지 확인하세요"
Write-Host "  3. 이 키를 코드나 문서에 직접 작성하지 마세요"
Write-Host ""

# .gitignore 확인
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "\.env") {
        Write-Host "✅ .gitignore에 .env가 포함되어 있습니다." -ForegroundColor Green
    } else {
        Write-Host "⚠️  .gitignore에 .env가 없습니다. 추가해주세요!" -ForegroundColor Yellow
    }
}

