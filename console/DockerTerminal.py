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
import asyncio

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
	
	async def connect(self,host,port,cid=""):
		
		self.target_host = host
		self.target_port = port
		self.cid = cid
		self.client = None
		
		print("Opening a connection")
		#Opening tcp connection via asyncio
		self.reader,self.writer = await asyncio.open_unix_connection('/var/run/docker.sock')
		print("Connected")

		#Getting exe id for terminal session
		print("Getting exec id")
		await self.get_exec_id(cid)
		print("Got it")

		#Upgrading the connection to TCP
		await self.init_connection()

	def __init__(self):
		self.lock = Lock()
		self.buffer = []
		self.is_connected = False
		pass
	
	async def get_exec_id(self,cid):
		#response = requests.post(Terminal.exec_url_prefix+cid+Terminal.exec_url_suffix,headers=Terminal.headers,data=json.dumps(Terminal.payload))
		header = ( 
				   "POST /containers/"+self.cid+"/exec HTTP/1.1\n"+
				   "Content-Type: application/json\n"+
				   "Host: localhost:8800\n"+
				   "Content-Length: "+str(len(json.dumps(self.payload)))+"\n\n"
				 )
		request = header + json.dumps(self.payload) + "\r\n\r\n"
		self.writer.write(request.encode())
		await self.writer.drain()
		
		response = b''
		while True:
			data = await self.reader.read(1)
			response = response + data
			if response[-4:] == b'\r\n\r\n':
				print("End reached")
				break
		response = response.split(b'\r\n')
		#print(response)
		for element in response:
			if 'Content-Length' in  element.decode():
				length  = element.decode().split(':')[1]
				break
		id = await self.reader.read(int(length))
		self.exec_id = json.loads(id.decode())["Id"]
		print(self.exec_id)

	"""
		This function upgrades the current connection with the socket to tcp with docker engine
	"""
	async def init_connection(self):
		data = '{"Detach": false, "Tty": true}'

		header = ( 
				   "POST /exec/"+self.exec_id+"/start HTTP/1.1\n"+
				   "Content-Type: application/json\n"+
				   "Host: localhost:8800\n"+
				   "Connection: upgrade\n"+
			       "Upgrade: tcp\n"
				 )

		content_length = "Content-Length: "+str(len(data))+"\n\n"
		request = header+content_length+data+"\r\n\r\n"

		"""
			Writing our request Detach false means starting interactive session. This upgrades connection to TCP(Can see from response header).
			Tty = true means we want raw strem of bytes from and to the container's session
			Tty = false would mean data will be send in format specified by docker api engine attach command docs
		"""
		self.writer.write(request.encode())
		await self.writer.drain()
		self.is_connected = True
	
	def get_command_code(self,command):	
		"""
			Special key code definitions
		"""
		KEY_UP = b'\x1b[A'
		KEY_DOWN = b'\x1b[B'
		KEY_RIGHT = b'\x1b[C'
		KEY_LEFT = b'\x1b[D'
		
		"""
			If else ladder to send keycode or the command itself
		"""
		if command == "ArrowUp":
			return KEY_UP
		elif command == "ArrowDown":
			return KEY_DOWN
		elif command == "ArrowLeft":
			return KEY_LEFT
		elif command == "ArrowRight":
			return KEY_RIGHT
		else:
			return bytes(command, 'utf-8')
		
	def send_command(self,command):
		self.writer.write(self.get_command_code(command))
		self.writer.drain()

	async def read_output(self):
		while True:
			if self.is_connected:
				try:
					response = await self.reader.read(4096)
					yield response.decode()
				except socket.error:
					print("\n\nSocket Error")
			else:
				pass
		
	def close_connection(self):
		self.client.close()
	

if __name__ == "__main__":
	target_host = "localhost"
	target_port = 8800
	terminal = Terminal()
	#terminal.connect(target_host,target_port,"183bc47d6823")
	command = ""

	loop = asyncio.get_event_loop()
	task = loop.create_task(terminal.connect(target_host,target_port,"183bc47d6823"))
	loop.run_until_complete(task)
	






    

