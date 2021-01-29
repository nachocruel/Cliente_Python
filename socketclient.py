import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## Send some data, this method can be called multiple times
sock.send("Twenty-five bytes to send")

## Receive up to 4096 bytes from a peer
sock.recv(4096)

## Close the socket connection, no more data trasmission
sock.close()




