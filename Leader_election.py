import zmq
import socket
import time

# To know if I'm the leader or not
amIleadr = False
# I'm alive time
aliveTime = 0.1
# IParray: holding IP's for all machines in the system, myID: containing my ID (index), basePort: 
def initializeMySockets(IParray,myID,basePort):
    # Publisher for publishing I'm alive: topic "1" (if master) else if ok msg: topic "2" (to reply for clients which ask for election),
    #  else elect msg topic "3" (to ask clients that have ID grater than mine)
    context = zmq.Context()
    publisherSocket = context.socket(zmq.PUB)
    port = basePort + myID
    publisherSocket.bind("tcp://*:%s" % str(port))
    # First subscriber for subscribing I'm alive msg (topic 1)
    aliveSocket = socket.setsockopt(zmq.SUBSCRIBE, "1")
    for i in range(len(IParray)):
        if i != myID:
            aliveSocket.connect(IParray[i])
    # Second subscriber for subscribing ok msg (topic 2)
    okSocket = socket.setsockopt(zmq.SUBSCRIBE, "2")
    okSocket.RCVTIMEO = aliveTime + .1*aliveTime
    for i in range(0,len(IParray)): # Connect with ID's lower than me
        if i != myID:
            okSocket.connect(IParray[i])
    # third subscriber for subscribing elect msg (topic 3)
    electSocket = socket.setsockopt(zmq.SUBSCRIBE, "3")
    for i in range(myID+1,len(IParray)): # Connect with ID's grater than me
        if i != myID:
            electSocket.connect(IParray[i])
    return publisherSocket,aliveSocket,okSocket,electSocket


def election(publisherSocket,aliveSocket,okSocket,electSocket,myID):
    publisherSocket.send_string("3") # Send ok msg to clients that have ID grater than mine
    message = ""
    try:
        message = okSocket.recv_string()
    except zmq.error.Again:
        # If no client with ID grater than me then I'm the leader
        amIleadr = True
    # If I got a message from ID grater than me then return
    return

