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

$jupyterLab = Join-Path $projectRoot ".venv\Scripts\jupyter-lab.exe"

if (-not (Test-Path -LiteralPath $jupyterLab)) {
    throw "Missing .venv. Create it and install requirements first."
}

& $jupyterLab --notebook-dir=$projectRoot
