import json
import os
from pathlib import Path
from typing import Any, cast

from utils import deep_sort, get_projects

IGNORE_LIST = [
    ".git",
    ".hg",
    ".mypy_cache",
    ".svn",
    "__pycache__",
    "node_modules",
    "venv",
]


class Tree:
    def __init__(self) -> None:
        self.ignoreList: list[str] = []
        self.file_suffixes: dict[str, int] = {".git": 1}

    def get_suffixes(self, directory: Path) -> dict[str, int]:
        """
        Returns a dictionary of file suffixes and their counts.
        """
        self.walk(directory)
        return self.file_suffixes

    def ignore(self, patterns: list[str]) -> None:
        self.ignoreList.extend(patterns)

    def register(self, path: Path) -> None:
        if not path.is_dir():
            suffix = path.suffix.lower() if path.suffix else ".default"
            self.file_suffixes[suffix] = self.file_suffixes.get(suffix, 0) + 1

    def walk(self, directory: Path) -> None:
        entries = sorted(
            [
                entry
                for entry in directory.iterdir()
                if entry.name not in self.ignoreList
            ]
        )

        for entry in entries:
            self.register(entry)
            if entry.is_dir():
                self.walk(entry)



def deep_merge_dict(a: dict[str, Any], b: dict[str, Any], path: str = "") -> dict[str, Any]:
    for key, b_value in b.items():
        current_path = f"{path}.{key}" if path else key
        if key in a:
            a_value = a[key]
            if isinstance(a_value, dict) and isinstance(b_value, dict):
                # Tell the type checker: these *are* dict[str, Any]
                a[key] = deep_merge_dict(
                    cast(dict[str, Any], a_value),
                    cast(dict[str, Any], b_value),
                    current_path
                )
            elif a_value != b_value:
                print(f"⚠️ Clash at '{current_path}': '{a_value}' will be overwritten by '{b_value}'")
                a[key] = b_value
            else:
                a[key] = b_value
        else:
            a[key] = b_value
    return a

def generate_workspace(workspace_name: str, base_path: Path) -> None:
    """
    Generates a vscode workspace file (template).

    Args:
        workspace_name (str): The name of the workspace.
        base_path (Path): The base path where the workspace will be created.
    """
    workspace_path = base_path / (workspace_name + ".code-workspace")

    json_data = {"folders": [{"path": f"../../{workspace_name}"}]}

    workspace_suffixes = get_workspace_suffixes(workspace_name)

    for suffix, count in sorted(workspace_suffixes.items()):
        if suffix != "No suffix":
            component_template = Path(
                f"workspace_component_templates/{suffix[1:]}.json"
            )
            if component_template.exists():
                with open(component_template, "r") as template_file:
                    try:
                        template_data = json.load(template_file)
                    except json.JSONDecodeError:
                        print(f"⚠️ Skipping invalid JSON template: {component_template}")
                        continue
                    if "folders" in template_data:
                        json_data["folders"].extend(template_data["folders"])
                    if "settings" in template_data:
                        json_data.setdefault("settings", {})
                        deep_merge_dict(
                            json_data["settings"], template_data["settings"]
                        )

                    if "extensions" in template_data:
                        json_data.setdefault("extensions", {}).setdefault(
                            "recommendations", []
                        ).extend(template_data["extensions"]["recommendations"])

    # Deduplicate recommendations if they exist
    if "extensions" in json_data and "recommendations" in json_data["extensions"]:
        json_data["extensions"]["recommendations"] = list(
            sorted(set(json_data["extensions"]["recommendations"]))
        )

    sorted_data = deep_sort(json_data)

    data = json.dumps(sorted_data, indent=2)
    # Ensure final newline
    data += "\n"

    write_workspace_file(workspace_path, data)


def get_workspace_suffixes(workspace_name: str) -> dict[str, int]:
    github_parent_dir = os.getenv("GITHUB_PARENT_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PARENT_DIR environment variable is not set.")
    projects_dir = Path(github_parent_dir)

    tree = Tree()
    tree.ignore(IGNORE_LIST)
    return tree.get_suffixes(projects_dir / workspace_name)


def write_workspace_file(workspace_path: Path, data: str) -> None:
    # Ensure output directory exists
    workspace_path.parent.mkdir(parents=True, exist_ok=True)

    with open(workspace_path, "w") as workspace_file:
        workspace_file.write(data)

    print(f"Workspace created: '{workspace_path}'")


if __name__ == "__main__":
    workspace_dir = Path("generated_workspaces")
    if not workspace_dir.exists():
        workspace_dir.mkdir(parents=True)

    projects = get_projects()

    for project in projects:
        generate_workspace(project, workspace_dir)
