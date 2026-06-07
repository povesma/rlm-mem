# rlm-mem has moved → [embo](https://github.com/povesma/embo)

**This project was renamed from `rlm-mem` to `embo`.** Same project —
a spec-driven Claude Code workflow backed by a persistent codebase
index (RLM) and cross-session memory (claude-mem). New name, new home.

## → New repository: https://github.com/povesma/embo

All current code, documentation, and releases live there. **This
repository is no longer maintained** and exists only to redirect
existing links so current users are not left stranded.

## Migrating an existing install

If you already cloned `rlm-mem`, point your clone at the new remote:

```bash
git remote set-url origin https://github.com/povesma/embo.git
git pull
```

Or re-clone from scratch:

```bash
git clone https://github.com/povesma/embo ~/embo
cd ~/embo && bash install.sh
```

The command set is unchanged — `/dev:init`, `/dev:start`, `/dev:prd`,
`/dev:tech-design`, `/dev:tasks`, `/dev:impl`, and the rest work
exactly as before. See the new repository's README for full install
and usage instructions.

## Why the rename

`rlm-mem` named the underlying technologies (RLM + mem). `embo` is a
shorter, cleaner project name. There is no functional change.
