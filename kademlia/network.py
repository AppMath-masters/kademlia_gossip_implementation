"""
Package for interacting on the network at a high level.
"""
import random
import pickle
import asyncio
import logging

from kademlia.file_data import FileData
from kademlia.gossip_protocol import GossipProtocol
from kademlia.storage import Storage
from kademlia.utils import digest
from kademlia.node import Node

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


# pylint: disable=too-many-instance-attributes
class Server:
    """
    High level view of a node instance.  This is the object that should be
    created to start listening as an active node on the network.
    """

    protocol_class = GossipProtocol

    def __init__(self, ksize=20, alpha=3, node_id=None, storage=None):
        """
        Create a server instance.  This will start listening on the given port.
        Args:
            ksize (int): The k parameter from the paper
            alpha (int): The alpha parameter from the paper
            node_id: The id for this node on the network.
            storage: An instance that implements the interface
                     :class:`~kademlia.storage.IStorage`
        """
        self.ksize = ksize
        self.alpha = alpha
        self.storage = Storage()
        self.node = Node(node_id or digest(random.getrandbits(255)))
        self.transport = None
        self.protocol = None
        self.refresh_loop = None
        self.save_state_loop = None

    def stop(self):
        if self.transport is not None:
            self.transport.close()

        if self.refresh_loop:
            self.refresh_loop.cancel()

        if self.save_state_loop:
            self.save_state_loop.cancel()

    def _create_protocol(self):
        return self.protocol_class(self.node, self.ksize)

    async def listen(self, port, interface='0.0.0.0'):
        """
        Start listening on the given port.
        Provide interface="::" to accept ipv6 address
        """
        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(self._create_protocol,
                                                                            local_addr=(interface,
                                                                                        port))
        log.info("Node %i listening on %s:%i",
                 self.node.long_id, interface, port)

    def bootstrappable_neighbors(self):
        """
        Get a :class:`list` of (ip, port) :class:`tuple` pairs suitable for
        use as an argument to the bootstrap method.
        The server should have been bootstrapped
        already - this is just a utility for getting some neighbors and then
        storing them if this server is going down for a while.  When it comes
        back up, the list of nodes can be used to bootstrap.
        """
        neighbors = self.protocol.find_neighbors(self.node)
        return [tuple(n)[-2:] for n in neighbors]

    def build_unique_code(self):
        return digest(random.getrandbits(255))

    async def bootstrap(self, address):
        """
        Bootstrap the server by connecting to other known nodes in the network.
        Args:
            addrs: (ip, port) `tuple` pair.  Note that only IP
                   addresses are acceptable - hostnames will cause an error.
        """
        log.debug("Attempting to bootstrap node with %i initial contact",
                  len(address))
        gathered = await self.bootstrap_node(address)
        request_id = self.build_unique_code()
        if gathered is not None:
            await self.protocol.call_connect(address, request_id)

    async def bootstrap_node(self, addr):
        result = await self.protocol.ping(addr, self.node.id)
        return Node(result[1], addr[0], addr[1]) if result[0] else None

    async def get(self, name):
        """
        Get a key if the network has it.
        Returns:
            :class:`None` if not found, the value otherwise.
        """
        log.info("Looking up key %s", name)
        request_id = str(Node(self.build_unique_code()).long_id)
        dkey = digest(name)
        # if this node has it, return it
        if self.storage.find_file(dkey):
            self.protocol.history_of_find_file_request_ids_from_this_node[request_id] = \
                FileData(request_id, name, self.storage.get_path(name))
        else:
            node = Node(dkey)
            closer = self.protocol.find_neighbours_closer_then_me(node)

            if not closer:
                log.warning("There are no known neighbors to get key %s", name)
                return None

            self.protocol.call_find(closer, dkey, request_id)
        return request_id

    def get_results_by_search_ids(self, ids):
        return self.protocol.get_results_by_ids(ids)

    def get_all_files(self):
        return self.storage.get_all()

    def get_all_neighbours(self):
        return self.protocol.neighbours

    async def set(self, name, path):
        """
        Set the given string key to the given value in the network.
        """

        log.info("Saving '%s' on network", name)
        dkey = digest(name)
        value = self.storage.upload(path)
        return await self.set_digest(name, dkey, value)

    async def set_digest(self, name, dkey, value):
        """
        Set the given SHA1 digest key (bytes) to the given value in the
        network.
        """
        node = Node(dkey)

        nearest = self.protocol.find_neighbors(node)
        if not nearest:
            log.warning("There are no known neighbors to set key %s", dkey.hex())
            return False
        neighbors = []
        for n in nearest:
            if n.distance_to(node) <= self.node.distance_to(node):
                neighbors.append(n)

        if len(neighbors) == 0:
            self.storage.download(name, value)
        for n in neighbors:
            await self.protocol.call_store(n, name, dkey, value)

        # return true only if at least one store call succeeded
        # return any(await asyncio.gather(*results))

    def save_state(self, fname):
        """
        Save the state of this node (the alpha/ksize/id/immediate neighbors)
        to a cache file with the given fname.
        """
        log.info("Saving state to %s", fname)
        data = {
            'ksize': self.ksize,
            'alpha': self.alpha,
            'id': self.node.id,
            'neighbors': self.bootstrappable_neighbors()
        }
        if not data['neighbors']:
            log.warning("No known neighbors, so not writing to cache.")
            return
        with open(fname, 'wb') as file:
            pickle.dump(data, file)

    @classmethod
    async def load_state(cls, fname, port, interface='0.0.0.0'):
        """
        Load the state of this node (the alpha/ksize/id/immediate neighbors)
        from a cache file with the given fname and then bootstrap the node
        (using the given port/interface to start listening/bootstrapping).
        """
        log.info("Loading state from %s", fname)
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        svr = Server(data['ksize'], data['alpha'], data['id'])
        await svr.listen(port, interface)
        if data['neighbors']:
            await svr.bootstrap(data['neighbors'])
        return svr

    def save_state_regularly(self, fname, frequency=600):
        """
        Save the state of node with a given regularity to the given
        filename.
        Args:
            fname: File name to save retularly to
            frequency: Frequency in seconds that the state should be saved.
                        By default, 10 minutes.
        """
        self.save_state(fname)
        loop = asyncio.get_event_loop()
        self.save_state_loop = loop.call_later(frequency,
                                               self.save_state_regularly,
                                               fname,
                                               frequency)


def check_dht_value_type(value):
    """
    Checks to see if the type of the value is a valid type for
    placing in the dht.
    """
    typeset = [
        int,
        float,
        bool,
        str,
        bytes
    ]
    return type(value) in typeset  # pylint: disable=unidiomatic-typecheck
