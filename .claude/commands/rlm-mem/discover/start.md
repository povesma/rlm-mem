# Start RLM-Mem Coding Session

Start a coding session with comprehensive context from both RLM code analysis and claude-mem historical knowledge.

## When to Use

- **Beginning of each coding session**
- After `/rlm-mem:discover:init` has been run
- When you need full project context
- Resuming work after a break

## What This Command Does

1. **Retrieves historical context** from claude-mem
2. **Analyzes current codebase** with RLM
3. **Synthesizes** both into actionable session summary
4. **Recommends** next task based on data

## Process

### Step 1: Verify Systems

```bash
# Check RLM status
python3 ~/.claude/rlm_scripts/rlm_repl.py status
```

**If not initialized**: Suggest running `/rlm-mem:discover:init` first

**Capture**:
- Project path
- Total files indexed
- Languages
- Last indexed timestamp

### Step 2: Query Claude-Mem for Historical Context

**2a. Search for project overview**:
```
mcp__plugin_claude-mem_mcp-search__search(
  query="project overview goals architecture",
  project="{project_name}",
  limit=5
)
```

**2b. Search for recent work**:
```
mcp__plugin_claude-mem_mcp-search__search(
  query="implementation completed features recent work",
  project="{project_name}",
  limit=10,
  orderBy="created_at DESC"
)
```

**2c. Search for active tasks**:
```
mcp__plugin_claude-mem_mcp-search__search(
  query="task list TODO in progress",
  project="{project_name}",
  limit=5
)
```

**2d. Get full observations for top results**:
```
mcp__plugin_claude-mem_mcp-search__get_observations(
  ids=[filtered_ids_from_above]
)
```

**Extract from claude-mem**:
- Project goals and purpose
- Completed features
- Active/pending tasks
- Recent architectural decisions
- Known issues or tech debt

### Step 3: RLM Code Analysis

**3a. Find documentation files via RLM**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Find documentation
doc_files = [
    path for path, meta in repo_index['files'].items()
    if meta['lang'] in ['Markdown', 'Text', 'ReStructuredText']
    and not meta['is_binary']
    and ('README' in path.upper() or 'CLAUDE' in path.upper() or 'ai-docs' in path)
]

# Sort by relevance (root level first)
doc_files.sort(key=lambda x: (x.count('/'), x))

print('\n'.join(doc_files[:10]))
PY
```

**3b. Find active task files**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Find task files (not archived)
task_files = [
    path for path, meta in repo_index['files'].items()
    if 'tasks/' in path
    and path.endswith('.md')
    and '/archive/' not in path
    and not meta['is_binary']
]

# Group by JIRA ID
from collections import defaultdict
import re

tasks_by_jira = defaultdict(list)
for tf in task_files:
    match = re.search(r'([A-Z]+-\d+)', tf)
    if match:
        jira_id = match.group(1)
        tasks_by_jira[jira_id].append(tf)

# Print summary
for jira_id, files in sorted(tasks_by_jira.items()):
    print(f"{jira_id}: {len(files)} files")
    for f in files:
        print(f"  - {f}")
PY
```

**3c. Analyze repository changes (if needed)**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Get recently modified files (requires git)
import subprocess
import json

try:
    result = subprocess.run(
        ['git', 'log', '--pretty=format:', '--name-only', '--since=1.week.ago'],
        capture_output=True,
        text=True,
        cwd=repo_index['repo_root']
    )
    recent_files = [f for f in result.stdout.split('\n') if f.strip()]

    # Count modifications
    from collections import Counter
    mod_count = Counter(recent_files)

    # Top 10 most modified
    top_modified = mod_count.most_common(10)

    print("Recently modified files:")
    for file, count in top_modified:
        lang = repo_index['files'].get(file, {}).get('lang', 'Unknown')
        print(f"  {file} ({lang}): {count} changes")
except Exception as e:
    print(f"Could not get recent changes: {e}")
PY
```

### Step 4: Synthesize Session Summary

Combine findings from claude-mem and RLM into comprehensive summary:

```markdown
# 🚀 Session Started: {project_name}

*Generated from RLM code analysis + claude-mem historical context*

## 📊 Project Overview

{overview_from_claude_mem_or_readme}

**Repository Statistics** (RLM):
- **Files**: {total_files:,} files ({size_mb:.1f} MB)
- **Primary languages**: {lang_breakdown}
- **Last indexed**: {rlm_timestamp}

## ✅ Completed Features

{completed_features_from_claude_mem}

Recent implementations:
{recent_work_from_mem}

## 🏗️ Current Architecture

{architecture_from_mem_or_docs}

**Key Patterns Discovered** (RLM):
{patterns_if_analyzed}

## 📝 Active Tasks

### From Task Files (RLM):
{active_tasks_from_rlm_analysis}

### From Memory (Claude-Mem):
{in_progress_tasks_from_mem}

## 🔥 Recent Activity

**Most Modified Files** (Past week):
{recently_modified_from_git}

**Recent Observations** (Claude-Mem):
{recent_observations}

## 💡 Recommended Next Task

Based on:
- Task priorities from {task_file_or_mem}
- Current momentum (recently modified areas)
- Historical context (what makes sense next)

**Suggestion**: {next_task_recommendation}

**Rationale**: {why_this_task}

## 🎯 Quick Actions

- **Start recommended task**: `/rlm-mem:develop:impl`
- **Create new feature**: `/rlm-mem:plan:prd`
- **Search past work**: Ask me about anything (claude-mem enabled)
- **Review codebase**: Ask specific questions (RLM will analyze)

---

**System Status**:
- ✅ RLM: Ready ({total_files} files indexed)
- ✅ Claude-Mem: Ready ({obs_count} observations)
- ✅ Git: {git_branch} ({git_status})

Ready to code! 🎉
```

## Context Quality Levels

Depending on what's available, provide appropriate detail:

### Full Context (Best Case)
- Claude-mem has project overview + recent work
- RLM has complete file index
- Git history available
- Task files exist
→ **Rich, actionable summary**

### Partial Context
- RLM index exists, but no claude-mem data yet
- Or vice versa
→ **Basic summary, suggest indexing missing system**

### Minimal Context
- Only RLM index, no docs, no mem
→ **File statistics, suggest creating documentation**

## Important Notes

1. **Fast Context Refresh**:
   - Use cached RLM index (don't re-index)
   - Quick claude-mem queries (limit results)
   - Aim for <30s total time

2. **Actionable Output**:
   - Don't just describe, recommend next action
   - Prioritize based on data, not guesses
   - Make it easy to start working

3. **Error Handling**:
   - If RLM not initialized: suggest `/rlm-mem:discover:init`
   - If claude-mem empty: that's OK, use RLM only
   - If no tasks found: suggest creating one

4. **No Implementation**:
   - This command only provides context
   - DO NOT start implementing tasks
   - DO NOT read entire source files
   - Wait for user to choose next action

## Example Output

```
# 🚀 Session Started: app-astudio

*Generated from RLM code analysis + claude-mem historical context*

## 📊 Project Overview

Professional 3D scanning application for desktop platforms (Windows, macOS, Linux).
Built with C++/Qt for performance and cross-platform support.

**Repository Statistics** (RLM):
- **Files**: 3,940 files (157.1 MB)
- **Primary languages**:
  - C/C++ (31.8%), C++ (22.2%), TypeScript (0.9%)
- **Last indexed**: 2 hours ago

## ✅ Completed Features

From claude-mem:
- OAuth2 authentication system (AS-1234)
- Real-time 3D preview (AS-1245)
- Export to multiple formats (AS-1267)

## 🏗️ Current Architecture

Clean Architecture pattern with Qt framework:
- UI Layer: Qt QML/Widgets
- Application Layer: C++ handlers
- Domain Layer: Core business logic
- Infrastructure: File I/O, networking

## 📝 Active Tasks

### From Task Files (RLM):
- AS-1289: Improve scanning accuracy (4 subtasks, 2 done)
- AS-1290: Add cloud storage integration (planning phase)

### From Memory (Claude-Mem):
- Last worked on: AS-1289 subtask 3 (mesh optimization)

## 🔥 Recent Activity

**Most Modified Files** (Past week):
- src/scanning/mesh_processor.cpp: 5 changes
- src/ui/preview_widget.qml: 3 changes

## 💡 Recommended Next Task

**Suggestion**: Continue AS-1289 subtask 3 (mesh optimization)

**Rationale**:
- 2 of 4 subtasks complete
- Recently modified files related to this task
- Builds on completed work
- High priority (from PRD)

## 🎯 Quick Actions

Ready to code! 🎉
```

## Final Instructions

1. Check RLM and claude-mem status
2. Query historical context (claude-mem)
3. Analyze current state (RLM)
4. Synthesize comprehensive summary
5. Recommend next task (data-driven)
6. DO NOT implement anything yet
7. Wait for user to choose action
