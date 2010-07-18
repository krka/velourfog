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

A nice property of this setup is that frontend nodes can be added and removed
at any time, and since they're stateless it's easy to scale by simply adding
more of them.

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
Iteration 1 is implemented as an in memory python dictionary without any
clustering or persistance.


Usage
=====

Starting the server
-------------------
python server.py
The server will listen for requests on port 8000

Stopping the server
-------------------
Send a regular kill signal to the server process

Retrieve value for a key
------------------------
Send a GET request to the server with the key as the url.
Example using curl: curl localhost:8000/KEY

Return code 200 signifies that the key existed.
The value follows in the data.

Return code 204 signifies that the key did not exist.
No data follows.

Set value for a key
-------------------
Send a POST request to the server with the key as the url,
and the value as the data
Example using curl: curl -d VALUE localhost:8000/KEY

