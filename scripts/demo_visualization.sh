#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./run.sh --config configs/demo.toml --output output/demo.d2
./run.sh --config configs/cycle.toml --output output/cycle.d2
./run.sh --reverse D --output output/reverse.d2
