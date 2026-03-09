# Context Guard - Task List

## Relevant Files

- [tasks/004-CONTEXT-GUARD-context-window-protection/
  2026-03-08-004-CONTEXT-GUARD-prd.md](
  2026-03-08-004-CONTEXT-GUARD-prd.md)
  :: Context Guard - Product Requirements Document
- [tasks/004-CONTEXT-GUARD-context-window-protection/
  2026-03-08-004-CONTEXT-GUARD-tech-design.md](
  2026-03-08-004-CONTEXT-GUARD-tech-design.md)
  :: Context Guard - Technical Design Document
- [.claude/hooks/context-guard.sh](
  ../../.claude/hooks/context-guard.sh)
  :: Main hook script — UserPromptSubmit bash hook
- [README.md](../../README.md)
  :: User guide — add installation instructions for the hook
- [.claude/commands/rlm-mem/develop/save.md](
  ../../.claude/commands/rlm-mem/develop/save.md)
  :: Session save command for rlm-mem tree (CREATE)
- [~/.claude/commands/coding/develop/save.md]
  :: Session save command for coding tree (CREATE)
- [~/.claude/commands/rlm/develop/save.md]
  :: Session save command for rlm tree (CREATE)

## Notes

- This is a bash script, not application code. TDD does not
  apply in the traditional sense. Testing means manually
  invoking the hook with crafted inputs and verifying outputs.
- The script must fail open on all error paths — never block
  due to a script error.
- No external dependencies beyond `python3` (already required
  for RLM). No `jq`.
- Context usage % and window size come directly from hook stdin
  JSON (`context_window.used_percentage`,
  `context_window.context_window_size`) — no transcript parsing.
- Context window size is dynamic (read from stdin), not hardcoded.

## Tasks

- [~] 1.0 **User Story:** As a developer, I want the hook script
  to parse stdin and read context usage so that it has accurate
  data to make allow/block decisions [3/3]
  - [~] 1.1 Create `.claude/hooks/` directory and
    `context-guard.sh` with top-level `trap 'exit 0' ERR` and
    stdin parsing via `python3` to extract
    `context_window.used_percentage`, `context_window_size`,
    and `user_prompt`
  - [~] 1.2 Read `CONTEXT_GUARD_THRESHOLD` env var (default 80);
    if `used_pct < threshold` exit 0
  - [~] 1.3 Implement `override:` escape hatch: if `user_prompt`
    starts with `override:` (case-insensitive), exit 0
    regardless of context level

- [~] 2.0 **User Story:** As a developer, I want the hook script
  to classify the user prompt against a keyword blocklist so
  that development requests are identified while safe operations
  pass through [1/1]
  - [~] 2.1 Implement blocklist classification: lowercase
    `user_prompt`, check against patterns (`implement`, `code`,
    `build`, `create`, `write`, `develop`, `add feature`,
    `start story`, `begin story`, `start task`, `begin task`,
    `refactor`, `fix bug`, `debug`); if any match, proceed to
    block; otherwise exit 0

- [~] 3.0 **User Story:** As a developer, I want the hook to
  output a clear block response when context exceeds the
  threshold so that users know why they were stopped and what
  they can do [1/1]
  - [~] 3.1 Output block JSON to stdout when classification
    returns a match:
    ```json
    {
      "continue": false,
      "systemMessage": "Context is {N}% full (threshold: {T}%,
    window: {W}k). Start a fresh session for new development.
    Allowed now: update docs, tasks, claude-mem, or commit."
    }
    ```
    where `{N}` is `used_pct`, `{T}` is threshold, `{W}k` is
    `context_window_size / 1000`

- [~] 4.0 **User Story:** As a developer, I want the hook to
  fail open on all error paths so that script bugs never block
  the user [2/2]
  - [~] 4.1 Top-level `trap 'exit 0' ERR` catches any uncaught
    error and exits 0
  - [~] 4.2 Python parse failures (malformed stdin, missing
    fields) print `0 0` defaults so script exits 0 at threshold
    check

- [~] 5.0 **User Story:** As a developer, I want the hook
  registered with installation instructions so that users can
  activate the feature [3/3]
  - [~] 5.1 Add a "Context Guard Hook" section to `README.md`
    with: copy command for the script, the `settings.json`
    snippet, and `CONTEXT_GUARD_THRESHOLD` env var explanation
  - [~] 5.2 Verify the hook config snippet matches the actual
    Claude Code `UserPromptSubmit` hook schema by cross-checking
    against the schema in the tech design
  - [~] 5.3 Create `install.sh` at repo root — syncs
    `.claude/agents/`, `.claude/commands/rlm-mem/`,
    `.claude/hooks/`, `.claude/rlm_scripts/` to `~/.claude/`

- [X] 6.0 **User Story:** As a developer, I want to manually
  verify all PRD Gherkin scenarios pass so that the feature is
  confirmed working end-to-end [4/4]
  - [X] 6.1 **Scenario: Block above threshold** — install hook,
    lower `CONTEXT_GUARD_THRESHOLD` to 1, submit a prompt
    containing `implement`; verify block systemMessage appears
  - [X] 6.2 **Scenario: Allow docs update above threshold** —
    same setup, submit "update the task list"; verify pass-through
  - [X] 6.3 **Scenario: Allow all requests below threshold** —
    restore default threshold, submit any prompt; verify
    pass-through
  - [X] 6.4 **Scenario: Configurable threshold** — set
    `CONTEXT_GUARD_THRESHOLD=85`, submit dev prompt below
    threshold; verify pass-through. Verified block fires when
    threshold < current usage.

- [~] 7.0 **User Story:** As a developer, I want the context
  guard to warn rather than hard-block so that I stay conscious
  of context usage but retain the ability to proceed on my own
  discretion [3/3]
  - [~] 7.1 Change hook from hard block (`exit 2`) to soft warn:
    output a `systemMessage` visible to Claude but let the
    prompt through (`exit 0`). The message must include current
    usage %, threshold, and suggest running `/rlm-mem:develop:save`
    before continuing.
  - [~] 7.2 Update the systemMessage text to be actionable:
    "Context is {N}% full (threshold: {T}%). Consider running
    `/…:develop:save` to wrap up this session before continuing.
    To proceed anyway, just continue normally."
  - [X] 7.3 Verify soft-warn behaviour: at threshold=1, submit
    a dev prompt — Claude should see the warning message but
    still process the prompt.

- [~] 8.0 **User Story:** As a developer, I want a `/…:develop:save`
  command in all active trees so that I can wrap up a session,
  save state, and be ready to start a fresh session [3/3]
  - [~] 8.1 Create `.claude/commands/rlm-mem/develop/save.md` —
    rlm-mem variant: search claude-mem for what's already saved,
    save missing decisions/agreements, confirm continuity ready,
    hard-stop with 🚨 if claude-mem unavailable
  - [~] 8.2 Create `~/.claude/commands/coding/develop/save.md` —
    coding variant: same as rlm-mem but without RLM steps
  - [~] 8.3 Create `~/.claude/commands/rlm/develop/save.md` —
    rlm variant: uses ai-docs/ instead of claude-mem

