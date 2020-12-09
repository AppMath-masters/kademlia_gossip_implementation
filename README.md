# Kademlia Gossip

The repository contains a modified [implementation of Kademlia](https://github.com/bmuller/kademlia).

The purpose of the modification is to reduce the number of IP-addresses of other nodes known to each node of the system as much as possible. The situation when a large number of third-party nodes become aware of the address of the current node is undesirable. In the original version of Kademlia, it is possible to find out the addresses of a fairly large number of nodes if you have an idea of the list of files stored in the system.

In this modification, the knowledge of a node about the system is limited to no more than *k* (*k > 1*) neighbors. This makes the network more anonymous, but at the same time increases the load on it. This feature introduces changes in the algorithms for processing almost all types of operations in the system.

#### File Search Request
Let's say node *A* wants to receive a file with a known identifier. It sends a find request to all of its neighbors. Further, this request is distributed through the system using the [Gossip protocol](https://en.wikipedia.org/wiki/Gossip_protocol#:~:text=A%20gossip%20protocol%20is%20a,all%20members%20of%20a%20group). The request contains a randomly generated identifier and id of the required file. Each node that receives this request retains information about the node it first received it from. Next, it checks if it stores the requested file.

When a node receives a request to find a file that is stored in it, it sends a response with the same identifier to the node from which the request was received. It ignores further find requests with the same identifier. The node that received the answer retains where the response was received from and redirects it further to the node from which it itself received the find request with this identifier.

Information about the request passed through the node is stored for a certain time *T*.

Thus, a chain from the node that requested the file to the node in which this file is stored is formed, and in this chain, each node knows the IP-addresses of only two of its neighbors.



#### Transferring a file to the requesting node
After receiving confirmation that the file was found, the requesting node sends a request for receiving the file through the chain. So, if the chain is *A-B-C-D*, and A requests a file that is stored in *D*, then *D* will send the file to *C*, after that *C* will send it to *B*, which will send it to *A*. After receiving and sending the file, the node no longer stores information about this request. Node *A* sends requests for confirmation of the status along the chain at regular intervals. The node in the chain that currently has the file returns the response through the chain in the opposite direction. If *A* does not receive a response for a long time, that means that one of the nodes in the chain has been disconnected and the find request should be sent again.

Thus, none of the nodes in the chain knows which node requested the file, and no one knows in which node the file is stored except for itself and its neighbors.

#### Adding a file
When a file is added to the system, the node evaluates the distance to the file ID of its ID and of its neighbors. If there is a neighbor whose identifier is closer to the file identifier than the one of the current node, the file is transferred to that neighbor, then the neighbor repeats this operation. The process is similar to the original Kademlia.

#### Adding a node

To add a new node to the system (let's denote it as *N*), the IP-address of at least one node in the system must be known, let's denote this node *O*. Then the new node sends a special bootstrap request to the *O* node. The request contains the address of the new node, the randomly generated request identifier, and the number of nodes that have processed this request *m*. Initially *m = 0*.

Each time the node *O* receives this request, it performs the following sequence of actions:

If *m* is less than a predetermined maximum value *M*:
- If node *O* has less than *k* neighbors at the time of receiving a request, it asks node *N* for its status. If *N* has not yet been added to the system, the two nodes add each other to their neighbor lists.

- If node *O* has *k* neighbors, it sends this request to its neighbors with *m = m + 1*. Thus, as long as *m* is less than the predefined maximum value of *M*, the request propagates over the network using the Gossip protocol.

If *m = M*:
*O* selects the node *On* from which the request was received and sends a request to that node with the requirement not to change its list of neighbors for some time. After receiving confirmation, *O* asks for status of *N*. If *N* has not yet been added to the system, it sends an affirmative answer. *O* sends a special request to *On*, *O* and *On* break the neighborhood with each other, and each of them adds *N* to the list of neighbors, *N*, in turn, does the same.

Regardless of the answer *N*, the node *O* sends *On* a message that it can change the list of its neighbors.

After being added to the system, a new node asks all of its neighbors for information about the files stored in them and saves it.
