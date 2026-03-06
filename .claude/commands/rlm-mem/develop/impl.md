# Task Implementation with RLM-Mem Hybrid

Implement tasks with pattern discovery (RLM) + historical context (claude-mem).

## Process

1. **Load current task**
2. **Search similar implementations** (claude-mem)
3. **Discover patterns** (RLM - analyze existing code)
4. **Implement** following discovered patterns + past lessons
5. **Test** (TDD)
6. **Update task list** and **save to claude-mem**

## Task Completion Rules

- **`[X]` (done)**: ONLY when tested AND passing, OR explicitly confirmed by user
- **`[~]` (coded, pending testing)**: implementation is written but not yet verified
- **`[ ]` (not started)**: no work done
- Tasks that are tests themselves (story 8-style verification) may be marked `[X]` once
  the test is run and the result is known, even if the result reveals bugs to fix
- Marking `[X]` without testing is **never acceptable** — be pessimistic, assume it
  doesn't work until proven otherwise

See /rlm:develop:impl for detailed process, enhanced with claude-mem queries.
