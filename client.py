import logging
import asyncio

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
server = Server()

"""
Client server
"""
find_requests = dict()


async def root_handler(request):
    return web.FileResponse('./front_build/index.html')


async def connect_handler(request):
    data = await request.json()
    ip = data['ip']
    port = data['port']
    """
    """
    return web.Response(status=204)


async def search_handler(request):
    data = await request.json()
    name = data['name']
    _id = 1
    """
    """
    return web.Response(headers={'Content-Type': 'application/json'},
                        text=json.dumps({'id': str(_id)}))


async def client_server():
    
    print("Running client on port: " + str(_front_port))
    app = web.Application()
    app.add_routes([web.get('/', root_handler),
                    web.post('/connect', connect_handler),
                    web.post('/search', search_handler)])
    
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=_front_port).start()
    await asyncio.Event().wait()


def run_async_client_server():
    asyncio.run(client_server())


threading.Thread(target=run_async_client_server).start()


"""
Kademlia server
"""
async def node_server():
    loop.set_debug(True)

    await server.listen(_node_port)
    
    while True:
        pass

def run_async_node_server():
    asyncio.run(node_server())


threading.Thread(target=run_async_node_server).start()
