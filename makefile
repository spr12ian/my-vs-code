# bash is required for some of the syntax used in the Makefile
SHELL := /bin/bash

# Check jq installed
ifeq (, $(shell which jq))
$(error jq is not installed. Please install jq to use this Makefile.)
endif

# Check diff installed
ifeq (, $(shell which diff))
$(error diff is not installed. Please install diff to use this Makefile.)
endif

# Check source file exists
ifeq (, $(wildcard settings.json))
$(error settings.json does not exist. Please create it before running this Makefile.)
endif

.PHONY: all compare debug find-all deploy

all:
	@echo "Put settings in alphabetical order..." && \
	jq empty settings.json && \
	jq -S . settings.json > settings.tmp && mv settings.tmp settings.json

compare:
	echo "Comparing settings files..." && \
	diff <(jq -S . settings.json) <(jq -S . $(VSCODE_SETTINGS_FILE)) && \
	echo "No differences found between settings files." || \
	echo "Differences found — consider running 'make all' to sync."

debug:
	@	echo "VSCODE_SETTINGS_FILE: $(VSCODE_SETTINGS_FILE)"

deploy:
	@echo "Deploying settings file to VS Code..." && \
	@cp settings.json $(VSCODE_SETTINGS_FILE) && \
	@echo "Deployment complete."

find-all:
	@echo "Finding all VS Code settings.json files..."
	@find ~ -type f -name settings.json | grep -i ".vscode\|Code/User" || true
	@echo "NOTE: settings.json in ~/.vscode-server is auto-generated. Do not edit manually."

export_extensions:
	@echo "Exporting VS Code extensions..."
	@code --list-extensions | sort > extensions.txt
	@echo "Extensions exported to extensions.txt."

list-extensions:
	@echo "Listing all VS Code extensions..."
	@code --list-extensions | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing extensions."
	@echo "To export installed extensions, use 'code --list-extensions > extensions.txt'."
list-extensions-installed:
	@echo "Listing installed VS Code extensions..."
	@code --list-extensions --show-versions | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions > extensions.txt'."
list-extensions-remote:
	@echo "Listing remote VS Code extensions..."
	@code --list-extensions --show-versions --remote || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote > extensions.txt'."
list-extensions-remote-installed:
	@echo "Listing installed remote VS Code extensions..."
	@code --list-extensions --show-versions --remote | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote > extensions.txt'."
list-extensions-remote-installed-json:
	@echo "Listing installed remote VS Code extensions in JSON format..."
	@code --list-extensions --show-versions --remote | jq -R . | jq -s . || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote | jq -R . | jq -s . > extensions.json'."

load-extensions:
	@echo "Loading VS Code extensions from extensions.json..."
	xargs -n 1 code --install-extension < extensions.txt
	@echo "Extensions loaded successfully."
