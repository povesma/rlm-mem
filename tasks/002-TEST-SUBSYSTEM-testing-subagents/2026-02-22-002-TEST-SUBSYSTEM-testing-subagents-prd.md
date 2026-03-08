# Testing Subagent Subsystem - Product Requirements Document

## Introduction/Overview

The RLM-Mem development workflow currently has a weak testing step —
`develop/impl` says "Test (TDD)" with no substance. When the main
implementation agent both writes code and writes tests, it "cheats":
it designs tests around the implementation it already planned, missing
edge cases like stale session state, auth boundary violations, and UI
error recovery.

This feature introduces a **testing subsystem** — a set of specialized
subagents that the main implementation agent delegates testing work to.
Each subagent runs in its own context (preventing the cheating problem),
writes and runs tests, and reports results back in structured YAML.

The primary goal is to catch the class of bugs where "it works in the
happy path" but fails under real-world conditions — role changes without
re-login, 403 errors on navigated pages, stale state after mutations.

## Objectives & Success Metrics

**Business Objectives:**
- Catch state/auth/session bugs before they reach manual testing or
  production
- Reduce context usage in the main implementation agent by offloading
  test work to dedicated subagents
- Improve test coverage quality (adversarial edge cases, not just
  happy paths)
- Provide a reusable testing subsystem across all RLM-Mem command sets
  (rlm, rlm-mem, coding, dev)

**Success Metrics:**
- Test subagents successfully write and run tests in isolation from
  the main agent's context
- Adversarial test-review agent identifies at least one coverage gap
  per feature that the main agent's tests missed
- Main agent context usage for testing-related work decreases (measured
  by comparing impl sessions with and without subagent delegation)
- Users report fewer "obvious" bugs slipping through to manual testing

## User Personas & Use Cases

### User Personas

**Solo Developer (primary)**: Uses Claude Code with RLM-Mem for
personal or small-team projects.
- **Characteristics**: Familiar with Claude Code, uses /impl workflow,
  writes features end-to-end
- **Needs**: Thorough testing without manually specifying every edge
  case; doesn't want to babysit the testing process
- **Goals**: Ship features with confidence that auth, state, and UI
  edge cases are covered

**AI Agent (internal)**: The main implementation agent that delegates
to test subagents.
- **Characteristics**: Has implementation context (changed files, task
  description), limited by context window
- **Needs**: Offload testing to a specialist, receive structured
  results back, decide what to do with gaps
- **Goals**: Complete the /impl workflow with thorough test coverage
  without exhausting its own context

### User Stories

- As a developer, I want the implementation workflow to automatically
  delegate testing to specialized subagents so that I get thorough test
  coverage without manually directing edge case testing
- As the main impl agent, I want to pass implementation context to a
  test subagent and receive structured YAML results back so that I can
  update the task list with any gaps found
- As a developer, I want an adversarial test reviewer that finds what
  the test-writer missed so that obvious bugs like 403-on-valid-nav
  don't slip through
- As a developer, I want E2E test agents that understand my frontend
  framework so that UI flows, error states, and cross-page navigation
  are tested automatically
- As a developer, I want test subagents to use claude-mem to recall
  past bug patterns so that known failure modes are tested proactively

### Use Cases

1. **Post-implementation test delegation**: Main agent finishes
   implementing a feature, calls appropriate test subagent(s) with
   implementation context, receives YAML report back
2. **Adversarial gap analysis**: After tests are written (by any
   agent), the test-review agent analyzes implementation + tests and
   reports missing coverage — state transitions, auth boundaries,
   error recovery paths
3. **E2E test generation**: For frontend changes, the E2E test agents
   plan test scenarios, generate Playwright tests, and run them against
   the live app
4. **Test healing**: When existing E2E tests break due to UI changes,
   the healer agent diagnoses and fixes them
5. **Bug pattern recall**: Test agents query claude-mem for past bugs
   in similar code areas and proactively test for recurrence

## Feature Scope

### In Scope

- **Three specialized test subagent definitions** installed to
  `~/.claude/agents/`:
  - `test-e2e-planner.md` — explores app, produces markdown test plan
  - `test-e2e-generator.md` — converts plans to Playwright tests,
    runs them
  - `test-e2e-healer.md` — debugs and fixes broken E2E tests
  - `test-backend.md` — writes and runs backend unit/integration tests
  - `test-review.md` — adversarial gap analysis, returns structured
    report
- **Framework-agnostic design**: Agents detect the project's test
  framework (pytest, vitest, jest, go test, etc.) rather than
  hardcoding one
- **Structured YAML output contract** between test subagents and the
  main agent
- **Claude-mem integration** in all test subagents (query past bugs,
  save new findings)
- **RLM integration** as optional enrichment (dependency graph
  analysis for deeper context when RLM is initialized)
- **Documentation** of how /impl and other commands invoke the test
  subsystem
- **Local copies of Playwright agent sources** with references to
  upstream for future updates
- **Installation flow** matching existing pattern (copy to
  `~/.claude/agents/`)

### Out of Scope

- Modifying the `/impl` command itself (separate follow-up task)
- CI/CD integration (test subagents run locally during development)
- Visual regression testing
- Load/performance testing agents
- Mobile-specific testing agents (future consideration)
- Creating a custom MCP server for test orchestration

### Future Considerations

- Modify `/impl` and other develop commands to automatically invoke
  test subagents as a mandatory step
- Add a `/test` top-level command for on-demand test subagent
  invocation
- Mobile testing agents (React Native, Flutter)
- Visual regression agent using screenshot comparison
- Integration with CI pipelines (run test subagents in CI)
- Test coverage metrics tracking via claude-mem over time

## Functional Requirements

### Cucumber/Gherkin Scenarios

```gherkin
Feature: Test subagent invocation by main agent

  Scenario: Main agent delegates backend testing
    Given the main agent has completed implementing a feature
    And the changed files include backend code
    When the main agent invokes the test-backend subagent
    And passes task description, changed files, and key patterns
    Then the test-backend subagent writes unit/integration tests
    And runs the tests
    And returns a YAML report with tests_written, results, and gaps

  Scenario: Main agent delegates E2E testing
    Given the main agent has completed implementing a feature
    And the changed files include frontend code
    When the main agent invokes the test-e2e-planner subagent
    Then the planner explores the app and produces a test plan
    When the main agent invokes the test-e2e-generator subagent
    And passes the test plan
    Then the generator writes Playwright tests and runs them
    And returns a YAML report with test results

  Scenario: Adversarial review finds coverage gap
    Given tests have been written for a feature
    And the implementation touches auth/session/state code
    When the main agent invokes the test-review subagent
    Then the review agent analyzes implementation and existing tests
    And identifies untested state transitions or auth boundaries
    And returns a YAML report with specific gap descriptions
    And recommendations for the main agent

  Scenario: Test subagent uses claude-mem for bug patterns
    Given a test subagent is invoked for a feature
    When the subagent queries claude-mem for past bugs in the
      affected code area
    And finds a previous session-state bug pattern
    Then the subagent includes a targeted test for that pattern
    And notes the claude-mem reference in its report

  Scenario: Test subagent uses RLM for dependency analysis
    Given RLM is initialized in the project
    When a test subagent is invoked
    Then the subagent optionally calls rlm_repl.py to trace
      dependencies of changed files
    And uses the dependency graph to identify additional code
      paths to test

  Scenario: E2E test healer fixes broken test
    Given an existing E2E test is failing
    And the failure is due to a UI change (selector, text, flow)
    When the main agent invokes the test-e2e-healer subagent
    Then the healer replays the failing test
    And inspects the current UI state
    And patches the test to match the new UI
    And confirms the test passes
```

### Detailed Requirements

1. **FR-1: Test subagent agent definitions** — Each subagent is a
   markdown file in `.claude/agents/` with YAML frontmatter specifying
   description, tools, model, and optionally permissionMode. The agent
   body contains the system prompt with role, expertise, input/output
   contract, and rules.

2. **FR-2: YAML output contract** — All test subagents return results
   in a standardized YAML format:
   ```yaml
   agent: test-backend  # or test-review, test-e2e-*
   task: "description of what was tested"
   tests_written:
     - path: tests/test_auth.py
       type: unit
       description: "Session state after role change"
   tests_run:
     total: 5
     passed: 4
     failed: 1
     errors: 0
   failures:
     - test: test_role_change_without_relogin
       error: "AssertionError: expected 200 got 403"
       file: tests/test_auth.py:42
   gaps_found:
     - area: auth/session
       description: "Role enable takes effect in DB but not
         session until re-login"
       severity: high
       recommendation: "Add test for mid-session role activation"
   claude_mem_refs:
     - id: 456
       title: "Past session bug in similar auth flow"
   ```

3. **FR-3: Input contract** — The main agent passes context to test
   subagents via the Task tool prompt:
   ```yaml
   task_description: "User story or task being tested"
   changed_files:
     - src/api/auth.py
     - src/models/user.py
   key_patterns:
     - auth/session management
     - role-based access control
   test_framework: pytest  # auto-detected or specified
   existing_tests:
     - tests/test_auth.py
     - tests/test_user.py
   rlm_available: true  # optional enrichment
   ```

4. **FR-4: Claude-mem integration** — All test subagents query
   claude-mem at the start of their run for:
   - Past bugs in the affected code area
   - Known failure patterns for the detected framework
   - Previous test review findings for the same module
   After completing, subagents save significant findings (new bugs,
   coverage gaps, pattern violations) to claude-mem.

5. **FR-5: RLM optional enrichment** — When RLM is initialized
   (`rlm_repl.py status` returns success), test subagents may call
   `rlm_repl.py` to:
   - Trace dependency chains of changed files
   - Find all callers/consumers of modified functions
   - Identify state management patterns in the codebase
   This is optional — agents must work without RLM.

6. **FR-6: Framework auto-detection** — Test subagents detect the
   project's test framework by examining:
   - Config files (pytest.ini, vitest.config.ts, jest.config.js, etc.)
   - Package files (package.json scripts, pyproject.toml, go.mod)
   - Existing test file patterns
   The agent adapts its test writing to the detected framework.

7. **FR-7: Playwright E2E agents** — The three E2E agents
   (planner, generator, healer) are forked from Playwright's official
   agent definitions. Local copies are maintained in this repo with:
   - Source reference comments at the top of each file
   - Upstream URL for pulling updates
   - Customizations clearly marked (claude-mem integration, YAML
     output, RLM enrichment)

8. **FR-8: Context isolation** — Each test subagent runs in its own
   context via the Claude Code Task tool. The test-writer never sees
   the main agent's implementation reasoning. The test-review agent
   sees only the code and tests, not the main agent's intent. This
   prevents the "cheating" problem where the same LLM tests what it
   planned rather than what was built.

## Non-Functional Requirements

### Performance
- **Subagent startup**: Should begin producing output within 10
  seconds of invocation
- **Total test cycle**: Backend test subagent should complete within
  5 minutes for a typical feature (under 10 changed files)
- **E2E test cycle**: Planner + generator should complete within
  10 minutes for a typical frontend feature

### Security
- **No credentials in context**: Test subagents must not receive or
  store API keys, passwords, or secrets in their prompts or reports
- **Sandboxed execution**: Tests run within Claude Code's existing
  sandbox — no elevated permissions

### Usability
- **Zero configuration for users**: Test subagents work out of the
  box after installation (copy to `~/.claude/agents/`)
- **Clear error messages**: If a test subagent fails (missing
  framework, no test files found), it returns a YAML report with
  clear error description rather than failing silently
- **Human-readable reports**: While YAML is the primary output,
  it should be readable by developers who inspect the subagent's
  results

### Reliability
- **Graceful degradation**: If claude-mem is unavailable, agents
  skip memory queries and proceed with available context. If RLM
  is not initialized, agents skip dependency analysis. Neither
  failure should block test execution.
- **Idempotent**: Running a test subagent twice on the same code
  should produce consistent results (same tests, same gaps)

### Architecture
- **KISS**: Each agent file is self-contained markdown with YAML
  frontmatter. No external build steps, no dependencies beyond
  Claude Code's built-in tools.
- **Same installation pattern**: Agents install alongside
  `rlm-subcall.md` — copy to `~/.claude/agents/`
- **Global MCP only**: Agents use globally-installed MCP servers
  (`~/.claude/mcp.json`) to avoid the known project-scoped MCP
  limitation for subagents

## Dependencies & Risks

### Dependencies
- **Claude Code Task tool**: Subagents are invoked via the Task
  tool with `subagent_type` parameter
- **Claude-mem MCP plugin**: Globally installed for memory queries
  (mandatory for full functionality, graceful degradation without)
- **Playwright** (for E2E agents): Must be installed in the target
  project. E2E agents detect its absence and report clearly.
- **Test frameworks**: At least one test framework must exist in
  the target project. Agents detect and adapt.

### Risks
- **Risk 1: Subagent context quality depends on main agent handoff**
  If the main agent provides a shallow summary of what was built,
  the test subagent produces shallow tests.
  *Mitigation*: Define a strict input contract (FR-3) that the
  /impl command enforces. Include changed files, key patterns,
  and task description as mandatory fields.
- **Risk 2: Playwright agent fork diverges from upstream**
  Local copies may fall behind Playwright's official agent updates.
  *Mitigation*: Document upstream source and version in each file
  header. Include update instructions in README.
- **Risk 3: Token cost per feature increases**
  Each test subagent call consumes additional tokens.
  *Mitigation*: Subagents use Haiku where possible (like
  rlm-subcall.md). The test-review agent is lightweight
  (analysis only, no test execution). Main agent context savings
  partially offset the cost.
- **Risk 4: Project-scoped MCP limitation**
  Subagents cannot access project-scoped MCP servers.
  *Mitigation*: Design requires global MCP only. Document this
  limitation clearly.

## Clarified Decisions (from discussion)

1. **Specialized agents over generic**: Three E2E agents (forked
   from Playwright) + backend test agent + adversarial review agent,
   rather than one parameterized generic agent
2. **RLM optional, claude-mem default**: Claude-mem is globally
   available and always used. RLM enrichment is optional (enhances
   dependency analysis when initialized)
3. **Main agent decides which subagent**: Infers from changed files
   (backend code → test-backend, frontend → test-e2e-*, mixed →
   both). User can override explicitly.
4. **Reuse existing Playwright agents**: Fork and customize rather
   than building E2E agents from scratch. Keep local copies with
   upstream references.
5. **YAML output format**: More token-efficient and LLM-friendly
   than JSON. Standardized across all test subagents.
6. **Frontend/E2E is priority**: Backend testing is acceptable in
   existing workflows. E2E coverage is the primary gap.
7. **Context isolation is a feature**: Test subagents intentionally
   don't see the main agent's reasoning — they test what was built,
   not what was intended.

## Open Questions

- What model should test subagents use? Haiku (cheaper, faster)
  vs Sonnet (more capable)? May vary by agent role — review agent
  may need Sonnet for deeper analysis while backend test-writer
  may work well with Haiku.
- Should test subagents run in worktree isolation by default, or
  only when explicitly requested? Worktrees prevent test file
  pollution but add overhead.
