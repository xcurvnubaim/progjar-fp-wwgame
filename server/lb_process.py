from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from server.http import HttpServer

class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('127.0.0.1',8000))
		self.servers.append(('127.0.0.1',8001))
		# self.servers.append(('127.0.0.1',8002))
		self.current=0
	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s

def ProcessTheClient(connection,address,backend_sock,mode='toupstream'):
		try:
			while True:
				try:
					if (mode=='toupstream'):
						datafrom_client = connection.recv(32)
						if datafrom_client:
							backend_sock.sendall(datafrom_client)
						else:
							backend_sock.close()
							break
					elif (mode=='toclient'):
						datafrom_backend = backend_sock.recv(32)

						if datafrom_backend:
							connection.sendall(datafrom_backend)
						else:
							connection.close()
							break

				except OSError as e:
					pass
		except Exception as ee:
			logging.warning(f"error {str(ee)}")
		connection.close()
		return

def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	backend = BackendList()

	my_socket.bind(('0.0.0.0', 1337))
	my_socket.listen(1)

	with ProcessPoolExecutor(20) as executor:
		while True:
			connection, client_address = my_socket.accept()
			
			backend_sock = None
			for _ in range(len(backend.servers)):
				backend_address = backend.getserver()
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.settimeout(1)
					sock.connect(backend_address)
					backend_sock = sock
					logging.warning(f"{client_address} connecting to {backend_address}")
					break
				except (ConnectionRefusedError, TimeoutError):
					logging.warning(f"Backend {backend_address} not available, trying next...")
			
			if backend_sock is None:
				logging.error("All backend servers are down")
				connection.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Type: text/plain\r\nAccess-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: *\r\nContent-Length: 15\r\n\r\n502 Bad Gateway")
				connection.close()
				continue

			try:
				#logging.warning("connection from {}".format(client_address))
				toupstream = executor.submit(ProcessTheClient, connection, client_address,backend_sock,'toupstream')
				#the_clients.append(toupstream)
				toclient = executor.submit(ProcessTheClient, connection, client_address,backend_sock,'toclient')
				#the_clients.append(toclient)

				#menampilkan jumlah process yang sedang aktif
				jumlah = ['x' for i in the_clients if i.running()==True]
				#print(jumlah)
			except Exception as err:
				logging.error(err)
				pass
def main():
	Server()

if __name__=="__main__":
	main()