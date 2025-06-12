"""Main CLI entry point for Aidant."""

import typer
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
from enum import Enum

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


class ProviderChoice(str, Enum):
    """Available LLM providers."""
    openai = "openai"
    anthropic = "anthropic"


class CoderChoice(str, Enum):
    """Available coder types."""
    editblock = "editblock"


# Create the main Typer app
app = typer.Typer(
    name="aidant",
    help="Aidant - AI Pair Programming Assistant with improved architecture.",
    add_completion=False
)


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('aidant.log'),
            logging.StreamHandler() if verbose else logging.NullHandler()
        ]
    )


def setup_container(
    workspace: str,
    provider: str,
    api_key: str,
    model: str,
    coder_type: str,
    base_url: Optional[str] = None
) -> None:
    """Setup dependency injection container."""
    
    # Register UI
    container.register_instance(IUserInterface, TerminalInterface())
    
    # Register Repository
    container.register_instance(IRepository, GitRepository(workspace))
    
    # Register LLM Provider
    if provider == "openai":
        llm_provider = OpenAIProvider(api_key, base_url=base_url)
    elif provider == "anthropic":
        if base_url:
            raise ValueError("Custom base URL is not supported for Anthropic provider")
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


@app.command()
def main(
    model: str = typer.Option("gpt-4o", help="LLM model to use"),
    provider: ProviderChoice = typer.Option(ProviderChoice.openai, help="LLM provider"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key for LLM provider (or set OPENAI_API_KEY/ANTHROPIC_API_KEY env var)"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="Custom base URL for OpenAI-compatible APIs (e.g., OpenRouter, local servers)"),
    workspace: str = typer.Option(".", help="Workspace directory"),
    coder: CoderChoice = typer.Option(CoderChoice.editblock, help="Coder type to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    files: Optional[List[str]] = typer.Option(None, "--files", help="Files to add to initial context")
) -> None:
    """Start Aidant - AI Pair Programming Assistant with improved architecture."""
    
    # Setup logging
    setup_logging(verbose)
    
    # Get API key from environment if not provided
    if not api_key:
        if provider == ProviderChoice.openai:
            api_key = os.getenv('OPENAI_API_KEY')
        elif provider == ProviderChoice.anthropic:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            typer.echo(f"Error: API key required. Set {provider.value.upper()}_API_KEY environment variable or use --api-key option.", err=True)
            raise typer.Exit(1)
    
    # Validate workspace
    workspace_path = Path(workspace).resolve()
    if not workspace_path.exists():
        typer.echo(f"Error: Workspace directory '{workspace}' does not exist.", err=True)
        raise typer.Exit(1)
    
    # Validate base_url usage
    if base_url and provider != ProviderChoice.openai:
        typer.echo(f"Error: --base-url option is only supported with --provider=openai", err=True)
        raise typer.Exit(1)
    
    try:
        # Setup container
        setup_container(str(workspace_path), provider.value, api_key, model, coder.value, base_url)
        
        # Get services
        ui = container.get(IUserInterface)
        chat_service = container.get(ChatService)
        
        # Validate API key
        llm_provider = container.get(ILLMProvider)
        if not llm_provider.validate_api_key():
            ui.show_error("Invalid API key. Please check your credentials.")
            raise typer.Exit(1)
        
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
        provider_info = f"{provider.value} {model}"
        if base_url:
            provider_info += f" (via {base_url})"
        ui.show_info(f"Using {provider_info} model. Type '/help' for commands or start chatting!")
        
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
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


def cli_main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    cli_main()