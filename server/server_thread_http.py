from socket import *
import socket
import time
import sys
import logging
import threading
from server.http import HttpServer

class ProcessTheClient(threading.Thread):
    def __init__(self, app : HttpServer, connection, address):
        self.app = app
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            buffer = ""
            while True:
                data = self.connection.recv(1024)
                if not data:
                    break
                buffer += data.decode('utf-8', errors='surrogateescape')
                if '\r\n\r\n' in buffer:
                    request = self.app.parse_request(buffer)
                    if request and 'content-length' in request['headers']:
                        cl = int(request['headers']['content-length'])
                        while len(request['body'].encode()) < cl:
                            data = self.connection.recv(1024)
                            buffer += data.decode('utf-8', errors='surrogateescape')
                            request = self.app.parse_request(buffer)
                    response = self.app.proses(request)
                    self.connection.sendall(response + b"\r\n\r\n")
                    break
        except Exception as e:
            print("Error:", e)
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self, app : HttpServer, port = 8888):
        self.the_clients = []
        self.app = app
        self.port = port
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(1)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}".format(self.client_address))

            clt = ProcessTheClient(self.app, self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    app = HttpServer()
    port = 8888
    svr = Server(app, port)
    svr.start()

if __name__=="__main__":
	main()
