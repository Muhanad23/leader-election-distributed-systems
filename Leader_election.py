import zmq
import socket
import time

def initializeAsLeader(numberOfClients,myID,basePort):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    port = str(basePort + myID)
    socket.bind("tcp://*:%s" % port)


