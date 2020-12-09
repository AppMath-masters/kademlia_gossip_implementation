import logging
import asyncio
import time

from kademlia.network import Server
import threading
from queue import Queue 

from aiohttp import web
import json

_node_port = 8470
_front_port = 8471

"""
Kademlia logging
"""
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


loop = asyncio.get_event_loop()


"""
Client server
"""
msg_queue = Queue() 

async def handler(request):
    return web.Response(text="Hello, world")


async def client_server(out_q):
    
    app = web.Application()
    app.add_routes([web.get('/', handler)])
    
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=_front_port).start()
    await asyncio.Event().wait()


def run_async_client_server(out_q):
    asyncio.run(client_server(out_q))

threading.Thread(target=run_async_client_server, args = (msg_queue, )).start()


"""
Kademlia server
"""
async def node_server(in_q):
    server = Server()
    loop.set_debug(True)

    await server.listen(_node_port)
    
    while True:
        try:
            data = in_q.get(timeout=2)
            print(data)

        except:
            print("No data")


def run_async_node_server(in_q):
    asyncio.run(node_server(in_q))


threading.Thread(target=run_async_node_server, args = (msg_queue, )).start()


"""
def main_server():
    server = Server()

    loop.set_debug(True)
    loop.run_until_complete(server.listen(8468))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


threading.Thread(target=main_server).start()

time.sleep(5)


async def run_set():
    server = Server()
    await server.listen(8470)
    bootstrap_node = ("127.0.0.1", 8468)
    await server.bootstrap([bootstrap_node])
    await server.set("test_key", "Hello")
    while True:
        pass
    # server.stop()


def run_async_set():
    asyncio.run(run_set())


threading.Thread(target=run_async_set).start()
time.sleep(3)
"""