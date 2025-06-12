"""File utility functions."""

import os
import mimetypes
from pathlib import Path
from typing import List, Optional


def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file."""
    try:
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Check by reading a small chunk
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return False  # Binary file
            
        # Try to decode as UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
        
    except (UnicodeDecodeError, PermissionError, OSError):
        return False


def get_file_language(file_path: Path) -> Optional[str]:
    """Detect programming language from file extension."""
    suffix = file_path.suffix.lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.txt': 'text',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini'
    }
    return language_map.get(suffix)


def find_files(
    root_path: Path,
    patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> List[Path]:
    """Find files matching patterns, excluding specified patterns."""
    import fnmatch
    
    files = []
    exclude_patterns = exclude_patterns or [
        '.git/*', '__pycache__/*', '*.pyc', 'node_modules/*',
        '.venv/*', 'venv/*', 'dist/*', 'build/*', '.DS_Store'
    ]
    
    for file_path in root_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        relative_path = file_path.relative_to(root_path)
        
        # Check exclude patterns
        excluded = False
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(str(relative_path), pattern):
                excluded = True
                break
        
        if excluded:
            continue
        
        # Check include patterns
        if patterns:
            included = False
            for pattern in patterns:
                if fnmatch.fnmatch(str(relative_path), pattern):
                    included = True
                    break
            if not included:
                continue
        
        files.append(file_path)
    
    return files


def safe_read_file(file_path: Path, max_size: int = 1024 * 1024) -> str:
    """Safely read a file with size limits."""
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")
    
    if file_path.stat().st_size > max_size:
        raise ValueError(f"File {file_path} is too large (>{max_size} bytes)")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def get_file_stats(file_path: Path) -> dict:
    """Get file statistics."""
    if not file_path.exists():
        return {}
    
    stat = file_path.stat()
    content = ""
    lines = 0
    
    if is_text_file(file_path):
        try:
            content = safe_read_file(file_path)
            lines = len(content.splitlines())
        except Exception:
            pass
    
    return {
        'size': stat.st_size,
        'lines': lines,
        'language': get_file_language(file_path),
        'is_text': is_text_file(file_path),
        'modified': stat.st_mtime
    }