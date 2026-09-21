#!/usr/bin/env sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

python3 scripts/generate_demo_assets.py
docker compose -f docker-compose.yml -f docker-compose.demo.yml up --build
