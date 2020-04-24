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
                terminal.connect(target_host,target_port,message['cid'])
                response = {
                    'type' : "status",
                    'message' : 'connected'
                }  
            elif message['type'] == 'command':
                if terminal == None:
                    response = {'type':'error','message':'Did not connect'}  
                else:
                    terminal.send_command(message['command'])
                    #output = terminal.read_output()
                    #print(output)
                    response = {'type':'success','message':""}
            await websocket.send(json.dumps(response))
            await asyncio.sleep(0.01)
    
    async def response_handler(websocket,terminal):
        while True:
            if not terminal.is_connected:
                print("Terminal None")
                pass
            else:
                output = "".join(terminal.read_buffer())
                if len(output)>0:
                    print("Output:: "+output)
                    await websocket.send(json.dumps({'type':'success','message':output}))
            await asyncio.sleep(0.1)
    
    async def read_output(terminal):
        await terminal.read_output()

    async def hello(websocket, path):
        terminal = Terminal()
        task1 = asyncio.create_task(request_handler(websocket,terminal))
        task2 = asyncio.create_task(response_handler(websocket,terminal))
        #thread1 = Thread(target=read_output,args=(terminal))
        #thread1.start()
        task3 = asyncio.create_task(read_output(terminal))
        await asyncio.gather(task1,task2,task3)
        #await asyncio.gather(task1,task2)
    
    target_host = "localhost"
    target_port = 8700
    start_server = websockets.serve(hello, "localhost", 8766)
    asyncio.get_event_loop().set_debug(True)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()