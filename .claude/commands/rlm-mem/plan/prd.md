# Generate PRD with RLM-Mem Hybrid Analysis

Create a Product Requirements Document informed by both historical context (claude-mem) and current codebase capabilities (RLM).

## When to Use

- Planning a new feature
- After `/rlm-mem:discover:start` has provided session context
- When you need a data-driven, context-aware PRD

## What This Command Does

1. **Searches past PRDs** (claude-mem) to learn structure and quality
2. **Analyzes current codebase** (RLM) to understand capabilities
3. **Synthesizes** a PRD that builds on existing work
4. **Saves** PRD to claude-mem for future reference

## Process

### Step 1: Gather Requirements from User

Ask the user for feature details:
- **JIRA ID**: (e.g., AS-1234) - required for file organization
- **Feature name**: Short descriptive name
- **User problem**: What problem does this solve?
- **Expected outcome**: What should the user be able to do?

### Step 2: Search Claude-Mem for Past PRDs

**2a. Find similar past features**:
```
mcp__plugin_claude-mem_mcp-search__search(
  query="{feature_name} requirements user stories similar features",
  project="{project_name}",
  type="PRD",
  limit=5
)
```

**2b. Get full details of best matches**:
```
mcp__plugin_claude-mem_mcp-search__get_observations(
  ids=[top_3_relevant_ids]
)
```

**Extract from past PRDs**:
- PRD structure and sections used
- Quality of user stories (format, detail level)
- Acceptance criteria patterns
- How requirements were scoped

### Step 3: RLM Analysis of Current Capabilities

**3a. Find related existing features**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Search for files related to this feature
# Example: if feature is "OAuth2 auth", search for auth files

search_terms = ['{feature_keyword1}', '{feature_keyword2}']
relevant_files = []

for term in search_terms:
    # Find files by name pattern
    matches = [
        path for path, meta in repo_index['files'].items()
        if term.lower() in path.lower()
        and not meta['is_binary']
        and meta['lang'] in ['C++', 'C/C++', 'Python', 'TypeScript', 'JavaScript']
    ]
    relevant_files.extend(matches)

# Remove duplicates
relevant_files = list(set(relevant_files))[:20]

# Print for analysis
import json
print(json.dumps({
    'found': len(relevant_files),
    'files': relevant_files
}))
PY
```

**3b. Analyze architecture patterns** (if relevant files found):

Use rlm-subcall subagent to analyze sample files:
- Query: "Identify existing architecture patterns, API structure, data models, and integration points that relate to this feature"
- Limit: Top 3-5 most relevant files
- Collect findings about current capabilities

**3c. Identify gaps**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# What's missing for this feature?
# Example: Do we have auth infrastructure? Do we have API endpoints?

capabilities = {
    'existing': [],  # What we have
    'missing': [],   # What we need to build
}

# Based on RLM analysis and file discovery
# Document current state

print(json.dumps(capabilities, indent=2))
PY
```

### Step 4: Synthesize PRD

Create PRD combining insights:

```markdown
# {JIRA-ID}: {Feature Name} - PRD

**Status**: Draft
**Created**: {date}
**JIRA**: [{JIRA-ID}](https://jira.example.com/browse/{JIRA-ID})
**Author**: Claude (via rlm-mem analysis)

---

## Context

{User-provided problem statement}

### Current State (from RLM analysis)
{What currently exists in the codebase that's relevant}

### Past Similar Features (from claude-mem)
{Reference to similar features we've built, what we learned}

## Problem Statement

**Who**: {Target user persona}
**What**: {Specific problem they face}
**Why**: {Impact of the problem}
**When**: {Context/triggers}

## Goals

### Primary Goal
{Main objective this feature achieves}

### Secondary Goals
- {Supporting objective 1}
- {Supporting objective 2}

## User Stories

### Epic
As a {user type}, I want to {capability}, so that {benefit}.

### User Stories
1. **As a** {user type}
   **I want** {specific functionality}
   **So that** {specific benefit}

   **Acceptance Criteria**:
   - [ ] {Testable criterion 1}
   - [ ] {Testable criterion 2}
   - [ ] {Testable criterion 3}

2. {Additional user stories following same pattern}

## Requirements

### Functional Requirements
1. **FR-1**: {Requirement description}
   - **Priority**: High/Medium/Low
   - **Rationale**: {Why this is needed}
   - **Dependencies**: {What this depends on from RLM analysis}

2. **FR-2**: {Next requirement}

### Non-Functional Requirements
1. **NFR-1**: Performance - {Specific metric}
2. **NFR-2**: Security - {Specific requirement}
3. **NFR-3**: Usability - {Specific expectation}

### Technical Constraints
{Based on RLM analysis of existing architecture}
- Must integrate with: {Existing systems found via RLM}
- Should follow patterns: {Patterns discovered in codebase}
- Cannot change: {Constraints from existing architecture}

## Out of Scope

{What we explicitly won't do in this iteration}
- {Out of scope item 1}
- {Out of scope item 2}

## Success Metrics

**How we'll measure success**:
1. {Metric 1}: {Target value}
2. {Metric 2}: {Target value}
3. {Metric 3}: {Target value}

## Open Questions

{Questions discovered during RLM analysis or missing from requirements}
- [ ] {Question 1}
- [ ] {Question 2}

## References

### From Codebase (RLM)
- Relevant files: {List of files from RLM analysis}
- Existing patterns: {Patterns to follow}
- Integration points: {Where this connects}

### From History (Claude-Mem)
- Similar features: {Reference to past PRDs}
- Lessons learned: {What to avoid/replicate}

---

**Next Steps**:
1. Review and refine this PRD
2. Run `/rlm-mem:plan:tech-design` to create technical design
3. Run `/rlm-mem:plan:tasks` to break down into tasks
```

### Step 5: Save PRD to Claude-Mem

```
mcp__plugin_claude-mem_mcp-search__save_memory(
  text=f"""[JIRA: {jira_id}]
[TYPE: PRD]
[PROJECT: {project_name}]
[STATUS: Draft]

{full_prd_content}
""",
  title=f"{jira_id} - {feature_name} PRD",
  project=project_name
)
```

### Step 6: Save PRD to File System

```bash
# Create task directory
mkdir -p tasks/{jira_id}-{feature_name_slug}

# Write PRD file
# tasks/{jira_id}-{feature_name_slug}/{YYYY-MM-DD}-{jira_id}-{feature_name_slug}-prd.md
```

### Step 7: Report Completion

```markdown
# ✅ PRD Created: {JIRA-ID}

**Feature**: {Feature Name}
**File**: `tasks/{jira_id}-{feature_name_slug}/{date}-{jira_id}-{feature_name_slug}-prd.md`

## Insights Used

### From Claude-Mem:
- Analyzed {n} past PRDs
- Learned structure from: {best_example_jira_id}
- Referenced similar feature: {similar_feature}

### From RLM:
- Analyzed {m} relevant files
- Discovered existing capabilities: {summary}
- Identified integration points: {list}
- Noted constraints: {constraints}

## Quality Improvements

Thanks to hybrid analysis, this PRD:
✅ Follows proven structure from past PRDs
✅ Aware of current codebase capabilities
✅ References actual integration points
✅ Scoped based on existing patterns
✅ Includes realistic constraints

## Next Steps

**Create technical design**:
```
/rlm-mem:plan:tech-design
```

**Or refine PRD first**:
- Review user stories
- Validate acceptance criteria
- Confirm scope
```

## Important Notes

1. **Quality from Examples**:
   - Use past PRDs as quality benchmarks
   - Don't just copy structure, learn what makes them good
   - Adapt to current feature needs

2. **Grounded in Reality**:
   - RLM analysis shows what actually exists
   - Don't assume capabilities, verify with code
   - Constraints come from actual architecture

3. **Iterative**:
   - This is a draft, expect refinement
   - User feedback may change requirements
   - Technical design may reveal gaps

4. **Save Everything**:
   - Save to both claude-mem and file system
   - File system: team collaboration
   - Claude-mem: future AI context

## Example Output

```
# ✅ PRD Created: AS-1290

**Feature**: Cloud Storage Integration
**File**: `tasks/AS-1290-cloud-storage/2025-02-06-AS-1290-cloud-storage-prd.md`

## Insights Used

### From Claude-Mem:
- Analyzed 3 past PRDs
- Learned structure from: AS-1245 (similar integration feature)
- Referenced: OAuth2 auth pattern

### From RLM:
- Analyzed 15 relevant files
- Discovered: Existing storage abstraction layer
- Integration points: FileManager, SyncService classes
- Constraints: Must support existing backup format

## Quality Improvements

✅ Follows proven structure
✅ Aware of storage abstraction layer
✅ References actual FileManager API
✅ Scoped to work with existing auth
✅ Realistic constraints from architecture

## Next Steps
/rlm-mem:plan:tech-design
```

## Final Instructions

1. Gather requirements from user (JIRA ID, feature name, problem)
2. Search claude-mem for past PRDs to learn from
3. Use RLM to analyze current codebase capabilities
4. Synthesize PRD combining historical best practices + current reality
5. Save to both claude-mem and file system
6. Report what insights were used and quality improvements
7. Suggest `/rlm-mem:plan:tech-design` as next step
8. DO NOT start technical design yet, wait for user approval
