"""Terminal UI implementation using Rich for enhanced display."""

from typing import List, Optional, Callable
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
import difflib

from ...core.interfaces.ui import IUserInterface, MessageType, UserChoice
from ...core.interfaces.coder import CodeChange


class TerminalInterface(IUserInterface):
    """Terminal-based user interface using Rich for enhanced display."""
    
    def __init__(self) -> None:
        self.console = Console()
        self.spinner_live: Optional[Live] = None
    
    def show_message(self, message: str, message_type: MessageType = MessageType.INFO) -> None:
        """Display a message with appropriate styling."""
        style_map = {
            MessageType.INFO: "blue",
            MessageType.WARNING: "yellow",
            MessageType.ERROR: "red",
            MessageType.SUCCESS: "green"
        }
        
        icon_map = {
            MessageType.INFO: "ℹ️",
            MessageType.WARNING: "⚠️",
            MessageType.ERROR: "❌",
            MessageType.SUCCESS: "✅"
        }
        
        style = style_map.get(message_type, "white")
        icon = icon_map.get(message_type, "")
        
        self.console.print(f"{icon} {message}", style=style)
    
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        return Prompt.ask(prompt)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask the user for confirmation."""
        return Confirm.ask(message, default=default)
    
    def choose_option(self, message: str, choices: List[UserChoice]) -> str:
        """Present multiple choices to the user."""
        self.console.print(f"\n{message}")
        
        for i, choice in enumerate(choices, 1):
            description = f" - {choice.description}" if choice.description else ""
            self.console.print(f"  {i}. {choice.label}{description}")
        
        while True:
            try:
                choice_input = Prompt.ask("Enter your choice", choices=[str(i) for i in range(1, len(choices) + 1)])
                choice_index = int(choice_input) - 1
                return choices[choice_index].key
            except (ValueError, IndexError):
                self.console.print("Invalid choice. Please try again.", style="red")
    
    def show_changes(self, changes: List[CodeChange]) -> None:
        """Display proposed code changes."""
        if not changes:
            self.console.print("No changes to display.", style="yellow")
            return
        
        table = Table(title="Proposed Changes", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Lines", style="green")
        table.add_column("Description", style="white")
        
        for change in changes:
            lines = "N/A"
            if change.line_start and change.line_end:
                lines = f"{change.line_start}-{change.line_end}"
            elif change.old_content:
                lines = str(len(change.old_content.splitlines()))
            
            description = ""
            if change.change_type.value == "create":
                description = "New file"
            elif change.change_type.value == "modify":
                description = "Modify existing file"
            elif change.change_type.value == "delete":
                description = "Delete file"
            
            table.add_row(
                change.file_path,
                change.change_type.value.title(),
                lines,
                description
            )
        
        self.console.print(table)
    
    def confirm_changes(self, changes: List[CodeChange]) -> bool:
        """Show changes and ask for confirmation."""
        self.console.print("\n" + "="*60)
        self.console.print("PROPOSED CHANGES", style="bold yellow", justify="center")
        self.console.print("="*60)
        
        self.show_changes(changes)
        
        # Show detailed diffs for modifications
        for change in changes:
            if change.change_type.value == "modify" and change.old_content and change.content:
                self.console.print(f"\n[bold]Detailed changes for {change.file_path}:[/bold]")
                self.show_diff(change.old_content, change.content, change.file_path)
        
        self.console.print("\n" + "="*60)
        return self.confirm("Apply these changes?", default=False)
    
    def show_diff(self, old_content: str, new_content: str, file_path: str) -> None:
        """Display a diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile=f"a/{file_path}", 
            tofile=f"b/{file_path}",
            lineterm=""
        ))
        
        if not diff:
            self.console.print("No differences found.", style="yellow")
            return
        
        # Display diff with syntax highlighting
        diff_text = "".join(diff)
        
        try:
            syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
            panel = Panel(syntax, title=f"Changes to {file_path}", border_style="blue")
            self.console.print(panel)
        except Exception:
            # Fallback to plain text
            self.console.print(diff_text)
    
    def start_spinner(self, message: str) -> None:
        """Start a loading spinner with a message."""
        if self.spinner_live:
            self.stop_spinner()
        
        spinner = Spinner("dots", text=message)
        self.spinner_live = Live(spinner, console=self.console, refresh_per_second=10)
        self.spinner_live.start()
    
    def stop_spinner(self) -> None:
        """Stop the current loading spinner."""
        if self.spinner_live:
            self.spinner_live.stop()
            self.spinner_live = None
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = """
[bold blue]🤖 Aider v2 - AI Pair Programming Assistant[/bold blue]

Welcome! I'm here to help you write and edit code. Here's how to get started:

[bold]Commands:[/bold]
• Type your request in natural language
• Use [cyan]/add <file>[/cyan] to add files to the conversation
• Use [cyan]/files[/cyan] to see current files
• Use [cyan]/help[/cyan] for more commands
• Use [cyan]/exit[/cyan] to quit

[bold]Tips:[/bold]
• Be specific about what you want to change
• I can create new files, modify existing ones, or explain code
• I'll show you exactly what changes I plan to make before applying them

Let's start coding! What would you like to work on?
"""
        panel = Panel(welcome_text, title="Welcome", border_style="green")
        self.console.print(panel)
    
    def show_file_content(self, file_path: str, content: str, language: Optional[str] = None) -> None:
        """Display file content with syntax highlighting."""
        try:
            # Detect language from file extension if not provided
            if not language:
                from pathlib import Path
                ext = Path(file_path).suffix.lower()
                language_map = {
                    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                    '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.go': 'go',
                    '.rs': 'rust', '.php': 'php', '.rb': 'ruby', '.html': 'html',
                    '.css': 'css', '.sql': 'sql', '.sh': 'bash', '.yml': 'yaml',
                    '.yaml': 'yaml', '.json': 'json', '.xml': 'xml', '.md': 'markdown'
                }
                language = language_map.get(ext, 'text')
            
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            panel = Panel(syntax, title=file_path, border_style="blue")
            self.console.print(panel)
        except Exception:
            # Fallback to plain text
            self.console.print(f"\n--- {file_path} ---")
            self.console.print(content)
            self.console.print("--- End ---\n")
    
    def show_help(self) -> None:
        """Show help information."""
        help_text = """
[bold]Available Commands:[/bold]

[cyan]/add <file>[/cyan]     - Add a file to the conversation context
[cyan]/files[/cyan]          - Show files currently in context
[cyan]/clear[/cyan]          - Clear the conversation context
[cyan]/status[/cyan]         - Show repository status
[cyan]/diff <file>[/cyan]    - Show diff for a file
[cyan]/history[/cyan]        - Show recent commit history
[cyan]/help[/cyan]           - Show this help message
[cyan]/exit[/cyan]           - Exit the application

[bold]Usage Examples:[/bold]

• "Add error handling to the login function"
• "Create a new API endpoint for user registration"
• "Fix the bug in the calculate_total method"
• "Add unit tests for the User class"
• "Refactor this code to use async/await"

[bold]Tips:[/bold]

• Be specific about what you want to change
• Mention file names when working with multiple files
• Ask me to explain code if you're unsure about something
• I'll always show you changes before applying them
"""
        panel = Panel(help_text, title="Help", border_style="yellow")
        self.console.print(panel)