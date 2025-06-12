"""Main CLI entry point for Aider v2."""

import click
import os
import sys
import logging
from pathlib import Path
from typing import Optional

from ..core.container import container
from ..core.interfaces.coder import ICoder
from ..core.interfaces.llm_provider import ILLMProvider
from ..core.interfaces.repository import IRepository
from ..core.interfaces.ui import IUserInterface
from ..core.services.chat_service import ChatService
from ..infrastructure.llm.openai_provider import OpenAIProvider
from ..infrastructure.llm.anthropic_provider import AnthropicProvider
from ..infrastructure.repository.git_repository import GitRepository
from ..infrastructure.coders.editblock.editblock_coder import EditBlockCoder
from ..ui.terminal.terminal_interface import TerminalInterface
from .commands import CommandHandler


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('aider_v2.log'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )


def setup_container(
    workspace: str,
    provider: str,
    api_key: str,
    model: str,
    coder_type: str
) -> None:
    """Setup dependency injection container."""
    
    # Register UI
    container.register_instance(IUserInterface, TerminalInterface())
    
    # Register Repository
    container.register_instance(IRepository, GitRepository(workspace))
    
    # Register LLM Provider
    if provider == "openai":
        llm_provider = OpenAIProvider(api_key)
    elif provider == "anthropic":
        llm_provider = AnthropicProvider(api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    container.register_instance(ILLMProvider, llm_provider)
    
    # Register Coder
    if coder_type == "editblock":
        coder = EditBlockCoder(workspace)
    else:
        raise ValueError(f"Unsupported coder type: {coder_type}")
    
    container.register_instance(ICoder, coder)
    
    # Register Chat Service
    container.register(ChatService, ChatService, singleton=True)


@click.command()
@click.option('--model', default='gpt-4o', help='LLM model to use')
@click.option('--provider', default='openai', type=click.Choice(['openai', 'anthropic']), help='LLM provider')
@click.option('--api-key', help='API key for LLM provider (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)')
@click.option('--workspace', default='.', help='Workspace directory')
@click.option('--coder', default='editblock', type=click.Choice(['editblock']), help='Coder type to use')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--files', multiple=True, help='Files to add to initial context')
def main(
    model: str,
    provider: str,
    api_key: Optional[str],
    workspace: str,
    coder: str,
    verbose: bool,
    files: tuple
) -> None:
    """Aider v2 - AI Pair Programming Assistant with improved architecture."""
    
    # Setup logging
    setup_logging(verbose)
    
    # Get API key from environment if not provided
    if not api_key:
        if provider == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
        elif provider == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            click.echo(f"Error: API key required. Set {provider.upper()}_API_KEY environment variable or use --api-key option.", err=True)
            sys.exit(1)
    
    # Validate workspace
    workspace_path = Path(workspace).resolve()
    if not workspace_path.exists():
        click.echo(f"Error: Workspace directory '{workspace}' does not exist.", err=True)
        sys.exit(1)
    
    try:
        # Setup container
        setup_container(str(workspace_path), provider, api_key, model, coder)
        
        # Get services
        ui = container.get(IUserInterface)
        chat_service = container.get(ChatService)
        
        # Validate API key
        llm_provider = container.get(ILLMProvider)
        if not llm_provider.validate_api_key():
            ui.show_error("Invalid API key. Please check your credentials.")
            sys.exit(1)
        
        # Show welcome message
        ui.show_welcome()
        
        # Start session with initial files
        initial_files = list(files) if files else []
        session = chat_service.start_session(initial_files)
        
        if initial_files:
            ui.show_info(f"Added {len(initial_files)} files to context: {', '.join(initial_files)}")
        
        # Create command handler
        command_handler = CommandHandler(chat_service, ui, container.get(IRepository))
        
        # Main chat loop
        ui.show_info(f"Using {provider} {model} model. Type '/help' for commands or start chatting!")
        
        while True:
            try:
                user_input = ui.get_user_input().strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if user_input == '/exit':
                        break
                    
                    try:
                        command_handler.handle_command(user_input)
                    except Exception as e:
                        ui.show_error(f"Command error: {str(e)}")
                    continue
                
                # Process regular chat message
                ui.start_spinner("Thinking...")
                try:
                    response = chat_service.process_user_message(user_input, model)
                    ui.stop_spinner()
                    ui.show_message(response)
                except Exception as e:
                    ui.stop_spinner()
                    ui.show_error(f"Error: {str(e)}")
                
            except KeyboardInterrupt:
                ui.stop_spinner()
                if ui.confirm("\nExit Aider?"):
                    break
            except EOFError:
                break
        
        # Show session summary
        summary = chat_service.get_session_summary()
        ui.show_info(f"Session completed. Messages: {summary.get('message_count', 0)}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()