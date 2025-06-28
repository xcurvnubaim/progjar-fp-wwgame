from datetime import datetime, UTC

def build_response(status_code=404, status_message='Not Found', body=b'', headers=None):
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

    response_line = f"HTTP/1.1 {status_code} {status_message}\r\n"
    headers_block = ''.join(f"{k}: {v}\r\n" for k, v in headers.items())
    return (response_line + headers_block + "\r\n").encode() + body

if __name__ == "__main__":
    # Example usage
    response = build_response(200, 'OK', 'Hello, World!', {'Content-Type': 'text/plain'})
    print(response.decode('utf-8', errors='replace'))
    # Output: HTTP/1.1 200 OK
    #         Content-Type: text/plain
    #         Content-Length: 13
    #         Connection: close
    #         Date: <current date>
    #         Server: CustomPythonServer/1.0
    #
    #         Hello, World!