#!/usr/bin/env bash
set -euo pipefail
trap 'exit 0' ERR

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty') || exit 0
[ -z "$FILE_PATH" ] && exit 0

case "$FILE_PATH" in
  *.md|*.json|*.yaml|*.yml|*.toml|*.txt) exit 0 ;;
esac
case "$FILE_PATH" in
  */tasks/*|*/.claude/*) exit 0 ;;
esac

MARKER="$HOME/.claude/rlm_state/.impl-active"
if [ -f "$MARKER" ]; then
  STALE=$(find "$MARKER" -mmin +120 2>/dev/null)
  if [ -z "$STALE" ]; then
    exit 0
  else
    rm -f "$MARKER"
  fi
fi

jq -n '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "ask",
    permissionDecisionReason: "⚠️ No /impl session active — this code edit is undocumented.\n\nConsider:\n  • /rlm-mem:develop:impl — start documented implementation\n  • /rlm-mem:plan:prd — create docs first\n  • Allow this edit if it is a quick fix\n\n(docs-first-guard hook — see README §Hooks)"
  }
}'
