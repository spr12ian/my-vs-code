.DEFAULT_GOAL := help

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
ifeq (, $(wildcard Code/User/settings.json))
$(error Code/User/settings.json does not exist. Create it before using this Makefile.)
endif

LOCAL_SETTINGS_FILE := Code/User/settings.json

.PHONY: \
	a_z_settings \
	compare \
	debug \
	deploy \
	export_extensions \
	find-all \
	help \
	list_extensions \
	list_extensions_installed \
	list_extensions_remote \
	list_extensions_remote_installed \
	list_extensions_remote_installed_json \
	load_extensions \
	settings_file_exists \
	tree

a_z_settings: ## Put settings.json in alphabetical order
	@echo "Put settings in alphabetical order..." && \
	jq empty "$(LOCAL_SETTINGS_FILE)" && \
	jq -S . "$(LOCAL_SETTINGS_FILE)" | sponge "$(LOCAL_SETTINGS_FILE)"


compare: ## Compare settings files
	echo "Comparing settings files..." && \
	diff <(jq -S . "$(LOCAL_SETTINGS_FILE)") <(jq -S . "$(VSCODE_SETTINGS_FILE)") && \
	echo "No differences found between settings files." || \
	echo "Differences found — Consider make sync."

debug: ## Show env vars
	@	echo "LOCAL_SETTINGS_FILE: $(LOCAL_SETTINGS_FILE)"
	@	ls -l "$(LOCAL_SETTINGS_FILE)"
	@	echo "VSCODE_SETTINGS_FILE: $(VSCODE_SETTINGS_FILE)"
	@	ls -l "$(VSCODE_SETTINGS_FILE)"

deploy:
	@echo "Deploying settings file to VS Code..." && \
	@cp settings.json $(VSCODE_SETTINGS_FILE) && \
	@echo "Deployment complete."

find_all:
	@echo "Finding all VS Code settings.json files..."
	@find ~ -type f -name settings.json | grep -i ".vscode\|Code/User" || true
	@echo "NOTE: settings.json in ~/.vscode-server is auto-generated. Do not edit manually."

help:  ## Auto-generate help from target comments
	@awk 'BEGIN {FS = ":.*?## "}; \
		/^[a-zA-Z_-]+:.*?## / { \
			printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST) | sort

export_extensions:
	@echo "Exporting VS Code extensions..."
	@code --list-extensions | sort > extensions.txt
	@echo "Extensions exported to extensions.txt."

list_extensions:
	@echo "Listing all VS Code extensions..."
	@code --list-extensions | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing " \
	      "extensions."
	@echo "To export installed extensions, use 'code --list-extensions > extensions.txt'."

list_extensions_installed:
	@echo "Listing installed VS Code extensions..."
	@code --list-extensions --show-versions | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing " \
	      "extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions > " \
	      "extensions.txt'."

list_extensions_remote:
	@echo "Listing remote VS Code extensions..."
	@code --list-extensions --show-versions --remote || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing " \
	      "extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote > extensions.txt'."

list_extensions_remote_installed:
	@echo "Listing installed remote VS Code extensions..."
	@code --list-extensions --show-versions --remote | sort || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing " \
	      "extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote > extensions.txt'."

list_extensions_remote_installed_json:
	@echo "Listing installed remote VS Code extensions in JSON format..."
	@code --list-extensions --show-versions --remote | jq -R . | jq -s . || true
	@echo "NOTE: Use 'code --install-extension <extension-id>' to install any missing " \
	      "extensions."
	@echo "To export installed extensions, use 'code --list-extensions --show-versions --remote | jq -R . | jq -s . > extensions.json'."

load_extensions:
	@echo "Loading VS Code extensions from extensions.json..."
	xargs -n 1 code --install-extension < extensions.txt
	@echo "Extensions loaded successfully."

tree: ## list contents of directories in a tree-like format
	tree -I '__pycache__|.git|.hatch' -a -F
