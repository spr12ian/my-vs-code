#!/usr/bin/env bash
# Convert TOML to JSON using Python

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <file.toml>"
  exit 1
fi

python3 -c "
import sys, json
import tomllib
if sys.version_info < (3, 11):
    print('Python 3.11 or higher is required for tomllib support.', file=sys.stderr)
    sys.exit(1)
with open(sys.argv[1], 'rb') as f:
    data = tomllib.load(f)
json.dump(data, sys.stdout, indent=2)
" "$1"
