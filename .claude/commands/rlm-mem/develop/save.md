# Session Save — RLM-Mem

Ensure a new session can resume exactly where this one left off.
Run this when context is getting full or before closing Claude Code.

## What Gets Preserved Automatically

- **Task files** (`tasks/**/*-tasks.md`) — on disk, always current
- **Code changes** — on disk
- **Claude-mem observations** — captured automatically via PostToolUse
  hook when files are written and read throughout the session

## What This Command Does

Saves what is NOT automatically captured: key decisions,
agreements, and context from this conversation that would be lost
if the session ended now.

## Process

### 1. Identify What's Missing from Claude-Mem

Search claude-mem for the current session's JIRA ID:

```
mcp__plugin_claude-mem_mcp-search__search(
  query="{jira_id} session decision",
  project="{project_name}",
  limit=5
)
```

Reflect on this session: what decisions, design choices, or
agreements were made that are NOT yet in claude-mem and NOT in
task/tech-design files?

### 2. Save Missing Context

For each significant item not yet captured, write it to a temp file
and Read it (the PostToolUse hook captures it as a claude-mem observation):

Write to `/tmp/claude-mem-{jira_id}-SESSION-DECISION-{n}.md`
(use n=1, 2, 3… for multiple decisions):
```
# {jira_id} - {short description}

[TYPE: SESSION-DECISION]
[PROJECT: {project_name}]

{decision or agreement}

Context: {why it was decided}
```

Then Read `/tmp/claude-mem-{jira_id}-SESSION-DECISION-{n}.md`.

Only save what's genuinely missing. Do not duplicate what's
already in task files or previous claude-mem observations.

### 3. Confirm Ready

Print:

```
## Session Saved ✓

**Continuity check:**
- Task files: up to date on disk
- Claude-mem: {N} new observations saved this session

**To resume:** Start a new session with `/rlm-mem:discover:start`
```

## Final Instructions

- Be concise and fast — this runs at high context
- Focus only on what would be LOST between sessions
- Do NOT re-read all task files (they're on disk, `/start` handles that)
- Do NOT implement anything

## Claude-Mem Unavailable — Critical Failure

If the claude-mem MCP tool is unavailable or returns an error:

**STOP immediately** and display:

```
🚨 CRITICAL: claude-mem is unavailable.

Session context CANNOT be saved. Starting a new session now will
lose all decisions and agreements made in this conversation.

DO NOT close this session until claude-mem is restored.

To fix:
1. Check that the claude-mem plugin is enabled in Claude Code settings
2. Restart Claude Code if the plugin was just installed
3. Run `/rlm-mem:discover:start` to verify claude-mem is reachable

Do NOT proceed with /save until this is resolved.
```

Do NOT output the "Session Saved ✓" summary if claude-mem failed.
