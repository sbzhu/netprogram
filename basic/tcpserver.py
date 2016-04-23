#!/usr/bin/python
from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)

hostName = ''; serverPort = 5888 
serverSocket.bind((hostName, serverPort))

serverSocket.listen(1)

print 'The server is ready to receive'

while(True) : 
	connectionSocket, clientAddress = serverSocket.accept()

	while(True):
		message = connectionSocket.recv(1024)

		modifiedMessage = message.upper() 
		connectionSocket.send(modifiedMessage)

