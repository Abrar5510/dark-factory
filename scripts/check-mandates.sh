#!/usr/bin/env bash
# Fails if any seat mandate names something specific to this track, this spec,
# or this stack. A mandate that does is an instant disqualification, so this
# runs on every commit and again before submission.
set -uo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "--selftest" ]; then
  tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
  printf 'Own the wallet balance and POST it.\n' > "$tmp/bad.md"
  if "$0" "$tmp" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: a mandate naming a domain noun was not caught"; exit 1
  fi
  printf 'Own the work item. Post the evidence. Get the result.\n' > "$tmp/good.md"
  rm "$tmp/bad.md"
  if ! "$0" "$tmp" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: ordinary English was flagged as a leak"; exit 1
  fi
  echo "SELFTEST PASS: catches leaks, ignores ordinary English."; exit 0
fi

targets=(mandates)
[ $# -gt 0 ] && targets=("$@")

list=scripts/denylist.txt
strip() { grep -vE '^\s*(#|$)' | sed 's/[[:space:]]*$//' | paste -sd'|' -; }

insens=$(sed '/^## case-sensitive/,$d' "$list" | strip)
sens=$(sed -n '/^## case-sensitive/,$p' "$list" | tail -n +2 | strip)

hits=$(grep -rninE "\b(${insens})\b" "${targets[@]}" 2>/dev/null || true)
[ -n "$sens" ] && hits="${hits}$(grep -rnE "\b(${sens})\b" "${targets[@]}" 2>/dev/null || true)"

if [ -n "${hits//[[:space:]]/}" ]; then
  echo "FAIL: track-, spec- or stack-specific terms found in ${targets[*]}:"
  echo "$hits"
  echo
  echo "Move this detail into the task you paste into the room."
  exit 1
fi

n_files=$(find "${targets[@]}" -name '*.md' | wc -l | tr -d ' ')
n_terms=$(grep -vcE '^\s*(#|$)' "$list")
echo "PASS: $n_files mandate file(s) clean against $n_terms denied terms."
