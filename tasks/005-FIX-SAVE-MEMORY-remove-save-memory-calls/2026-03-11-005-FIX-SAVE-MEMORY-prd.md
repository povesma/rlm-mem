# 005-FIX-SAVE-MEMORY - Product Requirements Document

## Introduction/Overview

All command and agent markdown files in this repo call
`mcp__plugin_claude-mem_mcp-search__save_memory`, a tool that does not
exist in claude-mem v10.5.2. The plugin exposes only read-only MCP tools
(`search`, `timeline`, `get_observations`, `smart_search`,
`smart_unfold`, `smart_outline`). Writing is handled exclusively by a
PostToolUse hook that auto-captures every tool call's input and output
into a SQLite database, then processes them into observations.

Because `save_memory` does not exist, any command or agent that calls it
fails silently: the call is attempted, nothing is saved, and no error
surfaces to the user. The result is that project context (PRDs, tech
designs, task lists, decisions, test findings) is never indexed in
claude-mem, forcing developers to re-read all files at the start of
every session.

The goal of this feature is to replace all `save_memory` calls with an
approach that works within v10.5.2 constraints while preserving the
original intent: structured, semantically-searchable observations that
give future sessions enough context to resume without re-indexing.

## Objectives & Success Metrics

**Business Objectives:**
- Eliminate silent failures caused by calling a non-existent MCP tool
- Preserve the semantic-search value of structured observations
- Achieve reliable context persistence across all 13 commands and 5
  test agents without requiring a claude-mem API change

**Success Metrics:**
- **Zero broken calls**: No command or agent references `save_memory`
  after this fix
- **Context continuity**: After running `discover:init` on a new project,
  running `discover:start` in a fresh session returns meaningful context
  without requiring the user to re-read any files
- **Structured observations**: claude-mem contains typed, tagged
  observations (PRD, TECH-DESIGN, TASK-LIST, etc.) for all indexed
  content — not just raw file reads
- **Coverage**: All 3 command trees (`rlm-mem/`, `coding/`, `rlm/`) and
  all 5 test agents are fixed

## User Personas & Use Cases

### User Personas

**Developer (primary user)**: Installs this repo's commands to `~/.claude/`
and uses them daily across multiple projects.
- **Needs**: Session continuity — starting a fresh session should not
  require re-reading all docs
- **Pain point**: Commands silently fail to save context, so every session
  starts cold

**Claude Code (secondary actor)**: Executes commands and agents. Cannot
call tools that don't exist. Will silently skip failed tool calls.
- **Needs**: Commands must only reference tools that actually exist in
  the active plugin version

### User Stories

- As a developer, I want `discover:init` to seed claude-mem with
  structured project context so that future sessions load quickly
- As a developer, I want `plan:prd`, `plan:tech-design`, and `plan:tasks`
  to persist their output to claude-mem so that I can search past
  decisions without opening files
- As a developer, I want `develop:impl`, `develop:save`, and `plan:check`
  to record implementation decisions so that I can trace why choices
  were made
- As a developer, I want test agents to persist significant findings so
  that recurring bugs are flagged in future test runs

### Use Cases

1. **Project init**: Developer runs `discover:init` on a new project.
   claude-mem is seeded with a structured project overview, existing
   task files, and config details. Next session starts with full context.
2. **PRD creation**: Developer runs `plan:prd`. The PRD is written to
   disk and an observation is created in claude-mem so future sessions
   can find it via `search("PRD requirements")`.
3. **Session resume**: Developer starts a new session, runs
   `discover:start`. It queries claude-mem and surfaces the project
   overview, active tasks, and recent decisions without reading any files.
4. **Test finding persistence**: `test-backend` finds a bug. An
   observation is saved so the next test run can query "past failures
   in this area" and avoid repeating the same investigation.

## Feature Scope

### In Scope

- Replace all `save_memory` calls in `.claude/commands/rlm-mem/` (8
  files: `init`, `prd`, `tech-design`, `tasks`, `check`, `impl`,
  `save`, plus README doc update)
- Replace all `save_memory` calls in `.claude/agents/` (5 agents:
  `test-backend`, `test-review`, `test-e2e-planner`, `test-e2e-generator`,
  `test-e2e-healer`)
- Mirror fixes to `coding/` and `rlm/` command trees where those trees
  have their own copies of affected commands
- Implement the replacement strategy: use `Read` tool calls with
  structured output written to a temp `.md` file, which the PostToolUse
  hook captures as a rich observation
- Update README and CLAUDE.md to document the corrected save approach

### Out of Scope

- Modifying the claude-mem plugin itself
- Adding a `save_memory` tool to the MCP server
- Changing how the PostToolUse hook processes observations
- Fixing the `coding/` or `rlm/` trees for commands that do NOT have
  `save_memory` calls (no regressions introduced)

### Future Considerations

- When claude-mem adds a write API, commands could be updated to use it
  directly alongside the hook approach for more reliable structured saves
- A validation step in `discover:start` could warn if expected
  observation types are missing for a project

## Functional Requirements

### The Replacement Strategy

The PostToolUse hook captures every tool call with full input + output.
To create a structured observation, the command must write a well-tagged
markdown file to a known temp path and then `Read` it. The hook then
captures the file content with full structure intact. The worker service
processes this into a searchable observation.

**Temp file path convention**: `/tmp/claude-mem-<type>-<timestamp>.md`

**Structured content format** (preserved from current `save_memory`
calls):
```
[JIRA: <id>]
[TYPE: <PRD|TECH-DESIGN|TASK-LIST|...>]
[PROJECT: <name>]

<content>
```

For commands that already write a file to disk (e.g., PRD, tech-design,
tasks), the sequence is:
1. Write the output file (already happens today)
2. `Read` the output file (hook captures it with full content)
3. No additional save step needed — the Read IS the save

For commands that save ephemeral content (decisions, completions,
findings) that don't have a persistent file:
1. Write content to `/tmp/claude-mem-<type>-<timestamp>.md`
2. `Read` the temp file (hook captures it)

### Cucumber/Gherkin Scenarios

```gherkin
Feature: Structured context persistence without save_memory

Scenario: discover:init seeds project context
  Given a new project with README.md, CLAUDE.md, and a /tasks/ dir
  When the developer runs discover:init
  Then claude-mem contains a PROJECT-OVERVIEW observation
  And claude-mem contains observations for all existing PRD, tech-
    design, and task-list files
  And no "tool not found" errors appear

Scenario: plan:prd saves PRD to claude-mem
  Given the developer has answered clarifying questions
  When plan:prd writes the PRD file to /tasks/
  Then a PRD observation is searchable in claude-mem
  And the observation includes [TYPE: PRD] and [JIRA: <id>] tags

Scenario: develop:save captures session decisions
  Given a coding session with decisions not yet in any file
  When the developer runs develop:save
  Then each decision is written to a temp .md file and Read
  And the observation appears in claude-mem with [TYPE: SESSION-DECISION]

Scenario: test-backend saves a significant finding
  Given test-backend finds a new bug not covered by existing tests
  When the agent completes its run
  Then a TEST-FINDING observation is in claude-mem
  And no save_memory call was attempted

Scenario: graceful degradation when hook is not active
  Given claude-mem PostToolUse hook is not configured
  When any command or agent writes and reads the temp file
  Then the temp file content is still present on disk
  And the command completes without error (no blocking failure)
```

### Detailed Requirements

1. **No save_memory calls**: No command or agent file in `.claude/`
   may reference `mcp__plugin_claude-mem_mcp-search__save_memory`
2. **Read-based persistence for file artifacts**: For every command that
   produces a file artifact (PRD, tech-design, tasks, init overview),
   the command must `Read` the file immediately after writing it
3. **Temp-file persistence for ephemeral data**: For decisions,
   completions, and findings with no on-disk artifact, the command must
   write a tagged `.md` to `/tmp/` and `Read` it
4. **Tag format preserved**: All observations must retain the existing
   `[JIRA:]`, `[TYPE:]`, `[PROJECT:]` tag format for backward-compatible
   search queries
5. **Graceful degradation**: If hook capture fails (no hook configured),
   commands must still complete successfully — the temp file approach
   fails open (content exists on disk even if not in claude-mem)
6. **All trees updated**: Fixes must be applied to all three command
   trees (`rlm-mem/`, `coding/`, `rlm/`) for every affected command
7. **README updated**: The README and CLAUDE.md must no longer reference
   `save_memory` as an available MCP tool

## Non-Functional Requirements

### Performance
- **Overhead**: Writing and reading a temp file adds <100ms per save
  operation — acceptable
- **Temp file cleanup**: Temp files in `/tmp/` are ephemeral; no cleanup
  step needed (OS manages `/tmp/`)

### Security
- **No credentials in temp files**: Temp files must not contain API
  keys or secrets — only the same content that was already being passed
  to `save_memory`
- **No world-readable secrets**: `/tmp/` is shared; content in temp
  files must be appropriate for local storage

### Usability
- **Transparent to user**: The fix must be invisible to users — the
  same workflow, the same commands, same output. Only the internal
  persistence mechanism changes
- **No new user steps**: Users must not be required to configure
  anything to benefit from the fix

### Reliability
- **Fail open**: A failed write to `/tmp/` must not block the command
  from completing
- **Idempotent**: Running the same command twice must not corrupt
  claude-mem — duplicate observations are acceptable (hook deduplication
  is handled by the worker service)

### Architecture
- **No new dependencies**: The fix uses only `Read`, `Write`, and `Bash`
  tools already available in all commands
- **Minimal change surface**: Each save_memory call is replaced with
  the smallest change that preserves the intent

## Dependencies & Risks

### Dependencies
- **Internal**: PostToolUse hook from claude-mem v10.5.2 must be
  configured in `~/.claude/settings.json` (already confirmed present)
- **Internal**: Worker service processes pending_messages into
  observations — requires claude-mem plugin to be active

### Risks

- **Risk 1: Hook doesn't create structured observations from Read calls**
  Observed behavior shows hook captures full file content via
  `tool_response`, but we haven't confirmed the worker creates a
  properly-tagged observation (with `[TYPE:]` parsing) vs a raw
  file-read record.
  *Mitigation*: Write the structured content to a temp `.md` file with
  the full tag header before Reading it, rather than relying on the
  Read of an existing file to carry the tags. Verify with a real
  claude-mem search after running the updated init.

- **Risk 2: Observation quality degrades vs explicit save_memory**
  `save_memory` had a `title` field for search display. The hook has
  no equivalent — the title is inferred by the worker from content.
  *Mitigation*: Use the `# Title` markdown H1 as the first line of
  every temp file so the worker can extract it as a title.

- **Risk 3: rlm/ tree divergence**
  The `rlm/` tree is installed to `~/.claude/` and may have diverged
  from this repo's source. We need to audit its copies before patching.
  *Mitigation*: Audit `~/.claude/commands/rlm/` during tech-design.

## Open Questions

1. Does the claude-mem worker create searchable observations with
   `[TYPE:]` tag parsing when it processes a Read of a tagged `.md`
   file? Or does it create a raw "file read" observation? **Must verify
   before implementing.**
2. For the `rlm/` tree (which uses ai-docs/ instead of claude-mem for
   some commands), which commands actually need the save approach vs
   which use ai-docs/ file writes as their persistence? Needs audit.
3. Should the `README.md` in `.claude/commands/rlm-mem/` be updated to
   remove `save_memory` from the list of available MCP tools?
   (Likely yes — it's documentation.)
