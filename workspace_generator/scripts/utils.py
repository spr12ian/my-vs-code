import json
import os
from pathlib import Path
from typing import Any, TypedDict

# JSON value type
JSONType = dict[str, Any] | list[Any] | str | int | float | bool | None


# TypedDicts for expected structures
class Folder(TypedDict):
    path: str


class Extensions(TypedDict):
    recommendations: list[str]


class WorkspaceJSON(TypedDict, total=False):
    folders: list[Folder]
    settings: JSONType
    extensions: Extensions


def _deep_sort(obj: JSONType) -> JSONType:
    if isinstance(obj, dict):
        return {k: _deep_sort(obj[k]) for k in sorted(obj)}
    elif isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return [_deep_sort(x) for x in sorted(obj, key=lambda d: sorted(d.items()))]
        else:
            return [_deep_sort(x) for x in obj]
    else:
        return obj


def _get_final_structure(json_data: WorkspaceJSON) -> WorkspaceJSON:
    final_json_data: WorkspaceJSON = {}

    if "folders" in json_data:
        folders = json_data["folders"]
        final_json_data["folders"] = sorted(folders, key=lambda f: f["path"])

    if "settings" in json_data:
        final_json_data["settings"] = _deep_sort(json_data["settings"])

    if "extensions" in json_data:
        extensions = json_data["extensions"]
        final_json_data["extensions"] = {
            "recommendations": sorted(extensions["recommendations"])
        }

    return final_json_data


def get_github_parent_path() -> Path:
    github_parent_dir = os.getenv("GITHUB_PARENT_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PARENT_DIR environment variable is not set.")

    github_parent_path = Path(github_parent_dir)

    if not github_parent_path.is_absolute():
        github_parent_path = github_parent_path.resolve()

    if not github_parent_path.exists():
        raise EnvironmentError(f"{github_parent_path} does not exist.")

    if not github_parent_path.is_dir():
        raise EnvironmentError(f"{github_parent_path} is not a directory.")

    return github_parent_path


def get_projects() -> list[str]:
    github_parent_path = get_github_parent_path()
    return sorted(
        str(project.name)
        for project in github_parent_path.iterdir()
        if project.is_dir()
    )


def write_final_structure(path: Path, json_data: WorkspaceJSON) -> None:
    final_json_data = _get_final_structure(json_data)
    data = json.dumps(final_json_data, indent=2, ensure_ascii=False) + "\n"

    with open(path, "w", encoding="utf-8") as workspace_file:
        workspace_file.write(data)

    print(f"Workspace created: '{path}'")
