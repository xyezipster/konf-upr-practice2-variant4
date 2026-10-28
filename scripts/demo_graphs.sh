#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for example in demo diamond cycle isolated; do
    ./run.sh --config "configs/$example.toml"
done
