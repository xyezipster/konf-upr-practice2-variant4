#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh
./run.sh --config configs/requests.toml
if ./run.sh --config configs/missing.toml; then
    exit 1
fi
