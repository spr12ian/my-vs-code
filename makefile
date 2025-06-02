# bash is required for some of the syntax used in the Makefile
SHELL := /bin/bash

# Default for Linux
DEPLOYMENT_SETTINGS := $(HOME)/.config/Code/User/settings.json

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
	@IS_WSL=$$(uname -r | grep -i microsoft || true); \
	if [ -n "$$IS_WSL" ]; then \
	  WINDOWS_USER=$$(cmd.exe /c "echo %USERNAME%" | tr -d '\r'); \
	  DEPLOYMENT_SETTINGS="/mnt/c/Users/$$WINDOWS_USER/AppData/Roaming/Code/User/settings.json"; \
	else \
	  DEPLOYMENT_SETTINGS="$(DEPLOYMENT_SETTINGS)"; \
	fi; \
	echo "Comparing settings files..." && \
	diff <(jq -S . settings.json) <(jq -S . $$DEPLOYMENT_SETTINGS) && \
	echo "No differences found between settings files." || \
	echo "Differences found — consider running 'make all' to sync."

debug:
	@IS_WSL=$$(uname -r | grep -i microsoft || true); \
	if [ -n "$$IS_WSL" ]; then \
	  WINDOWS_USER=$$(cmd.exe /c "echo %USERNAME%" | tr -d '\r'); \
	  DEPLOYMENT_SETTINGS="/mnt/c/Users/$$WINDOWS_USER/AppData/Roaming/Code/User/settings.json"; \
	else \
	  DEPLOYMENT_SETTINGS="$(DEPLOYMENT_SETTINGS)"; \
	fi; \
	echo "IS_WSL: $$IS_WSL"; \
	echo "WINDOWS_USER: $$WINDOWS_USER"; \
	echo "DEPLOYMENT_SETTINGS: $$DEPLOYMENT_SETTINGS"

deploy:
	@IS_WSL=$$(uname -r | grep -i microsoft || true); \
	if [ -n "$$IS_WSL" ]; then \
	  WINDOWS_USER=$$(cmd.exe /c "echo %USERNAME%" | tr -d '\r'); \
	  DEPLOYMENT_SETTINGS="/mnt/c/Users/$$WINDOWS_USER/AppData/Roaming/Code/User/settings.json"; \
	else \
	  DEPLOYMENT_SETTINGS="$(DEPLOYMENT_SETTINGS)"; \
	fi; \
	@echo "Deploying settings file to VS Code..." && \
	@cp settings.json $$DEPLOYMENT_SETTINGS && \
	@echo "Deployment complete."

find-all:
	@echo "Finding all VS Code settings.json files..."
	@find ~ -type f -name settings.json | grep -i ".vscode\|Code/User" || true
	@echo "NOTE: settings.json in ~/.vscode-server is auto-generated. Do not edit manually."
