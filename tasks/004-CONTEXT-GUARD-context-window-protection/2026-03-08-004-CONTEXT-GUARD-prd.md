# Context Guard - Product Requirements Document

## Introduction/Overview

When a Claude Code session approaches its context window limit,
the agent loses track of earlier conversation, makes worse
decisions, and may produce inconsistent or incorrect output.
Despite this, the agent will happily start implementing a new
feature at 90% context — then fail partway through, leaving
code in an inconsistent state.

The Context Guard is a `UserPromptSubmit` hook that reads the
current context usage from the session transcript and blocks
new development work when usage exceeds 80%. Only
docs/memory/task updates are permitted at that point.

## Objectives & Success Metrics

**Business Objectives:**
- Prevent mid-feature failures caused by context exhaustion
- Keep session state consistent (code always matches docs)
- Force developers to start fresh sessions for new features
  rather than cramming work into an exhausted context

**Success Metrics:**
- Hook fires correctly when context ≥ 80% and user submits
  a development request (verified by manual test)
- Hook passes through when context < 80% (no false positives)
- Hook passes through for allowed operations (docs, memory,
  tasks) even at 100% context
- Zero false blocks on `/rlm-mem:discover:start`,
  `/rlm-mem:plan:check`, commit commands

## User Personas & Use Cases

### User Personas

**Solo Developer**: Uses RLM-Mem daily, often loses track of
context level mid-session.
- **Needs**: Automatic protection without manual monitoring
- **Goals**: Never have a feature implementation fail halfway
  due to context exhaustion

### User Stories

- As a developer, I want the agent to block new feature
  implementation when context is ≥ 80% so that I don't start
  work that can't be completed in this session
- As a developer, I want docs/memory/task updates to always
  be allowed regardless of context level so that I can save
  state before starting a fresh session
- As a developer, I want a clear message explaining why the
  request was blocked and what I should do instead

### Use Cases

1. **Blocked at threshold**: Developer types "implement story
   3.2" at 85% context. Hook fires, returns `continue: false`
   with a message: "Context is 85% full. Start a fresh session
   for new development. You can still update docs, tasks, or
   save to claude-mem."
2. **Allowed docs update**: Developer types "update the task
   list to mark 3.1 as done" at 90% context. Hook detects
   this is a docs operation, passes through.
3. **Below threshold**: Developer types "implement story 1.1"
   at 60% context. Hook reads transcript, finds usage below
   80%, passes through normally.

## Feature Scope

### In Scope

- `UserPromptSubmit` command hook (bash script)
- Reads `transcript_path` from hook stdin to measure context
  usage
- Blocks requests classified as new development work when
  usage ≥ 80%
- Allows requests classified as docs/memory/task updates
  regardless of context level
- Returns clear `systemMessage` explaining the block and
  what's allowed
- Threshold configurable via env var (default: 80)
- Hook script shipped in this repo, installed to `~/.claude/`
- Installation instructions added to README

### Out of Scope

- Prompt-based (LLM) classification of request type — bash
  only, no LLM call in the hook
- Automatic session compaction or summarization
- Per-command-tree configuration (same rule applies to all)
- GUI or status bar integration

### Future Considerations

- Soft warning at 70% (allow but warn)
- Auto-save to claude-mem triggered when threshold hit
- Per-project threshold override via `.claude/settings.json`

## Functional Requirements

### Cucumber/Gherkin Scenarios

```gherkin
Feature: Context window protection

Scenario: Block new development above threshold
  Given context window usage is 85%
  When the user submits "implement story 3.2"
  Then the hook returns continue: false
  And Claude sees a systemMessage explaining the block
  And the message suggests starting a fresh session

Scenario: Allow docs update above threshold
  Given context window usage is 90%
  When the user submits "update the task list"
  Then the hook returns continue: true
  And Claude proceeds normally

Scenario: Allow all requests below threshold
  Given context window usage is 70%
  When the user submits any request
  Then the hook returns continue: true

Scenario: Configurable threshold
  Given CONTEXT_GUARD_THRESHOLD=85 is set
  When context window usage is 82%
  And the user submits a development request
  Then the hook returns continue: true
```

### Detailed Requirements

1. **Context measurement**: The hook script reads
   `transcript_path` from stdin JSON and derives context usage
   percentage. The transcript file format and token counting
   method must be determined during implementation — this is
   the primary technical research task.

2. **Request classification**: The hook classifies
   `user_prompt` (from stdin JSON) as either:
   - **Blocked at threshold**: implementing, coding, building,
     creating features, writing code, starting new stories
   - **Always allowed**: updating docs, tasks, memory,
     claude-mem, saving, committing, checking status, planning

3. **Block response**: When blocking, output:
   ```json
   {
     "continue": false,
     "systemMessage": "Context is {N}% full (threshold: 80%). Start a fresh session for new development. Allowed now: update docs, tasks, claude-mem, or commit."
   }
   ```

4. **Pass-through response**: When allowing, exit 0 (no
   output needed).

5. **Threshold configuration**: Read from env var
   `CONTEXT_GUARD_THRESHOLD`, default 80.

6. **Fail open**: If the script cannot read or parse the
   transcript, pass through (`exit 0`). Never block due to a
   script error.

7. **Installation**: Hook script at
   `.claude/hooks/context-guard.sh` in this repo. User copies
   to `~/.claude/hooks/` and adds hook config to
   `~/.claude/settings.json`.

## Non-Functional Requirements

### Performance
- Hook must complete in < 2 seconds (UserPromptSubmit blocks
  until the hook returns)
- No network calls — purely local file reading

### Reliability
- Fail open: script errors never block the user
- Handles missing/unreadable transcript gracefully
- Handles malformed JSON in stdin gracefully

### Usability
- Block message is actionable: tells user exactly what they
  can do (fresh session, docs update, commit)
- No false positives on common non-development commands
  (`/start`, `/check`, commit, search)

### Architecture
- Single bash script, no external dependencies beyond `jq`
- Hook config snippet provided for copy-paste into
  `~/.claude/settings.json`

## Dependencies & Risks

### Dependencies
- **Claude Code hook system**: `UserPromptSubmit` command hook
  (confirmed available)
- **`jq`**: Required to parse stdin JSON in bash
- **transcript_path format**: The exact format of the
  transcript file and whether it contains token counts must
  be verified during implementation — primary unknown

### Risks
- **Risk 1**: Transcript file doesn't contain token counts —
  *Mitigation*: Fall back to character count as a proxy, or
  discover an alternative source for context % during
  implementation
- **Risk 2**: Bash keyword classification produces false
  positives/negatives —
  *Mitigation*: Conservative keyword list; user can override
  by prefixing prompt with "override:"
- **Risk 3**: Hook adds latency to every prompt —
  *Mitigation*: Skip transcript parsing when file is small
  (low context is safe to allow without checking)

## Open Questions

- What is the exact format of the file at `transcript_path`?
  Does it contain token counts or only message text?
- Is there an alternative source for context % such as an
  env var set by Claude Code or a sidecar file alongside the
  transcript?
