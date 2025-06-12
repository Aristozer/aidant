"""Centralized printing module using Rich for enhanced display.

This module provides a clean interface for all printing operations,
ensuring separation of concerns and consistent styling throughout the application.
"""

from typing import List, Optional, Any, Dict
from enum import Enum
import difflib
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn


class PrintStyle(Enum):
    """Available print styles for messages."""
    INFO = "blue"
    WARNING = "yellow"
    ERROR = "red"
    SUCCESS = "green"
    ACCENT = "cyan"
    MUTED = "dim"
    BOLD = "bold"


class RichPrinter:
    """Centralized Rich-based printer for consistent output formatting."""
    
    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize the printer with an optional console instance."""
        self.console = console or Console()
        self._spinner_live: Optional[Live] = None
    
    def print(
        self, 
        message: str, 
        style: Optional[PrintStyle] = None,
        icon: Optional[str] = None,
        end: str = "\n"
    ) -> None:
        """Print a message with optional styling and icon."""
        formatted_message = message
        
        if icon:
            formatted_message = f"{icon} {message}"
        
        style_value = style.value if style else None
        self.console.print(formatted_message, style=style_value, end=end)
    
    def print_info(self, message: str, icon: str = "ℹ️") -> None:
        """Print an info message."""
        self.print(message, PrintStyle.INFO, icon)
    
    def print_warning(self, message: str, icon: str = "⚠️") -> None:
        """Print a warning message."""
        self.print(message, PrintStyle.WARNING, icon)
    
    def print_error(self, message: str, icon: str = "❌") -> None:
        """Print an error message."""
        self.print(message, PrintStyle.ERROR, icon)
    
    def print_success(self, message: str, icon: str = "✅") -> None:
        """Print a success message."""
        self.print(message, PrintStyle.SUCCESS, icon)
    
    def print_accent(self, message: str, icon: Optional[str] = None) -> None:
        """Print an accented message."""
        self.print(message, PrintStyle.ACCENT, icon)
    
    def print_muted(self, message: str, icon: Optional[str] = None) -> None:
        """Print a muted message."""
        self.print(message, PrintStyle.MUTED, icon)
    
    def print_bold(self, message: str, icon: Optional[str] = None) -> None:
        """Print a bold message."""
        self.print(message, PrintStyle.BOLD, icon)
    
    def print_panel(
        self, 
        content: str, 
        title: Optional[str] = None,
        border_style: str = "blue",
        padding: tuple = (1, 2)
    ) -> None:
        """Print content in a panel."""
        panel = Panel(
            content, 
            title=title, 
            border_style=border_style,
            padding=padding
        )
        self.console.print(panel)
    
    def print_table(
        self, 
        title: Optional[str] = None,
        headers: Optional[List[str]] = None,
        rows: Optional[List[List[str]]] = None,
        header_style: str = "bold magenta"
    ) -> Table:
        """Create and optionally print a table."""
        table = Table(title=title, show_header=bool(headers), header_style=header_style)
        
        if headers:
            for header in headers:
                table.add_column(header)
        
        if rows:
            for row in rows:
                table.add_row(*row)
        
        self.console.print(table)
        return table
    
    def print_syntax(
        self, 
        code: str, 
        language: str = "text",
        theme: str = "monokai",
        line_numbers: bool = True,
        title: Optional[str] = None,
        border_style: str = "blue"
    ) -> None:
        """Print code with syntax highlighting."""
        try:
            syntax = Syntax(code, language, theme=theme, line_numbers=line_numbers)
            if title:
                panel = Panel(syntax, title=title, border_style=border_style)
                self.console.print(panel)
            else:
                self.console.print(syntax)
        except Exception:
            # Fallback to plain text
            if title:
                self.console.print(f"\n--- {title} ---")
            self.console.print(code)
            if title:
                self.console.print("--- End ---\n")
    
    def print_diff(
        self, 
        old_content: str, 
        new_content: str, 
        file_path: str,
        context_lines: int = 3
    ) -> None:
        """Print a diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile=f"a/{file_path}", 
            tofile=f"b/{file_path}",
            lineterm="",
            n=context_lines
        ))
        
        if not diff:
            self.print_warning("No differences found.")
            return
        
        diff_text = "".join(diff)
        self.print_syntax(
            diff_text, 
            "diff", 
            title=f"Changes to {file_path}",
            border_style="blue"
        )
    
    def print_file_content(
        self, 
        file_path: str, 
        content: str, 
        language: Optional[str] = None,
        max_lines: Optional[int] = None
    ) -> None:
        """Print file content with syntax highlighting."""
        # Auto-detect language from file extension if not provided
        if not language:
            language = self._detect_language(file_path)
        
        # Truncate content if max_lines is specified
        if max_lines:
            lines = content.splitlines()
            if len(lines) > max_lines:
                content = "\n".join(lines[:max_lines])
                content += f"\n... (truncated, showing first {max_lines} lines)"
        
        self.print_syntax(
            content, 
            language, 
            title=file_path,
            border_style="blue"
        )
    
    def start_spinner(self, message: str, spinner_type: str = "dots") -> None:
        """Start a loading spinner with a message."""
        if self._spinner_live:
            self.stop_spinner()
        
        spinner = Spinner(spinner_type, text=message)
        self._spinner_live = Live(spinner, console=self.console, refresh_per_second=10)
        self._spinner_live.start()
    
    def stop_spinner(self) -> None:
        """Stop the current loading spinner."""
        if self._spinner_live:
            self._spinner_live.stop()
            self._spinner_live = None
    
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Get input from the user with a prompt."""
        return Prompt.ask(message, default=default, console=self.console)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask the user for confirmation."""
        return Confirm.ask(message, default=default, console=self.console)
    
    def print_separator(self, char: str = "=", length: int = 60, style: Optional[PrintStyle] = None) -> None:
        """Print a separator line."""
        separator = char * length
        self.print(separator, style)
    
    def print_header(self, title: str, char: str = "=", length: int = 60) -> None:
        """Print a header with title centered."""
        self.print_separator(char, length)
        self.print(title, PrintStyle.BOLD, end="")
        self.console.print("", justify="center")
        self.print_separator(char, length)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.go': 'go',
            '.rs': 'rust', '.php': 'php', '.rb': 'ruby', '.html': 'html',
            '.css': 'css', '.sql': 'sql', '.sh': 'bash', '.yml': 'yaml',
            '.yaml': 'yaml', '.json': 'json', '.xml': 'xml', '.md': 'markdown',
            '.toml': 'toml', '.ini': 'ini', '.cfg': 'ini', '.conf': 'ini'
        }
        return language_map.get(ext, 'text')


# Global printer instance for easy access
_global_printer: Optional[RichPrinter] = None


def get_printer() -> RichPrinter:
    """Get the global printer instance."""
    global _global_printer
    if _global_printer is None:
        _global_printer = RichPrinter()
    return _global_printer


def set_printer(printer: RichPrinter) -> None:
    """Set a custom global printer instance."""
    global _global_printer
    _global_printer = printer


# Convenience functions for direct access
def print_info(message: str, icon: str = "ℹ️") -> None:
    """Print an info message using the global printer."""
    get_printer().print_info(message, icon)


def print_warning(message: str, icon: str = "⚠️") -> None:
    """Print a warning message using the global printer."""
    get_printer().print_warning(message, icon)


def print_error(message: str, icon: str = "❌") -> None:
    """Print an error message using the global printer."""
    get_printer().print_error(message, icon)


def print_success(message: str, icon: str = "✅") -> None:
    """Print a success message using the global printer."""
    get_printer().print_success(message, icon)


def print_panel(content: str, title: Optional[str] = None, border_style: str = "blue") -> None:
    """Print content in a panel using the global printer."""
    get_printer().print_panel(content, title, border_style)


def print_syntax(code: str, language: str = "text", title: Optional[str] = None) -> None:
    """Print code with syntax highlighting using the global printer."""
    get_printer().print_syntax(code, language, title=title)