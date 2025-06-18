#!/usr/bin/env bash
mypy "$@" || mypy --install-types --non-interactive
