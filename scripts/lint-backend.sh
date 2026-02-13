#!/usr/bin/env bash
set -euo pipefail

if [[ -x ".venv/bin/pylint" ]]; then
  exec ".venv/bin/pylint" backend/
fi

if command -v pylint >/dev/null 2>&1; then
  exec pylint backend/
fi

echo "pylint not installed; skipping backend lint."
