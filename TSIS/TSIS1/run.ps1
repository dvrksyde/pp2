$ErrorActionPreference = "Stop"

function Set-EnvFromFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".env")) {
    Write-Host "Missing .env in TSIS1. Copy .env.example to .env and set real DB credentials." -ForegroundColor Yellow
    exit 1
}

Set-EnvFromFile ".env"

python -m pip install -r requirements.txt
python phonebook.py
