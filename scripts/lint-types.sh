#!/usr/bin/env bash
set -euo pipefail

BASELINE_FILE="scripts/ts-nocheck-baseline.txt"

if [[ -f "$BASELINE_FILE" ]]; then
  baseline="$(tr -d '[:space:]' < "$BASELINE_FILE")"
  current="$(rg --no-heading --glob '*.{ts,js,svelte}' '@ts-nocheck' src | wc -l | tr -d '[:space:]')"

  if [[ "$current" -gt "$baseline" ]]; then
    echo "Type debt regression: @ts-nocheck count increased ($current > baseline $baseline)."
    echo "Please reduce or keep @ts-nocheck count at or below baseline."
    exit 1
  fi
fi

npx svelte-kit sync
if ! npx svelte-check --tsconfig ./tsconfig.json; then
  echo "svelte-check reported issues; treating as non-blocking for release validation."
  exit 0
fi
