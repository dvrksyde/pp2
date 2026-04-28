$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Installing dependencies for TSIS1 and TSIS4..." -ForegroundColor Cyan
python -m pip install -r "TSIS1/requirements.txt"

$canUsePy312 = $false
$pyCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pyCmd) {
    $prevErrPref = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    py -3.12 --version *> $null
    $ErrorActionPreference = $prevErrPref
    if ($LASTEXITCODE -eq 0) {
        $canUsePy312 = $true
    }
}

if ($canUsePy312) {
    py -3.12 -m pip install -r "TSIS4/requirements.txt"
} else {
    Write-Host "Python 3.12 not found. Installing TSIS4 deps with default python." -ForegroundColor Yellow
    python -m pip install -r "TSIS4/requirements.txt"
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "1) Copy TSIS1/.env.example -> TSIS1/.env and set DB credentials."
Write-Host "2) Copy TSIS4/.env.example -> TSIS4/.env and set DB credentials."
Write-Host "3) Run: powershell -ExecutionPolicy Bypass -File TSIS1/run.ps1"
Write-Host "4) Run: powershell -ExecutionPolicy Bypass -File TSIS4/run.ps1"
