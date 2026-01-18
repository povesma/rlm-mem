# Claude Code RLM

A minimal implementation of Recursive Language Models (RLM) using Claude Code as the scaffold. Implemented by [Brainqub3](https://brainqub3.com/).

## About

This repository provides a basic RLM setup that enables Claude to process documents and contexts that exceed typical context window limits. It implements the core RLM pattern where a root language model orchestrates sub-LLM calls over chunks of a large document.

**This is a basic implementation** of the RLM paper. For the full research, see:

> **Recursive Language Models**
> Alex L. Zhang, Tim Kraska, Omar Khattab
> MIT CSAIL
> [arXiv:2512.24601](https://arxiv.org/abs/2512.24601)

*Abstract: RLMs treat long prompts as part of an external environment and allow the LLM to programmatically examine, decompose, and recursively call itself over snippets of the prompt. RLMs can handle inputs up to two orders of magnitude beyond model context windows.*

## Architecture

This implementation maps to the RLM paper architecture as follows:

| RLM Concept | Implementation | Model |
|-------------|----------------|-------|
| Root LLM | Main Claude Code conversation | **Claude Opus 4.5** |
| Sub-LLM (`llm_query`) | `rlm-subcall` subagent | **Claude Haiku** |
| External Environment | Persistent Python REPL (`rlm_repl.py`) | Python 3 |

The root LLM (Opus 4.5) orchestrates the overall task, while delegating chunk-level analysis to the faster, lighter sub-LLM (Haiku). The Python REPL maintains state across invocations and provides utilities for chunking, searching, and managing the large context.

## Prerequisites

- **Claude Code account** - You need access to [Claude Code](https://claude.ai/claude-code), Anthropic's official CLI tool
- **Python 3** - For the persistent REPL environment

## Usage

1. **Clone this repository**
   ```bash
   git clone https://github.com/Brainqub3/claude_code_RLM.git
   cd claude_code_RLM
   ```

2. **Start Claude Code in the repository directory**
   ```bash
   claude
   ```

3. **Run the RLM skill**
   ```
   /rlm
   ```

4. **Follow the prompts** - The skill will ask for:
   - A path to your large context file
   - Your query/question about the content

The RLM workflow will then:
- Initialize the REPL with your context
- Chunk the document appropriately
- Delegate chunk analysis to the sub-LLM
- Synthesize results in the main conversation

## Working with Long Files

When using RLM to process large context files, it is recommended to save them in a dedicated `context/` folder within this project directory. This keeps your working files organized and separate from the RLM implementation code.

```bash
mkdir context
# Place your large documents here, e.g.:
# context/my_large_document.txt
# context/codebase_dump.py
```

## Security Warning

**This project is not intended for production use.**

If you plan to run Claude Code in `--dangerously-skip-permissions` mode:

1. **Ensure your setup is correct** - Verify all file paths and configurations before enabling this mode
2. **Run in an isolated folder** - Never run with skipped permissions in directories containing sensitive data, credentials, or system files
3. **Understand the risks** - This mode allows Claude to execute commands without confirmation prompts, which can lead to unintended file modifications or deletions

**Recommended**: Create a dedicated, isolated working directory specifically for RLM tasks when using dangerous mode:

```bash
# Example: Create an isolated workspace
mkdir ~/rlm-workspace
cd ~/rlm-workspace
git clone https://github.com/Brainqub3/claude_code_RLM.git
cd claude_code_RLM
```

## Repository Structure

```
.
├── CLAUDE.md                          # Project instructions for Claude Code
├── .claude/
│   ├── agents/
│   │   └── rlm-subcall.md            # Sub-LLM agent definition (Haiku)
│   └── skills/
│       └── rlm/
│           ├── SKILL.md              # RLM skill definition
│           └── scripts/
│               └── rlm_repl.py       # Persistent Python REPL
├── context/                           # Recommended location for large context files
└── README.md
```

## License

See [LICENSE](LICENSE) for details.
