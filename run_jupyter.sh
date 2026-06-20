#!/usr/bin/env sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_ROOT"

mkdir -p \
    .jupyter-runtime \
    .jupyter-config \
    .ipython \
    .pytensor-cache \
    .numba-cache \
    .matplotlib-cache

export JUPYTER_RUNTIME_DIR="$PROJECT_ROOT/.jupyter-runtime"
export JUPYTER_CONFIG_DIR="$PROJECT_ROOT/.jupyter-config"
export IPYTHONDIR="$PROJECT_ROOT/.ipython"
export PYTENSOR_FLAGS="base_compiledir=.pytensor-cache"
export NUMBA_CACHE_DIR="$PROJECT_ROOT/.numba-cache"
export MPLCONFIGDIR="$PROJECT_ROOT/.matplotlib-cache"

if [ ! -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    echo "Creating .venv with Python 3.12..."

    if command -v python3.12 >/dev/null 2>&1; then
        python3.12 -m venv .venv
    elif command -v python3 >/dev/null 2>&1; then
        VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [ "$VERSION" != "3.12" ]; then
            echo "Python 3.12 is required, but python3 points to Python $VERSION." >&2
            exit 1
        fi
        python3 -m venv .venv
    else
        echo "Python 3.12 was not found. Install it from https://www.python.org/downloads/" >&2
        exit 1
    fi
fi

if [ ! -x "$PROJECT_ROOT/.venv/bin/jupyter-lab" ]; then
    echo "Installing project dependencies into .venv..."
    "$PROJECT_ROOT/.venv/bin/python" -m pip install --upgrade pip
    "$PROJECT_ROOT/.venv/bin/python" -m pip install -r requirements.txt
fi

if [ ! -x "$PROJECT_ROOT/.venv/bin/jupyter-lab" ]; then
    echo "JupyterLab installation failed." >&2
    exit 1
fi

exec "$PROJECT_ROOT/.venv/bin/jupyter-lab" --notebook-dir="$PROJECT_ROOT"
