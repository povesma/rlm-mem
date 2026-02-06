# Build Project

Build and test the project using RLM-aware error analysis.

## Process

### Step 1: Run Build
```bash
make build
```

### Step 2: Analyze Build Errors (if any)

**Use RLM to find related code**:
```bash
python3 ~/.claude/rlm_scripts/rlm_repl.py exec <<'PY'
# Parse error messages and find related files
error_files = ['{file_from_error}']  # Extract from build output

related = []
for ef in error_files:
    if ef in repo_index['files']:
        related.append(ef)
        # Find dependencies
        # ... (analyze imports, includes, etc.)

print('\n'.join(related[:20]))
PY
```

### Step 3: Fix Errors

- Use RLM to understand error context
- Fix following discovered patterns
- Iterate until build succeeds

### Step 4: Run Tests
```bash
make test
```

### Step 5: Analyze Test Failures (if any)

- Use RLM to find related test and source files
- Fix following TDD patterns
- Iterate until tests pass

## Success Criteria

- ✅ Build completes without errors
- ✅ All tests pass
- ✅ No warnings (if project enforces)
