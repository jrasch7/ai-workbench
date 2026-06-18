# Paperclip Vendor Snapshot

This directory contains a vendored source snapshot of Paperclip for AI Workbench integration.

## Upstream

- Remote: `https://github.com/paperclipai/paperclip.git`
- Branch at capture time: `master`
- Commit at capture time: `5f16efb3d018588345152153eba62507fbe36ed9`

## Why vendored

AIW needs the Paperclip control plane to be reproducible from this repository when moving between machines.

The local lab clone remains ignored under `.aiw/lab/`, but this `vendor/paperclip/` snapshot is committed so another machine can pull the integrated project source.

## Not included

- `.git/`
- `node_modules/`
- build/cache folders
- local databases
- logs
- `.env` / local secret files
