# Task Implementation with RLM-Mem Hybrid

Implement tasks with pattern discovery (RLM) + historical context (claude-mem).

## Process

1. **Load current task**
2. **Search similar implementations** (claude-mem)
3. **Discover patterns** (RLM - analyze existing code)
4. **Implement** following discovered patterns + past lessons
5. **Test** (TDD)
6. **Update task list** and **save to claude-mem**

See /rlm:develop:impl for detailed process, enhanced with claude-mem queries.
