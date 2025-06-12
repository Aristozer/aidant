#!/usr/bin/env python3
"""Demo script to test Aidant functionality."""

import tempfile
import os
from pathlib import Path

# Add the package to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from aidant.core.container import container
from aidant.core.interfaces.coder import ICoder
from aidant.core.interfaces.llm_provider import ILLMProvider
from aidant.core.interfaces.repository import IRepository
from aidant.core.interfaces.ui import IUserInterface
from aidant.core.services.chat_service import ChatService
from aidant.infrastructure.repository.git_repository import GitRepository
from aidant.infrastructure.coders.editblock.editblock_coder import EditBlockCoder
from aidant.ui.terminal.terminal_interface import TerminalInterface


class MockUI(TerminalInterface):
    """Mock UI that auto-confirms changes for demo."""
    
    def confirm_changes(self, changes):
        self.show_info("Auto-confirming changes for demo...")
        self.show_changes(changes)
        return True


class MockLLMProvider:
    """Mock LLM provider for demo purposes."""
    
    @property
    def name(self):
        return "mock"
    
    @property
    def available_models(self):
        return []
    
    def get_model_info(self, model_name):
        return None
    
    def generate_response(self, messages, model_name, config=None):
        from aidant.core.interfaces.llm_provider import GenerationResult, ChatMessage, MessageRole
        
        # Simple mock response with a code change
        user_message = messages[-1].content if messages else ""
        
        if "add" in user_message.lower() and "function" in user_message.lower():
            response_content = """I'll add a new function to the file:

demo_file.py
<<<<<<< SEARCH
# This is a demo file
def hello():
    print("Hello, World!")
=======
# This is a demo file
def hello():
    print("Hello, World!")

def new_function():
    print("This is a new function!")
>>>>>>> REPLACE
"""
        else:
            response_content = "I understand. How can I help you with your code?"
        
        return GenerationResult(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=response_content),
            usage={"total_tokens": 50},
            finish_reason="stop",
            model_used="mock-model"
        )
    
    async def generate_response_stream(self, messages, model_name, config=None):
        response = self.generate_response(messages, model_name, config)
        yield response.message.content
    
    def validate_api_key(self):
        return True
    
    def estimate_cost(self, messages, model_name):
        return 0.01


def setup_demo_workspace():
    """Setup a temporary workspace for demo."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)
    
    # Create a demo file
    demo_file = workspace / "demo_file.py"
    demo_file.write_text("""# This is a demo file
def hello():
    print("Hello, World!")
""")
    
    print(f"Created demo workspace at: {workspace}")
    return workspace


def main():
    """Run the demo."""
    print("🚀 Aidant Architecture Demo")
    print("=" * 50)
    
    # Setup demo workspace
    workspace = setup_demo_workspace()
    
    try:
        # Setup container with mock services
        container.register_instance(IUserInterface, MockUI())
        container.register_instance(IRepository, GitRepository(str(workspace)))
        container.register_instance(ILLMProvider, MockLLMProvider())
        container.register_instance(ICoder, EditBlockCoder(str(workspace)))
        
        # Get services
        ui = container.get(IUserInterface)
        chat_service = ChatService(
            container.get(ILLMProvider),
            container.get(ICoder),
            container.get(IRepository),
            container.get(IUserInterface)
        )
        
        print("\n✅ Services initialized successfully!")
        print(f"📁 Workspace: {workspace}")
        
        # Start a session
        session = chat_service.start_session(["demo_file.py"])
        print(f"🎯 Started session: {session.id}")
        
        # Show initial file content
        print("\n📄 Initial file content:")
        ui.show_file_content("demo_file.py", (workspace / "demo_file.py").read_text(), "python")
        
        # Simulate user interaction
        print("\n💬 Simulating user request: 'Add a new function to the file'")
        response = chat_service.process_user_message("Add a new function to the file", "mock-model")
        
        print("\n🤖 AI Response:")
        print(response)
        
        # Show final file content
        print("\n📄 Final file content:")
        final_content = (workspace / "demo_file.py").read_text()
        ui.show_file_content("demo_file.py", final_content, "python")
        
        # Show session summary
        summary = chat_service.get_session_summary()
        print(f"\n📊 Session Summary:")
        print(f"   Messages: {summary['message_count']}")
        print(f"   Files: {len(summary['active_files'])}")
        print(f"   Status: {summary['status']}")
        
        print("\n✨ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workspace, ignore_errors=True)
        print(f"\n🧹 Cleaned up workspace: {workspace}")


if __name__ == "__main__":
    main()