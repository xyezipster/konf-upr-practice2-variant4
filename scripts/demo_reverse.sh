#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --config configs/demo.toml --reverse D
./run.sh --config configs/demo.toml --reverse A
./run.sh --config configs/cycle.toml --reverse B
./run.sh --config configs/isolated.toml --reverse A
if ./run.sh --reverse Z; then
    exit 1
fi
