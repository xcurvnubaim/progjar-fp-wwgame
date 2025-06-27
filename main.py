from server.core import App
from game.routes import register_game_routes
from server.socket_server import HttpSocketServer

app = App()

@app.route('GET', '/')
def index(req):
    return app.response(200, 'OK', 'Welcome to Werewolf Game Server')

register_game_routes(app)

if __name__ == '__main__':
    HttpSocketServer(app).start()