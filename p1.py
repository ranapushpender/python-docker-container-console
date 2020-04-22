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
"""

import socket
import time

def readOutput(client):
	data = b''
	while True:
		response = client.recv(1)
		print(response[-2:])
		time.sleep(0.1)
		data+= response
		if data[-2:]==(b'# '):
			break
	

#POST Request Host
target_host = "localhost"


#Post request port 
target_port = 8800

#Create TCP Socket Connection
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host

#Parameters for post request of x-www-form-urlenoded
#data = "stream=1&stdout=1&stdin=1" 
data = '{"Detach": false, "Tty": true}'
#data = '{"AttachStdin": true,"AttachStdout": true,"AttachStderr": true,"DetachKeys": "ctrl-p,ctrl-q","Tty": true,"Cmd": ["bash"],"Env": ["FOO=bar","BAZ=quux"]}'

#Request Header
header = ( """POST /exec/0681bfcc4c756df9cc3a29c88a198f0b15bf67e4b3649aac04ff075346266219/start HTTP/1.1
Content-Type: application/json
Host: localhost:8800
Connection: upgrade
Upgrade: tcp
""" )

#Determining content lengtccch from parameter
content_length = "Content-Length: "+str(len(data))+"\n\n"

request = header+content_length+data+"\r\n\r\n"
print(request)

client.connect((target_host,target_port))

client.send(request.encode())
readOutput(client)

print("Response Recieved")

client.send('cd ls\r\n'.encode())
readOutput(client)

print("Ended")


client.close()

    

