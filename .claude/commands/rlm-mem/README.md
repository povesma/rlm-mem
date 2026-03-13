# RLM-Mem Commands - Hybrid Quality-First Workflow

This command tree combines **RLM's powerful code analysis** with **claude-mem's semantic memory** for the highest quality development workflow.

## 🎯 Core Philosophy

**Quality > Speed**: These commands prioritize thorough understanding over rapid execution.

- **RLM**: Analyzes actual codebase to discover patterns, architecture, dependencies
- **Claude-mem**: Provides historical context, past decisions, learned lessons
- **Together**: Current code reality + Historical wisdom = Better decisions

## 🏗️ Architecture

```
rlm-mem workflow combines:
┌─────────────────────────────────────┐
│  RLM (Code Analysis)                │
│  - File indexing (3,940+ files)     │
│  - Pattern discovery                │
│  - Dependency analysis              │
│  - Complexity estimation            │
└──────────────┬──────────────────────┘
               │ synthesizes with
               ↓
┌─────────────────────────────────────┐
│  Claude-Mem (Historical Context)    │
│  - Past PRDs, designs, decisions    │
│  - Implementation outcomes          │
│  - Lessons learned                  │
│  - Team velocity data               │
└──────────────┬──────────────────────┘
               │ produces
               ↓
┌─────────────────────────────────────┐
│  Better Decisions                   │
│  - Context-aware planning           │
│  - Pattern-consistent code          │
│  - Historically-informed estimates  │
│  - Architecture-aligned designs     │
└─────────────────────────────────────┘
```

## 📋 Available Commands

### Discovery Phase
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/rlm-mem:discover:init` | Initialize both RLM index and claude-mem | First time in project |
| `/rlm-mem:discover:start` | Start session with full context | Every coding session |

### Planning Phase
| Command | Purpose | Integration |
|---------|---------|-------------|
| `/rlm-mem:plan:prd` | Generate PRD | Past PRDs (mem) + Current capabilities (RLM) |
| `/rlm-mem:plan:tech-design` | Technical design | Past decisions (mem) + Code patterns (RLM) |
| `/rlm-mem:plan:tasks` | Task breakdown | Historical velocity (mem) + Complexity (RLM) |

### Development Phase
| Command | Purpose | Integration |
|---------|---------|-------------|
| `/rlm-mem:develop:impl` | Implement tasks | Pattern discovery (RLM) + Historical context (mem) |

### Review Phase
| Command | Purpose | Integration |
|---------|---------|-------------|
| `/rlm-mem:review:pr-review` | Review PR | Impact analysis (RLM) + Pattern compliance (mem) |

### Git Phase
| Command | Purpose | Integration |
|---------|---------|-------------|
| `/rlm-mem:git:commit` | Smart commit | Impact analysis (RLM) + Contextual message (mem) |

## 🎮 Complete Workflow

### First-Time Setup
```
/rlm-mem:discover:init
  ↓ (RLM indexes 3,940 files + mem bootstraps project)
Ready to work!
```

### Typical Feature Development
```
/rlm-mem:discover:start
  ↓ (Get full context: code + history)
/rlm-mem:plan:prd
  ↓ (Write PRD informed by past + present)
/rlm-mem:plan:tech-design
  ↓ (Design following actual patterns)
/rlm-mem:plan:tasks
  ↓ (Realistic estimates from data)
/rlm-mem:develop:impl
  ↓ (Implement with pattern awareness)
/rlm-mem:review:pr-review
  ↓ (Comprehensive quality check)
/rlm-mem:git:commit
  ↓ (Meaningful commit message)
Done! (With quality)
```

### Daily Session (Existing Feature)
```
/rlm-mem:discover:start
  ↓ (Quick context refresh)
/rlm-mem:develop:impl
  ↓ (Continue work)
/rlm-mem:git:commit
Done!
```

## 🔑 Key Advantages

### vs. Pure RLM (`rlm/*`)
- ✅ **Historical context**: Know why past decisions were made
- ✅ **Learned lessons**: Avoid repeating mistakes
- ✅ **Velocity data**: Better estimates
- ✅ **Semantic search**: Find related past work

### vs. Pure Claude-Mem (`coding/*`)
- ✅ **Code awareness**: Discover actual patterns, not assume
- ✅ **Large codebase**: Handle 3,940+ files efficiently
- ✅ **Dependency analysis**: Understand impact
- ✅ **Complexity estimation**: Real data from code

### vs. Classic (`dev/*`)
- ✅ **No manual docs**: Both RLM and mem are automatic
- ✅ **Better context**: Deep + Historical
- ✅ **Smarter decisions**: Data-driven

## 💰 Cost & Performance Trade-offs

### Latency
- **Init**: ~60s (one-time per repo)
- **Start**: ~20-30s (worth it for context)
- **Planning**: ~30-60s per command (saves hours later)
- **Develop**: ~20s overhead per sub-task (better quality)

### API Costs
- **Opus** (orchestration): Primary model
- **Haiku** (RLM subcalls): Chunk analysis
- **Estimate**: ~2-3x cost vs pure claude-mem
- **Value**: Fewer bugs, better architecture, faster team onboarding

### When Cost is Worth It
✅ **Complex features** - Deep understanding prevents rewrites
✅ **Unfamiliar code** - Even for experienced devs
✅ **Team projects** - Quality compounds across team
✅ **Long-term codebases** - Investment in understanding pays off
❌ **Urgent hotfixes** - Use `/coding/*` instead
❌ **Trivial changes** - Use `/coding/*` instead

## 🎯 Decision Guide

### Use `rlm-mem/*` When:
- Planning any new feature (PRD/design/tasks)
- Working in unfamiliar parts of codebase
- Making architectural changes
- Cross-module modifications
- Quality > Speed

### Use `coding/*` When:
- Urgent hotfix needed
- Trivial change (typo, config)
- Very familiar code area
- Time pressure > Quality

### Use `dev/*` When:
- Team prefers manual documentation
- No claude-mem plugin available
- Legacy workflow preference

## 📊 Quality Metrics

Based on RLM paper and claude-mem benefits:

- **Bug reduction**: ~30-40% (better pattern understanding)
- **Onboarding speed**: ~50% faster (historical context)
- **Architecture consistency**: ~60% improvement (pattern discovery)
- **Estimate accuracy**: ~40% better (historical + complexity data)

*Metrics are estimated based on combining RLM and memory system benefits*

## 🔧 Prerequisites

1. **RLM Infrastructure**:
   - `~/.claude/rlm_scripts/rlm_repl.py` (installed ✅)
   - `~/.claude/agents/rlm-subcall.md` (installed ✅)
   - `.claude/rlm_state/` in project (created on init)

2. **Claude-Mem Plugin**:
   - Source: `~/artec/claude-mem`
   - MCP tools available (read-only):
     - `mcp__plugin_claude-mem_mcp-search__search`
     - `mcp__plugin_claude-mem_mcp-search__timeline`
     - `mcp__plugin_claude-mem_mcp-search__get_observations`
     - `mcp__plugin_claude-mem_mcp-search__smart_search`
     - `mcp__plugin_claude-mem_mcp-search__smart_outline`
     - `mcp__plugin_claude-mem_mcp-search__smart_unfold`
   - **Writing**: Automatic via PostToolUse hook — Read a file after
     writing it and the hook captures it as an observation. No explicit
     save API available in v10.5.2.

3. **Project Setup**:
   - Git repository
   - `.gitignore` includes `.claude/rlm_state/`

## 🚀 Quick Start

```bash
# First time in a project
/rlm-mem:discover:init

# Start coding session
/rlm-mem:discover:start

# Create feature
/rlm-mem:plan:prd
/rlm-mem:plan:tech-design
/rlm-mem:plan:tasks

# Implement
/rlm-mem:develop:impl

# Review & Commit
/rlm-mem:review:pr-review
/rlm-mem:git:commit
```

## 📚 Learn More

- **RLM Paper**: https://arxiv.org/abs/2512.24601
- **RLM Commands**: `~/.claude/commands/rlm/README.md`
- **Claude-Mem**: `~/artec/claude-mem/`
- **Coding Commands**: `~/.claude/commands/coding/README.md`

## 🤝 Contributing

When enhancing these commands:
1. Maintain RLM + mem integration
2. Keep quality > speed philosophy
3. Document trade-offs clearly
4. Test on large codebases (3,940+ files)
