param(
    [switch]$RunEditor,
    [switch]$ForceReinstall,
    [switch]$FixUserConfig,
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[FLAtlas Fix] $Message"
}

function Invoke-Checked {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Kommando fehlgeschlagen ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}

function Test-PythonImports {
    param(
        [string]$PythonPath,
        [string[]]$Modules
    )

    if (-not (Test-Path $PythonPath -PathType Leaf)) {
        return $false
    }
    $snippet = "import " + ($Modules -join ",")
    try {
        & $PythonPath -c $snippet *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Get-BootstrapPythonPath {
    param([string]$ProjectRoot)

    $parentRoot = Split-Path -Parent $ProjectRoot
    $candidates = @(
        (Join-Path $parentRoot ".venv\Scripts\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"),
        (Join-Path $env:ProgramFiles "Python314\python.exe"),
        (Join-Path $env:ProgramFiles "Python313\python.exe"),
        (Join-Path $env:ProgramFiles "Python312\python.exe")
    )

    foreach ($candidate in $candidates) {
        if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
        if (Test-Path $candidate -PathType Leaf) {
            return $candidate
        }
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd -and $pythonCmd.Source -notmatch "WindowsApps\\python(\.exe)?$") {
        return $pythonCmd.Source
    }

    return $null
}

function Ensure-Venv {
    param(
        [string]$ProjectRoot,
        [switch]$ForceReinstall
    )

    $venvDir = Join-Path $ProjectRoot ".venv"
    $venvPython = Join-Path $venvDir "Scripts\python.exe"

    if ($ForceReinstall -and (Test-Path $venvDir)) {
        Write-Step "Entferne bestehende Projekt-venv: $venvDir"
        Remove-Item -Recurse -Force $venvDir
    }

    if (-not (Test-Path $venvPython -PathType Leaf)) {
        $bootstrapPython = Get-BootstrapPythonPath -ProjectRoot $ProjectRoot
        if (-not $bootstrapPython) {
            $pyCmd = Get-Command py -ErrorAction SilentlyContinue
            if ($pyCmd) {
                Write-Step "Erstelle .venv mit py -3"
                & py -3 -m venv $venvDir
                if ($LASTEXITCODE -ne 0) {
                    throw "Kommando fehlgeschlagen ($LASTEXITCODE): py -3 -m venv $venvDir"
                }
            }
            else {
                throw "Kein nutzbarer Python-Interpreter gefunden. Bitte Python 3.10+ installieren (nicht nur Windows Store Alias)."
            }
        }
        else {
            Write-Step "Erstelle .venv mit: $bootstrapPython"
            Invoke-Checked -FilePath $bootstrapPython -Arguments @("-m", "venv", $venvDir)
        }
    }
    else {
        Write-Step "Projekt-venv vorhanden: $venvPython"
    }

    if (-not (Test-Path $venvPython -PathType Leaf)) {
        throw "venv wurde nicht korrekt erstellt: $venvPython fehlt."
    }

    return $venvPython
}

function Install-Requirements {
    param(
        [string]$ProjectRoot,
        [string]$VenvPython,
        [string]$BootstrapPython
    )

    $requirements = Join-Path $ProjectRoot "requirements.txt"
    if (-not (Test-Path $requirements -PathType Leaf)) {
        throw "requirements.txt nicht gefunden: $requirements"
    }

    $hasPip = $true
    & $VenvPython -m pip --version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $hasPip = $false
    }

    if (-not $hasPip) {
        Write-Step "venv ohne pip erkannt, versuche ensurepip (offline)"
        & $VenvPython -m ensurepip --upgrade 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $hasPip = $true
        }
    }

    if (-not $hasPip) {
        if ([string]::IsNullOrWhiteSpace($BootstrapPython)) {
            throw "venv hat kein pip und es wurde kein Bootstrap-Python gefunden. Starte erneut mit -SkipInstall oder installiere Python mit ensurepip."
        }
        Write-Step "ensurepip nicht verfuegbar, bootstrappe pip ueber: $BootstrapPython"
        & $BootstrapPython -m pip --python $VenvPython install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            throw "pip-Bootstrap fehlgeschlagen (evtl. offline). Starte mit -SkipInstall und installiere spaeter bei verfuegbarem Netzwerk."
        }
        $hasPip = $true
    }

    Write-Step "Aktualisiere pip"
    Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip")

    Write-Step "Installiere Abhaengigkeiten aus requirements.txt"
    Invoke-Checked -FilePath $VenvPython -Arguments @("-m", "pip", "install", "-r", $requirements)
}

function Update-VSCodeSettings {
    param(
        [string]$ProjectRoot,
        [string]$InterpreterPath
    )

    $vscodeDir = Join-Path $ProjectRoot ".vscode"
    $settingsPath = Join-Path $vscodeDir "settings.json"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }

    $settings = [ordered]@{}
    if (Test-Path $settingsPath -PathType Leaf) {
        try {
            $loaded = Get-Content $settingsPath -Raw | ConvertFrom-Json
            if ($loaded) {
                $settings = [ordered]@{}
                foreach ($prop in $loaded.PSObject.Properties) {
                    $settings[$prop.Name] = $prop.Value
                }
            }
        }
        catch {
            Write-Step "Warnung: settings.json war nicht lesbar, wird neu geschrieben."
        }
    }

    $settings["python.defaultInterpreterPath"] = $InterpreterPath
    $settings["python.analysis.extraPaths"] = @(
        "."
    )
    $settings["python.terminal.activateEnvironment"] = $true

    ($settings | ConvertTo-Json -Depth 20) | Set-Content -Path $settingsPath -Encoding UTF8
    Write-Step "VSCode Settings aktualisiert: $settingsPath"
}

function Fix-LegacyUserConfigPath {
    $legacyRoot = Join-Path $HOME ".config"
    $legacyPath = Join-Path $legacyRoot "fl_editor"

    if (-not (Test-Path $legacyRoot -PathType Container)) {
        New-Item -ItemType Directory -Path $legacyRoot -Force | Out-Null
    }

    if (Test-Path $legacyPath -PathType Leaf) {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backup = "${legacyPath}.bak.$stamp"
        Rename-Item -Path $legacyPath -NewName (Split-Path -Leaf $backup)
        Write-Step "Legacy-Datei blockierte Config-Pfad, umbenannt zu: $backup"
    }

    if (-not (Test-Path $legacyPath -PathType Container)) {
        New-Item -ItemType Directory -Path $legacyPath -Force | Out-Null
        Write-Step "Legacy-Config-Ordner erstellt: $legacyPath"
    }
}

$projectRoot = Split-Path -Parent $PSCommandPath
Write-Step "Projektpfad: $projectRoot"
$parentVenvPython = Join-Path (Split-Path -Parent $projectRoot) ".venv\Scripts\python.exe"

$bootstrapPython = Get-BootstrapPythonPath -ProjectRoot $projectRoot
$venvPython = Ensure-Venv -ProjectRoot $projectRoot -ForceReinstall:$ForceReinstall
if (-not $SkipInstall) {
    Install-Requirements -ProjectRoot $projectRoot -VenvPython $venvPython -BootstrapPython $bootstrapPython
}
else {
    Write-Step "Install-Schritt uebersprungen (-SkipInstall)."
}

$requiredModules = @("PySide6", "pefile")
$runtimePython = $venvPython
if (-not (Test-PythonImports -PythonPath $venvPython -Modules $requiredModules)) {
    if (Test-PythonImports -PythonPath $parentVenvPython -Modules $requiredModules) {
        $runtimePython = $parentVenvPython
        Write-Step "Nutze funktionierende Parent-venv fuer Start/VSCode: $runtimePython"
    }
}

Update-VSCodeSettings -ProjectRoot $projectRoot -InterpreterPath $runtimePython

if ($FixUserConfig) {
    Fix-LegacyUserConfigPath
}

Write-Step "Setup abgeschlossen."

if ($RunEditor) {
    $entry = Join-Path $projectRoot "start_savegame_editor.py"
    Write-Step "Starte Editor: $entry"
    & $runtimePython $entry
}
else {
    Write-Host ""
    Write-Host "Optional starten mit:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -RunEditor"
}
