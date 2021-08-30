import asyncio
import json
import random

import websockets
import logging

async def status_server(stop_signal: asyncio.Event, message_queue: asyncio.Queue):

    clients = set()

    async def register(websocket, path):
        # Register client
        clients.add(websocket)
        try:
            # Wait forever for messages
            async for message in websocket:
                print(websocket, message)
        finally:
            try:
                clients.remove(websocket)
            except Exception:
                pass

    async with websockets.serve(register, "localhost", 8888):
        while not stop_signal.is_set():
            # TODO: there's a small bug here in that the stop signal is only checked
            #       after a message has been processed
            msg = await message_queue.get()
            for client in clients:
                await client.send(msg)


def get_status():
    return {"money": random.randint(3, 9),
            "liquid": random.randint(0, 100)}


async def main():

    stop_signal = asyncio.Event()
    message_queue = asyncio.Queue()

    ws_server_task = asyncio.create_task(
        status_server(stop_signal, message_queue)
    )

    try:
        while True:
            await asyncio.sleep(1)

            await message_queue.put(json.dumps(get_status()))

    except KeyboardInterrupt:
        stop_signal.set()

        # to return from waiting on the queue in ws_server_task
        message_queue.put(json.dumps(get_status()))

    await ws_server_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())

