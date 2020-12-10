import logging
import asyncio
import sys
import time

from kademlia.network import Server

# if len(sys.argv) != 4:
#     print("Usage: python get.py <bootstrap node> <bootstrap port> <key>")
#     sys.exit(1)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('kademlia')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def run():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    server = Server()
    loop.run_until_complete(server.listen(8469))
    bootstrap_node = ("127.0.0.1", 8468)
    loop.run_until_complete(server.bootstrap(bootstrap_node))
    id = loop.run_until_complete(server.get("File.txt"))
    print(id)
    time.sleep(10)
    print(server.get_results_by_search_ids([id]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


run()
