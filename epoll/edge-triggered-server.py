#!/usr/bin/python
from socket import * 
import select
import sys 

# note : the #### is the difference from level-edge triggered
serverSocket = socket(AF_INET, SOCK_STREAM)

hostName = ''; serverPort = 6888 
serverSocket.bind((hostName, serverPort))

serverSocket.listen(1)
serverSocket.setblocking(0) # it is neccessary because default is blocking

epoll = select.epoll() # create a epoll object 
# register read event on server socket, a read event will occur any time the server accepts a connection
#### 1. add EPOLLET mast to set edge-triggered
epoll.register(serverSocket.fileno(), select.EPOLLIN | select.EPOLLET) 

try:
	connectionSockets = {}; requests = {}; responses = {}; # use touple to record each connection's information
	DISCONNECT = '#disconnect'

	while True:
		# Query the epoll object to find out if any events of interst may occurred.
		# the parameter '1' signifies that we are willing to wait up to one second for such event.
		events = epoll.poll(1)
		for fileno, event in events:
			if serverSocket.fileno() == fileno: # read event happened in server, it's a new connection 
				#### 2. add a loop that run until an exception occurs (or data is known to be handled)
				try:
					while True:
						connectionSocket, clientAddress = serverSocket.accept() # create new connection
						connectionSocket.setblocking(0) # set the client connection none-block 
						#### 1. add EPOLLET mast to set edge-triggered
						epoll.register(connectionSocket.fileno(), select.EPOLLIN | select.EPOLLET) # register the client connection 

						connectionSockets[connectionSocket.fileno()] = connectionSocket # recored this connection
						requests[connectionSocket.fileno] = ''
						responses[connectionSocket.fileno] = ''

				except error:
					pass

					print 'created connection : %d' % connectionSocket.fileno()

			elif event & select.EPOLLIN: # read event 
				#### 2. add a loop that run until an exception occurs (or data is known to be handled)
				try:
					while True:
						requests[fileno] = connectionSockets[fileno].recv(1024) # read request, 4 Bytes max
						if not requests[fileno]: # the connection is broken
							break
				except error:
					pass

				if not requests[fileno]: # the client is disconnected
					epoll.modify(fileno, 0) # disable the interest in further read or write events 
					connectionSockets[fileno].shutdown(SHUT_RDWR) # send the FIN to client to ask client to close connection
					continue

				print 'received request from connection %d : %s' % (fileno, requests[fileno])
				# deal with the request, create response 
				responses[fileno] = requests[fileno].upper()

				#### 1. add EPOLLET mast to set edge-triggered
				epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET) # register it to write event 

			elif event & select.EPOLLOUT: # write event 
				print 'response to connection %d' % (fileno, )

				#### 2. add a loop that run until an exception occurs (or data is known to be handled)
				try:
					while responses[fileno]: #### note here : until the response sent over
						writeByte = connectionSockets[fileno].send(responses[fileno]) # send the response
						responses[fileno] = responses[fileno][writeByte : ]
				except error:
					pass
				
				if 0 == len(responses[fileno]): # continue send till to the end 
					#### 1. add EPOLLET mast to set edge-triggered
					epoll.modify(fileno, select.EPOLLIN | select.EPOLLET) # register in read event again 

			elif event & select.EPOLLHUP: # if client send FIN, a 'hung-up' event will trigger
				epoll.unregister(fileno)
				connectionSockets[fileno].close()
				del connectionSockets[fileno]; del requests[fileno]; del responses[fileno];

				print 'disconnect : %d' % fileno 

finally: # the program will likely be interrupted by a KeyboardInterrupt exception
	# unregister server socket's event and close it 
	epoll.unregister(serverSocket.fileno())
	serverSocket.close() 

	epoll.close()

