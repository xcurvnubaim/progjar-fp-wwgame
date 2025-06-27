from server.response import build_response

class App:
    def __init__(self):
        self.routes = {}

    def route(self, method, path):
        def decorator(func):
            self.routes[(method.upper(), path)] = func
            return func
        return decorator

    def handle_request(self, request):
        key = (request['method'], request['path'])
        handler = self.routes.get(key)
        if handler:
            return handler(request)
        return self.response(404, 'Not Found', 'Route not found')

    def response(self, code, message, body):
        return build_response(code, message, body)