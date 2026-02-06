# Comparison: RLM-Mem vs Claude Code RLM

This document compares `rlm-mem` with the original [claude_code_RLM](https://github.com/brainqub3/claude_code_RLM) project that inspired it.

## 🙏 Acknowledgment

**RLM-Mem is built on the foundation of [claude_code_RLM](https://github.com/brainqub3/claude_code_RLM)** by [Brainqub3](https://brainqub3.com/).

The original project demonstrated how to implement Recursive Language Models using Claude Code for processing large text documents. We extended this concept to work with large code repositories and integrated it with claude-mem for historical context.

**Thank you to the claude_code_RLM team for the excellent starting point!**

---

## 📊 Feature Comparison Matrix

| Component | claude_code_RLM | rlm-mem |
|-----------|-----------------|---------|
| **rlm_repl.py** | ✓ (431 lines)<br>Text-only processing | ✓ (833 lines)<br>+ Repository indexing<br>+ Multi-language (50+ types)<br>+ Binary file handling<br>+ Git integration<br>+ Complexity analysis |
| **Subagent** | ✓ (44 lines)<br>Text analysis | ✓ (79 lines)<br>+ Code-specific analysis<br>+ Symbol extraction<br>+ Pattern detection<br>+ File type awareness |
| **Commands** | ✓ (1 skill)<br>`/rlm` for text files | ✓ (12 commands)<br>+ discover (2)<br>+ plan (4)<br>+ develop (3)<br>+ review (1)<br>+ git (1) |
| **Documentation** | ✓ Basic README | ✓ README.md<br>+ TROUBLESHOOTING.md<br>+ IMPLEMENTATION_SUMMARY.md<br>+ Per-command docs |
| **Installation** | Work inside repo directory | Install to `~/.claude/`<br>(works in ANY project) |
| **Claude-mem** | ❌ Not integrated | ✅ Full integration |
| **Use Case** | Single large text file | Large code repositories (1000+ files) |
| **Workflow** | Ad-hoc text analysis | Complete dev lifecycle |

---

## 🎯 When to Use Each

### Use claude_code_RLM When:
- ✅ Processing large text documents (logs, transcripts, books)
- ✅ One-off analysis tasks
- ✅ Learning RLM concepts
- ✅ Simple text chunking and analysis
- ✅ You want the original, minimal implementation

### Use rlm-mem When:
- ✅ Working with large codebases (1000+ files)
- ✅ Need multi-language support
- ✅ Want historical context (claude-mem)
- ✅ Complete development workflow (plan → develop → review)
- ✅ Pattern discovery in code
- ✅ Architecture analysis
- ✅ Team collaboration with shared memory

---

## 🔄 Evolution Path

```
claude_code_RLM (Text-aware RLM)
        │
        ├─ Core concepts used:
        │  - Persistent REPL
        │  - Chunking strategy
        │  - Subagent pattern
        │
        ↓
rlm-mem (Code-aware RLM + Memory)
        │
        └─ Extensions added:
           - Repository indexing
           - Multi-language detection
           - Binary file handling
           - Git integration
           - Claude-mem integration
           - 12-command workflow
           - Pattern discovery
           - Complexity estimation
```

---

## 📝 Technical Differences

### rlm_repl.py Enhancements

**Original (`claude_code_RLM`):**
```python
# Commands: init, status, exec, reset, export-buffers
python3 rlm_repl.py init context.txt  # Single file
```

**Extended (`rlm-mem`):**
```python
# Commands: init, init-repo, status, exec, reset, export-buffers
python3 rlm_repl.py init-repo .  # Entire repository
```

**New features in rlm-mem:**
- `init-repo` command for repository indexing
- Language detection for 50+ file types
- Binary file detection and handling
- Git integration (respects `.gitignore`)
- Repository statistics and metrics
- File categorization (source/test/config/doc/binary)

### Subagent Enhancements

**Original (`claude_code_RLM`):**
- Generic text analysis
- Simple relevance extraction
- No code-specific features

**Enhanced (`rlm-mem`):**
- Code-aware analysis
- Symbol extraction (classes, functions, variables)
- Pattern detection (architectural patterns)
- Dependency tracking
- File type categorization
- Multiple language support

### Workflow Integration

**Original (`claude_code_RLM`):**
- Single `/rlm` skill
- Manual process
- No lifecycle support

**Extended (`rlm-mem`):**
- 12 specialized commands
- Full development lifecycle
- Planning phase (PRD, tech-design, tasks)
- Development phase (impl, build, test)
- Review phase (PR review)
- Git integration (smart commits)
- Historical learning via claude-mem

---

## 💡 Relationship to Original

**RLM-Mem is:**
- ✅ Built on claude_code_RLM's foundation
- ✅ An **extension** for code repositories (not a replacement for text analysis)
- ✅ A **superset** of functionality (includes everything from original + more)
- ✅ A **separate project** with different goals (code vs text)

**RLM-Mem is NOT:**
- ❌ A fork of claude_code_RLM (different use case)
- ❌ A replacement for claude_code_RLM (complements it)
- ❌ Unrelated to claude_code_RLM (builds on its concepts)

---

## 🤝 Contributing Back

Improvements made to core RLM concepts in `rlm-mem` that could benefit `claude_code_RLM`:
- Enhanced binary file detection
- Improved chunking strategies
- Better error handling
- Cross-platform compatibility (Windows + macOS + Linux)

We encourage sharing improvements between both projects!

---

## 📚 Further Reading

- **Original Project**: [claude_code_RLM on GitHub](https://github.com/brainqub3/claude_code_RLM)
- **RLM Paper**: [Recursive Language Models (arXiv)](https://arxiv.org/abs/2512.24601)
- **Claude Code**: [Official CLI](https://claude.ai/download)
- **Brainqub3**: [Project creator](https://brainqub3.com/)

---

## 🎓 Learning Path

**Recommended progression:**

1. **Start with claude_code_RLM** to learn RLM basics
   - Understand persistent REPL concept
   - Learn chunking strategies
   - Practice with text files

2. **Move to rlm-mem** for code projects
   - Apply RLM to code repositories
   - Use integrated workflow
   - Leverage claude-mem for context

Both projects have their place in the RLM ecosystem!

---

## ✨ Credits

- **Original RLM Implementation**: [claude_code_RLM](https://github.com/brainqub3/claude_code_RLM) by Brainqub3
- **RLM Research**: [MIT CSAIL](https://arxiv.org/abs/2512.24601) (Zhang, Kraska, Khattab)
- **Claude Code**: [Anthropic](https://anthropic.com)
- **Extensions**: Code-aware features, multi-language support, workflow integration

**RLM-Mem stands on the shoulders of giants. Thank you!** 🙏
