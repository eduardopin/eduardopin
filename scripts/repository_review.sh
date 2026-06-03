#!/usr/bin/env bash
set -euo pipefail

required=(README.md SECURITY.md CONTRIBUTING.md CHANGELOG.md)
for file in "${required[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "missing required file: $file" >&2
    exit 1
  fi
done

if git ls-files | grep -q '^.codex-repo-context.json$'; then
  echo "local context artifact is tracked" >&2
  exit 1
fi

echo "repository review checks passed"
