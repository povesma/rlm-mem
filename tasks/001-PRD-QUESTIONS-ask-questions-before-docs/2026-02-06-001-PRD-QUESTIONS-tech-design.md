# 001-PRD-QUESTIONS: Mandatory Question Resolution - Technical Design

**Status**: Implemented
**PRD**: [001-PRD-QUESTIONS-prd.md](2026-02-06-001-PRD-QUESTIONS-prd.md)
**Created**: 2026-02-06

---

## Overview

Modify three planning commands (prd.md, tech-design.md, tasks.md) to include a
mandatory clarification step using AskUserQuestion tool BEFORE writing the
final document. Questions incorporate insights from RLM analysis and claude-mem
history. Users can skip if all is clear, but must explicitly confirm.

## Current Architecture (RLM Analysis)

**Discovered Patterns**:

Commands follow consistent structure:
- Markdown files in `.claude/commands/rlm-mem/plan/`
- Use numbered "Process" sections (Step 1, Step 2, etc.)
- Mix Bash commands (RLM REPL) with tool calls (claude-mem MCP)
- Include document templates in markdown code blocks
- End with "Final Instructions" checklist

**Relevant Files**:
- `.claude/commands/rlm-mem/plan/prd.md` (361 lines)
  - Current flow: Gather → Search mem → RLM → Synthesize → Save
  - Has "Open Questions" section in template (line 202-206)
- `.claude/commands/rlm-mem/plan/tech-design.md` (271 lines)
  - Current flow: Load context → RLM discovery → Learn history → Synthesize →
Save
  - Has "Open Questions" section in template (line 226-228)
- `.claude/commands/rlm-mem/plan/tasks.md` (1237 lines, simpler structure)
  - May have unclear requirements from upstream

**Integration Points**:
- AskUserQuestion tool already used in commands (confirmed by user)
- Commands execute in Claude Code environment with access to all tools
- Changes to .md files take effect immediately (no restart needed)

## Proposed Design

### Architecture

Add mandatory clarification step as **new numbered step** in each command,
positioned **right before document synthesis** (before writing MD file).

**Flow for PRD command**:
```
Step 1: Gather requirements
Step 2: Search claude-mem
Step 3: RLM analysis
Step 4: MANDATORY CLARIFICATION ← NEW
Step 5: Synthesize PRD (was Step 4)
Step 6: Save to claude-mem (was Step 5)
Step 7: Save to file (was Step 6)
Step 8: Report completion (was Step 7)
```

### Components

**Modified Components**:

1. **`.claude/commands/rlm-mem/plan/prd.md`**
   - **Changes**:
     - Insert new Step 4 "Resolve All Uncertainties (MANDATORY)"
     - Update subsequent step numbers
     - Add clarification logic with AskUserQuestion examples
     - Update "Open Questions" section handling in template
     - Add note in Final Instructions
   - **Rationale**: PRD is foundation, must be most rigorous
   - **Risk**: Low - additive change, doesn't break existing flow

2. **`.claude/commands/rlm-mem/plan/tech-design.md`**
   - **Changes**:
     - Insert new step after "Step 4: Learn from History"
     - Becomes "Step 5: Resolve Architecture Questions (MANDATORY)"
     - Focus on architecture trade-offs and approach decisions
     - Update template to handle answered questions
   - **Rationale**: Design decisions must be explicit choices, not assumptions
   - **Risk**: Low - similar structure to PRD changes

3. **`.claude/commands/rlm-mem/plan/tasks.md`**
   - **Changes**:
     - **Complete rewrite** to match `/coding:plan:tasks` output format
     - Add structured output: user stories (`1.0`), numbered subtasks (`1.1`,
       `1.2`), checkboxes, progress tracking (`[4/0]`)
     - Add Relevant Files section, Notes, TDD Planning Guidelines
     - Add two-phase generation (parent tasks first → user confirms "Go" →
       subtasks)
     - Insert Step 4: Resolve Scope Uncertainties (MANDATORY) with
       AskUserQuestion
     - Add KISS principle and junior developer target audience
   - **Rationale**: Original was a 5-line skeleton with no output format;
     `/coding` version is proven and complete
   - **Risk**: Medium - complete rewrite, but based on working `/coding` format

### Clarification Step Structure

Each command's new step follows this pattern:

```markdown
### Step X: Resolve All Uncertainties (MANDATORY)

**🚨 BEFORE writing the document, you MUST resolve ALL ambiguities.**

**Execution**:
1. Review findings from previous steps
2. Identify any unclear requirements, decisions, or assumptions
3. Use AskUserQuestion tool to clarify (see examples below)
4. User can explicitly say "All clear, proceed" to skip
5. DO NOT PROCEED until answered or user confirms to skip

**Question Categories** (for {PRD/tech-design/tasks}):

{Command-specific question types}

**Example AskUserQuestion call**:
```
AskUserQuestion(
  questions=[
    {
      "question": "...",
      "header": "...",
      "multiSelect": false,
      "options": [
        {"label": "...", "description": "..."},
        {"label": "All clear, proceed", "description": "No clarification needed,
I'm ready for you to create the document"}
      ]
    }
  ]
)
```

**⚠️ If user selects "All clear, proceed", skip to next step.**
**Otherwise, incorporate answers into document synthesis.**
```

### Question Types by Command

**PRD Command** (Step 4):
- Product scope: Target users, use cases, success metrics
- Feature boundaries: What's in vs out of scope
- Architecture approach: Options discovered via RLM, user chooses
- Integration points: How to connect with existing systems
- Priorities: Must-have vs nice-to-have

**Tech-Design Command** (Step 5):
- Architecture trade-offs: Multiple approaches with pros/cons
- Implementation approach: Following existing pattern vs new pattern
- Technology choices: Use existing lib vs new dependency
- Risk mitigation: How to handle identified risks
- Performance/security requirements: Specific targets

**Tasks Command** (Step after reading PRD/design):
- Scope clarity: Is scope from PRD/design clear enough to break down?
- Complexity unknowns: "Should we use existing X or build new?"
- Dependencies: Are all dependencies identified and resolved?
- Estimation confidence: Can we reasonably estimate these tasks?

### Open Questions Section Handling

**User decision**: Do NOT have a separate section for answered questions.
Incorporate all answered questions into the relevant document sections.

**Implementation**:
- Remove "Open Questions" section from PRD and tech-design templates
- Only keep if genuinely unresolvable items exist (e.g., "Performance baseline
  TBD after load testing", or questions the user explicitly chose not to answer)
- Answered questions are woven into Context, Requirements, Architecture, etc.

### Error Handling

**If user provides unclear answers**:
- Command notes the ambiguity in the document
- Warns user that this may require iteration
- Still creates document (user chose to proceed)

**If user abandons AskUserQuestion**:
- Command halts with clear message
- Explains clarification is required
- Suggests restarting with clearer requirements

### Testing Strategy

**Manual testing**:
1. Run each modified command with deliberately vague requirements
2. Verify AskUserQuestion is invoked
3. Test "All clear, proceed" option skips correctly
4. Verify answered questions are incorporated into document body
5. Check Open Questions section is empty or minimal

## Trade-offs

**Considered Approaches**:

1. **Option A: Detect ambiguity automatically**
   - Pros: Only asks when needed, more efficient
   - Cons: AI might miss questions, inconsistent experience
   - Rejected: Too unreliable, mandatory is safer

2. **Option B: Always ask (no skip option)**
   - Pros: Most consistent, forces thoroughness
   - Cons: Annoying for experienced users with clear requirements
   - Rejected: User feedback preference for skip option

3. **Option C: Mandatory with skip option (SELECTED)**
   - Pros: Balance of rigor and flexibility, user in control
   - Cons: Slightly more complex logic
   - Why: Respects user expertise while ensuring opportunity to clarify

## Implementation Constraints

**From Existing Architecture** (RLM):
- Must maintain markdown format (commands are .md files)
- Cannot change tool availability (AskUserQuestion must exist)
- Step numbering must be sequential and clear
- Examples in commands must be valid syntax

**From Past Experience** (Claude-Mem):
- No past similar work - this is first iteration
- Lesson: Keep changes localized to minimize risk

## Files to Create/Modify

**Modify**:
- `.claude/commands/rlm-mem/plan/prd.md:19-361`
  - Insert new Step 4 after line ~109 (after RLM analysis)
  - Update all subsequent step numbers
  - Update template Open Questions section (line 202-206)
  - Update Final Instructions (line 352-360)

- `.claude/commands/rlm-mem/plan/tech-design.md:1-271`
  - Insert new Step 5 after line ~93 (after learning from history)
  - Update subsequent step numbers
  - Update template Open Questions section (line 226-228)
  - Update Final Instructions (line 262-270)

- `.claude/commands/rlm-mem/plan/tasks.md:1-1237`
  - Insert clarification step after reading PRD/design context
  - Simpler structure, fewer question types
  - Focus on scope/complexity clarification

**No new files needed** - all changes are edits to existing commands.

## Dependencies

**External**: None

**Internal**:
- AskUserQuestion tool (confirmed available)
- RLM REPL (already used in commands)
- Claude-mem MCP tools (already used in commands)

## Security Considerations

No security implications - changes are to command documentation/workflow only.

## Performance Considerations

**Impact**: Adds ~30-60 seconds per planning command (user question time)
**Mitigation**: Skip option for experienced users with clear requirements
**Trade-off**: Acceptable overhead for improved document quality

## Rollback Plan

If implementation causes issues:
1. Revert modified command files to git HEAD
2. Changes take effect immediately (no restart)
3. Old behavior restored instantly

## Implementation Sequence

1. **Start with prd.md** (most complex, most important)
2. Test thoroughly with sample feature
3. **Then tech-design.md** (similar structure)
4. **Finally tasks.md** (simplest, learns from first two)

## References

### Code (RLM):
- `.claude/commands/rlm-mem/plan/prd.md` - Primary template to follow
- `.claude/commands/rlm-mem/plan/tech-design.md` - Similar structure
- `.claude/commands/rlm-mem/plan/tasks.md` - Simpler variant

---

**Next Steps**:
1. Review and approve this design
2. Run `/rlm-mem:plan:tasks` to break down into implementation tasks
