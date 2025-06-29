import json
import os
import sys
from pathlib import Path

IGNORE_LIST = [".git", ".hg", ".mypy_cache", ".svn", "__pycache__", "venv"]


class Tree:
    def __init__(self) -> None:
        self.ignoreList: list[str] = []
        self.file_suffixes: dict[str, int] = {}

    def get_suffixes(self, directory: Path, prefix: str = "") -> dict[str, int]:
        """
        Returns a dictionary of file suffixes and their counts.
        """

        self.walk(directory, prefix)

        return self.file_suffixes

    def ignore(self, patterns: list[str]) -> None:
        self.ignoreList.extend(patterns)

    def print_summary(self) -> None:
        print(self.summary())

    def register(self, path: Path) -> None:
        if not path.is_dir():
            if len(path.suffix) > 0:
                suffix = path.suffix.lower()
            else:
                suffix = "No suffix"

            self.file_suffixes[suffix] = self.file_suffixes.get(suffix, 0) + 1

    def summary(self):
        return f"File types found: {len(self.file_suffixes)}\n" + "\n".join(
            f"{ext}: {count}" for ext, count in sorted(self.file_suffixes.items())
        )

    def walk(self, directory: Path, prefix: str = "") -> None:
        entries = sorted(
            [entry for entry in directory.iterdir() if not entry.name.startswith(".")]
        )

        for index, entry in enumerate(entries):
            if entry.name in self.ignoreList:
                continue

            self.register(entry)

            if entry.is_dir():
                new_prefix = prefix + ("    " if index == len(entries) - 1 else "│   ")
                self.walk(entry, new_prefix)


def generate_workspace(workspace_name: str, base_path: Path) -> None:
    """
    Generates a vscode workspace file (template).

    Args:
        workspace_name (str): The name of the workspace.
        base_path (str): The base path where the workspace will be created.
    """
    workspace_path = base_path / (workspace_name + ".code-workspace")

    header = {"folders": [{"path": f"../../{workspace_name}"}]}

    workspace_suffixes = get_workspace_suffixes(workspace_name)
    print(workspace_suffixes)

    for suffix, count in workspace_suffixes.items():
        if suffix != "No suffix":
            component_template = Path(
                f"workspace_component_templates/{suffix[1:]}.json"
            )
            if component_template.exists():
                with open(component_template, "r") as template_file:
                    template_data = json.load(template_file)
                    if "folders" in template_data:
                        header["folders"].extend(template_data["folders"])
                    if "settings" in template_data:
                        header.setdefault("settings", {}).update(
                            template_data["settings"]
                        )
                    if "extensions" in template_data:
                        header.setdefault("extensions", {}).setdefault(
                            "recommendations", []
                        ).extend(template_data["extensions"]["recommendations"])

    data = json.dumps(header, indent=2, sort_keys=True)

    with open(workspace_path, "w") as workspace_file:
        workspace_file.write(data)

    print(f"Workspace '{workspace_name}' created at '{workspace_path}'.")


def get_workspace_suffixes(workspace_name):
    github_parent_dir = os.getenv("GITHUB_PARENT_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PARENT_DIR environment variable is not set.")
    projects_dir = Path(github_parent_dir)

    tree = Tree()
    tree.ignore(IGNORE_LIST)
    return tree.get_suffixes(projects_dir / workspace_name)


def get_workspace_name() -> str:
    import argparse

    parser = argparse.ArgumentParser(description="Generate a workspace template.")
    parser.add_argument(
        "workspace_name", type=str, help="The name of the workspace to create."
    )

    args = parser.parse_args()

    return args.workspace_name


if __name__ == "__main__":
    workspace_dir = Path("generated_workspaces")
    generate_workspace(get_workspace_name(), workspace_dir)
