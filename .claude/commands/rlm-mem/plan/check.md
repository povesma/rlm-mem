# Check Task List Status with RLM

Check task completion status by analyzing actual code implementation.

## Process

### Step 1: Load Task List

```bash
# Find task files
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
task_files = [
    path for path, meta in repo_index['files'].items()
    if 'tasks/' in path
    and path.endswith('-tasks.md')
    and '/archive/' not in path
]
print('\n'.join(sorted(task_files)))
PY
```

### Step 2: Read Task File

Read the active task file

### Step 3: Verify Each Task Against Code

For each incomplete task `[ ]`:

**Use RLM to verify implementation**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Search for files related to task
# Example: task is "Add OAuth2 handler"
search_terms = ['oauth2', 'handler']

found_files = []
for term in search_terms:
    matches = [
        path for path, meta in repo_index['files'].items()
        if term.lower() in path.lower()
        and not meta['is_binary']
    ]
    found_files.extend(matches)

print(f"Found {len(set(found_files))} related files")
print('\n'.join(sorted(set(found_files))[:10]))
PY
```

**Read relevant files** to verify implementation

### Step 4: Update Task Status

**For completed tasks**:
- Mark subtask as `[X]`
- If all subtasks done, mark parent as `[X]`
- Update ai-docs/ when parent complete:
  - ai-docs/API.md
  - ai-docs/ARCHITECTURE.md
  - ai-docs/DEVELOPMENT.md
  - ai-docs/PRD.md
  - ai-docs/README.md
  - ai-docs/SCHEMA.md
  - ai-docs/USAGE.md

**Save completion to claude-mem**:
```
mcp__plugin_claude-mem_mcp-search__save_memory(
  text=f"[JIRA: {jira_id}]\n[TYPE: TASK-COMPLETION]\n\nTask '{task_name}' verified complete via code analysis.\n\nFiles modified:\n{file_list}",
  title=f"{jira_id} - Task Completion",
  project=project_name
)
```

### Step 5: Halt on First Incomplete

Stop checking when you find first truly incomplete task

## Final Instructions

1. Load and read task file
2. For each `[ ]` task, use RLM to verify in code
3. Update status for completed tasks
4. Update ai-docs/ when parent tasks complete
5. Save completions to claude-mem
6. Halt at first incomplete
