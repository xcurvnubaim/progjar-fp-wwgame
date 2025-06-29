import signal
import sys
from server.server_thread_http import Server
from server.lb_process import Server as ServerLB
from game.controller import create_app
from game.game_state import GameStateManager
import argparse

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
    parser = argparse.ArgumentParser(description="Werewolf Game Server")
    parser.add_argument(
        '--type',
        type=str,
        choices=['backend', 'lb'],
        required=True,
        help="Specify the server type to run: 'backend' for the game server, 'lb' for the load balancer."
    )
    parser.add_argument(
        '--port',
        type=int,
        required=False,
        help="Specify the port number for the server to listen on."
    )
    args = parser.parse_args()
    if args.type == 'backend':
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
            port = args.port
            Server(app, port).start()
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
    elif args.type == 'lb':
        try:
            ServerLB().start()
        except KeyboardInterrupt:
            print("\nLoad Balancer shutting down...")