import sys
import os.path
import uuid
from glob import glob
from datetime import datetime, UTC
import re

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.routes = {}
        self.pattern_routes = {}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'

    def parse_request(self, data):
        try:
            headers, body = data.split('\r\n\r\n', 1)
            lines = headers.split('\r\n')
            method, path, _ = lines[0].split(' ')
            header_dict = {}
            for line in lines[1:]:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    header_dict[key.lower()] = value
            return {
                'method': method,
                'path': path,
                'headers': header_dict,
                'body': body
            }
        except Exception:
            return None

    def response(self, kode=404,message='Not Found',body=bytes(),headers={}):
        if not isinstance(body, bytes):
            body = body.encode('utf-8', errors='replace')

        if headers is None:
            headers = {}

        headers.setdefault('Content-Type', 'text/plain')
        headers['Content-Length'] = str(len(body))
        headers['Connection'] = 'close'
        headers['Date'] = datetime.now(UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers['Server'] = 'WWPythonServer/1.0'

        # Add CORS headers
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers["Access-Control-Allow-Private-Network"] = "true"

        response_line = f"HTTP/1.1 {kode} {message}\r\n"
        headers_block = ''.join(f"{k}: {v}\r\n" for k, v in headers.items())
        return (response_line + headers_block + "\r\n").encode() + body

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

    def proses(self,request):
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
            return self.response(204, 'No Content', '')
        
        # Try pattern matching
        if method in self.pattern_routes:
            for pattern, handler in self.pattern_routes[method]:
                match = pattern.match(clean_path)
                if match:
                    # Add matched parameters to request
                    request['path_params'] = match.groupdict()
                    return handler(request)
        
        return self.response(404, 'Not Found', 'Route not found')
        
    def http_get(self,object_address,headers):
        files = glob('./*')
        #print(files)
        thedir='./'
        if (object_address == '/'):
            return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

        if (object_address == '/video'):
            return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200,'OK','santai saja',dict())


        object_address=object_address[1:]
        if thedir+object_address not in files:
            return self.response(404,'Not Found','',{})
        fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
        #harus membaca dalam bentuk byte dan BINARY
        isi = fp.read()
        
        fext = os.path.splitext(thedir+object_address)[1]
        content_type = self.types[fext]
        
        headers={}
        headers['Content-type']=content_type
		
        return self.response(200,'OK',isi,headers)
    
    def http_post(self,object_address,headers):
        headers ={}
        isi = "kosong"
        return self.response(200,'OK',isi,headers)
        
                
    #>>> import os.path
    #>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
    httpserver = HttpServer()
    d = httpserver.proses('GET testing.txt HTTP/1.0')
    print(d)
    d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
    print(d)
    #d = httpserver.http_get('testing2.txt',{})
    #print(d)
    #	d = httpserver.http_get('testing.txt')
    #	print(d)