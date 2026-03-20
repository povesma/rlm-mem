#!/usr/bin/env bash
# install.sh — sync this repo's .claude/ files to ~/.claude/
# Run after cloning or after making changes in .claude/ to update your installation.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$HOME/.claude"

echo "Syncing from $REPO_DIR/.claude/ to $TARGET/"

# agents
mkdir -p "$TARGET/agents"
cp "$REPO_DIR/.claude/agents/"*.md "$TARGET/agents/"
echo "  agents: $(ls "$REPO_DIR/.claude/agents/"*.md | wc -l | tr -d ' ') files"

# commands/rlm-mem
mkdir -p "$TARGET/commands/rlm-mem"
cp -r "$REPO_DIR/.claude/commands/rlm-mem/"* "$TARGET/commands/rlm-mem/"
echo "  commands/rlm-mem: synced"

# hooks
if ls "$REPO_DIR/.claude/hooks/"*.sh 2>/dev/null | grep -q .; then
    mkdir -p "$TARGET/hooks"
    cp "$REPO_DIR/.claude/hooks/"*.sh "$TARGET/hooks/"
    chmod +x "$TARGET/hooks/"*.sh
    echo "  hooks: $(ls "$REPO_DIR/.claude/hooks/"*.sh | wc -l | tr -d ' ') files"
fi

# rlm_scripts
mkdir -p "$TARGET/rlm_scripts"
cp "$REPO_DIR/.claude/rlm_scripts/"*.py "$TARGET/rlm_scripts/"
echo "  rlm_scripts: $(ls "$REPO_DIR/.claude/rlm_scripts/"*.py | wc -l | tr -d ' ') files"

# statusline
if [ -f "$REPO_DIR/.claude/statusline.sh" ]; then
    cp "$REPO_DIR/.claude/statusline.sh" "$TARGET/statusline.sh"
    chmod +x "$TARGET/statusline.sh"
    echo "  statusline: copied to $TARGET/statusline.sh"

    SETTINGS="$TARGET/settings.json"
    if ! command -v jq >/dev/null 2>&1; then
        echo ""
        echo "  statusline settings.json: jq not found — manual step required"
        echo "    Install jq:  brew install jq   (macOS)"
        echo "                 apt install jq    (Linux)"
        echo "    Then add to $SETTINGS:"
        echo '    { "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" } }'
    else
        if [ ! -f "$SETTINGS" ]; then
            echo '{}' > "$SETTINGS"
        fi
        if jq -e '.statusLine' "$SETTINGS" > /dev/null 2>&1; then
            echo "  settings.json: statusLine already configured — skipping"
            echo "    (run /statusline-setup to switch scripts)"
        else
            echo ""
            read -r -p "  Add statusLine to $SETTINGS? [y/N] " yn
            case "$yn" in
                [Yy]*)
                    jq '.statusLine = {"type": "command", "command": "~/.claude/statusline.sh"}' \
                        "$SETTINGS" > /tmp/_rlm_settings.tmp \
                        && mv /tmp/_rlm_settings.tmp "$SETTINGS"
                    echo "  settings.json: statusLine added"
                    echo "  Restart Claude Code for the change to take effect."
                    ;;
                *)
                    echo "  settings.json: skipped — see README §Statusline for manual step"
                    ;;
            esac
        fi
    fi
fi

# docs-first-guard hook registration
SETTINGS="$TARGET/settings.json"
if command -v jq >/dev/null 2>&1 && [ -f "$SETTINGS" ]; then
    if ! jq -e '.hooks.PreToolUse[]? | select(.hooks[]?.command | test("docs-first-guard"))' \
        "$SETTINGS" >/dev/null 2>&1; then
        jq '.hooks.PreToolUse += [{
            "matcher": "Edit|Write",
            "hooks": [{
                "type": "command",
                "command": "bash ~/.claude/hooks/docs-first-guard.sh"
            }]
        }]' "$SETTINGS" > /tmp/_rlm_settings.tmp \
            && mv /tmp/_rlm_settings.tmp "$SETTINGS"
        echo "  docs-first-guard: registered in settings.json"
    else
        echo "  docs-first-guard: already registered in settings.json"
    fi
else
    echo "  docs-first-guard: jq not found or settings.json missing — manual hook setup needed"
    echo "    See README §Hooks for the PreToolUse entry to add"
fi

echo ""
echo "Done. Run /rlm-mem:discover:start to begin a session."
