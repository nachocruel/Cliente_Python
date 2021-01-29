
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
 client.connect(("127.0.0.1", 8080))
except:
	print("The server is not connected")
	

client.send("I am the client")

from_server = client.recv(4096)

client.close()

print from_server
