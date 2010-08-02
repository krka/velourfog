Dependencies
============
Required:
* python 2.6 - it could possibly work with newer python version,
               but that is untested
* bash       - to run the example start script.
Optional:
* curl / webbrowser - to test the system.

Overview
========
Velour Fog is named after Zapp Brannigan, the greatest starship captain of all
time. Also, in this day in age, where cloud computing is a buzzword, "fog"
seemed a relevant choice of words.

The system consists of three distinct types of nodes, which together form a
usable distributed key-value storage: controller, frontend and storage.

Each system needs exactly one controller node running.
(This could be changed in the future, but the development started with the
simplest possible solution first.)
The controller is responsible for notifying the other nodes of each others
existance. The storage is extremely simple, it doesn't know about any other node
apart from the controller, and it only handles get/set-requests by using its own
internal dictionary. Frontend nodes handle all the incoming requests and forward
to appropriate storage nodes. The frontend nodes themselves are stateless.
See more details further down.

There are no permanent connections in the system, just a bunch of one off http-
queries, so you could technically
disconnect and reconnect nodes for short times, assuming that no one else
tries to communicate with them during that time, but the node states might get
messed up. Controllers would lose information about which nodes are currently
running and storage nodes would lose all the key-value pairs. Frontend nodes
are stateless and would be safe to reconnect.

In conclusion, for this limited key-value storage, don't shutdown it partially,
it won't cope very well.

Usage
=====
For a simple example of how to use it, see the runlocal.sh script.
It runs a fully clustered solution, but running on a single machine.
This is useful for testing purposes.

It should be straightforward to adapt the script to run nodes on multiple
machines.

Startup
-------
The three types of services in the system are run like this:

python controller.py <CONTROLLER_PORT> <NUM_STORAGE> <REDUNDANCY>
python storagenode.py <CONTROLLER_HOST:CONTROLLER_PORT> <OWN_HOST:OWN_PORT>
python frontend.py <CONTROLLER_HOST:CONTROLLER_PORT> <OWN_HOST:OWN_PORT>

All hosts and ports should be on the form such that all nodes in the system can
reach each other. I.e. localhost or incorrect subnets are a bad idea.
* CONTROLLER_HOST and CONTROLLER_PORT should point to the single controller node
* OWN_HOST and OWN_PORT should point to the node itself
  (and reachable from the other nodes)
* NUM_STORAGE is the number of storage nodes that's expected to run in the
system. This is important to know in advance with the current design (no dynamic
adding / removing of nodes), to calculate the number of partitions.
* REDUNDANCY is the number of distinct nodes that should store each key-value
pair. High numbers increase throughput for get-requests on a key, but lower the
throughput for set-requests.

Shutdown
--------
Simply send a sigterm to all python processes.
If you use the runlocal.sh script (or a modified version), it's enough to simply
kill that process, which will kill the rest automatically.


Querying
--------
As an end user, you only need to connect to frontend nodes. (You can pick any
frontend node, they are all created equal.)

Get request:
curl <host:port>/get/?key=KEY

Set request:
curl <host:port>/set/?key=KEY[&value=VALUE]

The value is optional as a GET-parameter - you could also provide it in the
POST-data.

The http return codes are 200 on success and 501 for incorrect usage.

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

Not yet implemented
-------------------
* Iteration 4: Let frontends notify controller of dead storage nodes, and remove them.
* Iteration 5: Let newly added storage nodes be able to query for the complete state
before accepting external requests.
* Iteration 6: Let the controller persist its state to disk to survive shutdowns.
* Iteration 7: Persist storage data to disk for robustness.
* Iteration 8: Let frontend nodes function more event driven to increase throughput.
 
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

Limitations
===========

Input / Output:
* Keys may not contain any weird characters (less than ascii 32) or any of
the following characters: "&", "=", "?". This also applies to values if they
are supplied as GET-parameters instead of POST-data.

Error tolerance:
* Not much tolerance of any kind for network problems or nodes coming up / down.
It's also sensitive to timeouts.

Scalability limitations of the system:
* The system does not support adding and removing nodes when running.

Robustness limitations of the system:
* The system does not remember any state when shutdown.
* The system does not guarantee synchronized state across nodes if one or more
nodes is temporarily unavailable to other nodes.

Correctness limitations of the system:
* After a set operation has finished, i.e. the set-request to a frontend node
has finished, you're guaranteed that a new get-request for the same key would
result in the new value or an even newer value.
* All frontend nodes must run with their system time in sync, for instance by
running ntp-clients continously. Assuming that the largest difference in time
between any two frontend nodes is E seconds,
then any set-request executed at least E seconds after the previous set-request
is guaranteed to succeed. With good ntp clients installed, E should in practice
be below 100 ms.

Scalability
===========

Traffic scaling
---------------
The scaling of the system depends on several things:

1) There is only one controller node, which would make it a bottleneck if there
were a lot of nodes added or removed in runtime. However, the current solution
does not handle that at all, so the controller is not a scalability problem.

2) The frontend nodes are completely stateless, all they remember are which
storage nodes are available. Frontend nodes can be scaled almost endlessly.

The frontend nodes communicate a lot. Each get triggers a blocking request to
one storage node. Each set triggers K blocking requests to storage nodes,
where K is the redundancy value (number of nodes that can handle a specific
partition).

3) The storage nodes are purely dumb storage nodes.
All they do is store and retrieve data from an in-memory map.
All incoming requests are replied to immediately after having done the
appropriate map operation, which is quick.

Optimal scenario scaling
------------------------
The system is optimized for scenarios with a lot of get-requests and few
set-requests. It is also optimized for traffic with
requests for many different keys instead of a small set of keys.

In this case, you could scale up by simply adding more frontend nodes or
storage nodes, depending on which is the bottleneck.

Worst case scenario scaling
---------------------------
The absolute worst thing you could do to the system is sending a lot of
set-requests with the same key. This would trigger sets on all storage nodes
in the same partition, and thus would leave all other partitions without any
load at all.

I can't think of any good way of solving that.

Data size scaling
-----------------
Since all data lives in memory, the addressable memory is a definite upper bound
of amount of data per partition. However, by using many partitions and only
running a few partitions per node, you could easily scale up the total amount
of stored data.
A weakness would be having many large key/value pairs in the same partition,
this would be hard to protect against in the current setup.

