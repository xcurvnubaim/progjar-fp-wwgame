# Werewolf Game Server API Documentation

## Overview

The Werewolf Game Server provides a comprehensive RESTful API for managing multiplayer Werewolf (Mafia) games. The API supports game creation, player management, real-time gameplay, and administrative functions.

## Interactive Documentation

Once the server is running, you can access the interactive API documentation at:

- **Swagger UI**: [http://localhost:8888/swagger-ui](http://localhost:8888/swagger-ui)
- **OpenAPI JSON**: [http://localhost:8888/api-docs](http://localhost:8888/api-docs)
- **OpenAPI YAML**: [http://localhost:8888/api-docs.yaml](http://localhost:8888/api-docs.yaml)

## Quick Start

1. **Start the server**:
   ```bash
   python main.py
   ```

2. **Create a game**:
   ```bash
   curl -X POST http://localhost:8888/games
   ```

3. **Join the game**:
   ```bash
   curl -X POST http://localhost:8888/games/{game_id}/join \
        -H "Content-Type: application/json" \
        -d '{"name": "Alice"}'
   ```

4. **View interactive docs**: Visit [http://localhost:8888/swagger-ui](http://localhost:8888/swagger-ui)

## API Endpoints Summary

### Game Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/` | Server information and endpoint list |
| POST   | `/games` | Create a new game |
| POST   | `/games/{id}/join` | Join an existing game |
| POST   | `/games/{id}/start` | Start the game (assign roles) |

### Game Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/games/{id}/action` | Perform role-specific actions (night phase) |
| POST   | `/games/{id}/vote` | Vote to eliminate a player (day phase) |
| POST   | `/games/{id}/chat` | Send chat message (day phase) |

### Information
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/games/{id}/state` | Get current game state |
| GET    | `/games/{id}/player/{pid}` | Get player role information |

### Admin/Debug
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/admin/games` | List all games and timers |
| POST   | `/admin/games/{id}/force-end-phase` | Force end current phase |

### API Documentation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/swagger-ui` | Interactive Swagger UI documentation |
| GET    | `/api-docs` | OpenAPI specification (JSON) |
| GET    | `/api-docs.yaml` | OpenAPI specification (YAML) |

## Example Usage

### Complete Game Flow

```bash
# 1. Create a game
GAME_ID=$(curl -s -X POST http://localhost:8888/games | jq -r .game_id)
echo "Game ID: $GAME_ID"

# 2. Add players
ALICE_ID=$(curl -s -X POST http://localhost:8888/games/$GAME_ID/join \
           -H "Content-Type: application/json" \
           -d '{"name": "Alice"}' | jq -r .player_id)

BOB_ID=$(curl -s -X POST http://localhost:8888/games/$GAME_ID/join \
         -H "Content-Type: application/json" \
         -d '{"name": "Bob"}' | jq -r .player_id)

CHARLIE_ID=$(curl -s -X POST http://localhost:8888/games/$GAME_ID/join \
             -H "Content-Type: application/json" \
             -d '{"name": "Charlie"}' | jq -r .player_id)

# 3. Start the game
curl -X POST http://localhost:8888/games/$GAME_ID/start

# 4. Get game state
curl "http://localhost:8888/games/$GAME_ID/state?player_id=$ALICE_ID"

# 5. Get Alice's role information
curl http://localhost:8888/games/$GAME_ID/player/$ALICE_ID
```

### Night Phase Actions

```bash
# Werewolf votes to kill (if Alice is werewolf)
curl -X POST http://localhost:8888/games/$GAME_ID/action \
     -H "Content-Type: application/json" \
     -d '{
       "player_id": "'$ALICE_ID'",
       "action_type": "werewolf_vote",
       "target_id": "'$BOB_ID'"
     }'

# Seer investigates (if Charlie is seer)
curl -X POST http://localhost:8888/games/$GAME_ID/action \
     -H "Content-Type: application/json" \
     -d '{
       "player_id": "'$CHARLIE_ID'",
       "action_type": "seer_investigate",
       "target_id": "'$ALICE_ID'"
     }'
```

### Day Phase Actions

```bash
# Send chat message
curl -X POST http://localhost:8888/games/$GAME_ID/chat \
     -H "Content-Type: application/json" \
     -d '{
       "player_id": "'$ALICE_ID'",
       "message": "I think Bob is acting suspicious!"
     }'

# Vote to eliminate
curl -X POST http://localhost:8888/games/$GAME_ID/vote \
     -H "Content-Type: application/json" \
     -d '{
       "player_id": "'$ALICE_ID'",
       "target_id": "'$BOB_ID'"
     }'
```

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    "game_id": "abc12345"
  }
}
```

### Error Response
```json
{
  "error": "Game not found"
}
```

### Game State Response
```json
{
  "game_id": "abc12345",
  "phase": "day",
  "started": true,
  "ended": false,
  "winner": null,
  "players": [
    {
      "id": "def67890",
      "name": "Alice",
      "alive": true,
      "role": "villager"
    }
  ],
  "alive_count": 3,
  "dead_count": 0,
  "phase_end": 1640995200.0,
  "time_remaining": 45.2,
  "recent_chat": [
    {
      "player": "def67890",
      "message": "Hello everyone!",
      "time": 1640995100.0
    }
  ]
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request (invalid parameters) |
| 403  | Forbidden (action not allowed) |
| 404  | Not Found (game/player doesn't exist) |
| 409  | Conflict (game already started, name taken) |
| 429  | Too Many Requests (rate limited) |
| 500  | Internal Server Error |

## Game Rules Reference

### Roles
- **Werewolf**: Vote to kill during night phase
- **Seer**: Investigate one player each night to learn their role
- **Villager**: Vote during day phase to eliminate players

### Phases
- **Setup**: Players join, game hasn't started
- **Night** (2 minutes): Special role actions only
- **Day** (5 minutes): Chat and voting to eliminate
- **Ended**: Game finished, winner determined

### Win Conditions
- **Villagers**: Eliminate all werewolves
- **Werewolves**: Equal or outnumber villagers

## Rate Limits

- **Chat**: 3 messages per player per minute
- **Actions**: No limit, but one action per phase per player

## Testing

Use the included test script to verify all endpoints:

```bash
python test_werewolf.py
```

## Error Handling

The API provides detailed error messages for common issues:

- **Invalid game ID**: Game not found
- **Wrong phase**: Action not allowed in current phase
- **Dead player**: Dead players cannot perform actions
- **Invalid role**: Only certain roles can perform specific actions
- **Rate limiting**: Too many chat messages
- **Game state**: Game already started/ended

## Development

For development and debugging, use the admin endpoints:

```bash
# List all games and active timers
curl http://localhost:8888/admin/games

# Force end current phase (for testing)
curl -X POST http://localhost:8888/admin/games/$GAME_ID/force-end-phase
```

## Security Considerations

- Input validation on all endpoints
- Message sanitization for chat
- Rate limiting on chat messages
- No authentication required (game-based access control)

## Future Enhancements

Potential API improvements:
- WebSocket support for real-time updates
- Player authentication and sessions
- Spectator mode endpoints
- Game replay functionality
- Advanced role configurations
