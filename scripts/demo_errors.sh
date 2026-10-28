#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for config in configs/errors/*.toml; do
    if ./run.sh --config "$config"; then
        exit 1
    fi
done
