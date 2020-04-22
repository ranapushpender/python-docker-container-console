from DockerTerminal import Terminal
import asyncio
import json
import websockets

class DockerSocket():
     def __init__(self):
         pass

if __name__ == "__main__":
    target_host = "localhost"
    target_port = 8800
    terminal = None

    async def hello(websocket, path):
        message = await websocket.recv()
        message = json.loads(message)
        print("Message Recv: ",end="")
        print(message)
        response = {}

        if message['type']=="begin":
            terminal = Terminal(target_host,target_port,message['cid'])
            response = {
                'type' : "status",
                'message' : 'connected'
            }  
        elif message['type'] == 'command':
            if terminal == None:
                message = {'type':'error','message':'Did not connect'}  
            else:
                terminal.send_command(message['command'])
                output = terminal.read_output()
                print(output)
                response = {'type':'success','message':output}
        await websocket.send(json.dumps(response))

    start_server = websockets.serve(hello, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()