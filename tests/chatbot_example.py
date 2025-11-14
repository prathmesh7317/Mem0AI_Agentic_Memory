"""
Simple Chatbot Example using Mem0 with Neo4j + Qdrant
Tests the memory service with interactive chat and domain catalog integration
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.memory_service import MemoryService
from app.core.config.config import NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD
from app.utils.catalog_loader import catalog_manager
from tests.test_neo4j import Neo4jTester


def main():
    """Run an interactive chatbot session with domain catalog support"""
    print("Initializing Chatbot with Mem0 (Neo4j + Qdrant)...")
    
    # Test Neo4j connection first
    neo4j_tester = Neo4jTester(NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    if not neo4j_tester.test_connection():
        print("ERROR: Neo4j connection failed! Check logs/app.log for details")
        return
    
    # Initialize the chatbot
    bot = MemoryService()
    
    # Set user ID
    user_id = "test_user_123"
    
    print("\n" + "="*60)
    print("Chatbot ready! Type 'exit' or 'quit' to end.")
    print("Commands: 'domains' - show your domains, 'clear' - clear session")
    print("="*60 + "\n")
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("\n You: ")
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Bot: Goodbye! 👋")
            break
        
        # Skip empty inputs
        if not user_input.strip():
            continue
        
        # Handle special commands
        if user_input.lower() == 'domains':
            try:
                # Get user domains using catalog_manager
                domain_names = catalog_manager.get_user_domain_names(user_id)
                if domain_names:
                    print(f"\n📚 Your Domains: {', '.join(domain_names)}")
                else:
                    print("\n📚 No domains found. Add domains via the web UI.")
            except Exception as e:
                print(f"Error fetching domains: {e}")
            continue
        
        if user_input.lower() == 'clear':
            try:
                # Clear session history
                result = bot.clear_session_history(user_id)
                print(f"\n🗑️ {result}")
            except Exception as e:
                print(f"Error clearing session: {e}")
            continue
        
        try:
            # Get bot response (domain catalogs are automatically loaded by the service)
            response = bot.chat(user_input, user_id)
            print(f"\n🤖 AI Assistant: {response}\n")
        
        except Exception as e:
            print(f"Error: {e}\n")
            print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()