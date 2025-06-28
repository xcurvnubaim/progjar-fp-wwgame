import json
import time
import urllib.parse
from server.core import App
from server.response import build_response
from game.game_state import GameStateManager
from game.game_logic import GameLogic
from game.phase_timer import phase_timer

class WerewolfApp:
    """
    Main application class that handles all Werewolf game HTTP endpoints.
    """
    
    def __init__(self):
        self.app = App()
        self.state_manager = GameStateManager()
        self.game_logic = GameLogic()
        self.setup_routes()
    
    def setup_routes(self):
        """Register all game routes."""
        
        @self.app.route('GET', '/')
        def index(req):
            return self.json_response(200, {
                'message': 'Werewolf Game Server',
                'version': '1.0',
                'documentation': {
                    'swagger_ui': '/swagger-ui',
                    'openapi_json': '/api-docs',
                    'openapi_yaml': '/api-docs.yaml'
                },
                'endpoints': [
                    'POST /games - Create new game',
                    'POST /games/{id}/join - Join game',
                    'POST /games/{id}/start - Start game',
                    'POST /games/{id}/action - Perform action',
                    'POST /games/{id}/vote - Vote',
                    'POST /games/{id}/chat - Send chat',
                    'GET /games/{id}/state - Get game state',
                    'GET /games/{id}/player/{pid} - Get player info',
                    'GET /admin/games - List all games (debug)',
                    'GET /swagger-ui - Interactive API documentation',
                    'GET /api-docs - OpenAPI specification (JSON)',
                    'GET /api-docs.yaml - OpenAPI specification (YAML)'
                ]
            })

        @self.app.route('POST', '/games')
        def create_game(req):
            """Create a new game."""
            try:
                game_id = self.state_manager.create_game()
                return self.json_response(200, {'game_id': game_id})
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/games/<game_id>/join')
        def join_game(req):
            """Join a game."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                body = self.parse_json_body(req)
                
                if not body or 'name' not in body:
                    return self.json_response(400, {'error': 'Name required'})
                
                name = body['name'].strip()
                if not name or len(name) > 20:
                    return self.json_response(400, {'error': 'Invalid name'})
                
                player_id = self.state_manager.add_player(game_id, name)
                if not player_id:
                    return self.json_response(409, {'error': 'Cannot join game'})
                
                return self.json_response(200, {'player_id': player_id})
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/games/<game_id>/start')
        def start_game(req):
            """Start a game."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                game = self.state_manager.get_game_state(game_id)
                if not game:
                    return self.json_response(404, {'error': 'Game not found'})
                
                if game['started']:
                    return self.json_response(409, {'error': 'Game already started'})
                
                if len(game['players']) < 3:
                    return self.json_response(400, {'error': 'Need at least 3 players'})
                
                # Assign roles
                if not self.game_logic.assign_roles(game_id):
                    return self.json_response(500, {'error': 'Failed to start game'})
                
                # Start night phase
                phase_timer.start_night_phase(game_id)
                
                return self.json_response(200, {'status': 'started'})
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/games/<game_id>/action')
        def perform_action(req):
            """Perform a game action (werewolf vote, seer investigate)."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                body = self.parse_json_body(req)
                
                if not body or not all(k in body for k in ['player_id', 'action_type']):
                    return self.json_response(400, {'error': 'player_id and action_type required'})
                
                player_id = body['player_id']
                action_type = body['action_type']
                target_id = body.get('target_id')
                
                # Validate action
                valid, error_msg = self.game_logic.validate_action(
                    game_id, player_id, action_type, target_id
                )
                if not valid:
                    return self.json_response(403, {'error': error_msg})
                
                # Record action
                if self.state_manager.record_action(game_id, action_type, player_id, target_id):
                    return self.json_response(200, {'status': 'recorded'})
                else:
                    return self.json_response(500, {'error': 'Failed to record action'})
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/games/<game_id>/vote')
        def vote(req):
            """Vote for a player during day phase."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                body = self.parse_json_body(req)
                
                if not body or not all(k in body for k in ['player_id', 'target_id']):
                    return self.json_response(400, {'error': 'player_id and target_id required'})
                
                player_id = body['player_id']
                target_id = body['target_id']
                
                # Validate vote
                valid, error_msg = self.game_logic.validate_action(
                    game_id, player_id, 'day_vote', target_id
                )
                if not valid:
                    return self.json_response(403, {'error': error_msg})
                
                # Record vote
                if self.state_manager.record_action(game_id, 'day_vote', player_id, target_id):
                    return self.json_response(200, {'status': 'voted'})
                else:
                    return self.json_response(500, {'error': 'Failed to record vote'})
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/games/<game_id>/chat')
        def send_chat(req):
            """Send a chat message during day phase."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                body = self.parse_json_body(req)
                
                if not body or not all(k in body for k in ['player_id', 'message']):
                    return self.json_response(400, {'error': 'player_id and message required'})
                
                player_id = body['player_id']
                message = body['message']
                
                # Validate chat
                valid, error_msg = self.game_logic.validate_action(
                    game_id, player_id, 'chat'
                )
                if not valid:
                    return self.json_response(403, {'error': error_msg})
                
                # Add chat message
                if self.state_manager.add_chat_message(game_id, player_id, message):
                    return self.json_response(200, {'status': 'sent'})
                else:
                    return self.json_response(429, {'error': 'Rate limited or invalid message'})
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('GET', '/games/<game_id>/state')
        def get_game_state(req):
            """Get the current game state."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                # Parse query parameters for player-specific view
                query_params = self.parse_query_params(req['path'])
                player_id = query_params.get('player_id')
                
                summary = self.game_logic.get_game_summary(game_id, player_id)
                if 'error' in summary:
                    return self.json_response(404, summary)
                
                return self.json_response(200, summary)
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('GET', '/games/<game_id>/player/<player_id>')
        def get_player_info(req):
            """Get player-specific information (role, abilities, etc.)."""
            try:
                path_params = req.get('path_params', {})
                game_id = path_params.get('game_id')
                player_id = path_params.get('player_id')
                
                if not game_id or not player_id:
                    return self.json_response(400, {'error': 'Invalid game or player ID'})
                
                role_info = self.game_logic.get_player_role_info(game_id, player_id)
                if 'error' in role_info:
                    return self.json_response(404, role_info)
                
                return self.json_response(200, role_info)
                
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        # Admin/Debug endpoints
        @self.app.route('GET', '/admin/games')
        def list_all_games(req):
            """List all games (debug endpoint)."""
            try:
                games = self.state_manager.get_all_games()
                active_timers = phase_timer.get_active_timers()
                
                return self.json_response(200, {
                    'games': games,
                    'active_timers': active_timers
                })
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        @self.app.route('POST', '/admin/games/<game_id>/force-end-phase')
        def force_end_phase(req):
            """Force end the current phase (admin endpoint)."""
            try:
                game_id = req.get('path_params', {}).get('game_id')
                if not game_id:
                    return self.json_response(400, {'error': 'Invalid game ID'})
                
                if phase_timer.force_end_phase(game_id):
                    return self.json_response(200, {'status': 'phase ended'})
                else:
                    return self.json_response(404, {'error': 'Game not found or ended'})
                    
            except Exception as e:
                return self.json_response(500, {'error': str(e)})
        
        # API Documentation endpoints
        @self.app.route('GET', '/api-docs')
        def api_docs(req):
            """Serve the OpenAPI/Swagger documentation as JSON."""
            try:
                with open('api_docs.json', 'r') as f:
                    content = f.read()
                headers = {'Content-Type': 'application/json'}
                return build_response(200, 'OK', content, headers)
            except FileNotFoundError:
                return self.json_response(404, {'error': 'API documentation not found'})
            except Exception as e:
                return self.json_response(500, {'error': f'Error loading API docs: {str(e)}'})
        
        @self.app.route('GET', '/api-docs.yaml')
        def api_docs_yaml(req):
            """Serve the raw OpenAPI YAML file."""
            try:
                with open('api_docs.yaml', 'r') as f:
                    content = f.read()
                headers = {'Content-Type': 'text/yaml'}
                return build_response(200, 'OK', content, headers)
            except FileNotFoundError:
                return self.json_response(404, {'error': 'API documentation not found'})
            except Exception as e:
                return self.json_response(500, {'error': f'Error loading API docs: {str(e)}'})
        
        @self.app.route('GET', '/swagger-ui')
        def swagger_ui(req):
            """Serve a simple Swagger UI HTML page."""
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Werewolf Game Server API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: '/api-docs',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
            """
            headers = {'Content-Type': 'text/html'}
            return build_response(200, 'OK', html_content, headers)
    
    def parse_json_body(self, req) -> dict:
        """Parse JSON body from request."""
        try:
            if req['body']:
                return json.loads(req['body'])
        except (json.JSONDecodeError, KeyError):
            pass
        return {}
    
    def parse_query_params(self, path: str) -> dict:
        """Parse query parameters from path."""
        if '?' not in path:
            return {}
        
        query_string = path.split('?', 1)[1]
        return dict(urllib.parse.parse_qsl(query_string))
    
    def json_response(self, status_code: int, data: dict):
        """Create a JSON response."""
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data, indent=2)
        return build_response(status_code, self.get_status_message(status_code), body, headers)
    
    def get_status_message(self, code: int) -> str:
        """Get HTTP status message for code."""
        messages = {
            200: 'OK',
            400: 'Bad Request',
            403: 'Forbidden',
            404: 'Not Found',
            409: 'Conflict',
            429: 'Too Many Requests',
            500: 'Internal Server Error'
        }
        return messages.get(code, 'Unknown')
    
    def get_app(self):
        """Get the underlying App instance."""
        return self.app


def create_app():
    """Factory function to create the application."""
    werewolf_app = WerewolfApp()
    return werewolf_app.get_app()
