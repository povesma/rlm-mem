#!/usr/bin/env python3
"""Persistent mini-REPL for RLM-style workflows in Claude Code.

This script provides a *stateful* Python environment across invocations by
saving a pickle file to disk. It is intentionally small and dependency-free.

Typical flow:
  1) Initialise context:
       python rlm_repl.py init path/to/context.txt
  OR for code repositories:
       python rlm_repl.py init-repo /path/to/repo
  2) Execute code repeatedly (state persists):
       python rlm_repl.py exec -c 'print(len(content))'
       python rlm_repl.py exec <<'PYCODE'
       # you can write multi-line code
       hits = grep('TODO')
       print(hits[:3])
       PYCODE

The script injects these variables into the exec environment:
  - context: dict with keys {path, loaded_at, content}
  - content: string alias for context['content']
  - buffers: list[str] for storing intermediate text results
  - repo_index: dict with file index (when using init-repo)

It also injects helpers:
  - peek(start=0, end=1000) -> str
  - grep(pattern, max_matches=20, window=120, flags=0) -> list[dict]
  - chunk_indices(size=200000, overlap=0) -> list[(start,end)]
  - write_chunks(out_dir, size=200000, overlap=0, prefix='chunk') -> list[str]
  - add_buffer(text: str) -> None

Security note:
  This runs arbitrary Python via exec. Treat it like running code you wrote.
"""

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import pickle
import re
import subprocess
import sys
import textwrap
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set, Optional


DEFAULT_STATE_PATH = Path(".claude/rlm_state/state.pkl")
DEFAULT_MAX_OUTPUT_CHARS = 8000

# Language detection by file extension
LANGUAGE_MAP = {
    # Programming languages
    '.py': 'Python',
    '.pyx': 'Python',
    '.pyi': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.c': 'C',
    '.h': 'C/C++',
    '.hpp': 'C++',
    '.cs': 'C#',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.m': 'Objective-C',
    '.mm': 'Objective-C++',
    '.scala': 'Scala',
    '.r': 'R',
    '.R': 'R',
    '.lua': 'Lua',
    '.perl': 'Perl',
    '.pl': 'Perl',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.zsh': 'Zsh',
    '.fish': 'Fish',
    '.vim': 'VimScript',
    '.el': 'Emacs Lisp',
    '.clj': 'Clojure',
    '.cljs': 'ClojureScript',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hrl': 'Erlang',
    '.ml': 'OCaml',
    '.mli': 'OCaml',
    '.hs': 'Haskell',
    '.lhs': 'Haskell',
    '.dart': 'Dart',
    '.v': 'Verilog',
    '.vhd': 'VHDL',
    '.vhdl': 'VHDL',
    '.sql': 'SQL',
    '.asm': 'Assembly',
    '.s': 'Assembly',
    '.S': 'Assembly',

    # Web/markup
    '.html': 'HTML',
    '.htm': 'HTML',
    '.xml': 'XML',
    '.svg': 'SVG',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',

    # Documentation
    '.md': 'Markdown',
    '.markdown': 'Markdown',
    '.rst': 'ReStructuredText',
    '.txt': 'Text',
    '.tex': 'LaTeX',
    '.adoc': 'AsciiDoc',

    # Data/config
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'Config',
    '.conf': 'Config',
    '.xml': 'XML',
    '.csv': 'CSV',
    '.tsv': 'TSV',

    # Build/project files
    '.cmake': 'CMake',
    '.gradle': 'Gradle',
    '.make': 'Makefile',
    '.dockerfile': 'Dockerfile',

    # Binary/compiled (common ones)
    '.pyc': 'Python Bytecode',
    '.pyo': 'Python Bytecode',
    '.so': 'Shared Library',
    '.dll': 'Dynamic Library',
    '.dylib': 'Dynamic Library',
    '.a': 'Static Library',
    '.o': 'Object File',
    '.obj': 'Object File',
    '.exe': 'Executable',
    '.bin': 'Binary',
    '.class': 'Java Bytecode',
    '.jar': 'Java Archive',
    '.war': 'Web Archive',

    # Images
    '.png': 'PNG Image',
    '.jpg': 'JPEG Image',
    '.jpeg': 'JPEG Image',
    '.gif': 'GIF Image',
    '.bmp': 'BMP Image',
    '.ico': 'Icon',
    '.webp': 'WebP Image',

    # Archives
    '.zip': 'ZIP Archive',
    '.tar': 'TAR Archive',
    '.gz': 'Gzip Archive',
    '.bz2': 'Bzip2 Archive',
    '.xz': 'XZ Archive',
    '.7z': '7-Zip Archive',

    # Media
    '.mp3': 'Audio',
    '.wav': 'Audio',
    '.mp4': 'Video',
    '.avi': 'Video',
    '.mov': 'Video',
    '.pdf': 'PDF',
}

# Binary file extensions
BINARY_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.dll', '.dylib', '.a', '.o', '.obj',
    '.exe', '.bin', '.class', '.jar', '.war',
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.webp', '.svg',
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
    '.mp3', '.wav', '.ogg', '.flac', '.aac',
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.db', '.sqlite', '.sqlite3',
}


class RlmReplError(RuntimeError):
    pass


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.exists():
        raise RlmReplError(
            f"No state found at {state_path}. Run: python rlm_repl.py init <context_path>"
        )
    with state_path.open("rb") as f:
        state = pickle.load(f)
    if not isinstance(state, dict):
        raise RlmReplError(f"Corrupt state file: {state_path}")
    return state


def _save_state(state: Dict[str, Any], state_path: Path) -> None:
    _ensure_parent_dir(state_path)
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    with tmp_path.open("wb") as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    tmp_path.replace(state_path)


def _read_text_file(path: Path, max_bytes: int | None = None) -> str:
    if not path.exists():
        raise RlmReplError(f"Context file does not exist: {path}")
    data: bytes
    with path.open("rb") as f:
        data = f.read() if max_bytes is None else f.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to a lossy decode that will not crash.
        return data.decode("utf-8", errors="replace")


def _truncate(s: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + f"\n... [truncated to {max_chars} chars] ...\n"


def _is_pickleable(value: Any) -> bool:
    try:
        pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    except Exception:
        return False


def _filter_pickleable(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    kept: Dict[str, Any] = {}
    dropped: List[str] = []
    for k, v in d.items():
        if _is_pickleable(v):
            kept[k] = v
        else:
            dropped.append(k)
    return kept, dropped


# Repository-specific helpers

def _detect_language(file_path: Path) -> str:
    """Detect language/type from file extension."""
    # Handle special cases
    if file_path.name.lower() in {'makefile', 'gnumakefile', 'dockerfile'}:
        name_lower = file_path.name.lower()
        if 'makefile' in name_lower:
            return 'Makefile'
        if 'dockerfile' in name_lower:
            return 'Dockerfile'

    # Check extension
    ext = file_path.suffix.lower()
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]

    # Default to unknown
    return 'Unknown'


def _is_binary_file(file_path: Path) -> bool:
    """Check if a file is binary."""
    # Check by extension first
    ext = file_path.suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True

    # For files without recognized extensions, check content
    if not file_path.exists() or file_path.is_dir():
        return False

    try:
        # Read first 8KB and check for null bytes
        with file_path.open('rb') as f:
            chunk = f.read(8192)
            if not chunk:  # Empty file
                return False
            # If there are null bytes, it's likely binary
            return b'\x00' in chunk
    except (OSError, PermissionError):
        # If we can't read it, assume binary
        return True


def _discover_git_files(repo_root: Path) -> List[Path]:
    """Use git to discover all tracked and untracked files (respects .gitignore)."""
    try:
        # Get tracked files
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        tracked = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()

        # Get untracked files (excluding ignored)
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        untracked = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()

        all_files = tracked | untracked
        return [repo_root / f for f in sorted(all_files) if f]

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or not a git repo, fall back to walking directory
        return _discover_files_fallback(repo_root)


def _discover_files_fallback(repo_root: Path) -> List[Path]:
    """Fallback file discovery when git is not available."""
    files = []
    # Common directories to skip
    skip_dirs = {
        '.git', '.svn', '.hg', '__pycache__', 'node_modules',
        'venv', 'env', '.env', 'build', 'dist', '.idea',
        '.vscode', 'target', 'bin', 'obj'
    }

    for item in repo_root.rglob('*'):
        # Skip if any parent is in skip_dirs
        if any(part in skip_dirs for part in item.parts):
            continue
        if item.is_file():
            files.append(item)

    return sorted(files)


def _build_repo_index(repo_root: Path, max_file_size_mb: int = 10) -> Dict[str, Any]:
    """Build an index of all files in the repository."""
    repo_root = repo_root.resolve()
    files = _discover_git_files(repo_root)

    index = {
        'repo_root': str(repo_root),
        'indexed_at': time.time(),
        'total_files': 0,
        'total_size': 0,
        'files': {},
        'languages': {},
    }

    max_size_bytes = max_file_size_mb * 1024 * 1024

    for file_path in files:
        if not file_path.exists():
            continue

        try:
            rel_path = str(file_path.relative_to(repo_root))
            size = file_path.stat().st_size
            is_binary = _is_binary_file(file_path)
            language = _detect_language(file_path)

            # Store file metadata
            index['files'][rel_path] = {
                'size': size,
                'is_binary': is_binary,
                'lang': language,
                'too_large': size > max_size_bytes,
                'abs_path': str(file_path),
            }

            # Update statistics
            index['total_files'] += 1
            index['total_size'] += size

            # Track language counts
            if language not in index['languages']:
                index['languages'][language] = {'count': 0, 'size': 0}
            index['languages'][language]['count'] += 1
            index['languages'][language]['size'] += size

        except (OSError, PermissionError) as e:
            # Skip files we can't access
            continue

    return index


def _make_helpers(context_ref: Dict[str, Any], buffers_ref: List[str]):
    # These close over context_ref/buffers_ref so changes persist.
    def peek(start: int = 0, end: int = 1000) -> str:
        content = context_ref.get("content", "")
        return content[start:end]

    def grep(
        pattern: str,
        max_matches: int = 20,
        window: int = 120,
        flags: int = 0,
    ) -> List[Dict[str, Any]]:
        content = context_ref.get("content", "")
        out: List[Dict[str, Any]] = []
        for m in re.finditer(pattern, content, flags):
            start, end = m.span()
            snippet_start = max(0, start - window)
            snippet_end = min(len(content), end + window)
            out.append(
                {
                    "match": m.group(0),
                    "span": (start, end),
                    "snippet": content[snippet_start:snippet_end],
                }
            )
            if len(out) >= max_matches:
                break
        return out

    def chunk_indices(size: int = 200_000, overlap: int = 0) -> List[Tuple[int, int]]:
        if size <= 0:
            raise ValueError("size must be > 0")
        if overlap < 0:
            raise ValueError("overlap must be >= 0")
        if overlap >= size:
            raise ValueError("overlap must be < size")

        content = context_ref.get("content", "")
        n = len(content)
        spans: List[Tuple[int, int]] = []
        step = size - overlap
        for start in range(0, n, step):
            end = min(n, start + size)
            spans.append((start, end))
            if end >= n:
                break
        return spans

    def write_chunks(
        out_dir: str | os.PathLike,
        size: int = 200_000,
        overlap: int = 0,
        prefix: str = "chunk",
        encoding: str = "utf-8",
    ) -> List[str]:
        content = context_ref.get("content", "")
        spans = chunk_indices(size=size, overlap=overlap)
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        paths: List[str] = []
        for i, (s, e) in enumerate(spans):
            p = out_path / f"{prefix}_{i:04d}.txt"
            p.write_text(content[s:e], encoding=encoding)
            paths.append(str(p))
        return paths

    def add_buffer(text: str) -> None:
        buffers_ref.append(str(text))

    return {
        "peek": peek,
        "grep": grep,
        "chunk_indices": chunk_indices,
        "write_chunks": write_chunks,
        "add_buffer": add_buffer,
    }


def cmd_init(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    ctx_path = Path(args.context)

    content = _read_text_file(ctx_path, max_bytes=args.max_bytes)
    state: Dict[str, Any] = {
        "version": 1,
        "context": {
            "path": str(ctx_path),
            "loaded_at": time.time(),
            "content": content,
        },
        "buffers": [],
        "globals": {},
        "repo_index": None,
    }
    _save_state(state, state_path)

    print(f"Initialised RLM REPL state at: {state_path}")
    print(f"Loaded context: {ctx_path} ({len(content):,} chars)")
    return 0


def cmd_init_repo(args: argparse.Namespace) -> int:
    """Initialize state for a code repository."""
    state_path = Path(args.state)
    repo_path = Path(args.repo_path).resolve()

    if not repo_path.exists():
        raise RlmReplError(f"Repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise RlmReplError(f"Repository path is not a directory: {repo_path}")

    print(f"Indexing repository: {repo_path}")
    print("This may take a moment for large repositories...")

    # Build file index
    repo_index = _build_repo_index(repo_path, max_file_size_mb=args.max_file_size_mb)

    # Create state
    state: Dict[str, Any] = {
        "version": 1,
        "context": {
            "path": str(repo_path),
            "loaded_at": time.time(),
            "content": "",  # Empty for repo mode
        },
        "buffers": [],
        "globals": {},
        "repo_index": repo_index,
    }
    _save_state(state, state_path)

    # Print summary
    total_files = repo_index['total_files']
    total_size_mb = repo_index['total_size'] / (1024 * 1024)

    print(f"\n✓ RLM initialized for repository: {repo_path}")
    print(f"  - {total_files:,} files indexed")
    print(f"  - Size: {total_size_mb:.1f} MB")

    # Show top languages
    langs = sorted(
        repo_index['languages'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    if langs:
        print(f"  - Primary languages:")
        for lang, stats in langs[:5]:
            count = stats['count']
            pct = (count / total_files * 100) if total_files > 0 else 0
            print(f"    • {lang}: {count} files ({pct:.1f}%)")

    print(f"  - State saved to: {state_path}")
    print(f"\nNext steps:")
    print(f"  python3 {sys.argv[0]} status  # View index status")
    print(f"  python3 {sys.argv[0]} exec -c 'print(repo_index)' # Explore index")

    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state = _load_state(Path(args.state))
    ctx = state.get("context", {})
    content = ctx.get("content", "")
    buffers = state.get("buffers", [])
    g = state.get("globals", {})
    repo_index = state.get("repo_index")

    print("RLM REPL status")
    print(f"  State file: {args.state}")
    print(f"  Context path: {ctx.get('path')}")

    if repo_index:
        # Repository mode
        print(f"  Mode: Repository")
        print(f"  Total files: {repo_index['total_files']:,}")
        print(f"  Total size: {repo_index['total_size'] / (1024 * 1024):.1f} MB")
        print(f"  Languages: {len(repo_index['languages'])}")
        if args.show_vars:
            langs = sorted(
                repo_index['languages'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
            for lang, stats in langs[:10]:
                print(f"    - {lang}: {stats['count']} files")
    else:
        # Single file mode
        print(f"  Mode: Single file")
        print(f"  Context chars: {len(content):,}")

    print(f"  Buffers: {len(buffers)}")
    print(f"  Persisted vars: {len(g)}")
    if args.show_vars and g:
        print(f"  Variables:")
        for k in sorted(g.keys()):
            print(f"    - {k}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    if state_path.exists():
        state_path.unlink()
        print(f"Deleted state: {state_path}")
    else:
        print(f"No state to delete at: {state_path}")
    return 0


def cmd_export_buffers(args: argparse.Namespace) -> int:
    state = _load_state(Path(args.state))
    buffers = state.get("buffers", [])
    out_path = Path(args.out)
    _ensure_parent_dir(out_path)
    out_path.write_text("\n\n".join(str(b) for b in buffers), encoding="utf-8")
    print(f"Wrote {len(buffers)} buffers to: {out_path}")
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = _load_state(state_path)

    ctx = state.get("context")
    if not isinstance(ctx, dict):
        raise RlmReplError("State is missing a valid 'context'. Re-run init or init-repo.")

    buffers = state.setdefault("buffers", [])
    if not isinstance(buffers, list):
        buffers = []
        state["buffers"] = buffers

    persisted = state.setdefault("globals", {})
    if not isinstance(persisted, dict):
        persisted = {}
        state["globals"] = persisted

    repo_index = state.get("repo_index")

    code = args.code
    if code is None:
        code = sys.stdin.read()

    # Build execution environment.
    # Start from persisted variables, then inject context, buffers and helpers.
    env: Dict[str, Any] = dict(persisted)
    env["context"] = ctx
    env["content"] = ctx.get("content", "")
    env["buffers"] = buffers
    if repo_index:
        env["repo_index"] = repo_index

    helpers = _make_helpers(ctx, buffers)
    env.update(helpers)

    # Capture output.
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code, env, env)
    except Exception:
        traceback.print_exc(file=stderr_buf)

    # Pull back possibly mutated context/buffers.
    maybe_ctx = env.get("context")
    if isinstance(maybe_ctx, dict) and "content" in maybe_ctx:
        state["context"] = maybe_ctx
        ctx = maybe_ctx

    maybe_buffers = env.get("buffers")
    if isinstance(maybe_buffers, list):
        state["buffers"] = maybe_buffers
        buffers = maybe_buffers

    # Persist any new variables, excluding injected keys.
    injected_keys = {
        "__builtins__",
        "context",
        "content",
        "buffers",
        "repo_index",
        *helpers.keys(),
    }
    to_persist = {k: v for k, v in env.items() if k not in injected_keys}
    filtered, dropped = _filter_pickleable(to_persist)
    state["globals"] = filtered

    _save_state(state, state_path)

    out = stdout_buf.getvalue()
    err = stderr_buf.getvalue()

    if dropped and args.warn_unpickleable:
        msg = "Dropped unpickleable variables: " + ", ".join(dropped)
        err = (err + ("\n" if err else "") + msg + "\n")

    if out:
        sys.stdout.write(_truncate(out, args.max_output_chars))

    if err:
        sys.stderr.write(_truncate(err, args.max_output_chars))

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rlm_repl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Persistent mini-REPL for RLM-style workflows.

            Examples:
              python rlm_repl.py init context.txt
              python rlm_repl.py status
              python rlm_repl.py exec -c "print(len(content))"
              python rlm_repl.py exec <<'PY'
              print(peek(0, 2000))
              PY
            """
        ),
    )
    p.add_argument(
        "--state",
        default=str(DEFAULT_STATE_PATH),
        help=f"Path to state pickle (default: {DEFAULT_STATE_PATH})",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialise state from a context file")
    p_init.add_argument("context", help="Path to the context file")
    p_init.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Optional cap on bytes read from the context file",
    )
    p_init.set_defaults(func=cmd_init)

    p_init_repo = sub.add_parser(
        "init-repo",
        help="Initialise state from a code repository (indexes all files)"
    )
    p_init_repo.add_argument(
        "repo_path",
        help="Path to the repository root directory"
    )
    p_init_repo.add_argument(
        "--max-file-size-mb",
        type=int,
        default=10,
        help="Mark files larger than this as 'too_large' (default: 10 MB)",
    )
    p_init_repo.set_defaults(func=cmd_init_repo)

    p_status = sub.add_parser("status", help="Show current state summary")
    p_status.add_argument(
        "--show-vars", action="store_true", help="List persisted variable names"
    )
    p_status.set_defaults(func=cmd_status)

    p_reset = sub.add_parser("reset", help="Delete the current state file")
    p_reset.set_defaults(func=cmd_reset)

    p_export = sub.add_parser(
        "export-buffers", help="Export buffers list to a text file"
    )
    p_export.add_argument("out", help="Output file path")
    p_export.set_defaults(func=cmd_export_buffers)

    p_exec = sub.add_parser("exec", help="Execute Python code with persisted state")
    p_exec.add_argument(
        "-c",
        "--code",
        default=None,
        help="Inline code string. If omitted, reads code from stdin.",
    )
    p_exec.add_argument(
        "--max-output-chars",
        type=int,
        default=DEFAULT_MAX_OUTPUT_CHARS,
        help=f"Truncate stdout/stderr to this many characters (default: {DEFAULT_MAX_OUTPUT_CHARS})",
    )
    p_exec.add_argument(
        "--warn-unpickleable",
        action="store_true",
        help="Warn on stderr when variables could not be persisted",
    )
    p_exec.set_defaults(func=cmd_exec)

    return p


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except RlmReplError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
