import protobuf
import socket, threading, select, struct

'''
Chat client
'''
class ChatClient:
	'''
	Initiate client and start two threads, for receiving and sending messages
	
	Input:	
			usr:		string, username
			host:		string, chat server address
			port:		integer, port to listen too, must be same as server
	'''
	def __init__(self, usr, channel, host = "", port = 8942):
		#protocol buffer user
		self.user = protobuf.newUser(usr, channel)

		self.host = host
		self.port = port
		
		#inet streaming socket
		self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.csocket.connect((self.host, self.port))
		
		#let server know who we are
		self.sendDataSet([self.user])
		
		#server aknowledge connection?
		response = self.receiveDataSet(self.csocket)
		response = protobuf.getMsg(response)
		
		if response == "n":
			print "connection refused by server"
			exit()
		
		#thread to handle incoming data
		threading.Thread(target = self.listen).start()
		
		#thread to send data
		threading.Thread(target = self.send).start()

	'''
	handle incoming data from server
	'''
	def listen(self):
		while True:
			#read socket, write socket, exception socket
			rsocket, wsocket, xsocket = select.select([self.csocket], [], [], 0)

			#print incoming messages
			for sock in rsocket:
				msg = self.receiveDataSet(sock)
				msg = protobuf.getMsg(msg)
				print msg
	
	'''
	Enter and send data (messages) to server
	'''
	def send(self):
		while True:
			msg = raw_input()
			msg = protobuf.newMsg(msg)
			self.sendDataSet([msg])

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
	Send data sets to server through socket csocket
	
	a data set consist of two transmissions.
	  - struct, length of message to be sent
	  - string, message
	  
	Input:	
			data:		List of protocol buffer message's to be transmitted
	'''
	def sendDataSet(self, data):
		#send elements in data
		for el in data:
			#serialize to string
			el = el.SerializeToString()

			#send int struct specifying length of message
			self.csocket.send(struct.pack("I", len(el)))
			
			#send message
			self.csocket.send(el)

if __name__ == "__main__":
	usr = raw_input("name: ")
	channel = raw_input("Choose a channel: ")
	ChatClient(usr, channel)
