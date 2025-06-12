"""Terminal UI implementation using centralized Rich printing module."""

from typing import List, Optional, Callable
from pathlib import Path

from ...core.interfaces.ui import IUserInterface, MessageType, UserChoice
from ...core.interfaces.coder import CodeChange
from ..printing import RichPrinter, PrintStyle


class TerminalInterface(IUserInterface):
    """Terminal-based user interface using centralized Rich printing."""
    
    def __init__(self) -> None:
        self.printer = RichPrinter()
    
    def show_message(self, message: str, message_type: MessageType = MessageType.INFO) -> None:
        """Display a message with appropriate styling."""
        if message_type == MessageType.INFO:
            self.printer.print_info(message)
        elif message_type == MessageType.WARNING:
            self.printer.print_warning(message)
        elif message_type == MessageType.ERROR:
            self.printer.print_error(message)
        elif message_type == MessageType.SUCCESS:
            self.printer.print_success(message)
        else:
            self.printer.print(message)
    
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        return self.printer.prompt(prompt)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask the user for confirmation."""
        return self.printer.confirm(message, default)
    
    def choose_option(self, message: str, choices: List[UserChoice]) -> str:
        """Present multiple choices to the user."""
        self.printer.print(f"\n{message}")
        
        for i, choice in enumerate(choices, 1):
            description = f" - {choice.description}" if choice.description else ""
            self.printer.print(f"  {i}. {choice.label}{description}")
        
        while True:
            try:
                choice_input = self.printer.prompt(
                    "Enter your choice", 
                    default=None
                )
                choice_index = int(choice_input) - 1
                if 0 <= choice_index < len(choices):
                    return choices[choice_index].key
                else:
                    raise IndexError("Choice out of range")
            except (ValueError, IndexError):
                self.printer.print_error("Invalid choice. Please try again.")
    
    def show_changes(self, changes: List[CodeChange]) -> None:
        """Display proposed code changes."""
        if not changes:
            self.printer.print_warning("No changes to display.")
            return
        
        headers = ["File", "Type", "Lines", "Description"]
        rows = []
        
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
            
            rows.append([
                change.file_path,
                change.change_type.value.title(),
                lines,
                description
            ])
        
        self.printer.print_table(
            title="Proposed Changes",
            headers=headers,
            rows=rows,
            header_style="bold magenta"
        )
    
    def confirm_changes(self, changes: List[CodeChange]) -> bool:
        """Show changes and ask for confirmation."""
        self.printer.print_header("PROPOSED CHANGES")
        
        self.show_changes(changes)
        
        # Show detailed diffs for modifications
        for change in changes:
            if change.change_type.value == "modify" and change.old_content and change.content:
                self.printer.print_bold(f"\nDetailed changes for {change.file_path}:")
                self.show_diff(change.old_content, change.content, change.file_path)
        
        self.printer.print_separator()
        return self.printer.confirm("Apply these changes?", default=False)
    
    def show_diff(self, old_content: str, new_content: str, file_path: str) -> None:
        """Display a diff between old and new content."""
        self.printer.print_diff(old_content, new_content, file_path)
    
    def start_spinner(self, message: str) -> None:
        """Start a loading spinner with a message."""
        self.printer.start_spinner(message)
    
    def stop_spinner(self) -> None:
        """Stop the current loading spinner."""
        self.printer.stop_spinner()
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = """🤖 Aidant - AI Pair Programming Assistant

Welcome! I'm here to help you write and edit code. Here's how to get started:

Commands:
• Type your request in natural language
• Use /add <file> to add files to the conversation
• Use /files to see current files
• Use /help for more commands
• Use /exit to quit

Tips:
• Be specific about what you want to change
• I can create new files, modify existing ones, or explain code
• I'll show you exactly what changes I plan to make before applying them

Let's start coding! What would you like to work on?"""
        
        self.printer.print_panel(welcome_text, title="Welcome", border_style="green")
    
    def show_file_content(self, file_path: str, content: str, language: Optional[str] = None) -> None:
        """Display file content with syntax highlighting."""
        self.printer.print_file_content(file_path, content, language)
    
    def show_help(self) -> None:
        """Show help information."""
        help_text = """Available Commands:

/add <file>     - Add a file to the conversation context
/files          - Show files currently in context
/clear          - Clear the conversation context
/status         - Show repository status
/diff <file>    - Show diff for a file
/history        - Show recent commit history
/help           - Show this help message
/exit           - Exit the application

Usage Examples:

• "Add error handling to the login function"
• "Create a new API endpoint for user registration"
• "Fix the bug in the calculate_total method"
• "Add unit tests for the User class"
• "Refactor this code to use async/await"

Tips:

• Be specific about what you want to change
• Mention file names when working with multiple files
• Ask me to explain code if you're unsure about something
• I'll always show you changes before applying them"""
        
        self.printer.print_panel(help_text, title="Help", border_style="yellow")