# Cloud-Company ADK Web UI 起動スクリプト
# 使用方法: .\scripts\start_adk_web.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$EnvFile = Join-Path $ProjectRoot ".env"

# .env を読み込んでハッシュテーブルに保存
$envVars = @{}
if (Test-Path $EnvFile) {
    Write-Host "[INFO] Loading .env from: $EnvFile"
    $lines = Get-Content $EnvFile
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if ($trimmed -and (-not $trimmed.StartsWith("#"))) {
            $eqIdx = $trimmed.IndexOf("=")
            if ($eqIdx -gt 0) {
                $k = $trimmed.Substring(0, $eqIdx).Trim()
                $v = $trimmed.Substring($eqIdx + 1).Trim()
                $envVars[$k] = $v
                # $env: スコープに直接セット
                Set-Item -Path "Env:$k" -Value $v
                Write-Host "  [SET] $k"
            }
        }
    }
} else {
    Write-Host "[WARN] .env not found: $EnvFile"
    return
}

# GOOGLE_API_KEY チェック
if (-not $envVars.ContainsKey("GOOGLE_API_KEY")) {
    Write-Host "[ERROR] GOOGLE_API_KEY not found in .env"
    return
}

# ANTHROPIC_API_KEY は .env に無くても、adk web の中で cloud_company が資格情報マネージャーから読む
# （cloud_company/keyring_env.py）。ここでは確定できないので、.env にあるときだけ Claude と表示する。
$modelName = "Gemini 2.5 Flash (Google)、資格情報マネージャーに ANTHROPIC_API_KEY があれば Claude"
if ($envVars["ANTHROPIC_API_KEY"]) {
    $modelName = "Claude (Anthropic)"
}

Write-Host ""
Write-Host "============================================================"
Write-Host " Starting ADK Web UI"
Write-Host " Model: $modelName"
Write-Host " URL:   http://localhost:8000"
Write-Host "============================================================"
Write-Host ""

Set-Location $ProjectRoot
adk web cloud_company
