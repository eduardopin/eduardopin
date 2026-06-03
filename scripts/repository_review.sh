#!/usr/bin/env bash
set -euo pipefail

required=(README.md SECURITY.md CONTRIBUTING.md CHANGELOG.md)
for file in "${required[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "missing required file: $file" >&2
    exit 1
  fi
done

if git ls-files | grep -E '(^|/)\.env$|\.tfstate(\..*)?$'; then
  echo "sensitive local file pattern is tracked" >&2
  exit 1
fi

echo "repository review checks passed"
