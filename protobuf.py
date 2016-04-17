import chat_pb2

'''
create a protocol buffer user object

Input:	string username
		channel to join
output:	protocol buffer object
'''
def newUser(nick, channel):
	usr = chat_pb2.join()
	usr.nick = nick
	usr.channel = channel
	return usr

'''
create a protocol buffer message object

Input:	string message
output:	protocol buffer object
'''
def newMsg(txt):
	msg = chat_pb2.message()
	msg.text = txt
	return msg

'''
get protocol buffer message object from serialized message

Input:	string serialized protobuf message object
output:	protocol buffer message object
'''
def getMsg(serialized):
	msg = chat_pb2.message()
	msg.ParseFromString(serialized)
	return msg

'''
get protocol buffer user object from serialized user

Input:	string serialized protobuf user object
output:	protocol buffer user object
'''
def getUsr(serialized):
	usr = chat_pb2.join()
	usr.ParseFromString(serialized)
	return usr
