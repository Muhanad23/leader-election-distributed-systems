import zmq
import socket
import time

# IParray: holding IP's for all machines in the system, myID: containing my ID (index), basePort: 
def initializeMySockets(IParray,myID,basePort):
    # Publisher for publishing I'm alive: topic 1 (if master) else ok msg: topic 2 (to reply for clients which ask for election)
    context = zmq.Context()
    publisherSocket = context.socket(zmq.PUB)
    port = basePort + myID
    publisherSocket.bind("tcp://*:%s" % str(port))
    # First subscriber for subscribing I'm alive msg (topic 1)
    aliveSocket = socket.setsockopt(zmq.SUBSCRIBE, 1)
    for i in range(len(IParray)):
        if i != myID:
            aliveSocket.connect(IParray[i])
    # Second subscriber for subscribing ok msg (topic 2)
    okSocket = socket.setsockopt(zmq.SUBSCRIBE, 2)
    for i in range(len(IParray)):
        if i != myID:
            okSocket.connect(IParray[i])
    return True







