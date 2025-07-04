generate_workspaces combines some, or all, of these components into a single workspace
template for each project (one project per GitHib repo); the components used will
depend on the files / file suffixes found in the project

The default component (_default.json) will be included for every workspace

Every workspace should have a README.md and a Makefile as well as a .git directory
