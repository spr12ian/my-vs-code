import json
import sys
from pathlib import Path
from typing import Any, Callable, cast

from utils import deep_sort, get_projects


def compare_lists(path: str, a: list, b: list) -> list[str]:
    """
    Compare two lists, showing added and removed elements cleanly.
    Handles lists of scalars; falls back to full comparison for lists of dicts.
    """
    if all(isinstance(x, (str, int, float)) for x in a + b):
        set_a = set(a)
        set_b = set(b)
        added = sorted(set_b - set_a)
        removed = sorted(set_a - set_b)

        if not added and not removed:
            return []

        lines = [f"{path} differs:"]
        for item in removed:
            lines.append(f"   - {item}")
        for item in added:
            lines.append(f"   + {item}")
        return lines

    else:
        # Lists contain dicts or mixed types — fallback to basic comparison
        if a != b:
            return [
                f"{path}: lists differ (complex structures not diffed element-by-element)"
            ]
        else:
            return []


def deep_conflict_detection(a: Any, b: Any, path: str = "") -> list[str]:
    """
    Recursively detect conflicts between two JSON-like structures.
    Returns a list of conflict descriptions, pretty-printed.
    """
    conflicts = []

    IGNORED_PATHS = {"settings.cSpell.words"}

    if path in IGNORED_PATHS:
        return []  # Skip this path

    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a.keys()) | set(b.keys())
        for k in sorted(keys):
            sub_path = f"{path}.{k}" if path else k
            a_val = a.get(k)
            b_val = b.get(k)

            if k not in a:
                if sub_path not in IGNORED_PATHS:
                    conflicts.append(f"{sub_path} only in second file: {b_val}")
            elif k not in b:
                if sub_path not in IGNORED_PATHS:
                    conflicts.append(f"{sub_path} only in first file: {a_val}")
            else:
                conflicts.extend(deep_conflict_detection(a_val, b_val, sub_path))

    elif isinstance(a, list) and isinstance(b, list):
        conflicts.extend(compare_lists(path, a, b))

    else:
        if a != b:
            conflicts.append(f"{path}: {a} != {b}")

    return conflicts


def load_workspace(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merge_project(
    project: str,
    load_workspace: Callable[[Path], dict],
    merge_workspaces: Callable[[dict, dict], dict],
) -> None:
    g_dir = Path("generated_workspaces")
    w_dir = Path("workspaces")

    file1 = g_dir / f"{project}.code-workspace"
    print(f"First file: {file1}")
    ws1 = load_workspace(file1)

    file2 = w_dir / f"{project}.code-workspace"
    print(f"Second file: {file2}")
    ws2 = load_workspace(file2)

    merged = merge_workspaces(ws1, ws2)

    with open(f"{g_dir}/merged/{project}.code-workspace", "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

        f.write("\n")  # Ensure final newline


def merge_workspaces(ws1: dict, ws2: dict) -> dict:
    if conflicts := deep_conflict_detection(ws1, ws2):
        print("❌ Conflicts detected:")
        for conflict in conflicts:
            print(f" - {conflict}")
        sys.exit(1)

    merged: dict[str, Any] = {}

    # Extract folder lists from both workspaces, defaulting to empty lists

    folders1 = ws1.get("folders", [])
    folders2 = ws2.get("folders", [])

    # Merge folders into a map keyed by unique 'path' to eliminate duplicates
    folder_map = {f["path"]: f for f in folders1 + folders2}

    # Ensure unique paths and sort by path
    merged["folders"] = sorted(folder_map.values(), key=lambda f: f["path"])

    ws1_settings = ws1.get("settings") or {}
    ws2_settings = ws2.get("settings") or {}

    if not isinstance(ws1_settings, dict):
        raise TypeError(f"ws1 settings is not a dict: {type(ws1_settings)}")
    if not isinstance(ws2_settings, dict):
        raise TypeError(f"ws2 settings is not a dict: {type(ws2_settings)}")

    # Merge settings
    merged["settings"] = {**ws1_settings, **ws2_settings}

    # Merge extensions.recommendations
    rec1 = ws1.get("extensions", {}).get("recommendations", [])
    rec2 = ws2.get("extensions", {}).get("recommendations", [])
    merged["extensions"] = {"recommendations": sorted(set(rec1 + rec2))}

    return cast(dict[Any, Any], deep_sort(merged))


projects = get_projects()

for project in projects:
    print(f"Processing project: {project}")
    merge_project(project, load_workspace, merge_workspaces)
