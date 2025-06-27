from game.engine import GameEngine
from urllib.parse import parse_qs

def register_game_routes(app):
    engine = GameEngine()

    @app.route('POST', '/game/start')
    def start_game(req):
        result = engine.start_game()
        return app.response(200, 'OK', str(result))

    @app.route('POST', '/game/vote')
    def vote(req):
        data = parse_qs(req['body'])
        voter = data.get('voter', [''])[0]
        target = data.get('target', [''])[0]
        result = engine.vote(voter, target)
        return app.response(200, 'OK', str(result))