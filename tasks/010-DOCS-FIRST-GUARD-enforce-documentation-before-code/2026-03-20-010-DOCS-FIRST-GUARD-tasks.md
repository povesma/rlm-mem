# 010-DOCS-FIRST-GUARD - Task List

## Relevant Files

- [tasks/010-DOCS-FIRST-GUARD-enforce-documentation-before-code/
  2026-03-20-010-DOCS-FIRST-GUARD-prd.md](
  2026-03-20-010-DOCS-FIRST-GUARD-prd.md)
  :: Product Requirements Document
- [tasks/010-DOCS-FIRST-GUARD-enforce-documentation-before-code/
  2026-03-20-010-DOCS-FIRST-GUARD-tech-design.md](
  2026-03-20-010-DOCS-FIRST-GUARD-tech-design.md)
  :: Technical Design Document
- [.claude/hooks/docs-first-guard.sh](
  ../../.claude/hooks/docs-first-guard.sh)
  :: Create — PreToolUse hook script
- [.claude/commands/rlm-mem/develop/impl.md](
  ../../.claude/commands/rlm-mem/develop/impl.md)
  :: Modify — add marker file management + tighten Scope Verification
- [.claude/commands/rlm-mem/discover/start.md](
  ../../.claude/commands/rlm-mem/discover/start.md)
  :: Modify — rewrite Docs-First Principle section
- [install.sh](../../install.sh)
  :: Modify — add hook copy + settings.json registration
- [README.md](../../README.md)
  :: Modify — add hook documentation

## Notes

- The hook script is testable by piping JSON to stdin and checking
  stdout/exit code. No Claude Code session needed for unit-level
  verification.
- The marker file lives at `~/.claude/rlm_state/.impl-active` — the
  directory already exists (used by RLM REPL).
- Hook registration goes in user-level `~/.claude/settings.json`,
  not project-level. This project is an installation package.
- TDD applies to the hook script: pipe JSON in, check exit code and
  stdout. All other changes are markdown prompt files (manual
  verification only).

## Tasks

- [X] 1.0 **User Story:** As a developer, I want a PreToolUse hook
  script that fires on Edit/Write and asks permission when no
  `/impl` session is active, so that undocumented code edits are
  caught [5/5]
  - [X] 1.1 Create `.claude/hooks/docs-first-guard.sh` with
    shebang `#!/usr/bin/env bash`, `set -euo pipefail`,
    `trap 'exit 0' ERR`, and `INPUT=$(cat)`. Extract
    `FILE_PATH` via `jq -r '.tool_input.file_path // empty'`.
    Exit 0 if `FILE_PATH` is empty.
  - [X] 1.2 Add the allow-list: exit 0 for files matching
    `*.md`, `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.txt`,
    or paths containing `/tasks/` or `/.claude/`. Use two
    `case` statements as shown in tech-design pseudocode.
  - [X] 1.3 Add marker file check: if
    `~/.claude/rlm_state/.impl-active` exists and is less
    than 2 hours old (`find -mmin +120` returns empty),
    exit 0. If stale, `rm -f` the marker and proceed.
  - [X] 1.4 Add the "ask" response: output JSON with
    `hookSpecificOutput.permissionDecision: "ask"` and the
    permission message from tech-design §Permission message.
    Use `jq -n` to produce valid JSON.
  - [X] 1.5 Verify by piping test JSON to the script:
    (a) `.ts` file, no marker → expect JSON output with "ask";
    (b) `.md` file → expect exit 0, no output;
    (c) `.ts` file, fresh marker exists → expect exit 0;
    (d) `.ts` file, stale marker (touch -t) → expect "ask"
    and marker deleted.
    Run: `echo '{"tool_input":{"file_path":"/foo/bar.ts"}}' |
    bash .claude/hooks/docs-first-guard.sh`

- [X] 2.0 **User Story:** As a developer using `/impl`, I want the
  command to create a marker file at start and remove it at end,
  so that the hook stays silent during documented implementation
  [2/2]
  - [X] 2.1 Add "Step 0: Activate Implementation Session" to
    `.claude/commands/rlm-mem/develop/impl.md` as the very
    first step (before current "1. Load Context" at line 76):
    `touch ~/.claude/rlm_state/.impl-active`. Include a
    one-line explanation of what the marker does.
  - [X] 2.2 Add "Step 8: Deactivate Implementation Session"
    as the final step (after current Step 7 at line 176):
    `rm -f ~/.claude/rlm_state/.impl-active`. Renumber
    existing steps if needed to accommodate Step 0 and Step 8.

- [X] 3.0 **User Story:** As a developer, I want the docs-first
  language in `start.md` and `impl.md` tightened to remove soft
  exceptions, so that the prompt reinforces what the hook enforces
  [3/2]
  - [X] 3.1 Rewrite the Docs-First Principle section in
    `.claude/commands/rlm-mem/discover/start.md` (lines
    217-226) using the exact new text from tech-design
    §Component 3. Remove the "Minor changes" bullet. Add
    the hook reference paragraph.
  - [X] 3.2 In `.claude/commands/rlm-mem/develop/impl.md`
    Scope Verification section (lines 23-48): remove
    "If updating docs costs more context/time than the change
    itself, skip the update" and "Be smart. The goal is
    maintaining idempotency... not creating bureaucratic
    overhead." Replace with the strict clarification-level
    exception text from tech-design §Component 3.
  - [ ] 3.3 Verify both files read correctly: run `/start`
    and `/impl` commands and confirm the new text appears
    in Claude's output without the removed language.

- [X] 4.0 **User Story:** As a new installer, I want `install.sh`
  to copy the hook and register it in settings.json, so that I
  get protection without manual setup [3/3]
  - [X] 4.1 Add a "Docs-First Guard Hook" block to
    `install.sh` after the existing hooks section: copy
    `.claude/hooks/docs-first-guard.sh` to
    `$TARGET/hooks/docs-first-guard.sh` and `chmod +x`.
  - [X] 4.2 Add settings.json hook registration to
    `install.sh`: if `jq` is available and settings.json
    exists, check if `docs-first-guard` is already registered
    in PreToolUse. If not, append the hook entry using `jq`.
    Use the exact jq command from tech-design §Component 4.
  - [X] 4.3 Verify: run `install.sh` in a temp dir, confirm
    the hook file is copied with +x permission, and the
    settings.json contains the PreToolUse entry for
    `docs-first-guard`. Also verify running install.sh
    again doesn't duplicate the entry.

- [X] 5.0 **User Story:** As a new user reading docs, I want the
  README updated with hook documentation, so that I understand
  the guard and how to bypass it [2/2]
  - [X] 5.1 Add docs-first-guard to the §Hooks section in
    `README.md`: purpose (prevents undocumented code edits),
    how it works (fires on Edit/Write, checks marker file),
    how to bypass (approve at prompt, or `disableAllHooks`).
  - [X] 5.2 Update `CLAUDE.md` File Structure listing to
    include `docs-first-guard.sh` under the hooks tree.

- [ ] 6.0 **User Story:** As a developer, I want all PRD Gherkin
  scenarios manually verified so that the feature is confirmed
  working end-to-end [5/0]
  - [ ] 6.1 **Scenario: Code edit outside /impl** — without
    a marker file, attempt to Edit a `.ts` or `.py` file.
    Confirm the permission prompt appears with the expected
    message text.
  - [ ] 6.2 **Scenario: Markdown edit outside /impl** —
    without a marker file, Edit a `.md` file. Confirm no
    prompt appears (hook allows silently).
  - [ ] 6.3 **Scenario: Code edit during /impl** — create
    the marker file (`touch ~/.claude/rlm_state/.impl-active`),
    then Edit a code file. Confirm no prompt appears.
  - [ ] 6.4 **Scenario: Stale marker ignored** — create a
    marker file with old timestamp
    (`touch -t 202603200100 ~/.claude/rlm_state/.impl-active`),
    then Edit a code file. Confirm the prompt appears and the
    stale marker is deleted.
  - [ ] 6.5 **Scenario: User approves/denies** — trigger
    the permission prompt, approve once (edit proceeds) and
    deny once (edit blocked). Confirm both work correctly.
