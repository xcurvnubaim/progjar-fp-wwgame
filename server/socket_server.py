from socket import socket, SOL_SOCKET, SO_REUSEADDR, AF_INET, SOCK_STREAM
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from server.request import parse_request
from server.core import App

class HttpSocketServer:
    def __init__(self, app : App, host='0.0.0.0', port=8888, workers=5, executor='thread'):
        self.app = app
        self.host = host
        self.port = port
        self.workers = workers
        self.executor = executor

    def start(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print(f"HTTP server listening at http://{self.host}:{self.port}")

        if self.executor == 'process':
            with ProcessPoolExecutor(max_workers=self.workers) as executor:
                while True:
                    conn, addr = sock.accept()
                    executor.submit(self.handle_client, conn, addr)
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                while True:
                    conn, addr = sock.accept()
                    executor.submit(self.handle_client, conn, addr)

    def handle_client(self, conn, addr):
        try:
            buffer = ""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode('utf-8', errors='surrogateescape')
                if '\r\n\r\n' in buffer:
                    request = parse_request(buffer)
                    if request and 'content-length' in request['headers']:
                        cl = int(request['headers']['content-length'])
                        while len(request['body'].encode()) < cl:
                            data = conn.recv(1024)
                            buffer += data.decode('utf-8', errors='surrogateescape')
                            request = parse_request(buffer)
                    response = self.app.handle_request(request)
                    conn.sendall(response + b"\r\n\r\n")
                    break
        except Exception as e:
            print("Error:", e)
        finally:
            conn.close()
