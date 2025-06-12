"""Git repository implementation."""

from typing import List, Optional, Dict, Any
import git
from pathlib import Path
import os
import mimetypes
from datetime import datetime

from ...core.interfaces.repository import (
    IRepository, FileInfo, FileStatus, CommitInfo, CommitError
)


class GitRepository(IRepository):
    """Git repository implementation."""
    
    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = None
    
    @property
    def root_path(self) -> str:
        return str(self.repo_path)
    
    @property
    def is_git_repo(self) -> bool:
        return self.repo is not None
    
    def get_files(self, patterns: Optional[List[str]] = None) -> List[FileInfo]:
        """Get files in the repository."""
        files = []
        
        if self.is_git_repo:
            # Get tracked files
            try:
                tracked_files = self.repo.git.ls_files().splitlines()
                for file_path in tracked_files:
                    full_path = self.repo_path / file_path
                    if full_path.exists() and full_path.is_file():
                        files.append(self._create_file_info(file_path, full_path))
            except Exception:
                # Fallback to filesystem scan
                files = self._scan_filesystem()
        else:
            # Fallback to filesystem scan
            files = self._scan_filesystem()
        
        # Apply patterns if provided
        if patterns:
            import fnmatch
            filtered_files = []
            for file_info in files:
                for pattern in patterns:
                    if fnmatch.fnmatch(file_info.path, pattern):
                        filtered_files.append(file_info)
                        break
            files = filtered_files
        
        return files
    
    def get_file_content(self, file_path: str) -> str:
        """Get the content of a specific file."""
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(full_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def get_context(self, file_paths: List[str]) -> Dict[str, Any]:
        """Get repository context for the given files."""
        context = {
            "root_path": self.root_path,
            "is_git_repo": self.is_git_repo,
            "files": file_paths,
            "file_contents": {},
            "languages": set(),
            "total_lines": 0
        }
        
        # Add current branch if git repo
        if self.is_git_repo:
            try:
                context["current_branch"] = self.repo.active_branch.name
            except Exception:
                context["current_branch"] = "unknown"
        
        # Get file contents and analyze
        for file_path in file_paths:
            try:
                content = self.get_file_content(file_path)
                context["file_contents"][file_path] = content
                context["total_lines"] += len(content.splitlines())
                
                # Detect language
                language = self._detect_language(file_path)
                if language:
                    context["languages"].add(language)
                    
            except Exception as e:
                context["file_contents"][file_path] = f"Error reading file: {str(e)}"
        
        context["languages"] = list(context["languages"])
        return context
    
    def get_status(self) -> List[FileInfo]:
        """Get the status of all files in the repository."""
        if not self.is_git_repo:
            return self.get_files()
        
        files = []
        
        try:
            # Get status from git
            status = self.repo.git.status('--porcelain').splitlines()
            
            for line in status:
                if len(line) < 3:
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                
                # Map git status codes to our enum
                if status_code == '??':
                    file_status = FileStatus.UNTRACKED
                elif status_code[0] == 'M' or status_code[1] == 'M':
                    file_status = FileStatus.MODIFIED
                elif status_code[0] == 'A':
                    file_status = FileStatus.ADDED
                elif status_code[0] == 'D':
                    file_status = FileStatus.DELETED
                elif status_code[0] == 'R':
                    file_status = FileStatus.RENAMED
                else:
                    file_status = FileStatus.MODIFIED
                
                full_path = self.repo_path / file_path
                if full_path.exists():
                    file_info = self._create_file_info(file_path, full_path)
                    file_info.status = file_status
                    files.append(file_info)
                    
        except Exception:
            # Fallback to regular file listing
            files = self.get_files()
        
        return files
    
    def commit_changes(self, changes: List[Any], message: str) -> str:
        """Commit changes to the repository."""
        if not self.is_git_repo:
            raise CommitError("Not a git repository")
        
        try:
            # Stage all changes
            self.repo.git.add('--all')
            
            # Commit
            commit = self.repo.index.commit(message)
            return commit.hexsha[:8]  # Return short hash
            
        except Exception as e:
            raise CommitError(f"Failed to commit changes: {str(e)}")
    
    def get_commit_history(self, limit: int = 10) -> List[CommitInfo]:
        """Get recent commit history."""
        if not self.is_git_repo:
            return []
        
        commits = []
        try:
            for commit in self.repo.iter_commits(max_count=limit):
                commits.append(CommitInfo(
                    hash=commit.hexsha[:8],
                    message=commit.message.strip(),
                    author=str(commit.author),
                    timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                    files_changed=list(commit.stats.files.keys())
                ))
        except Exception:
            pass
        
        return commits
    
    def get_diff(self, file_path: str, commit_hash: Optional[str] = None) -> str:
        """Get diff for a file."""
        if not self.is_git_repo:
            return ""
        
        try:
            if commit_hash:
                return self.repo.git.diff(commit_hash, file_path)
            else:
                return self.repo.git.diff('HEAD', file_path)
        except Exception:
            return ""
    
    def is_clean(self) -> bool:
        """Check if the repository has no uncommitted changes."""
        if not self.is_git_repo:
            return True
        
        try:
            return not self.repo.is_dirty()
        except Exception:
            return False
    
    def _scan_filesystem(self) -> List[FileInfo]:
        """Scan filesystem for files when git is not available."""
        files = []
        
        # Common patterns to ignore
        ignore_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', 'dist', 'build', '.DS_Store'
        }
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                # Skip ignored directories
                if any(part in ignore_patterns for part in file_path.parts):
                    continue
                
                relative_path = file_path.relative_to(self.repo_path)
                files.append(self._create_file_info(str(relative_path), file_path))
        
        return files
    
    def _create_file_info(self, relative_path: str, full_path: Path) -> FileInfo:
        """Create FileInfo object for a file."""
        try:
            stat = full_path.stat()
            
            # Determine file status
            status = FileStatus.UNTRACKED
            if self.is_git_repo:
                try:
                    # Check if file is tracked
                    self.repo.git.ls_files(relative_path, error_unmatch=True)
                    
                    # Check if file is modified
                    if self.repo.git.diff('HEAD', relative_path):
                        status = FileStatus.MODIFIED
                    else:
                        status = FileStatus.ADDED
                except git.GitCommandError:
                    status = FileStatus.UNTRACKED
            
            return FileInfo(
                path=relative_path,
                status=status,
                size=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                content_type=self._detect_content_type(full_path)
            )
        except Exception:
            return FileInfo(
                path=relative_path,
                status=FileStatus.UNTRACKED,
                size=0,
                last_modified="",
                content_type="unknown"
            )
    
    def _detect_content_type(self, file_path: Path) -> str:
        """Detect the content type of a file."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type
        
        # Check if it's a text file
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return "application/octet-stream"  # Binary
                return "text/plain"
        except Exception:
            return "unknown"
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = Path(file_path).suffix.lower()
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
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
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
            '.txt': 'text'
        }
        return language_map.get(suffix)