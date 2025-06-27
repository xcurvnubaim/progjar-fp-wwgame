# Werewolf Game Server

A custom HTTP server implementation built from scratch in Python for hosting a multiplayer Werewolf game. This project demonstrates low-level network programming using Python sockets and concurrent request handling.

## Features

- **Custom HTTP Server**: Built from scratch using Python sockets
- **Concurrent Request Handling**: Supports both thread-based and process-based execution
- **RESTful API**: Simple REST endpoints for game management
- **Game Engine**: Basic Werewolf game logic implementation
- **Modular Architecture**: Clean separation between server, game logic, and routing

## Project Structure

```
fp-progjar/
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
├── server/                 # HTTP server implementation
│   ├── __init__.py
│   ├── core.py            # Main application class and routing
│   ├── request.py         # HTTP request parsing
│   ├── response.py        # HTTP response building
│   └── socket_server.py   # Socket server with concurrency
└── game/                  # Game logic and routes
    ├── __init__.py
    ├── engine.py          # Game engine implementation
    └── routes.py          # Game-specific API endpoints
```

## Quick Start

### Prerequisites

- Python 3.12 or higher
- uv (recommended) or pip for dependency management

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fp-progjar
```

2. Install dependencies (if using uv):
```bash
uv sync
```

### Running the Server

Start the server using:

```bash
python main.py
```

The server will start on `http://0.0.0.0:8888` by default.

## API Endpoints

### Basic Endpoints

- **GET /** - Welcome message
  ```
  GET /
  Response: "Welcome to Werewolf Game Server"
  ```

### Game Endpoints

- **POST /game/start** - Start a new game
  ```
  POST /game/start
  Response: {"status": "game started", "players": ["alice", "bob", "charlie"]}
  ```

- **POST /game/vote** - Submit a vote
  ```
  POST /game/vote
  Content-Type: application/x-www-form-urlencoded
  Body: voter=alice&target=bob
  
  Response: {"status": "vote recorded", "votes": {"alice": "bob"}}
  ```

## Server Configuration

The `HttpSocketServer` class supports several configuration options:

```python
server = HttpSocketServer(
    app=app,
    host='0.0.0.0',      # Server host
    port=8888,           # Server port
    workers=5,           # Number of concurrent workers
    executor='thread'    # 'thread' or 'process'
)
```

### Execution Modes

- **Thread Mode** (`executor='thread'`): Uses ThreadPoolExecutor for concurrent request handling
- **Process Mode** (`executor='process'`): Uses ProcessPoolExecutor for true parallelism

## Architecture

### Server Components

1. **HttpSocketServer**: Core socket server with concurrency support
2. **App**: Application framework with routing capabilities
3. **Request Parser**: HTTP request parsing and validation
4. **Response Builder**: HTTP response formatting with proper headers

### Game Components

1. **GameEngine**: Core game logic and state management
2. **Game Routes**: REST API endpoints for game interactions

## Development

### Adding New Routes

To add new routes, use the `@app.route` decorator:

```python
@app.route('GET', '/new-endpoint')
def new_handler(request):
    return app.response(200, 'OK', 'Response body')
```

### Extending Game Logic

The `GameEngine` class can be extended to add more sophisticated game mechanics:

```python
class GameEngine:
    def new_game_feature(self):
        # Implement new game logic here
        pass
```

## Testing

You can test the server using curl or any HTTP client:

```bash
# Test welcome endpoint
curl http://localhost:8888/

# Start a game
curl -X POST http://localhost:8888/game/start

# Submit a vote
curl -X POST http://localhost:8888/game/vote \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "voter=alice&target=bob"
```

## Technical Details

- **Protocol**: HTTP/1.1
- **Concurrency**: ThreadPoolExecutor or ProcessPoolExecutor
- **Request Parsing**: Custom HTTP parser with content-length support
- **Response Format**: Standard HTTP responses with proper headers
- **Error Handling**: Graceful error handling with proper HTTP status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of a programming course assignment and is intended for educational purposes.

## Acknowledgments

This project was developed as part of a network programming course to demonstrate:
- Low-level socket programming
- HTTP protocol implementation
- Concurrent server architecture
- RESTful API design