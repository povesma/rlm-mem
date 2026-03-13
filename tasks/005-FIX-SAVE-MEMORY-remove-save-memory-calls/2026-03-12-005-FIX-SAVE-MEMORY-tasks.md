# 005-FIX-SAVE-MEMORY - Task List

## Relevant Files

- [tasks/005-FIX-SAVE-MEMORY-remove-save-memory-calls/2026-03-11-005-FIX-SAVE-MEMORY-prd.md](
  2026-03-11-005-FIX-SAVE-MEMORY-prd.md)
  :: Product Requirements Document
- [tasks/005-FIX-SAVE-MEMORY-remove-save-memory-calls/2026-03-11-005-FIX-SAVE-MEMORY-tech-design.md](
  2026-03-11-005-FIX-SAVE-MEMORY-tech-design.md)
  :: Technical Design Document
- [.claude/commands/rlm-mem/discover/init.md](
  .claude/commands/rlm-mem/discover/init.md)
  :: Most complex fix — 7 save_memory calls, Pattern A+B
- [.claude/commands/rlm-mem/plan/prd.md](
  .claude/commands/rlm-mem/plan/prd.md)
  :: Pattern A — remove save_memory, add Read instruction
- [.claude/commands/rlm-mem/plan/tech-design.md](
  .claude/commands/rlm-mem/plan/tech-design.md)
  :: Pattern A — remove save_memory, add Read instruction
- [.claude/commands/rlm-mem/plan/tasks.md](
  .claude/commands/rlm-mem/plan/tasks.md)
  :: Pattern A — remove save_memory, add Read instruction
- [.claude/commands/rlm-mem/plan/check.md](
  .claude/commands/rlm-mem/plan/check.md)
  :: Pattern B — write temp file + Read
- [.claude/commands/rlm-mem/develop/impl.md](
  .claude/commands/rlm-mem/develop/impl.md)
  :: Pattern B — write temp file + Read
- [.claude/commands/rlm-mem/develop/save.md](
  .claude/commands/rlm-mem/develop/save.md)
  :: Pattern B — one temp file per decision + Read
- [.claude/commands/rlm-mem/README.md](
  .claude/commands/rlm-mem/README.md)
  :: Remove save_memory from listed MCP tools
- [~/.claude/commands/coding/discover/init.md]
  :: Mirror of rlm-mem/init fix — installed location
- [~/.claude/commands/coding/plan/prd.md]
  :: Mirror of rlm-mem/prd fix — installed location
- [~/.claude/commands/coding/plan/tech-design.md]
  :: Mirror of rlm-mem/tech-design fix — installed location
- [~/.claude/commands/coding/plan/tasks.md]
  :: Mirror of rlm-mem/tasks fix — installed location
- [~/.claude/commands/coding/plan/check.md]
  :: Mirror of rlm-mem/check fix — installed location
- [~/.claude/commands/coding/develop/save.md]
  :: Mirror of rlm-mem/save fix — installed location
- [~/.claude/commands/coding/review/pr-review.md]
  :: coding/ has 2 save_memory calls here, not in rlm-mem
- [.claude/agents/test-backend.md](
  .claude/agents/test-backend.md)
  :: Pattern B — replace save_memory in findings section
- [.claude/agents/test-review.md](
  .claude/agents/test-review.md)
  :: Pattern B — replace save_memory in findings section
- [.claude/agents/test-e2e-planner.md](
  .claude/agents/test-e2e-planner.md)
  :: Pattern B — replace save_memory in findings section
- [.claude/agents/test-e2e-generator.md](
  .claude/agents/test-e2e-generator.md)
  :: Pattern B — replace save_memory in findings section
- [.claude/agents/test-e2e-healer.md](
  .claude/agents/test-e2e-healer.md)
  :: Pattern B — replace save_memory in findings section

## Notes

- TDD does not apply — these are markdown command/agent prompt files,
  not application code. Testing means manually invoking the command
  and verifying no save_memory errors occur and claude-mem receives
  a searchable observation.
- **Pattern A** (file-producing commands): Replace the `save_memory`
  call with: "Read the file you just created. The PostToolUse hook
  captures it automatically."
- **Pattern B** (ephemeral content): Replace the `save_memory` call
  with: Write tagged content to `/tmp/claude-mem-{id}-{TYPE}.md`,
  then Read it. Include `# Title` H1 as first line.
- The `coding/` tree files live at `~/.claude/commands/coding/` (not
  in this repo). Edit them in place with the Edit tool. Do NOT use
  install.sh — it copies rlm-mem/ to ~/.claude/commands/rlm-mem/ only.
- The `rlm/` tree has NO save_memory calls — skip entirely.
- Verification: after each story, grep the patched files for
  `save_memory` to confirm zero remaining calls.

## Tasks

- [X] 1.0 **User Story:** As a developer, I want
  `rlm-mem/discover/init.md` to use write+read instead of
  `save_memory` so that running discover:init reliably seeds
  claude-mem with project context [7/7]
  - [X] 1.1 Read `.claude/commands/rlm-mem/discover/init.md` in
    full to understand all 7 save_memory call sites and surrounding
    context
  - [X] 1.2 Replace the **project overview** save_memory call
    (README+CLAUDE.md synthesis): change to instruct Claude to write
    the synthesized overview to
    `/tmp/claude-mem-{project_name}-PROJECT-OVERVIEW.md` then Read
    it. H1 title line: `# {project_name} - Project Overview`
  - [X] 1.3 Replace the **RLM codebase analysis** save_memory call:
    change to instruct Claude to write the analysis to
    `/tmp/claude-mem-{project_name}-CODEBASE-ANALYSIS.md` then Read
    it. H1 title: `# {project_name} - Codebase Analysis`
  - [X] 1.4 Replace the **PRD file indexing** save_memory calls:
    change to instruct Claude to Read each `*-prd.md` file directly
    (Pattern A — the file already exists on disk, hook captures the
    Read)
  - [X] 1.5 Replace the **tech-design, task-list, review file
    indexing** save_memory calls: same as 1.4 — Read each
    `*-tech-design.md`, `*-tasks.md`, `*-review.md` file directly
  - [X] 1.6 Replace the **project config** save_memory call
    (package.json etc.): change to instruct Claude to write config
    summary to `/tmp/claude-mem-{project_name}-PROJECT-CONFIG.md`
    then Read it. H1 title: `# {project_name} - Project Config`
  - [X] 1.7 Verify: grep `.claude/commands/rlm-mem/discover/init.md`
    for `save_memory` — must return zero matches

- [X] 2.0 **User Story:** As a developer, I want
  `rlm-mem/plan/prd.md`, `plan/tech-design.md`, and `plan/tasks.md`
  to use Pattern A so that plan artifacts are persisted via the
  PostToolUse hook without broken save_memory calls [3/3]
  - [X] 2.1 Edit `.claude/commands/rlm-mem/plan/prd.md`: in the
    "Final Instructions" / "Index in claude-mem" section, replace
    the save_memory code block with: "Read the PRD file you just
    created. The PostToolUse hook captures the full content
    automatically."
  - [X] 2.2 Edit `.claude/commands/rlm-mem/plan/tech-design.md`:
    same replacement in the "Index in Claude-Mem" / "Step 7" section
  - [X] 2.3 Edit `.claude/commands/rlm-mem/plan/tasks.md`: same
    replacement in the "Index in claude-mem" final instructions
  - [X] 2.4 Verify: grep all three files for `save_memory` — must
    return zero matches in all three

- [X] 3.0 **User Story:** As a developer, I want
  `rlm-mem/plan/check.md` and `develop/impl.md` to use Pattern B
  so that task completions and implementation records are captured
  in claude-mem [2/2]
  - [X] 3.1 Edit `.claude/commands/rlm-mem/plan/check.md`: replace
    the save_memory call with instructions to Write
    `/tmp/claude-mem-{jira_id}-TASK-COMPLETION.md` (with H1 title
    `# {jira_id} - Task Completion`, `[TYPE: TASK-COMPLETION]`,
    `[PROJECT: {project_name}]`, and the completion details), then
    Read it
  - [X] 3.2 Edit `.claude/commands/rlm-mem/develop/impl.md`: replace
    the save_memory call with instructions to Write
    `/tmp/claude-mem-{jira_id}-IMPLEMENTATION.md` (with H1 title
    `# {jira_id} - {task_name} Implementation`, `[TYPE:
    IMPLEMENTATION]`, `[PROJECT: {project_name}]`, patterns used,
    and files), then Read it
  - [X] 3.3 Verify: grep both files for `save_memory` — zero matches

- [X] 4.0 **User Story:** As a developer, I want
  `rlm-mem/develop/save.md` to use Pattern B (one temp file per
  decision) so that session wrap-up decisions are persisted to
  claude-mem correctly [1/1]
  - [X] 4.1 Read `.claude/commands/rlm-mem/develop/save.md` in full
    to understand the current save_memory usage (2 calls — one in
    the "What Gets Preserved" description, one in the actual save
    step)
  - [X] 4.2 Replace the save_memory call in the save step with:
    for each decision, Write to
    `/tmp/claude-mem-{jira_id}-SESSION-DECISION-{n}.md` (with H1
    title, `[TYPE: SESSION-DECISION]`, `[PROJECT: {project_name}]`,
    decision text), then Read it. Update the descriptive mention of
    save_memory in the "What Gets Preserved" section to reference
    the write+read pattern instead.
  - [X] 4.3 Verify: grep `.claude/commands/rlm-mem/develop/save.md`
    for `save_memory` — zero matches

- [X] 5.0 **User Story:** As a developer, I want
  `rlm-mem/README.md` to accurately document the available MCP
  tools so that there is no reference to the non-existent
  save_memory tool [1/1]
  - [X] 5.1 Edit `.claude/commands/rlm-mem/README.md`: remove
    `save_memory` from the MCP tools list. Add a note that writing
    to claude-mem is automatic via PostToolUse hook — commands Read
    output files or temp files to trigger capture.
  - [X] 5.2 Verify: grep `.claude/commands/rlm-mem/README.md` for
    `save_memory` — zero matches

- [X] 6.0 **User Story:** As a developer, I want all 7 affected
  `~/.claude/commands/coding/` files patched with the same patterns
  so that the `coding/` command tree works correctly [7/7]
  - [X] 6.1 Edit `~/.claude/commands/coding/discover/init.md`:
    apply same changes as Story 1 (Pattern A for existing files,
    Pattern B for synthesized content). Note: coding/init may have
    fewer save_memory calls (4 vs 7) — read the file first to
    confirm exact call sites before editing
  - [X] 6.2 Edit `~/.claude/commands/coding/plan/prd.md`: Pattern A
    — same as Story 2.1
  - [X] 6.3 Edit `~/.claude/commands/coding/plan/tech-design.md`:
    Pattern A — same as Story 2.2
  - [X] 6.4 Edit `~/.claude/commands/coding/plan/tasks.md`: Pattern
    A — same as Story 2.3
  - [X] 6.5 Edit `~/.claude/commands/coding/plan/check.md`: Pattern
    B — same as Story 3.1
  - [X] 6.6 Edit `~/.claude/commands/coding/develop/save.md`:
    Pattern B — same as Story 4.2. Note: coding/save.md has 2
    save_memory calls — read the file first
  - [X] 6.7 Edit `~/.claude/commands/coding/review/pr-review.md`:
    this file has 2 save_memory calls not present in the rlm-mem
    tree — read it first, then apply Pattern A or B as appropriate
    based on what content it saves
  - [X] 6.8 Verify: grep all 7 files for `save_memory` — zero
    matches in all

- [X] 7.0 **User Story:** As a developer, I want all 5 test agents
  updated to use Pattern B for their findings sections so that test
  findings are persisted to claude-mem correctly [5/5]
  - [X] 7.1 Edit `.claude/agents/test-backend.md`: in "Step 6: Save
    Findings to Claude-Mem", replace the save_memory call with
    Write to `/tmp/claude-mem-test-backend-TEST-FINDING.md`
    (H1 title `# {area} - {finding summary}`, `[TYPE: TEST-FINDING]`,
    `[PROJECT: {project_name}]`, finding details), then Read it.
    Keep the "if available" guard unchanged — it should now wrap
    the write+read block instead.
  - [X] 7.2 Edit `.claude/agents/test-review.md`: same pattern,
    temp file `/tmp/claude-mem-test-review-TEST-FINDING.md`,
    `[TYPE: TEST-FINDING][REVIEW]` tags
  - [X] 7.3 Edit `.claude/agents/test-e2e-planner.md`: same pattern,
    temp file `/tmp/claude-mem-test-e2e-planner-TEST-FINDING.md`,
    `[TYPE: TEST-FINDING][E2E-PLAN]` tags
  - [X] 7.4 Edit `.claude/agents/test-e2e-generator.md`: same
    pattern, temp file
    `/tmp/claude-mem-test-e2e-generator-TEST-FINDING.md`,
    `[TYPE: TEST-FINDING][E2E-PATTERN]` tags
  - [X] 7.5 Edit `.claude/agents/test-e2e-healer.md`: same pattern,
    temp file `/tmp/claude-mem-test-e2e-healer-TEST-FINDING.md`,
    `[TYPE: TEST-FINDING][E2E-HEALING]` tags
  - [X] 7.6 Verify: grep all 5 agent files for `save_memory` — zero
    matches in all
