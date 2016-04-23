#!/usr/bin/python
from socket import * 
import select

serverSocket = socket(AF_INET, SOCK_STREAM)

hostName = ''; serverPort = 6888 
serverSocket.bind((hostName, serverPort))

serverSocket.listen(1)
serverSocket.setblocking(0) # it is neccessary because default is blocking

epoll = select.epoll() # create a epoll object 
# register read event on server socket, a read event will occur any time the server accepts a connection
epoll.register(serverSocket.fileno(), select.EPOLLIN) 

try:
	connectionSockets = {}; requests = {}; responses = {}; # use touple to record each connection's information
	DISCONNECT = '#disconnect'

	while True:
		# Query the epoll object to find out if any events of interst may occurred.
		# the parameter '1' signifies that we are willing to wait up to one second for such event.
		events = epoll.poll(1) # get events list
		for fileno, event in events: # do for each event in the list
			if serverSocket.fileno() == fileno: # read event happened in server, it's a new connection 
				connectionSocket, clientAddress = serverSocket.accept() # create new connection
				connectionSocket.setblocking(0) # set the client connection none-block
				epoll.register(connectionSocket.fileno(), select.EPOLLIN) # register the client connection 

				connectionSockets[connectionSocket.fileno()] = connectionSocket # recored this connection
				requests[connectionSocket.fileno] = ''
				responses[connectionSocket.fileno] = ''

				print 'created connection : %d' % connectionSocket.fileno()

			elif event & select.EPOLLIN: # read event 
				requests[fileno] = connectionSockets[fileno].recv(1024) # read request, 4 Bytes max
				# when connection breaks, a EPOLLIN event will happen, and the read return will be None
				if not requests[fileno]: # received nothing indicates that the connection is broken 
					epoll.modify(fileno, 0) # disable the interest in further read or write events 
					connectionSockets[fileno].shutdown(SHUT_RDWR) # send the FIN to client to ask client to close connection
					continue

				print 'received request from connection %d : %s' % (fileno, requests[fileno])
				# deal with the request, create response 
				responses[fileno] = requests[fileno].upper()

				# with level-triggered epoll, we should manually change the event state, 
				# or it'll continuely trigger event
				epoll.modify(fileno, select.EPOLLOUT) # register it to write event 

			elif event & select.EPOLLOUT: # write event 
				print 'response to connection %d' % (fileno, )

				writeByte = connectionSockets[fileno].send(responses[fileno]) # send the response
				responses[fileno] = responses[fileno][writeByte : ]
				
				if 0 == len(responses[fileno]): # continue send till to the end
					epoll.modify(fileno, select.EPOLLIN) # register in read event again 

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

