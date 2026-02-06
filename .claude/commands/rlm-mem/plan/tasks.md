# Generate Task List with RLM-Mem Hybrid

Create realistic task breakdown using RLM complexity analysis + claude-mem historical velocity.

## Process

1. **Load tech design** (from file or claude-mem)

2. **Search historical velocity** (claude-mem):
```
mcp__plugin_claude-mem_mcp-search__search(
  query="task list estimates velocity similar features",
  type="TASK-LIST",
  limit=5
)
```

3. **RLM complexity estimation**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Estimate based on files to modify/create from tech design
files_to_change = ['{list_from_design}']

complexity_score = 0
for file in files_to_change:
    if file in repo_index['files']:
        meta = repo_index['files'][file]
        size = meta['size']
        # Larger files = more complex to modify
        complexity_score += min(size / 1000, 10)  # Cap at 10 points
    else:
        # New file creation
        complexity_score += 3

print(f"Complexity score: {complexity_score}")
print(f"Estimated subtasks: {int(complexity_score / 2) + 2}")
PY
```

4. **Generate task breakdown** combining:
   - Technical design (what to build)
   - RLM complexity (how hard)
   - Past velocity (how long similar took)

5. **Save to claude-mem and file**
