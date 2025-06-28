from server.socket_server import HttpSocketServer
from game.controller import create_app

# Create the Werewolf game application
app = create_app()

if __name__ == '__main__':
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
    print()
    
    HttpSocketServer(app).start()