"""Core chat service that orchestrates the conversation flow."""

from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid

from ..interfaces.coder import ICoder, CodeChange
from ..interfaces.llm_provider import ILLMProvider, ChatMessage, MessageRole, GenerationConfig
from ..interfaces.repository import IRepository
from ..interfaces.ui import IUserInterface
from ..domain.models import ChatSession, SessionStatus


class ChatService:
    """Core service that manages chat conversations and coordinates between components."""
    
    def __init__(
        self,
        llm_provider: ILLMProvider,
        coder: ICoder,
        repository: IRepository,
        ui: IUserInterface
    ) -> None:
        self.llm_provider = llm_provider
        self.coder = coder
        self.repository = repository
        self.ui = ui
        self.logger = logging.getLogger(__name__)
        
        self.current_session: Optional[ChatSession] = None
        self.generation_config = GenerationConfig(temperature=0.7)
    
    def start_session(self, initial_files: Optional[List[str]] = None) -> ChatSession:
        """Start a new chat session."""
        session_id = str(uuid.uuid4())
        
        # Get repository context
        repo_context = self.repository.get_context(initial_files or [])
        
        # Create system message with coder instructions
        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=self._build_system_prompt(repo_context)
        )
        
        self.current_session = ChatSession(
            id=session_id,
            created_at=datetime.now(),
            status=SessionStatus.ACTIVE,
            messages=[system_message],
            context=repo_context,
            active_files=initial_files or []
        )
        
        self.logger.info(f"Started chat session {session_id}")
        return self.current_session
    
    def process_user_message(self, user_input: str, model_name: str) -> str:
        """Process a user message and return the assistant's response."""
        if not self.current_session:
            raise ValueError("No active chat session")
        
        try:
            # Add user message to session
            user_message = ChatMessage(role=MessageRole.USER, content=user_input)
            self.current_session.add_message(user_message)
            
            # Get LLM response
            self.logger.info(f"Generating response with model {model_name}")
            result = self.llm_provider.generate_response(
                messages=self.current_session.messages,
                model_name=model_name,
                config=self.generation_config
            )
            
            # Add assistant response to session
            self.current_session.add_message(result.message)
            
            # Check if response contains code changes
            if self._contains_code_changes(result.message.content):
                self._handle_code_changes(result.message.content)
            
            return result.message.content
            
        except Exception as e:
            self.logger.error(f"Error processing user message: {str(e)}")
            self.current_session.status = SessionStatus.ERROR
            raise
    
    def add_files_to_context(self, file_paths: List[str]) -> None:
        """Add files to the current session context."""
        if not self.current_session:
            raise ValueError("No active chat session")
        
        # Get file contents
        new_context = self.repository.get_context(file_paths)
        
        # Update session context
        self.current_session.context.update(new_context)
        self.current_session.active_files.extend(file_paths)
        
        # Update system message with new context
        self.current_session.messages[0] = ChatMessage(
            role=MessageRole.SYSTEM,
            content=self._build_system_prompt(self.current_session.context)
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.id,
            "status": self.current_session.status.value,
            "message_count": self.current_session.get_message_count(),
            "active_files": self.current_session.active_files,
            "context_size": self.current_session.get_context_size()
        }
    
    def _build_system_prompt(self, repo_context: Dict[str, Any]) -> str:
        """Build the system prompt with repository context and coder instructions."""
        base_prompt = f"""You are an AI pair programming assistant. You help users edit code in their repository.

Repository Information:
- Root: {repo_context.get('root_path', 'Unknown')}
- Files: {len(repo_context.get('files', []))} files
- Languages: {', '.join(repo_context.get('languages', []))}

{self.coder.generate_prompt(repo_context)}

Guidelines:
1. Always understand the user's request before making changes
2. Explain your reasoning for changes
3. Make minimal, focused changes
4. Test your changes when possible
5. Follow the project's existing code style
"""
        
        # Add file context if available
        if repo_context.get('file_contents'):
            base_prompt += "\n\nCurrent file contents:\n"
            for file_path, content in repo_context['file_contents'].items():
                # Truncate very long files
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                base_prompt += f"\n--- {file_path} ---\n{content}\n"
        
        return base_prompt
    
    def _contains_code_changes(self, response: str) -> bool:
        """Check if the response contains code changes."""
        change_indicators = [
            "<<<<<<< SEARCH",
            ">>>>>>> REPLACE",
            "```diff",
            "--- a/",
            "+++ b/"
        ]
        return any(indicator in response for indicator in change_indicators)
    
    def _handle_code_changes(self, response: str) -> None:
        """Handle code changes found in the LLM response."""
        try:
            # Parse changes using the coder
            changes = self.coder.parse_response(response)
            
            if not changes:
                return
            
            # Validate changes
            validation_result = self.coder.validate_changes(changes)
            
            if not validation_result.is_valid:
                self.ui.show_error("Invalid changes detected:")
                for error in validation_result.errors:
                    self.ui.show_error(f"  - {error}")
                return
            
            # Show warnings if any
            if validation_result.warnings:
                for warning in validation_result.warnings:
                    self.ui.show_warning(warning)
            
            # Show changes to user and get confirmation
            if self.ui.confirm_changes(changes):
                # Apply changes
                success = self.coder.apply_changes(changes)
                
                if success:
                    # Commit changes to repository
                    commit_message = self._generate_commit_message(changes)
                    commit_hash = self.repository.commit_changes(changes, commit_message)
                    
                    self.ui.show_success(f"Changes applied and committed: {commit_hash}")
                    self.logger.info(f"Applied {len(changes)} changes, commit: {commit_hash}")
                else:
                    self.ui.show_error("Failed to apply changes")
            else:
                self.ui.show_info("Changes cancelled by user")
                
        except Exception as e:
            self.logger.error(f"Error handling code changes: {str(e)}")
            self.ui.show_error(f"Error processing changes: {str(e)}")
    
    def _generate_commit_message(self, changes: List[CodeChange]) -> str:
        """Generate a commit message based on the changes."""
        if len(changes) == 1:
            change = changes[0]
            if change.change_type.value == "create":
                return f"Add {change.file_path}"
            elif change.change_type.value == "modify":
                return f"Update {change.file_path}"
            elif change.change_type.value == "delete":
                return f"Remove {change.file_path}"
        
        # Multiple changes
        file_count = len(set(change.file_path for change in changes))
        return f"Update {file_count} file{'s' if file_count > 1 else ''}"