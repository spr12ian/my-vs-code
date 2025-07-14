import json
import os
from pathlib import Path
from typing import Any, cast

from utils import get_projects, is_log_file, write_final_structure, WorkspaceJSON

IGNORE_LIST = [
    ".git",
    ".hg",
    ".mypy_cache",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
    "venv",
]


class Tree:
    def __init__(self, initial_components: set[str] = set()) -> None:
        self.ignoreList: list[str] = []
        self.components: set[str] = initial_components

    def get_components(self, directory: Path) -> set[str]:
        """
        Returns a set of components.
        """
        self.walk(directory)
        return self.components

    def ignore(self, patterns: list[str]) -> None:
        self.ignoreList.extend(patterns)

    def register(self, path: Path) -> None:
        if not path.is_dir():
            suffix = path.suffix.lower() if path.suffix else "._default"
            if suffix == '.log':
                if not is_log_file(path):
                    print(f"Not a real log file: {path}")
                    return
            self.components.add(suffix)

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


def deep_merge_dict(
    a: dict[str, Any], b: dict[str, Any], path: str = ""
) -> dict[str, Any]:
    for key, b_value in b.items():
        current_path = f"{path}.{key}" if path else key
        if key in a:
            a_value = a[key]
            if isinstance(a_value, dict) and isinstance(b_value, dict):
                # Tell the type checker: these *are* dict[str, Any]
                a[key] = deep_merge_dict(
                    cast(dict[str, Any], a_value),
                    cast(dict[str, Any], b_value),
                    current_path,
                )
            elif a_value != b_value:
                print(
                    f"⚠️ Clash at '{current_path}': '{a_value}' will be overwritten by '{b_value}'"
                )
                a[key] = b_value
            else:
                a[key] = b_value
        else:
            a[key] = b_value
    return a


def detect_hugo_repo(path: Path) -> bool:
    """
    Detects whether a given directory is a Hugo site by requiring:
    - config.toml
    - content/ directory
    - layouts/ directory
    - themes/ directory

    Args:
        path (Path): The directory to check.

    Returns:
        bool: True if it matches strict Hugo structure, False otherwise.
    """
    if not path.is_dir():
        return False

    has_config = (path / "config.toml").is_file()
    has_content = (path / "content").is_dir()
    has_layouts = (path / "layouts").is_dir()
    has_themes = (path / "themes").is_dir()

    return has_config and has_content and has_layouts and has_themes


def detect_makefile(path: Path) -> bool:
    """
    Detects whether a given directory contains a Makefile.
    """
    if not path.is_dir():
        return False

    has_makefile = (path / "Makefile").is_file()
    return has_makefile


def generate_workspace(workspace_name: str, base_path: Path) -> None:
    """
    Generates a vscode workspace file (template).

    Args:
        workspace_name (str): The name of the workspace.
        base_path (Path): The base path where the workspace will be created.
    """
    workspace_path = base_path / (workspace_name + ".code-workspace")
    print(workspace_path)

    json_data: WorkspaceJSON = {"folders": [{"path": f"../../{workspace_name}"}]}

    workspace_components = get_workspace_components(workspace_name)
    print(workspace_components)

    for component in sorted(workspace_components):
        component_template = Path(f"workspace_component_templates/{component[1:]}.json")
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
                    if "settings" not in json_data:
                        json_data["settings"] = {}

                    if isinstance(template_data["settings"], dict):
                        deep_merge_dict(
                            cast(dict[str, Any], json_data["settings"]),
                            template_data["settings"]
                        )
                if "extensions" in template_data:
                    if "extensions" not in json_data:
                        json_data["extensions"] = {"recommendations": []}
                    elif "recommendations" not in json_data["extensions"]:
                        json_data["extensions"]["recommendations"] = []

                    json_data["extensions"]["recommendations"].extend(
                        template_data["extensions"]["recommendations"]
                    )


    # Deduplicate recommendations if they exist
    if "extensions" in json_data and "recommendations" in json_data["extensions"]:
        json_data["extensions"]["recommendations"] = list(
            sorted(set(json_data["extensions"]["recommendations"]))
        )

    write_final_structure(workspace_path, json_data)


def get_workspace_components(workspace_name: str) -> set[str]:
    github_parent_dir = os.getenv("GITHUB_PROJECTS_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PROJECTS_DIR environment variable is not set.")

    projects_dir = Path(github_parent_dir)
    if not projects_dir.exists():
        raise FileNotFoundError(f"{projects_dir} does not exist.")
    if not projects_dir.is_dir():
        raise NotADirectoryError(f"{projects_dir} is not a valid directory.")

    project_dir = projects_dir / workspace_name

    initial_components: set[str] = {".git"}
    if detect_hugo_repo(project_dir):
        initial_components.add(".hugo")
    if detect_makefile(project_dir):
        initial_components.add(".makefile")

    tree = Tree(initial_components)
    tree.ignore(IGNORE_LIST)
    return tree.get_components(project_dir)


if __name__ == "__main__":
    workspace_dir = Path("generated_workspaces")
    if not workspace_dir.exists():
        workspace_dir.mkdir(parents=True)

    projects = get_projects()

    for project in projects:
        generate_workspace(project, workspace_dir)
