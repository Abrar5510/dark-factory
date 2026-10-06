# Stage 1: Pocketful Payments and Settlements Service

## Overview
HTTP service for payments, requests, splits, and settlements between users.

## Requirements
See `/Users/abrar/band/dark-factory-wearedevs/pocketful/spec/stage-1.md` for complete specification.

## Timeline
- Start: 09:04:45 PKT 2026
- 45-minute total runtime
- 30-minute deadline for committed stage-1 that builds and serves

## Implementation Status
- Builder: Implementing service
- Second Reader: Creating reference implementation
- Referee: Will check for divergences

## Checks
Run isolated checks with:
```bash
python -m harness run --track pocketful --repo /Users/abrar/band/band-work/result --stage 1 --mode isolated --out /Users/abrar/band/band-work/checks/stage1-isolated-1
```

From working folder with .venv activated.