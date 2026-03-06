# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

RLM-Mem is an **installation package** for Claude Code that combines:
- **RLM**: Analyzes large codebases via persistent Python REPL
- **Claude-Mem** (MANDATORY): Semantic memory of past decisions
- **12 Commands**: Complete development workflow
- **5 Test Subagents**: Isolated testing agents invoked via Task tool

Users install to `~/.claude/` to use across all their projects.

## Architecture

### Three Components

1. **RLM REPL** (`.claude/rlm_scripts/rlm_repl.py`)
   - Pure Python stdlib, no dependencies
   - Indexes repositories: `python3 rlm_repl.py init-repo .`
   - Stores state in `.claude/rlm_state/state.pkl`
   - Detects 50+ languages via `LANGUAGE_MAP` (line 60-130)

2. **RLM Subagent** (`.claude/agents/rlm-subcall.md`)
   - Haiku-powered chunk analysis
   - Returns JSON with patterns/dependencies/symbols

3. **Test Subagents** (`.claude/agents/test-*.md`)
   - Five specialized agents invoked via `Task` tool during `/impl`
   - **test-backend** (Haiku): writes & runs unit/integration tests, auto-detects
     pytest/vitest/jest/go/cargo/phpunit
   - **test-review** (Sonnet): adversarial gap analysis — finds untested state
     transitions, auth boundaries, error paths. Reads code only, writes nothing.
   - **test-e2e-planner** (Sonnet): explores live app via Playwright MCP, produces
     markdown test plan. Forked from `microsoft/playwright`.
   - **test-e2e-generator** (Sonnet): converts plan to `.spec.ts` files, verifies
     selectors live. Forked from `microsoft/playwright`.
   - **test-e2e-healer** (Sonnet): debugs failing tests, patches selectors/timing/
     data, marks environmental blockers with `test.fixme()`. Forked from
     `microsoft/playwright`.
   - All agents use YAML input/output contracts and degrade gracefully without
     claude-mem or RLM

4. **Commands** (`.claude/commands/rlm-mem/`)
   - 12 commands: discover (2), plan (4), develop (3), review (1), git (1)
   - Each integrates RLM + claude-mem via Bash and MCP tools

### Installation Flow

```bash
# Users copy FROM this repo TO their system:
cp .claude/rlm_scripts/rlm_repl.py ~/.claude/rlm_scripts/
cp .claude/agents/rlm-subcall.md ~/.claude/agents/
cp .claude/agents/test-*.md ~/.claude/agents/     # test subagents
cp -r .claude/commands/rlm-mem ~/.claude/commands/
```

## Claude-Mem Integration (MANDATORY)

Commands use MCP tools (requires plugin):
- `mcp__plugin_claude-mem_mcp-search__search`
- `mcp__plugin_claude-mem_mcp-search__save_memory`

Commands should **fail with clear error** if claude-mem unavailable.

## Development

### Test RLM REPL
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py --help
python3 ~/.claude/rlm_scripts/rlm_repl.py init-repo .
python3 ~/.claude/rlm_scripts/rlm_repl.py status
```

### Modify Commands
Edit `.claude/commands/rlm-mem/<phase>/<name>.md` directly - changes apply immediately.

### Add Language Support
Edit `rlm_repl.py` → `LANGUAGE_MAP` dict.

## File Structure

```
.claude/
├── agents/
│   ├── rlm-subcall.md          # RLM chunk analysis subagent (Haiku)
│   ├── test-backend.md         # Backend test writer (Haiku)
│   ├── test-review.md          # Adversarial gap analyzer (Sonnet)
│   ├── test-e2e-planner.md     # E2E planner, Playwright fork (Sonnet)
│   ├── test-e2e-generator.md   # E2E generator, Playwright fork (Sonnet)
│   └── test-e2e-healer.md      # E2E healer, Playwright fork (Sonnet)
├── commands/rlm-mem/           # 12 command definitions
└── rlm_scripts/rlm_repl.py     # REPL (833 lines)

README.md                       # User guide
TROUBLESHOOTING.md              # Common errors
COMPARISON.md                   # vs original claude_code_RLM
```

## Key Constraints

- **No dependencies**: REPL uses stdlib only
- **Claude-mem required**: Not optional
- **Local state**: `.claude/rlm_state/` never committed (in `.gitignore`)
- **Quality over speed**: Commands intentionally thorough

## Task Marking Convention

- **`[X]`** — done: ONLY when tested/verified AND passing, or explicitly confirmed by user
- **`[~]`** — coded, pending testing: implementation written but not yet verified
- **`[ ]`** — not started
- Never mark `[X]` based on writing code alone. Assume it doesn't work until proven.

## Related

Extends [claude_code_RLM](https://github.com/brainqub3/claude_code_RLM) for code repos + claude-mem. Based on [RLM paper](https://arxiv.org/abs/2512.24601) (MIT CSAIL).
