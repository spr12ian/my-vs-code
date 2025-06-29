import os

def generate_workspace(workspace_name, base_path):
    """
    Generates a workspace directory structure with a README file.

    Args:
        workspace_name (str): The name of the workspace.
        base_path (str): The base path where the workspace will be created.
    """
    workspace_path = os.path.join(base_path, workspace_name)

    # Create the workspace directory
    os.makedirs(workspace_path, exist_ok=True)

    # Create a README file in the workspace directory
    readme_path = os.path.join(workspace_path, "README.md")
    with open(readme_path, "w") as readme_file:
        readme_file.write(f"# {workspace_name}\n\nThis is the {workspace_name} workspace.\n")

    print(f"Workspace '{workspace_name}' created at '{workspace_path}'.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a workspace directory structure.")
    parser.add_argument("workspace_name", type=str, help="The name of the workspace to create.")
    parser.add_argument("--base_path", type=str, default=".", help="The base path where the workspace will be created.")

    args = parser.parse_args()

    project_dir = os.environ.get("GITHUB_PARENT_DIR_DIR", args.base_path)
    generate_workspace(args.workspace_name, project_dir)
