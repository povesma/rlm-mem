# Generate Technical Design with RLM-Mem Hybrid Analysis

Create a technical design informed by past architectural decisions (claude-mem) and current code patterns (RLM).

## When to Use

- After PRD is approved
- When planning implementation approach
- Before breaking down into tasks

## Process

### Step 1: Load Context

**Read PRD**:
- From file: `tasks/{jira-id}-{feature}/...-prd.md`
- Or search claude-mem for recent PRD

**Search past tech designs** (claude-mem):
```
mcp__plugin_claude-mem_mcp-search__search(
  query="{feature_keywords} architecture design patterns technical",
  type="TECH-DESIGN",
  limit=5
)
```

### Step 2: RLM Architecture Discovery

**Discover existing patterns**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Find architecture-relevant files
arch_files = []

# Look for main architectural components
patterns = ['handler', 'service', 'controller', 'manager', 'repository', 'model']
for pattern in patterns:
    matches = [
        path for path, meta in repo_index['files'].items()
        if pattern in path.lower()
        and meta['lang'] in ['C++', 'C/C++', 'TypeScript', 'Python']
        and not meta['is_binary']
    ]
    arch_files.extend(matches[:5])  # Top 5 per pattern

print('\n'.join(set(arch_files)[:30]))
PY
```

**Analyze patterns with rlm-subcall**:
- Query: "Extract architectural patterns: layering, dependency injection, error handling, data flow, module structure"
- Files: Top 10 most representative architecture files
- Collect: Design patterns, conventions, anti-patterns

### Step 3: Identify Integration Points

**Find where new code will connect**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Based on PRD requirements, find integration points
# Example: If adding auth, find where current auth is used

integration_points = {
    'will_modify': [],   # Existing files we'll change
    'will_create': [],   # New files we'll add
    'dependencies': [],  # External deps we'll use
}

# Analyze based on feature requirements
# ...

import json
print(json.dumps(integration_points, indent=2))
PY
```

### Step 4: Learn from History

**Query past decisions** (claude-mem):
```
mcp__plugin_claude-mem_mcp-search__search(
  query="why we chose {relevant_tech} architecture decision trade-offs",
  limit=5
)
```

Extract:
- Past architectural decisions and rationale
- Trade-offs made and lessons learned
- Patterns that worked well
- Patterns that caused problems

### Step 5: Synthesize Technical Design

Create design document:

```markdown
# {JIRA-ID}: {Feature Name} - Technical Design

**Status**: Draft
**PRD**: [{JIRA-ID}-prd.md](link)
**Created**: {date}

## Overview

{High-level technical approach}

## Current Architecture (RLM Analysis)

**Discovered Patterns**:
- {Pattern 1 from codebase}
- {Pattern 2 from codebase}

**Relevant Components**:
- {Component 1}: {Description + file locations}
- {Component 2}: {Description + file locations}

## Past Decisions (Claude-Mem)

**Relevant Historical Context**:
- {Decision 1 from past}: {Why it matters for this feature}
- {Decision 2}: {Lesson learned}

## Proposed Design

### Architecture

{Detailed design following discovered patterns}

**Layering**:
- UI Layer: {What we'll add/modify}
- Application Layer: {What we'll add/modify}
- Domain Layer: {What we'll add/modify}
- Infrastructure: {What we'll add/modify}

### Components

**New Components**:
1. **{Component Name}**
   - **Purpose**: {Why}
   - **Location**: {Where in codebase}
   - **Pattern**: {Following which existing pattern}
   - **Dependencies**: {What it uses}

**Modified Components**:
1. **{Existing Component}** ({file:line})
   - **Changes**: {What we'll modify}
   - **Rationale**: {Why}
   - **Risk**: {Impact assessment}

### Data Models

{New or modified data structures}

### API Design

{New endpoints, methods, or interfaces}

### Integration Points

**Connects To** (from RLM analysis):
- {System 1}: via {interface}
- {System 2}: via {method}

### Error Handling

{Following discovered patterns from codebase}

### Testing Strategy

{Based on existing test patterns}

## Trade-offs

**Considered Approaches**:
1. **Option A**: {Description}
   - Pros: {Benefits}
   - Cons: {Drawbacks}
   - Historical context: {From claude-mem}

2. **Option B (Recommended)**: {Description}
   - Pros: {Benefits}
   - Cons: {Drawbacks}
   - Why recommended: {Rationale based on RLM + mem}

## Implementation Constraints

**From Existing Architecture** (RLM):
- {Constraint 1}
- {Constraint 2}

**From Past Experience** (Claude-Mem):
- {Lesson 1}
- {Lesson 2}

## Files to Create/Modify

**Create**:
- `{path/to/new/file.ext}` - {Purpose}

**Modify**:
- `{path/to/existing/file.ext:line}` - {Changes}

## Dependencies

**External**:
- {Library 1}: {Version, why}

**Internal**:
- {Module 1}: {How we'll use it}

## Security Considerations

{Security requirements and mitigations}

## Performance Considerations

{Performance requirements and optimizations}

## Rollback Plan

{How to revert if issues arise}

## Open Questions

- [ ] {Technical question 1}
- [ ] {Technical question 2}

## References

### Code (RLM):
- {File 1}: {Relevant pattern}
- {File 2}: {Example to follow}

### History (Claude-Mem):
- {Past design}: {What to learn}

---

**Next Steps**:
1. Review and approve design
2. Run `/rlm-mem:plan:tasks` for task breakdown
```

### Step 6: Save to Claude-Mem

```
mcp__plugin_claude-mem_mcp-search__save_memory(
  text=f"[JIRA: {jira_id}]\n[TYPE: TECH-DESIGN]\n\n{design_content}",
  title=f"{jira_id} - Technical Design",
  project=project_name
)
```

### Step 7: Save to File

```
tasks/{jira-id}-{feature}/{date}-{jira-id}-{feature}-tech-design.md
```

## Final Instructions

1. Load PRD and search past designs
2. Use RLM to discover existing patterns
3. Identify integration points via RLM
4. Learn from historical decisions via claude-mem
5. Synthesize design that follows patterns + learns from past
6. Save to both systems
7. Suggest `/rlm-mem:plan:tasks` as next step
