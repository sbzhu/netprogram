#!/usr/bin/python
from socket import *

clientSocket = socket(AF_INET, SOCK_STREAM) #tcp

serverName = '10.136.64.114'; serverPort = 6888 
clientSocket.connect((serverName, serverPort))

while True:
	message = raw_input('Input lowercase sentence : ')
	clientSocket.send(message)

	modifiedMessage = clientSocket.recv(1024)
	print modifiedMessage

clientSocket.close()
