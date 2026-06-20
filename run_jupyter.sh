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

if [ ! -x "$PROJECT_ROOT/.venv/bin/jupyter-lab" ]; then
    echo "Missing .venv. Create it and install requirements first." >&2
    exit 1
fi

exec "$PROJECT_ROOT/.venv/bin/jupyter-lab" --notebook-dir="$PROJECT_ROOT"
