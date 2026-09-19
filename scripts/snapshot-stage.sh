#!/usr/bin/env bash
# Copies the working service into stage-N/ and freezes it there.
#
# Grading rule: stage-N is graded against every suite up to N, and a folder
# that also passes suite N+1 earns nothing for its own stage. So a stage is
# snapshotted the day it is accepted, before the next stage's work starts, and
# is not edited afterwards except to repair its own suite.
set -euo pipefail
cd "$(dirname "$0")/.."

n=${1:?usage: snapshot-stage.sh <n>}
dest="stage-$n"

[ -d "$dest" ] && { echo "FAIL: $dest already exists. A snapshotted stage is frozen; delete it deliberately if you really mean to redo it."; exit 1; }

echo "==> checks must pass in the working copy first"
( cd service && npm test >/dev/null ) || { echo "FAIL: service checks are not green"; exit 1; }

mkdir -p "$dest"
tar -cf - -C service --exclude='.git' --exclude='node_modules' --exclude='*.db*' . | tar -xf - -C "$dest"

echo "==> $dest written:"
find "$dest" -type f | sort | sed 's/^/    /'
echo
echo "Next: scripts/offline-build.sh $dest, then record the result in evidence/stage-$n.md,"
echo "then confirm $dest does NOT contain anything the next stage introduces."
