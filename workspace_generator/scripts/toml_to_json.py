import json
import sys
from pathlib import Path

import tomllib


def main():
    if len(sys.argv) != 2:
        print("Usage: python toml_to_json.py <input_file>", file=sys.stderr)
        sys.exit(1)

    toml_filename = sys.argv[1]
    if not Path(toml_filename).is_file():
        print(f"Error: File '{toml_filename}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not toml_filename.endswith(".toml"):
        print("Error: Input file must have a .toml extension.", file=sys.stderr)
        sys.exit(1)

    json_filename = Path(toml_filename).with_suffix(".json")

    with open(toml_filename, "rb") as f:
        data = tomllib.load(f)

    with open(json_filename, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
