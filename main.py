import signal
import sys
from server.server_thread_http import Server
from game.controller import create_app
from game.game_state import GameStateManager

# Create the Werewolf game application
app = create_app()

def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT/SIGTERM."""
    print("\nShutting down server gracefully...")
    
    # Clean up shared memory
    try:
        game_manager = GameStateManager()
        game_manager.cleanup_shared_memory()
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    print("Server shutdown complete.")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting Werewolf Game Server...")
    print("Available endpoints:")
    print("  POST /games - Create new game")
    print("  POST /games/{id}/join - Join game")
    print("  POST /games/{id}/start - Start game")
    print("  POST /games/{id}/action - Perform action")
    print("  POST /games/{id}/vote - Vote")
    print("  POST /games/{id}/chat - Send chat")
    print("  GET /games/{id}/state - Get game state")
    print("  GET /games/{id}/player/{pid} - Get player info")
    print("  GET /admin/games - List all games (debug)")
    print("  GET /api-docs - OpenAPI JSON documentation")
    print("  GET /api-docs.yaml - OpenAPI YAML documentation")
    print("  GET /swagger-ui - Swagger UI interface")
    print()
    print("Press Ctrl+C to stop the server gracefully.")
    
    try:
        Server(app, 8888).start()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)