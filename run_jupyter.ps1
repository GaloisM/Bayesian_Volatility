$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$runtimeDir = Join-Path $projectRoot ".jupyter-runtime"
$configDir = Join-Path $projectRoot ".jupyter-config"
$ipythonDir = Join-Path $projectRoot ".ipython"
$pytensorDir = Join-Path $projectRoot ".pytensor-cache"
$numbaDir = Join-Path $projectRoot ".numba-cache"
$matplotlibDir = Join-Path $projectRoot ".matplotlib-cache"

New-Item -ItemType Directory -Force -Path `
    $runtimeDir, `
    $configDir, `
    $ipythonDir, `
    $pytensorDir, `
    $numbaDir, `
    $matplotlibDir | Out-Null

$env:JUPYTER_RUNTIME_DIR = $runtimeDir
$env:JUPYTER_CONFIG_DIR = $configDir
$env:IPYTHONDIR = $ipythonDir
$env:PYTENSOR_FLAGS = "base_compiledir=.pytensor-cache"
$env:NUMBA_CACHE_DIR = $numbaDir
$env:MPLCONFIGDIR = $matplotlibDir

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$jupyterLab = Join-Path $projectRoot ".venv\Scripts\jupyter-lab.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating .venv with Python 3.12..."

    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -m venv .venv
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ($version -ne "3.12") {
            throw "Python 3.12 is required, but 'python' points to Python $version."
        }
        & python -m venv .venv
    }
    else {
        throw "Python 3.12 was not found. Install it from https://www.python.org/downloads/"
    }

    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "Failed to create .venv with Python 3.12."
    }
}

if (-not (Test-Path -LiteralPath $jupyterLab)) {
    Write-Host "Installing project dependencies into .venv..."
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")
}

if (-not (Test-Path -LiteralPath $jupyterLab)) {
    throw "JupyterLab installation failed."
}

& $jupyterLab --notebook-dir=$projectRoot
