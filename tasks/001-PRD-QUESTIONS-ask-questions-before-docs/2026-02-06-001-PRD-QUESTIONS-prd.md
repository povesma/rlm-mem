# 001-PRD-QUESTIONS: Mandatory Question Resolution Before Document Creation - PRD

**Status**: Implemented
**Created**: 2026-02-06
**Task ID**: 001-PRD-QUESTIONS
**Author**: Claude (via rlm-mem analysis)

---

## Context

Currently, RLM-Mem planning commands (PRD, tech-design, tasks) may create
documents with "Open Questions" sections containing unresolved uncertainties.
This leads to incomplete planning, requiring back-and-forth iterations and
potentially building features on unclear requirements.

### Current State (from RLM analysis)

Existing command files:
- `.claude/commands/rlm-mem/plan/prd.md`: Creates PRD with "Open Questions"
section
- `.claude/commands/rlm-mem/plan/tech-design.md`: Creates design with "Open
Questions" section
- `.claude/commands/rlm-mem/plan/tasks.md`: Creates task list, may have unclear
requirements

These commands analyze codebase (RLM) and historical context (claude-mem) but
don't mandate resolving ambiguities before document creation.

## Problem Statement

**Who**: Claude Code users creating planning documents via rlm-mem commands
**What**: Planning documents get created with unresolved questions, leading to
ambiguous requirements
**Why**: Wastes time in iterations, risks building wrong features, creates
confusion
**When**: During PRD creation, tech design, and task breakdown phases

## Goals

### Primary Goal

Enforce mandatory clarification step BEFORE creating planning documents, ensuring
all documents are complete and actionable from the start.

### Secondary Goals

- Reduce planning iterations and back-and-forth
- Improve document quality by eliminating ambiguity
- Leverage AskUserQuestion tool for structured clarification
- Handle "Open Questions" sections: keep only for genuinely unresolvable items;
  incorporate answered questions into document body (no separate section)
- Align tasks.md output format with `/coding:plan:tasks` (user stories,
  numbered subtasks, TDD guidelines, two-phase generation)

## User Stories

### Epic

As a Claude Code user, I want planning commands to ask me clarifying questions
before creating documents, so that I get complete, actionable plans without
ambiguity.

### User Stories

1. **As a** developer creating a PRD
   **I want** Claude to ask me clarifying questions about product scope and
architecture options
   **So that** the PRD is complete and unambiguous from the start

   **Acceptance Criteria**:
   - [ ] PRD command uses AskUserQuestion tool when encountering unclear
requirements
   - [ ] All product scope, target users, and success metrics are clarified
before writing
   - [ ] Architecture options discovered via RLM are presented for user decision
   - [ ] Final PRD has no "Open Questions" section with unresolved items

2. **As a** developer creating a technical design
   **I want** Claude to ask me about architecture trade-offs and implementation
approaches
   **So that** the design reflects actual decisions, not assumptions

   **Acceptance Criteria**:
   - [ ] Tech-design command uses AskUserQuestion for architecture choices
   - [ ] Trade-offs between multiple approaches are presented with context
   - [ ] User selects preferred approach before design is written
   - [ ] Final design has no unresolved architectural questions

3. **As a** developer breaking down tasks
   **I want** Claude to clarify scope and complexity uncertainties before
creating task list
   **So that** tasks are well-defined and estimatable

   **Acceptance Criteria**:
   - [ ] Tasks command asks about scope boundaries if unclear from PRD/design
   - [ ] Complexity questions are resolved (e.g., "use existing X or build new?")
   - [ ] Dependencies and blockers are identified and clarified
   - [ ] Final task list has actionable, clear task definitions

## Requirements

### Functional Requirements

1. **FR-1**: Mandatory clarification step in PRD command
   - **Priority**: High
   - **Rationale**: PRD is foundation for all other planning
   - **Dependencies**: AskUserQuestion tool availability

2. **FR-2**: Mandatory clarification step in tech-design command
   - **Priority**: High
   - **Rationale**: Design decisions must be explicit, not assumed
   - **Dependencies**: RLM pattern discovery working

3. **FR-3**: Mandatory clarification step in tasks command
   - **Priority**: High
   - **Rationale**: Tasks must be unambiguous for implementation
   - **Dependencies**: PRD and design already clarified

4. **FR-4**: Use AskUserQuestion tool for structured questions
   - **Priority**: High
   - **Rationale**: Better UX than conversational, forces clear options
   - **Dependencies**: Tool must support multiple questions, options, descriptions

5. **FR-5**: Handle "Open Questions" sections properly
   - **Priority**: Medium
   - **Rationale**: Answered questions belong in the document body, not a
     separate section. Only genuinely unresolvable items (e.g., "performance
     TBD after load testing") may remain in Open Questions.
   - **Dependencies**: Clarification process resolves most questions

6. **FR-6**: Align tasks.md output format with `/coding:plan:tasks`
   - **Priority**: High
   - **Rationale**: rlm-mem tasks format was a skeleton; coding format has
     proven structure (user stories, numbered subtasks, TDD guidelines,
     two-phase generation with user confirmation)
   - **Dependencies**: None

### Non-Functional Requirements

1. **NFR-1**: User experience - Questions should be clear and actionable
2. **NFR-2**: Efficiency - Don't over-question; ask only what's genuinely unclear
3. **NFR-3**: Context - Questions should leverage RLM findings (show discovered
patterns)
4. **NFR-4**: Guidance - Question options should include trade-off descriptions

### Technical Constraints

Based on RLM analysis of existing architecture:
- Must use AskUserQuestion tool (not conversational questions)
- Commands are markdown files in `.claude/commands/rlm-mem/plan/`
- Changes to command files take effect immediately (no rebuild needed)
- Must maintain compatibility with existing RLM REPL and claude-mem integration

## Clarified Decisions (from user discussion)

- **Scope**: All planning commands (PRD, tech-design, tasks)
- **Question format**: ALWAYS use AskUserQuestion tool (not conversational)
- **Execution trigger**: Mandatory with "All clear, proceed" skip option
- **Open Questions handling**: Keep section only for genuinely unresolvable
  items; answered questions get incorporated into document body
- **Clarification placement**: Right before writing the MD file (after all
  RLM/claude-mem analysis completes)
- **Additional fix**: tasks.md output format must match `/coding:plan:tasks`

## Out of Scope

What we explicitly won't do in this iteration:
- Applying to non-planning commands (develop, review, git commands unchanged)
- Changing document structure beyond Open Questions handling

## Success Metrics

**How we'll measure success**:
1. **Completion rate**: 100% of PRD/tech-design/tasks docs created with no
unresolved "Open Questions"
2. **Iteration reduction**: <10% of documents require revision for missing
clarifications
3. **User satisfaction**: Qualitative feedback that planning is clearer

## References

### From Codebase (RLM)

Relevant files to modify:
- `.claude/commands/rlm-mem/plan/prd.md` - Add clarification step
- `.claude/commands/rlm-mem/plan/tech-design.md` - Add clarification step
- `.claude/commands/rlm-mem/plan/tasks.md` - Add clarification step

Existing pattern: Commands use structured markdown with numbered steps in
"Process" sections

Integration points: Commands already use AskUserQuestion tool (seen in other
commands)

### From History (Claude-Mem)

This is first iteration - no past similar work

---

**Next Steps**:
1. Review and approve this PRD
2. Run `/rlm-mem:plan:tech-design` to create technical design
3. Run `/rlm-mem:plan:tasks` to break down into implementation tasks
