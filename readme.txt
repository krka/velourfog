Technical documentation
=======================
Velour Fog is a distributed key value storage designed for usage in a private
intranet.

Here are some parameters that need to be considered when implementing such a
thing.

* Security is not important at all since all clients and the servers in
Velour Fog can be trusted - only access from within the same network should be
allowed.

* Performance - very important.
* Scalability - very important.
* Robustness - very important.
* Availability - very important.
* Avoiding stale data - important. It's impossible to avoid possibly sending
stale data if scalability and availability are prioritized, but it's still
important to try to reduce the propagation time of new key/value pairs as much
as possible.

Strategies
==========

Partitioning
-----------
Some scalability can be gained by partitioning keys to different and independent
sets of clusters. This assumes that clients will get and set a lot of different
keys. If the clients were to mainly query a limited set of keys,
then partitioning wouldn't help scalability much.

A good way of doing this would be to keep a set of completely stateless frontend
servers, who only accepted requests and determined the partition by applying a
cryptographically nice hash algorithm (such as SHA-1). You would then calculate
the hash value mod N, where N is the number of partitions, and then forward the
query to a random node in that cluster. (Either with a manual selection of
node or by using a load balancer.)

For simplicity, I let the number of partitions be on the form 2**(4*N) where N
is an integer >= 1. This reduces the mod-operation on the key hash to picking
the last N hexdigits of the hash. (In the implementation, it actually takes
the first N hexdigits, but it doesn't really matter anyway.)

A nice property of this setup is that frontend nodes can be added and removed
at any time, and since they're stateless it's easy to scale by simply adding
more of them.

Redundancy
----------
I chose to store each key-value pair on K nodes, where K is configurable.
This means that a frontend that gets a get-request can randomly pick one of K
nodes to ask for the value. However, for a set-request the frontend-node needs
to notify all K nodes of the new value.
This is useful for several reasons. First of all it increases the scalability
if the traffic pattern has more get-requests than set-requests. If
set-requests are numerous enough, K could be lowered for better performance.
If backup and recovery strategies had been implemented, keeping K atleast at
2 or 3 would keep the system more robust.


Persistant storage
------------------
It's possibly unnecessary to implement disk based storage of keys and values
at all, as long as all new nodes in the cluster would gather all existing data
from the currently live nodes.

Versioning
----------
It's possible that two different nodes try to set the same key to different
values, so some sort of versioning is needed to ensure that all nodes eventually
have the same value for the same key.

A simple solution is to use a timestamp as version number. The server machines
could just run ntp clients regularly to keep them somewhat in sync.
It's not critical to ensure that the true latest version will win in an
extremely tight race condition, but it's critical that all nodes agree on which
version is the latest. Should two updates have the same timestamp, then any
disagreement would be solved by inspecting the value itself. (A simple
lexicographical string comparison.)

Iterations
==========
* Iteration 1 is implemented as an in memory python dictionary without any
clustering or persistance.
* Iteration 2: Make a layered solution with stateless frontends that
sends get-requests to only one storage node, and sends set-requests to all
storage nodes. Use a controller that notifies frontends when storage nodes are
added.
* Iteration 3: Implement the partitioning strategy.

Future iterations
-----------------
* Iteration 4: Let frontends notify controller of dead storage nodes, and remove them.
* Iteration 5: Let newly added storage nodes be able to query for the complete state
before accepting external requests.
* Iteration 6: Let the controller persist its state to disk to survive shutdowns.
* Iteration 7: Persist storage data to disk for robustness.
* Iteration 8: Let frontend nodes function more event driven to increase throughput.
 
Usage
=====

Starting the cluster
--------------------
python server.py [port] <otherhost:port>
The server will listen for requests on the given port.
If there's another known node online, you can add it on the commandline to
start clustering with it.

Stopping the server
-------------------
Send a regular kill signal to all processes related to the cluster.

Retrieve value for a key
------------------------
Send a GET request to the server with the key as the url.
Example using curl: curl localhost:8000/get/?key=KEY

Return code 200 signifies that the key existed.
The value follows in the data.

Return code 204 signifies that the key did not exist.
No data follows.

Set value for a key
-------------------
Send a POST request to the server with the key as the url,
and the value as the data
Example using curl: curl -d VALUE localhost:8000/KEY



Overall structure
=================

Client get     Client set      Client get
  |               |               |
Frontend 1     Frontend 2      Frontend 3             Controller
  |          /    |    \          |                   (connects to all frontends and all nodes)
Node 1         Node 2          Node 3

Clients only communicate with frontends,
and do so by sending get- / set-requests.

If it's a get-request, the frontend node
finds an appropriate storage node (randomly)
and forwards the request, and returns the answer.

If it's a set-request, the frontend node 
adds a timestamp to the request and forwards
it to all nodes (within the same partition (when that's implemented)).

All frontends and nodes also report to a controller,
which keeps tracks of available nodes and notifies frontends
when a new node becomes available.

Note that this means that the system scales poorly if the traffic pattern is
multiple set-requests for keys within a single partition, but it
scales good if most of the traffic is get-requests.

