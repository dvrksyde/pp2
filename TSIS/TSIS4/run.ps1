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
    Write-Host "Missing .env in TSIS4. Copy .env.example to .env and set real DB credentials." -ForegroundColor Yellow
    exit 1
}

Set-EnvFromFile ".env"

function Resolve-PythonCommand {
    $py312 = Get-Command py -ErrorAction SilentlyContinue
    if ($py312) {
        $prevErrPref = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        py -3.12 --version *> $null
        $ErrorActionPreference = $prevErrPref
        if ($LASTEXITCODE -eq 0) {
            return @("py", "-3.12")
        }
    }
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        return @("python")
    }
    return @()
}

$pyCmd = Resolve-PythonCommand

if ($pyCmd.Count -eq 0) {
    Write-Host "No usable Python runtime found. Install Python 3.12+ and re-run." -ForegroundColor Red
    Write-Host "Tip: run 'py -0' to list available runtimes." -ForegroundColor Yellow
    exit 1
}

if ($pyCmd[0] -eq "py") {
    & $pyCmd[0] $pyCmd[1] -m pip install -r requirements.txt
    & $pyCmd[0] $pyCmd[1] main.py
} else {
    Write-Host "Python 3.12 not available via py launcher. Using default python." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    python main.py
}
