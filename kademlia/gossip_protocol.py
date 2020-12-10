import logging

from rpcudp.protocol import RPCProtocol

from kademlia.file_data import FileData
from kademlia.node import Node
from kademlia.storage import Storage
import random

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class GossipProtocol(RPCProtocol):
    def __init__(self, source_node, ksize):
        RPCProtocol.__init__(self)
        self.neighbours = dict()
        self.source_node = source_node
        self.k = 10
        self.M = 3
        self.storage = Storage()
        self.history_of_request_ids = set()
        self.file_transfer_request_ids = set()
        self.history_of_find_file_request_ids = dict()
        self.history_of_find_file_request_ids_from_this_node = dict()

    async def call_connect(self, address, request_id):
        await self.connect(address, self.source_node.id,
                           self.source_node.id, request_id, 0)

    def accept_connection(self, node_id, node_address):
        log.debug("Accept connection from node %s with id %s", str(node_address), str(node_id))
        source = Node(node_id, node_address[0], node_address[1])
        self.welcome_if_new(source)
        self.neighbours[node_id] = Node(node_id, node_address[0], node_address[1])
        self.connection_accepted(node_address, self.source_node.id)

    def rpc_connection_accepted(self, source, source_id):
        log.debug("Node %s connected with id %s", str(source), str(source_id))
        if len(self.neighbours.keys()) < self.k:
            self.neighbours[source_id] = Node(source_id, source[0], source[1])

    def remove_any_neighbour(self, sender_id):
        if self.neighbours.get(sender_id, None) is not None:
            self.neighbours.pop(sender_id, None)
        else:
            self.neighbours.pop(random.choice(self.neighbours.keys()))

    def rpc_connect(self, sender, sender_id,
                    node_id, request_id, m, node_address=None):  # pylint: disable=no-self-use
        if node_address is None:
            node_address = sender

        if self.neighbours.get(node_id, None) is not None:
            self.accept_connection(node_id, node_address)
        elif not self.history_of_request_ids.__contains__(request_id):
            if len(self.neighbours.keys()) < self.k:
                self.accept_connection(node_id, node_address)
            else:
                if m == self.M:
                    self.remove_any_neighbour(sender_id)
                    self.accept_connection(node_id, node_address)
                else:
                    m += 1
                    neigbours_found = False
                    for key in self.neighbours.keys():
                        neigbour = self.neighbours[key]
                        if neigbour.id != sender_id:
                            neigbours_found = True
                            self.connect((neigbour.ip, neigbour.port),
                                         self.source_node.id, node_id, request_id, m, node_address)
                    if not neigbours_found:
                        self.remove_any_neighbour(sender_id)
                        self.accept_connection(node_id, node_address)

        else:
            self.accept_connection(node_id, node_address)
        self.history_of_request_ids.add(request_id)

        return sender

    def rpc_stun(self, sender):  # pylint: disable=no-self-use
        return sender

    def rpc_ping(self, sender, nodeid):
        print(self.source_node.id)
        return self.source_node.id

    def get_results_by_ids(self, ids):
        result = []
        for id in ids:
            result.append(self.history_of_find_file_request_ids_from_this_node[id])
        return result

    def rpc_store(self, sender, nodeid, name, key, value):
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        log.debug("got a store request from %s, storing '%s'='%s'",
                  sender, key.hex(), value)
        nearest = self.find_neighbors(source)
        if not nearest:
            log.warning("There are no known neighbors to set key %s", key.hex())
            self.storage.download(name,value)
            return False
        neighbors = []
        for n in nearest:
            if n.distance_to(source)<=self.source_node.distance_to(source):
                neighbors.append(n)
        if len(neighbors)==0:
            self.storage.download(name,value)
            return False
        else:
            for n in neighbors:
                self.store(n,name,key,value)
        return True

    def rpc_find_node(self, sender, nodeid, key):
        log.info("finding neighbors of %i in local table",
                 int(nodeid.hex(), 16))
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        node = Node(key)
        neighbors = self.router.find_neighbors(node, exclude=source)
        return list(map(tuple, neighbors))

    async def call_ping(self, node_to_ask):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.ping(address, self.source_node.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_store(self, node_to_ask, name, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.store(address, self.source_node.id, name, key, value)
        # return self.handle_call_response(result, node_to_ask)

    def rpc_accept_file(self, sender, file_content, file_name, request_id):
        if not self.file_transfer_request_ids.__contains__(request_id):
            self.file_transfer_request_ids.add(request_id)
            requester = self.history_of_find_file_request_ids.get(request_id, None)
            if requester is not None:
                self.accept_file(requester, file_content, file_name, request_id)
            else:
                path = self.storage.download(file_name, file_content)
                self.history_of_find_file_request_ids_from_this_node[request_id] \
                    = FileData(request_id, file_name, path)

    def send_file_to_requester(self, request_id, file_content, address):
        self.accept_file(address, file_content, request_id)

    def rpc_find(self, sender, key, request_id):
        if not self.history_of_request_ids.__contains__(request_id):
            self.history_of_find_file_request_ids[request_id] = sender
            if self.storage.find_file(key):
                file_content = self.storage.upload(key)
                self.send_file_to_requester(request_id, file_content=file_content, address=sender)
            else:
                closer = self.find_neighbours_closer_then_me(Node(key), Node(sender))
                for node in closer:
                    self.find((node.ip, node.port), key, request_id)

    async def call_find(self, closer_nodes, key, request_id):
        self.history_of_find_file_request_ids_from_this_node[request_id] = None
        for node in closer_nodes:
            self.find((node.ip, node.port), key, request_id)

    def _is_new_node(self, node):
        return self.neighbours.get(node.id, None) is not None

    def find_neighbors(self, node, exclude=None):
        nodes = []
        for neighbour in self.neighbours.values():
            notexcluded = exclude is None or not neighbour.same_home_as(exclude)
            if neighbour.id != node.id and notexcluded:
                nodes.append((node.distance_to(neighbour), neighbour))
        return list(map(lambda x: x[1], sorted(nodes)))

    def find_neighbours_closer_then_me(self, node, exclude=None):
        neighbours = self.find_neighbors(node, exclude)
        my_distance = node.distance_to(self.source_node)
        closer = []
        for neighbour in neighbours:
            if neighbour.distance_to(node) < my_distance:
                closer.append(neighbour)
        return closer

    def add_contact(self, node):
        self.neighbours[node.id] = node

    def is_new_node(self, node):
        return self.neighbours.get(node.id, None) is None

    def welcome_if_new(self, node):
        """
        Given a new node, send it all the keys/values it should be storing,
        then add it to the routing table.

        @param node: A new node that just joined (or that we just found out
        about).

        Process:
        For each key in storage, get k closest nodes.  If newnode is closer
        than the furtherst in that list, and the node for this server
        is closer than the closest in that list, then store the key/value
        on the new node (per section 2.5 of the paper)
        """
        if not self.is_new_node(node):
            return

        log.info("never seen %s before. Check if I should at it to neighbours", node)
        if len(self.neighbours.keys()) < self.k:
            self.neighbours[node.id] = node

        # TODO(Implement when storage is ready)
        # for key, value in self.storage:
        #     keynode = Node(digest(key))
        #     neighbors = self.find_neighbors(keynode)
        #     if neighbors:
        #         last = neighbors[-1].distance_to(keynode)
        #         new_node_close = node.distance_to(keynode) < last
        #         first = neighbors[0].distance_to(keynode)
        #         this_closest = self.source_node.distance_to(keynode) < first
        #     if not neighbors or (new_node_close and this_closest):
        #         asyncio.ensure_future(self.call_store(node, key, value))
        self.add_contact(node)

    def handle_call_response(self, result, node):
        """
        If we get a response, add the node to the routing table.  If
        we get no response, make sure it's removed from the routing table.
        """
        if not result[0]:
            log.warning("no response from %s, removing from router", node)
            self.router.remove_contact(node)
            return result

        log.info("got successful response from %s", node)
        self.welcome_if_new(node)
        return result
