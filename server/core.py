from server.response import build_response
import re

class App:
    def __init__(self):
        self.routes = {}
        self.pattern_routes = {}

    def route(self, method, path):
        def decorator(func):
            method_upper = method.upper()
            
            # Check if path has parameters (contains < >)
            if '<' in path and '>' in path:
                # Convert to regex pattern
                pattern = path
                # Replace <param> with named groups
                pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)
                pattern = '^' + pattern + '$'
                
                if method_upper not in self.pattern_routes:
                    self.pattern_routes[method_upper] = []
                self.pattern_routes[method_upper].append((re.compile(pattern), func))
            else:
                # Exact match route
                self.routes[(method_upper, path)] = func
            
            return func
        return decorator

    def handle_request(self, request):
        method = request['method']
        path = request['path']
        
        # Remove query parameters for routing
        clean_path = path.split('?')[0]
        
        # Try exact match first
        key = (method, clean_path)
        handler = self.routes.get(key)
        if handler:
            return handler(request)
        
        # Handle OPTIONS method for CORS preflight
        if method == 'OPTIONS':
            return build_response(204, 'No Content', '')
        
        # Try pattern matching
        if method in self.pattern_routes:
            for pattern, handler in self.pattern_routes[method]:
                match = pattern.match(clean_path)
                if match:
                    # Add matched parameters to request
                    request['path_params'] = match.groupdict()
                    return handler(request)
        
        return self.response(404, 'Not Found', 'Route not found')

    def response(self, code, message, body):
        return build_response(code, message, body)