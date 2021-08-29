import asyncio
import websockets

async def handler(websocket, path):
    async for message in websocket:
        print("msg = {}".format(message))
        await websocket.send(str(2).encode())

asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, 'localhost', 8888))

asyncio.get_event_loop().run_forever()