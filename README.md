# Werewolf Game Server

A complete multiplayer Werewolf (Mafia) game server built with Python using a custom HTTP framework. The server manages game state, handles player roles, automates phase transitions, and persists data to JSON files.

## Features

- **Complete Game Logic**: Werewolf, Seer, and Villager roles with proper win conditions
- **Automatic Phase Management**: Timed night (2 min) and day (5 min) phases
- **Real-time Chat**: During day phases with rate limiting
- **Persistent Storage**: Game states saved to JSON files
- **Thread-safe**: Concurrent game support with proper locking
- **RESTful API**: JSON-based HTTP endpoints
- **Custom HTTP Server**: No external dependencies except standard library

## Game Rules

- **Minimum 3 players** required to start
- **Roles**: 1 Werewolf, 1 Seer, remaining Villagers
- **Night Phase**: Werewolves vote to kill, Seer investigates
- **Day Phase**: All players discuss and vote to eliminate someone
- **Win Conditions**:
  - Villagers win when all werewolves are eliminated
  - Werewolves win when they equal/outnumber villagers

## Installation & Setup

1. **Clone/Download** the project
2. **No external dependencies** required - uses only Python standard library
3. **Run the server**:
   ```bash
   python main.py
   ```
4. **Server starts** on `http://localhost:8888`

## API Endpoints

### Game Management

#### Create Game
```bash
POST /games
Response: {"game_id": "abc123"}
```

#### Join Game
```bash
POST /games/{game_id}/join
Body: {"name": "PlayerName"}
Response: {"player_id": "def456"}
```

#### Start Game
```bash
POST /games/{game_id}/start
Response: {"status": "started"}
```

### Game Actions

#### Night Actions (Werewolf Vote)
```bash
POST /games/{game_id}/action
Body: {
  "player_id": "def456",
  "action_type": "werewolf_vote",
  "target_id": "ghi789"
}
Response: {"status": "recorded"}
```

#### Night Actions (Seer Investigate)
```bash
POST /games/{game_id}/action
Body: {
  "player_id": "def456",
  "action_type": "seer_investigate", 
  "target_id": "ghi789"
}
Response: {"status": "recorded"}
```

#### Day Voting
```bash
POST /games/{game_id}/vote
Body: {
  "player_id": "def456",
  "target_id": "ghi789"
}
Response: {"status": "voted"}
```

#### Chat (Day Phase Only)
```bash
POST /games/{game_id}/chat
Body: {
  "player_id": "def456",
  "message": "I think Alice is suspicious!"
}
Response: {"status": "sent"}
```

### Information

#### Get Game State
```bash
GET /games/{game_id}/state?player_id={player_id}
Response: {
  "game_id": "abc123",
  "phase": "day",
  "started": true,
  "ended": false,
  "players": [...],
  "alive_count": 3,
  "dead_count": 1,
  "recent_chat": [...]
}
```

#### Get Player Role Info
```bash
GET /games/{game_id}/player/{player_id}
Response: {
  "role": "werewolf",
  "allies": [...],
  "can_kill": true
}
```

### Admin/Debug

#### List All Games
```bash
GET /admin/games
Response: {
  "games": {...},
  "active_timers": {...}
}
```

#### Force End Phase
```bash
POST /admin/games/{game_id}/force-end-phase
Response: {"status": "phase ended"}
```

## Testing

Run the test script to see the complete game flow:

```bash
# Terminal 1: Start the server
python main.py

# Terminal 2: Run tests
python test_werewolf.py
```

## API Documentation

The server provides comprehensive API documentation:

- **Interactive Swagger UI**: [http://localhost:8888/swagger-ui](http://localhost:8888/swagger-ui)
- **OpenAPI JSON**: [http://localhost:8888/api-docs](http://localhost:8888/api-docs)
- **OpenAPI YAML**: [http://localhost:8888/api-docs.yaml](http://localhost:8888/api-docs.yaml)
- **Detailed API Guide**: See [API_DOCS.md](API_DOCS.md)

The interactive Swagger UI provides a complete interface to test all endpoints directly from your browser.

## Architecture

### Core Components

1. **`game_state.py`** - Thread-safe singleton for state management
   - In-memory storage with file persistence
   - Atomic writes with locking
   - Player management and chat handling

2. **`game_logic.py`** - Game rules and validation
   - Role assignment and win condition checking
   - Action validation and resolution
   - Player-specific information filtering

3. **`phase_timer.py`** - Background phase management
   - Automatic phase transitions
   - Timer cleanup and management
   - Thread-safe timer operations

4. **`app.py`** - HTTP application and routing
   - RESTful API endpoint handlers
   - JSON request/response processing
   - Error handling and validation

5. **`server/`** - Custom HTTP server framework
   - Socket-based HTTP server
   - Request/response parsing
   - Path parameter support

### Game State Structure

```json
{
  "game_id": {
    "phase": "setup|night|day|ended",
    "phase_end": 1640995200.0,
    "started": true,
    "ended": false,
    "winner": null,
    "players": {
      "player_id": {
        "name": "Alice",
        "role": "werewolf",
        "alive": true,
        "vote": null
      }
    },
    "actions": {
      "werewolf_votes": {"target_id": 1},
      "seer_target": "target_id",
      "day_votes": {"target_id": ["voter1", "voter2"]}
    },
    "chat": [
      {
        "player": "player_id",
        "message": "Hello!",
        "time": 1640995200.0
      }
    ]
  }
}
```

## File Persistence

- **`game_states.json`** - Automatically created/updated
- **Atomic writes** prevent corruption
- **Auto-loading** on server restart
- **Cleanup** removes old games (24h default)

## Phase Timing

- **Night Phase**: 120 seconds (2 minutes)
  - Werewolves vote to kill
  - Seer investigates one player
  - No chat allowed

- **Day Phase**: 300 seconds (5 minutes)
  - All players can chat (rate limited: 3 msgs/min)
  - All players vote to eliminate someone
  - Discussion and strategy

## Validation & Security

- **Input sanitization** for chat messages (200 char limit)
- **Rate limiting** on chat (3 messages per minute per player)
- **Action validation** based on role and phase
- **Dead player restrictions** (cannot act)
- **Self-targeting prevention** (cannot vote/kill yourself)

## Error Handling

- **404**: Game/player not found
- **403**: Invalid action for current phase/role
- **400**: Invalid request format
- **409**: Game already started/ended
- **429**: Rate limited (chat)
- **500**: Server errors

## Example Game Flow

1. **Create Game**: `POST /games` → Get game_id
2. **Players Join**: Each player `POST /games/{id}/join`
3. **Start Game**: `POST /games/{id}/start` → Roles assigned, night begins
4. **Night Phase** (2 min):
   - Werewolf: `POST /games/{id}/action` (werewolf_vote)
   - Seer: `POST /games/{id}/action` (seer_investigate)
5. **Day Phase** (5 min):
   - Players: `POST /games/{id}/chat` (discuss)
   - Players: `POST /games/{id}/vote` (eliminate)
6. **Repeat** until win condition met

## Development Notes

- **Thread-safe**: Uses locks for concurrent access
- **Scalable**: Supports multiple simultaneous games
- **Extensible**: Easy to add new roles or features
- **Testable**: Comprehensive test coverage
- **Maintainable**: Clear separation of concerns

## License

This project is open source. Feel free to modify and distribute.
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