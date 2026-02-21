# 001-PRD-QUESTIONS - Task List

## Relevant Files
- [.claude/commands/rlm-mem/plan/prd.md](.claude/commands/rlm-mem/plan/prd.md)
  :: PRD command - add mandatory clarification step
- [.claude/commands/rlm-mem/plan/tech-design.md](.claude/commands/rlm-mem/plan/tech-design.md)
  :: Tech-design command - add mandatory clarification step
- [.claude/commands/rlm-mem/plan/tasks.md](.claude/commands/rlm-mem/plan/tasks.md)
  :: Tasks command - complete rewrite to match coding format

## Tasks
- [x] 1.0 **User Story:** As a developer, I want the tasks command output
  format to match `/coding:plan:tasks` so that task lists are structured and
  actionable [6/6]
  - [x] 1.1 Rewrite tasks.md with structured output format (user stories,
    numbered subtasks, checkboxes, progress tracking)
  - [x] 1.2 Add Relevant Files section template
  - [x] 1.3 Add TDD Planning Guidelines section
  - [x] 1.4 Add two-phase generation (parent tasks → "Go" → subtasks)
  - [x] 1.5 Add Step 4: Resolve Scope Uncertainties (MANDATORY) with
    AskUserQuestion
  - [x] 1.6 Add KISS principle and junior developer target audience
- [x] 2.0 **User Story:** As a developer creating a PRD, I want Claude to ask
  me clarifying questions before writing the document so that the PRD is
  complete from the start [4/4]
  - [x] 2.1 Insert Step 4: Ask Clarifying Questions (MANDATORY) with
    AskUserQuestion examples (product + RLM-informed technical questions)
  - [x] 2.2 Add "All clear, proceed" skip option
  - [x] 2.3 Remove "Open Questions" section from PRD template
  - [x] 2.4 Update Final Instructions and renumber steps (5-8)
- [x] 3.0 **User Story:** As a developer creating a tech design, I want Claude
  to ask me about architecture trade-offs before writing the document so that
  the design reflects actual decisions [4/4]
  - [x] 3.1 Insert Step 5: Ask Technical Clarifying Questions (MANDATORY) with
    AskUserQuestion examples (architecture + RLM-informed pattern questions)
  - [x] 3.2 Add "All clear, proceed" skip option
  - [x] 3.3 Remove "Open Questions" section from tech-design template
  - [x] 3.4 Update Final Instructions and renumber steps (6-8)
