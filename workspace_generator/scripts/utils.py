import os
from pathlib import Path


def deep_sort(obj):
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


def get_projects():
    github_parent_path = get_github_parent_path()

    projects = sorted(
        [project for project in github_parent_path.iterdir() if project.is_dir()]
    )
    return projects


def get_github_parent_path():
    github_parent_dir = os.getenv("GITHUB_PARENT_DIR")
    if github_parent_dir is None:
        raise EnvironmentError("GITHUB_PARENT_DIR environment variable is not set.")

    github_parent_path = Path(github_parent_dir)
    if not github_parent_path.exists():
        raise EnvironmentError(
            "GITHUB_PARENT_DIR environment variable is not set or invalid."
        )
    if not github_parent_path.is_dir():
        raise EnvironmentError("GITHUB_PARENT_DIR is not a directory.")
    if not github_parent_path.is_absolute():
        github_parent_path = github_parent_path.resolve()
    return github_parent_path
