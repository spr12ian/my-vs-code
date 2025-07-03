import os
from pathlib import Path
from typing import Any

JSONType = dict[str, Any] | list[Any] | str | int | float | bool | None

def deep_sort(obj: JSONType) -> JSONType:
    if isinstance(obj, dict):
        return {k: deep_sort(obj[k]) for k in sorted(obj)}
    elif isinstance(obj, list):
        # Optionally sort lists of dicts
        if all(isinstance(x, dict) for x in obj):
            # Convert dicts to tuples of sorted items for comparison, then sort
            return [deep_sort(x) for x in sorted(obj, key=lambda d: sorted(d.items()))]
        else:
            return [deep_sort(x) for x in obj]
    else:
        return obj


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

    projects = sorted(
        [
            str(project.name)
            for project in github_parent_path.iterdir()
            if project.is_dir()
        ]
    )

    return projects
