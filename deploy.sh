#!/bin/sh
# Publish the live demo (worker.js + site/) to Cloudflare Workers.
set -e
cd "$(dirname "$0")"
mkdir -p site/mandates
cp mandates/*.md site/mandates/
npx wrangler deploy
