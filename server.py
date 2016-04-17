import protobuf
import select, socket, struct

class ChatServer:
	def __init__(self, host = "", port = 8942):
		self.port = port
		self.host = host
		
		#inet streaming server socket
		self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#bind to host and port
		self.ssocket.bind((self.host, self.port))
		#allow to que up to 5 connection requests
		self.ssocket.listen(5)

		#list to store connected sockets
		self.connections = [self.ssocket]
		
		#dictionary to store basic data on connected peers
		self.peers = {}
		
		self.startServer()
		
	'''
	run server
	'''
	def startServer(self):
		print "server started on port %i" %self.port
		while True:
			#read socket, write socket, exception socket
			rsocket, wsocket, xsocket = select.select(self.connections, [], [], 0)
			
			for sock in rsocket:
				#new connection request
				if sock == self.ssocket:
					self.newConnection(sock)

				else:
					#data received
					try:
						self.dataReceived(sock)

					#disconnected user
					except struct.error:
						self.closeConnection(sock)

	'''
	process a connection request
	'''
	def newConnection(self, sock):
		#accept connection
		connsocket, address = sock.accept()
		
		#let the client identify itself
		user = self.receiveDataSet(connsocket)
		user = protobuf.getUsr(user)
		
		#if username is already taken
		if user.nick in [usr.nick for usr in self.peers.values()]:
			#connection denied
			self.sendDataSet(connsocket, [protobuf.newMsg("n")])
			
			#close connection
			connsocket.shutdown(socket.SHUT_RDWR)
			connsocket.close()
			return
		
		#connection confirmed
		self.sendDataSet(connsocket, [protobuf.newMsg("y")])

		#store connected client in connections
		self.connections.append(connsocket)
		
		#dictionary with some info on the users
		self.peers[connsocket] = user
		
		#notify peers
		print address[0] + " connected"
		self.transmit(user.channel, protobuf.newMsg("server > " + user.nick + " (" + address[0] + ") joined the chat"))

	'''
	close and remove a disconnected socket
	'''
	def closeConnection(self, sock):
		#remove from list of connected sockets
		self.connections.remove(sock)

		#notify peers
		print sock.getsockname()[0] + " disconnected"
		self.transmit(self.peers[sock].channel, protobuf.newMsg("server > " + self.peers[sock].nick + " (" + sock.getsockname()[0] + ") left the chat"))
		
		#remove from dict of users
		del self.peers[sock]
		
		#ensure socket gets closed
		sock.close()

	'''
	Read a incoming transmision and send it to all connected sockets on same channel
	'''
	def dataReceived(self, sock):
		#receive data
		msg = self.receiveDataSet(sock)
		msg = protobuf.getMsg(msg)
		
		#send data to peers in same channel
		if msg != "":
			msg = self.peers[sock].nick + " > " + msg.text
			self.transmit(self.peers[sock].channel, protobuf.newMsg(msg))
	
	'''
	Receive a data set from server
	
	a data set consist of two transmissions.
	  - struct, length of message to be sent
	  - string, message
	  
	Input: 	
			sock:		socket to receive from
	Return: 			protocol buffer message
	'''
	def receiveDataSet(self, sock):
		#receive a int struct specifying length of message
		length = sock.recv(4)
		length = struct.unpack("I", length)[0]
		
		#receive message
		data = sock.recv(length)
		return data
	
	'''
	Send data sets to client
	
	a data set consist of two transmissions.
	  - struct, length of message to be sent
	  - string, message
	  
	Input:	
			sock:		socket to transmit on
			data:		List of protocol buffer message's to be transmitted
	'''
	def sendDataSet(self, sock, data):
		#send elements in data to socket
		for el in data:
			#serialize to string
			el = el.SerializeToString()
	
			#send int struct specifying length of message
			sock.send(struct.pack("I", len(el)))
			
			#send message
			sock.send(el)
	
	'''
	Transmit a message to all connected user on a channel
	
	input:
			channel:	channel to send on
			msg			protocol buffer message to send
	'''
	def transmit(self, channel, msg):
		for sock in self.connections:
			if sock != self.ssocket and self.peers[sock].channel == channel:
				self.sendDataSet(sock, [msg])

if __name__ == "__main__":
	ChatServer()
