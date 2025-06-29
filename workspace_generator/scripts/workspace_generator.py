import json
import os
from pathlib import Path

IGNORE_LIST = [".git", ".hg", ".mypy_cache", ".svn", "__pycache__", "venv"]


class Tree:
    def __init__(self) -> None:
        self.ignoreList: list[str] = []
        self.file_suffixes: dict[str, int] = {}

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
            suffix = path.suffix.lower() if path.suffix else "No suffix"
            self.file_suffixes[suffix] = self.file_suffixes.get(suffix, 0) + 1

    def walk(self, directory: Path) -> None:
        entries = sorted(
            [entry for entry in directory.iterdir() if entry.name not in self.ignoreList]
        )

        for entry in entries:
            self.register(entry)
            if entry.is_dir():
                self.walk(entry)


def generate_workspace(workspace_name: str, base_path: Path) -> None:
    """
    Generates a vscode workspace file (template).

    Args:
        workspace_name (str): The name of the workspace.
        base_path (Path): The base path where the workspace will be created.
    """
    workspace_path = base_path / (workspace_name + ".code-workspace")

    header = {"folders": [{"path": f"../../{workspace_name}"}]}

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
                        header["folders"].extend(template_data["folders"])
                    if "settings" in template_data:
                        header.setdefault("settings", {}).update(
                            template_data["settings"]
                        )
                    if "extensions" in template_data:
                        header.setdefault("extensions", {}).setdefault(
                            "recommendations", []
                        ).extend(template_data["extensions"]["recommendations"])

    # Deduplicate recommendations if they exist
    if "extensions" in header and "recommendations" in header["extensions"]:
        header["extensions"]["recommendations"] = list(
            sorted(set(header["extensions"]["recommendations"]))
        )

    data = json.dumps(header, indent=2)

    # Ensure output directory exists
    workspace_path.parent.mkdir(parents=True, exist_ok=True)

    with open(workspace_path, "w") as workspace_file:
        workspace_file.write(data)

    print(f"Workspace '{workspace_name}' created at '{workspace_path}'.")


def get_workspace_suffixes(workspace_name: str) -> dict[str, int]:
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
