"""
	* Install socat
	* run command : sudo socat TCP-LISTEN:8800,reuseaddr,fork UNIX-CONNECT:/var/run/docker.sock
	* the above command serves the docker socket on port 8800
	* Use localhost:8800/containers/your_container_id/exec to obtain the id of the exec command
	* Create a tcp socket and connect to your server and port
	* Create a post request with detach:false tty:true as json. Refer to docker engine API for more information
	* Post request must be for /exec/the_id_recieved_from_point_4/start
	* Content-Type Must be application/json
	* Connection: upgrade  - This header should be included as docker upgrades the http connection with the current socket to tcp connection so that stream of data can be exchanged. This can only be done if you pass the upgrade header, you will recieve response 101 with upgraded and response as docker raw stream.
	* Upgrade: tcp - to tell to upgrade to tcp only
	* Content-length - calculate len() of your json data string
	* Make sure if using documenttation quotes that POST word starts from the beginning and not from next line as it would cause invalid request.See ss1 image for referece
	* Write json in single line with single quote enclosing it
	* make sure to add \r\n\r\n after the appending the data and \n\n after content-length to seperate data otherwise will be invalid request
	* Connect the socket client to host and port
	* read the data
	* after read complete and you see terminal's root@sdd# then the connection has been upgraded now you can send recieve data using this socket and execute commands as a simple raw stream.
	* client.sent("command\r\n".encode()) eg:- client.send("ls\r\n".encode())
	* then read again to get output
	* Note :- send commands using send() only after reading the complete response else the webserver will be busy and you won't get your response
	* Convert string to bytes using bytes() class as encoding of "/" will break the code
"""
import socket
import time
import requests
import json
import _thread
from threading import Lock,Thread

class Terminal:
	
	exec_url_prefix = "http://localhost:8800/containers/"
	exec_url_suffix = "/exec"
	headers = {'content-type': 'application/json'}
	payload = {
		"AttachStdin": True,
		"AttachStdout": True,
		"AttachStderr": True,
		"DetachKeys": "ctrl-p,ctrl-q",
		"Tty": True,
		"Cmd": ["bash"],
		"Env": ["FOO=bar","BAZ=quux"]
	}
	
	def __init__(self,host,port,cid=""):
		self.lock = Lock()
		self.buffer = []
		self.target_host = host
		self.target_port = port
		self.cid = cid
		self.get_exec_id(cid)
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Create TCP Socket Connection
		self.client.setblocking(0)
		self.client.settimeout(100)
		self.init_connection()
	
	def get_exec_id(self,cid):
		response = requests.post(Terminal.exec_url_prefix+cid+Terminal.exec_url_suffix,headers=Terminal.headers,data=json.dumps(Terminal.payload))
		self.exec_id = response.json()['Id']
		

	def init_connection(self):
		data = '{"Detach": false, "Tty": true}'
		#Request Header
		header = ( """POST /exec/"""+self.exec_id+"""/start HTTP/1.1
Content-Type: application/json
Host: localhost:8800
Connection: upgrade
Upgrade: tcp
""" )
		content_length = "Content-Length: "+str(len(data))+"\n\n"
		request = header+content_length+data+"\r\n\r\n"
#		print(request)
		self.client.connect((self.target_host,self.target_port))
		self.client.send(request.encode())
		#output = self.read_output().split('\n')
		#print(output[-1])
		
	def send_command(self,command):
		self.client.send(bytes(command+"\r", 'utf-8'))

	def read_output(self):
		data = b''
		while True:
			response = self.client.recv(1)
			data+= response
			self.lock.acquire()
			self.buffer.append(response.decode())
			#print(response.decode('utf-8'),end=" ")
			self.lock.release()
			if data[-2:]==(b'# '):
				#print(data)
				data=b''
				#break
				#pass

	def read_buffer(self):
		self.lock.acquire()
		output = self.buffer
		self.buffer = []
		self.lock.release()
		return output
		
	def close_connection(self):
		self.client.close()
	

if __name__ == "__main__":
	def print_output(args,a):
		while True:
			op = args.read_buffer()
			time.sleep(0.001)
			if(len(op)>0):
				print("".join(op))

	target_host = "localhost"
	target_port = 8800

	terminal = Terminal(target_host,target_port,"183bc47d6823")
	command = ""
	
	t = Thread(target=terminal.read_output,args=tuple())
	
	t2= _thread.start_new_thread(print_output,(terminal,1))
	t.start()
	#t.run()
	while command != "exit":
		command = input("")
		if(command=="exit"):
			break
		terminal.send_command(command)
		#print(terminal.read_output(),end="")
	t.join()
	terminal.close_connection()






    

