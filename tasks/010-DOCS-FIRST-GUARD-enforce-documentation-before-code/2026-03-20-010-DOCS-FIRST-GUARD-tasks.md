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
- [.claude/commands/rlm-mem/develop/impl.md](
  ../../.claude/commands/rlm-mem/develop/impl.md)
  :: Modify — remove marker file management, update docs-first text
- [.claude/commands/rlm-mem/discover/start.md](
  ../../.claude/commands/rlm-mem/discover/start.md)
  :: Modify — rewrite Docs-First Principle (remove hook references)
- [README.md](../../README.md)
  :: Modify — remove hook documentation, update install steps
- [install.sh](../../install.sh)
  :: Modify — remove hook registration from settings.json
- [CLAUDE.md](../../CLAUDE.md)
  :: Modify — remove hook from file structure listing

## Notes

- **V1 (hook-based) was implemented and abandoned.** The PreToolUse
  hook (`docs-first-guard.sh`) broke Shift+Tab "Allow all edits" and
  could not reason about semantic context. See PRD for full rationale.
- V2 uses prompt-based enforcement in command files only. No hooks,
  no marker files, no filesystem state.
- The hook file remains in the repo for reference but must NOT be
  registered in settings.json or installed.
- All V1 tasks below are marked with their actual status. V2 tasks
  follow.

## V1 Tasks (hook-based — abandoned)

- [X] 1.0 ~~PreToolUse hook script~~ **ABANDONED** — hook breaks
  Shift+Tab permission mode [5/5]
  - [X] 1.1–1.5 (implemented, tested, works in isolation — but
    incompatible with Claude Code permission modes)

- [X] 2.0 ~~Marker file management~~ **ABANDONED** — filesystem
  flag can't reason about semantic context [2/2]
  - [X] 2.1–2.2 (implemented in impl.md — must be reverted)

- [X] 3.0 ~~Prompt hardening with hook references~~ **PARTIALLY
  VALID** — prompt tightening was good, hook references must be
  removed [3/2]
  - [X] 3.1–3.2 (text changes valid, hook references to remove)
  - [ ] 3.3 Verify (not done)

- [X] 4.0 ~~install.sh hook registration~~ **ABANDONED** — hook
  should not be auto-registered [3/3]
  - [X] 4.1–4.3 (implemented — must be reverted)

- [X] 5.0 ~~README hook documentation~~ **MUST BE REVISED** [2/2]
  - [X] 5.1–5.2 (written — must be updated to remove hook docs)

- [ ] 6.0 ~~E2E Gherkin scenarios~~ **CANCELLED** — hook-based
  scenarios no longer applicable

## V2 Tasks (prompt-based enforcement)

- [ ] 7.0 **Revert V1 hook artifacts** — remove marker file
  management, hook references, and hook registration [5/0]
  - [ ] 7.1 Remove Step 0 (touch marker) and Step 9 (rm marker)
    from `impl.md`
  - [ ] 7.2 Remove hook reference paragraph from `impl.md`
    Scope Verification section (lines 52-54)
  - [ ] 7.3 Remove hook reference paragraph from `start.md`
    Docs-First Principle section (lines 228-230)
  - [ ] 7.4 Remove hook registration block from `install.sh`
    (the jq block that adds PreToolUse entry to settings.json)
  - [ ] 7.5 Remove hook copy step from `install.sh` and manual
    install sections in `README.md` (macOS + Windows)

- [ ] 8.0 **Update prompt-based enforcement in command files** —
  Claude uses semantic judgment instead of hooks [3/0]
  - [ ] 8.1 Rewrite Docs-First Principle in `start.md`: remove
    hook mention, add semantic cases (research/POC, minor
    changes, undocumented code), instruct Claude to warn
    before proceeding with unjustified code edits
  - [ ] 8.2 Update Scope Verification in `impl.md`: remove hook
    reference, keep the tightened clarification-level exception
    text, add note that docs-first enforcement is prompt-based
  - [ ] 8.3 Verify: read both files and confirm no hook/marker
    references remain

- [ ] 9.0 **Update README and CLAUDE.md** — remove hook section,
  update file tree, revise install steps [4/0]
  - [ ] 9.1 Remove §Hooks > docs-first-guard section from README
    (keep context-guard section)
  - [ ] 9.2 Remove `docs-first-guard.sh` from "What Gets
    Installed" file tree in README
  - [ ] 9.3 Remove hook copy steps from macOS and Windows manual
    install sections in README
  - [ ] 9.4 Remove `docs-first-guard.sh` from CLAUDE.md file
    structure listing

- [ ] 10.0 **Clean up installation artifacts** [2/0]
  - [ ] 10.1 Remove hook registration block from `install.sh`
  - [ ] 10.2 Remove hook copy line from `install.sh`
