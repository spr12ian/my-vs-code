SHELL := /bin/bash

.PHONY: all

all:
	@echo "Syncing settings files..." && \
	jq empty settings-human.json && \
	diff <(jq -S . settings.json) <(jq -S . settings-human.json) && \
	jq -c . settings-human.json >settings.json  && \
    jq -S . settings.json >settings-human.json && \
	jq empty settings.json
