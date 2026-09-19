#!/usr/bin/env bash
# Proves a stage starts and answers in a clean, network-isolated container.
# A service that does not start scores zero, so this is the gate every stage
# passes before its folder is snapshotted, and again before submission.
#
#   scripts/offline-build.sh stage-1     # a snapshotted stage
#   scripts/offline-build.sh service     # the working copy
set -euo pipefail
cd "$(dirname "$0")/.."

dir=${1:?usage: offline-build.sh <dir>}
[ -f "$dir/Dockerfile" ] || { echo "FAIL: $dir has no Dockerfile"; exit 1; }
tag="darkfactory-${dir//\//-}:offline"
name="darkfactory-check-$$"
cpus=${CPUS:-1}
memory=${MEMORY:-512m}

cleanup() { docker rm -f "$name" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "==> building $dir with no network"
docker build --network=none -t "$tag" "$dir"

echo "==> running with no network, cpus=$cpus memory=$memory"
docker run -d --name "$name" --network=none --cpus="$cpus" --memory="$memory" "$tag" >/dev/null

echo "==> waiting for the service to answer"
ok=""
for _ in $(seq 1 30); do
  if docker exec "$name" node -e \
    "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))" 2>/dev/null; then
    ok=1; break
  fi
  sleep 1
done

if [ -z "$ok" ]; then
  echo "FAIL: the service never answered inside the container"
  docker logs "$name" 2>&1 | tail -30
  exit 1
fi

echo "==> checks, inside the same isolated container"
docker cp "$dir/tests" "$name:/app/tests" 2>/dev/null || true
if docker exec -e NODE_ENV=test "$name" node --test 2>&1 | tail -12; then
  echo "PASS: $dir builds, starts and passes its checks with no network."
else
  echo "FAIL: $dir starts but its checks do not pass in the container"
  exit 1
fi
