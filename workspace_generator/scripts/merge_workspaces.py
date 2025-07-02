import json
from pathlib import Path

from deep_sort import deep_sort

def load_workspace(path:Path) -> dict:
    with open(path) as f:
        return json.load(f)

def merge_workspaces(ws1:dict, ws2:dict) -> dict:
    merged = {}
    # Merge folders
    folders1 = ws1.get("folders", [])
    folders2 = ws2.get("folders", [])
    merged["folders"] = {f["path"]: f for f in folders1 + folders2}
    merged["folders"] = list(merged["folders"].values())

    # Merge settings
    merged["settings"] = {**ws1.get("settings", {}), **ws2.get("settings", {})}

    # Merge extensions.recommendations
    rec1 = ws1.get("extensions", {}).get("recommendations", [])
    rec2 = ws2.get("extensions", {}).get("recommendations", [])
    merged["extensions"] = {
        "recommendations": sorted(set(rec1 + rec2))
    }

    return deep_sort(merged)

g_dir = Path("generated_workspaces")
w_dir = Path("workspaces")

workspace="bin"

ws1 = load_workspace(g_dir/f"{workspace}.code-workspace")
ws2 = load_workspace(w_dir/f"{workspace}.code-workspace")

merged = merge_workspaces(ws1, ws2)

with open(f"merged_{workspace}.code-workspace", "w") as f:
    json.dump(merged, f, indent=2)
