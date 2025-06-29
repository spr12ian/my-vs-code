import os
from pathlib import Path

IGNORE_LIST = [".git", ".hg", ".mypy_cache", ".svn", "__pycache__", "venv"]


class Tree:
    def __init__(self) -> None:
        self.ignoreList: list[str] = []
        self.file_suffixes: dict[str, int] = {}

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


def get_workspace_name() -> str:
    import argparse

    parser = argparse.ArgumentParser(description="Generate a workspace template.")
    parser.add_argument(
        "workspace_name", type=str, help="The name of the workspace to create."
    )

    args = parser.parse_args()

    return args.workspace_name


if __name__ == "__main__":
    github_parent_dir = os.getenv("GITHUB_PARENT_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PARENT_DIR environment variable is not set.")
    projects_dir = Path(github_parent_dir)
    workspace_path = projects_dir / get_workspace_name()

    tree = Tree()
    tree.ignore(IGNORE_LIST)
    tree.walk(workspace_path)
    tree.print_summary()
