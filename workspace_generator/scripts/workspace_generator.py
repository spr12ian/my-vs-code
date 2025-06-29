import json
from pathlib import Path


def generate_workspace(workspace_name: str, base_path: Path) -> None:
    """
    Generates a vscode workspace file (template).

    Args:
        workspace_name (str): The name of the workspace.
        base_path (str): The base path where the workspace will be created.
    """
    workspace_path = base_path / (workspace_name + ".code-workspace")

    header = {"folders": [{"path": f"../../{workspace_name}"}]}

    data = json.dumps(header, indent=2, sort_keys=True)

    with open(workspace_path, "w") as workspace_file:
        workspace_file.write(data)

    print(f"Workspace '{workspace_name}' created at '{workspace_path}'.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a workspace directory structure."
    )
    parser.add_argument(
        "workspace_name", type=str, help="The name of the workspace to create."
    )
    parser.add_argument(
        "--base_path",
        type=str,
        default=".",
        help="The base path where the workspace will be created.",
    )

    args = parser.parse_args()

    workspace_dir = Path("generated_workspaces")
    generate_workspace(args.workspace_name, workspace_dir)
