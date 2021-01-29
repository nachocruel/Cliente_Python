import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(('127.0.0.1', 8080))
server.listen(5)

while True:
	conn, addr = server.accept()
	from_client = ''
	print("client: ",addr)
	
	while True:
		data = conn.recv(4096)
		if not data:break
		from_client += data
		print from_client
		
		conn.send("I am the server\n")
		
	conn.close()
	print("Client disconnected")
		
