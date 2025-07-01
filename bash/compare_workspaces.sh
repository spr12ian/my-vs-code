#!/usr/bin/env bash
set -euo pipefail

DIR1="generated_workspaces"
DIR2="workspaces"

for f1 in "$DIR1"/*.code-workspace; do
    file=$(basename "$f1")
    f2="$DIR2/$file"
    if [[ -f "$f2" ]]; then
        echo "Diffing $file..."
        jq -S . "$f1" > /tmp/1.json
        jq -S . "$f2" > /tmp/2.json
        diff /tmp/1.json /tmp/2.json || true
    fi
done
