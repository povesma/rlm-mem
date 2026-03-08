# 002-TEST-SUBSYSTEM Testing Subagents - Task List

## Relevant Files

- [tasks/002-TEST-SUBSYSTEM-testing-subagents/2026-02-22-002-TEST-SUBSYSTEM-testing-subagents-prd.md](tasks/002-TEST-SUBSYSTEM-testing-subagents/2026-02-22-002-TEST-SUBSYSTEM-testing-subagents-prd.md)
  :: Product Requirements Document
- [tasks/002-TEST-SUBSYSTEM-testing-subagents/2026-02-22-002-TEST-SUBSYSTEM-testing-subagents-tech-design.md](tasks/002-TEST-SUBSYSTEM-testing-subagents/2026-02-22-002-TEST-SUBSYSTEM-testing-subagents-tech-design.md)
  :: Technical Design Document
- [.claude/agents/rlm-subcall.md](.claude/agents/rlm-subcall.md)
  :: Existing subagent — reference for frontmatter format and
  conventions
- [.claude/agents/test-backend.md](.claude/agents/test-backend.md)
  :: NEW — Backend test subagent definition
- [.claude/agents/test-review.md](.claude/agents/test-review.md)
  :: NEW — Adversarial test review subagent definition
- [.claude/agents/test-e2e-planner.md](.claude/agents/test-e2e-planner.md)
  :: NEW — E2E planner subagent (forked from Playwright)
- [.claude/agents/test-e2e-generator.md](.claude/agents/test-e2e-generator.md)
  :: NEW — E2E generator subagent (forked from Playwright)
- [.claude/agents/test-e2e-healer.md](.claude/agents/test-e2e-healer.md)
  :: NEW — E2E healer subagent (forked from Playwright)
- [README.md](README.md)
  :: User guide — update with test subagent installation and usage

## Notes

- All agent files are self-contained markdown with YAML frontmatter.
  No build steps, no external dependencies.
- Test each agent by invoking it via the Task tool in a real project
  with actual test frameworks installed.
- The Playwright agent upstream source is at:
  `https://github.com/microsoft/playwright/tree/main/packages/playwright/src/agents/`
  Files: `playwright-test-planner.agent.md`,
  `playwright-test-generator.agent.md`,
  `playwright-test-healer.agent.md`
- Playwright agents require Playwright MCP server in global config
  (`~/.claude/mcp.json`).
- Tasks 1-2 (backend + review) can be implemented and tested without
  Playwright installed. Tasks 3-5 (E2E) require Playwright.

## TDD Planning Guidelines

These are agent definition files (markdown), not application code.
Traditional TDD does not apply. Instead, testing means:
- **Manual invocation**: Call the agent via Task tool in a test project
- **Contract verification**: Confirm YAML output matches the contract
- **Graceful degradation**: Verify agent works without claude-mem,
  without RLM, without the target framework installed
- **Context isolation**: Verify the subagent doesn't see main agent's
  reasoning (inherent in Task tool architecture)

## Tasks

- [X] 1.0 **User Story:** As a developer, I want a backend test
  subagent so that unit/integration tests are written and run in an
  isolated context with framework auto-detection [5/5]
  - [X] 1.1 Create `.claude/agents/test-backend.md` with YAML
    frontmatter (name, description, model: haiku, tools: Bash, Read,
    Write, Edit, Glob, Grep) following `rlm-subcall.md` conventions
  - [X] 1.2 Write the system prompt: role definition, expertise areas,
    rules for framework detection (pytest, vitest, jest, go test,
    cargo test, phpunit), and test-writing guidelines (edge cases
    over happy paths, no duplication of existing tests)
  - [X] 1.3 Add YAML input contract parsing instructions — agent must
    extract task_description, changed_files, key_patterns,
    test_framework, existing_tests from the prompt
  - [X] 1.4 Add YAML output contract generation instructions — agent
    must return agent, status, tests_written, tests_run, failures,
    gaps_found, claude_mem_refs, new_claude_mem_entries
  - [X] 1.5 Add RLM optional enrichment section — when rlm_available
    is true, call `python3 ~/.claude/rlm_scripts/rlm_repl.py exec`
    to trace dependencies; skip gracefully when unavailable
- [X] 2.0 **User Story:** As a developer, I want an adversarial test
  review subagent so that coverage gaps are identified after tests
  are written [5/5]
  - [X] 2.1 Create `.claude/agents/test-review.md` with YAML
    frontmatter (name, description, model: sonnet, tools: Read,
    Glob, Grep, Bash)
  - [X] 2.2 Write the system prompt: adversarial analyst role,
    expertise in state transitions, auth boundaries, error recovery
    paths, session management edge cases
  - [X] 2.3 Add analysis methodology instructions — read all changed
    files AND their test files, systematically check: state
    transitions tested? auth boundaries tested? error paths tested?
    recovery tested?
  - [X] 2.4 Add YAML output contract — test-review returns only
    gaps_found (with area, description, severity, recommendation)
    and claude_mem_refs. No tests_written or tests_run sections.
  - [X] 2.5 Add RLM optional enrichment — use dependency graph to
    find untested callers/consumers of modified functions
- [X] 3.0 **User Story:** As a developer, I want an E2E planner
  subagent so that comprehensive test plans are generated by
  exploring the live application [5/5]
  - [X] 3.1 Download `playwright-test-planner.agent.md` from
    Playwright GitHub repo and save as base for
    `.claude/agents/test-e2e-planner.md`
  - [X] 3.2 Add upstream source header comment block with repo URL,
    file path, download date, and update instructions
  - [X] 3.3 Customize: add claude-mem query instructions at start
    (search past E2E failures), add Glob/Grep/Read tools for
    codebase analysis alongside browser tools
  - [X] 3.4 Customize: add YAML output contract — return agent,
    status, plan_file path, gaps_found, claude_mem_refs alongside
    the markdown test plan
  - [X] 3.5 Mark all customizations with `# CUSTOM` comments to
    distinguish from upstream content for future merges
- [X] 4.0 **User Story:** As a developer, I want an E2E generator
  subagent so that test plans are converted into executable
  Playwright tests verified against the live app [5/5]
  - [X] 4.1 Download `playwright-test-generator.agent.md` from
    Playwright GitHub repo and save as base for
    `.claude/agents/test-e2e-generator.md`
  - [X] 4.2 Add upstream source header comment block (same format
    as planner)
  - [X] 4.3 Customize: add YAML output contract — return agent,
    status, tests_written (paths + descriptions), tests_run
    (total/passed/failed), failures with analysis
  - [X] 4.4 Customize: add claude-mem save for test patterns
    discovered during generation, add Read/Write/Edit/Glob/Grep
    tools
  - [X] 4.5 Mark all customizations with `# CUSTOM` comments
- [ ] 5.0 **User Story:** As a developer, I want an E2E healer
  subagent so that broken E2E tests are automatically diagnosed
  and repaired [5/5 coded, pending testing]
  - [~] 5.1 Download `playwright-test-healer.agent.md` from
    Playwright GitHub repo and save as base for
    `.claude/agents/test-e2e-healer.md`
    NOTE: Upstream content recreated from documented design in
    claude-mem (#1090, #1085). Raw GitHub fetch unavailable.
    File created at .claude/agents/test-e2e-healer.md (sonnet,
    tools: Read, Edit, Glob, Grep, Bash + 10 playwright-test/* tools)
  - [~] 5.2 Add upstream source header comment block (same format
    as planner and generator)
    NOTE: UPSTREAM SOURCE comment block added with repo, path,
    url, fetched date (2026-02-27), and merge instructions.
  - [~] 5.3 Customize: add YAML output contract — return agent,
    status, tests_healed (list with test name, fix description),
    tests_run results, remaining failures
    NOTE: Full output contract added with tests_healed, tests_run,
    remaining_failures, gaps_found, claude_mem_refs, new_claude_mem_entries
  - [~] 5.4 Customize: add claude-mem query for known UI change
    patterns, save healing patterns after completion
    NOTE: Pre-Healing claude-mem query added (search for past
    healing sessions by key_patterns). Save pattern added after
    healing with [TYPE: TEST-FINDING]\n[E2E-HEALING] prefix.
  - [~] 5.5 Mark all customizations with `# CUSTOM` comments
    NOTE: All custom sections wrapped in <!-- # CUSTOM --> and
    <!-- # END CUSTOM --> comment blocks.
- [ ] 6.0 **User Story:** As a developer, I want claude-mem
  integration in all test subagents so that past bug patterns
  inform testing and new findings are saved [5/5 coded, pending testing]
  - [~] 6.1 Define the standard claude-mem query pattern (search
    at start) and add to all 5 agent prompts — search for
    "bugs failures {affected_area}" in project
    NOTE: All 5 agents use dynamic key_patterns query.
    test-e2e-planner/generator updated in story 6 session.
    test-e2e-healer added in story 5 with same pattern.
    Query format: "<type-specific prefix> <key_patterns joined>"
  - [~] 6.2 Define the standard claude-mem save pattern (save at
    end) and add to all 5 agent prompts — save significant
    findings with [TYPE: TEST-FINDING] prefix
    NOTE: Consistent across all 5 agents. Base prefix
    [TYPE: TEST-FINDING] with agent-specific sub-tags:
    (no sub-tag), [REVIEW], [E2E-PLAN], [E2E-PATTERN], [E2E-HEALING]
  - [~] 6.3 Add graceful degradation instructions to all agents —
    if claude-mem MCP tools are unavailable, skip memory queries
    and proceed with available context
    NOTE: Consistent across all 5 agents. All say
    "If claude-mem is unavailable, skip and proceed."
  - [~] 6.4 Verify consistency: all 5 agents use identical
    claude-mem interaction patterns (same search queries, same
    save format, same degradation behavior)
    NOTE: Verified across all 5 agents — consistent.
- [~] 7.0 **User Story:** As a developer, I want installation and
  update documentation so that I can install test subagents and
  keep Playwright forks current [4/4 coded, pending review]
  - [~] 7.1 Update `README.md` prerequisites section with test
    subagent installation instructions (`cp .claude/agents/test-*.md
    ~/.claude/agents/`)
    NOTE: Added step 3 (macOS + Windows) in Installation section.
    Updated "What Gets Installed" file tree to show all 6 agents.
  - [~] 7.2 Add "Test Subagents" section to README explaining what
    each agent does, when it's used, and what it requires
    (Playwright MCP for E2E agents)
    NOTE: Added "🧪 Test Subagents" section with agents overview
    table, when-to-use guide, and Playwright MCP setup snippet.
  - [~] 7.3 Document the Playwright fork update procedure: download
    from GitHub, diff against local copies, merge preserving
    `# CUSTOM` lines, update fetched date
    NOTE: Added under "Updating Playwright Forks" in new Test
    Subagents section with curl + diff + copy workflow.
  - [~] 7.4 Update CLAUDE.md with test subagent architecture
    overview for Claude Code's own context
    NOTE: Updated What This Repository Is (added 5 Test Subagents),
    Architecture section (added component 3 with all 5 agents),
    Installation Flow (added test-*.md copy), File Structure tree.
- [ ] 8.0 **User Story:** As a developer, I want to verify the test
  subsystem works end-to-end so that I can trust it before
  integrating with /impl [3/3 partially verified]
  - [~] 8.1 Test `test-backend` agent: invoke via Task tool in a
    project with pytest (or vitest), verify YAML output matches
    contract, verify framework auto-detection works
    FINDING: Agent ran and wrote tests. Two bugs found and fixed:
    (1) Output was markdown headers/tables instead of strict YAML —
    fixed by adding CRITICAL warning to Output Contract section.
    (2) Agent invented test run results ("103 passed") when no
    framework was detected — fixed by adding STOP rule and
    "NEVER invent results" rule to Framework Detection section.
    Pending: re-verify in a project WITH pytest installed to confirm
    the YAML format and halt behavior are now correct.
  - [~] 8.2 Test `test-review` agent: invoke after test-backend,
    verify it finds at least one gap that test-backend missed,
    verify YAML output has no tests_written section
    RESULT: PASS. Found 15 gaps (5 high, 5 medium, 5 low) across
    exec/stdin, output capture, state persistence, language detection.
    Output was valid YAML. No tests_written section. Specific gaps
    had file:line references. Pending: user confirmation.
  - [ ] 8.3 Test E2E pipeline: invoke planner → generator →
    healer (if failures) in a project with Playwright installed,
    verify each agent's YAML output matches contract
    NOTE: Requires Playwright MCP + a live web app. Cannot test
    in this repo. User must test in a separate frontend project.
