"""Command handler for CLI commands."""

from typing import List
from pathlib import Path

from ..core.services.chat_service import ChatService
from ..core.interfaces.ui import IUserInterface
from ..core.interfaces.repository import IRepository


class CommandHandler:
    """Handles CLI commands for the chat interface."""
    
    def __init__(
        self,
        chat_service: ChatService,
        ui: IUserInterface,
        repository: IRepository
    ) -> None:
        self.chat_service = chat_service
        self.ui = ui
        self.repository = repository
    
    def handle_command(self, command: str) -> None:
        """Handle a command input."""
        parts = command[1:].split()  # Remove leading '/' and split
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Map commands to methods
        command_map = {
            'help': self._help,
            'add': self._add_files,
            'files': self._show_files,
            'clear': self._clear_context,
            'status': self._show_status,
            'diff': self._show_diff,
            'history': self._show_history,
            'session': self._show_session,
            'models': self._show_models,
        }
        
        if cmd in command_map:
            command_map[cmd](args)
        else:
            self.ui.show_error(f"Unknown command: /{cmd}. Type '/help' for available commands.")
    
    def _help(self, args: List[str]) -> None:
        """Show help information."""
        self.ui.show_help()
    
    def _add_files(self, args: List[str]) -> None:
        """Add files to the conversation context."""
        if not args:
            self.ui.show_error("Usage: /add <file1> [file2] ...")
            return
        
        # Validate files exist
        valid_files = []
        for file_path in args:
            path = Path(file_path)
            if path.exists() and path.is_file():
                valid_files.append(str(path))
            else:
                self.ui.show_warning(f"File not found: {file_path}")
        
        if valid_files:
            try:
                self.chat_service.add_files_to_context(valid_files)
                self.ui.show_success(f"Added {len(valid_files)} files to context")
                
                # Show file contents
                for file_path in valid_files:
                    try:
                        content = self.repository.get_file_content(file_path)
                        # Truncate very long files for display
                        if len(content) > 1000:
                            content = content[:1000] + "\n... (truncated)"
                        self.ui.show_file_content(file_path, content)
                    except Exception as e:
                        self.ui.show_warning(f"Could not display {file_path}: {str(e)}")
                        
            except Exception as e:
                self.ui.show_error(f"Error adding files: {str(e)}")
    
    def _show_files(self, args: List[str]) -> None:
        """Show files currently in context."""
        if not self.chat_service.current_session:
            self.ui.show_warning("No active session")
            return
        
        files = self.chat_service.current_session.active_files
        if not files:
            self.ui.show_info("No files in context")
            return
        
        self.ui.show_info("Files in context:")
        for i, file_path in enumerate(files, 1):
            self.ui.show_info(f"  {i}. {file_path}")
    
    def _clear_context(self, args: List[str]) -> None:
        """Clear the conversation context."""
        if not self.chat_service.current_session:
            self.ui.show_warning("No active session")
            return
        
        if self.ui.confirm("Clear all files from context?"):
            self.chat_service.current_session.active_files.clear()
            self.chat_service.current_session.context.clear()
            self.ui.show_success("Context cleared")
    
    def _show_status(self, args: List[str]) -> None:
        """Show repository status."""
        try:
            status_files = self.repository.get_status()
            
            if not status_files:
                self.ui.show_info("Repository is clean")
                return
            
            self.ui.show_info("Repository status:")
            
            # Group by status
            status_groups = {}
            for file_info in status_files:
                status = file_info.status.value
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(file_info.path)
            
            for status, files in status_groups.items():
                self.ui.show_info(f"\n{status.title()}:")
                for file_path in files:
                    self.ui.show_info(f"  {file_path}")
                    
        except Exception as e:
            self.ui.show_error(f"Error getting status: {str(e)}")
    
    def _show_diff(self, args: List[str]) -> None:
        """Show diff for a file."""
        if not args:
            self.ui.show_error("Usage: /diff <file>")
            return
        
        file_path = args[0]
        try:
            diff = self.repository.get_diff(file_path)
            if diff:
                self.ui.show_info(f"Diff for {file_path}:")
                self.ui.show_message(diff)
            else:
                self.ui.show_info(f"No changes in {file_path}")
        except Exception as e:
            self.ui.show_error(f"Error getting diff: {str(e)}")
    
    def _show_history(self, args: List[str]) -> None:
        """Show commit history."""
        try:
            limit = 10
            if args and args[0].isdigit():
                limit = int(args[0])
            
            commits = self.repository.get_commit_history(limit)
            
            if not commits:
                self.ui.show_info("No commit history available")
                return
            
            self.ui.show_info(f"Recent commits (last {len(commits)}):")
            for commit in commits:
                self.ui.show_info(f"  {commit.hash} - {commit.message}")
                self.ui.show_info(f"    by {commit.author} at {commit.timestamp}")
                if commit.files_changed:
                    self.ui.show_info(f"    files: {', '.join(commit.files_changed[:3])}")
                    if len(commit.files_changed) > 3:
                        self.ui.show_info(f"    ... and {len(commit.files_changed) - 3} more")
                self.ui.show_info("")
                
        except Exception as e:
            self.ui.show_error(f"Error getting history: {str(e)}")
    
    def _show_session(self, args: List[str]) -> None:
        """Show session information."""
        summary = self.chat_service.get_session_summary()
        
        if not summary:
            self.ui.show_warning("No active session")
            return
        
        self.ui.show_info("Session Information:")
        self.ui.show_info(f"  ID: {summary.get('session_id', 'Unknown')}")
        self.ui.show_info(f"  Status: {summary.get('status', 'Unknown')}")
        self.ui.show_info(f"  Messages: {summary.get('message_count', 0)}")
        self.ui.show_info(f"  Active files: {len(summary.get('active_files', []))}")
        self.ui.show_info(f"  Context size: {summary.get('context_size', 0)} characters")
    
    def _show_models(self, args: List[str]) -> None:
        """Show available models."""
        # This would be implemented to show available models from the LLM provider
        self.ui.show_info("Available models:")
        self.ui.show_info("  OpenAI: gpt-4o, gpt-4, gpt-3.5-turbo, o1-mini, o3-mini")
        self.ui.show_info("  Anthropic: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307")
        self.ui.show_info("\nUse --model <model_name> to specify a model when starting Aider.")