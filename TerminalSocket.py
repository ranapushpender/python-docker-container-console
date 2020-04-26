from DockerTerminal import Terminal
import asyncio
import json
import websockets
from threading import Thread

class DockerSocket():
     def __init__(self):
         pass

if __name__ == "__main__":
    async def request_handler(websocket,terminal):
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            print("Message Recv: ")
            print(message)
            response = {}

            if message['type']=="begin":
                print("Connected")
                await terminal.connect(target_host,target_port,message['cid'])
                response = {
                    'type' : "status",
                    'message' : 'connected'
                }  
            elif message['type'] == 'command':
                if terminal == None:
                    response = {'type':'error','message':'Did not connect'}  
                else:
                    terminal.send_command(message['command'])
                    response = {'type':'success','message':""}
            await websocket.send(json.dumps(response))
    
    async def read_output(terminal,websocket):
        ro = terminal.read_output()
        while True:
            if not terminal.is_connected:
                pass
            else:
                try:
                    output = await ro.__anext__()
                    if len(output)>0:
                        print("Output:: "+output)
                        await websocket.send(json.dumps({'type':'success','message':output}))
                except StopIteration:
                    print("Iteration EMpty")
            await asyncio.sleep(0.01)

    async def hello(websocket, path):
        terminal = Terminal()
        task1 = asyncio.create_task(request_handler(websocket,terminal))
        task2 = asyncio.create_task(read_output(terminal,websocket))
        await asyncio.gather(task1,task2)
    
    target_host = "localhost"
    target_port = 8800
    start_server = websockets.serve(hello, "localhost", 8766)
    asyncio.get_event_loop().set_debug(True)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
