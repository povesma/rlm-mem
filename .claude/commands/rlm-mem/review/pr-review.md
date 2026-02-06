# PR Review with RLM-Mem Hybrid

Comprehensive PR review using RLM impact analysis + claude-mem pattern compliance.

## Process

1. **Get PR changes** (git diff or gh pr diff)

2. **RLM impact analysis**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Find all files that depend on changed files
changed_files = ['{list_from_pr}']

impacted = set()
for cf in changed_files:
    # Find files that import/include this file
    # Analyze dependency graph
    pass

print(f"Directly changed: {len(changed_files)}")
print(f"Potentially impacted: {len(impacted)}")
PY
```

3. **Check pattern compliance** (claude-mem):
```
mcp__plugin_claude-mem_mcp-search__search(
  query="coding patterns architecture decisions standards",
  limit=10
)
```

4. **Generate review**:
   - Code quality
   - Pattern consistency (from RLM + mem)
   - Impact assessment (from RLM)
   - Security/performance concerns

5. **Save review to claude-mem**
