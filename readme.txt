Technical documentation
-----------------------
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

----------
Iterations
----------
Iteration 1 is implemented as an in memory python dictionary without any
clustering or persistance.


Usage
-----

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

