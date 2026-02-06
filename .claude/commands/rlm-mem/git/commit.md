# Smart Git Commit with RLM-Mem

Create commit with RLM impact analysis + claude-mem contextual message.

## Process

1. **Analyze changes** (git diff, git status)

2. **RLM impact analysis**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Analyze changed files
changed = ['{files_from_git}']

impact = {
    'modules_affected': [],
    'apis_changed': [],
    'breaking_changes': [],
}

for file in changed:
    # Analyze what changed
    pass

import json
print(json.dumps(impact, indent=2))
PY
```

3. **Search similar commits** (claude-mem):
```
mcp__plugin_claude-mem_mcp-search__search(
  query="commit {feature_area} similar changes",
  limit=5
)
```

4. **Generate commit message**:
```
{type}({scope}): {subject}

{body explaining why, impact from RLM}

{footer with references}
```

5. **Execute commit** (following git safety protocol)

6. **Save commit context to claude-mem**
