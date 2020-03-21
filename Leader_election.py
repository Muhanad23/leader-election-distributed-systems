import zmq
import socket
import time
from threading import Thread

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
    aliveSocket = context.socket(zmq.SUB)
    aliveSocket.setsockopt(zmq.SUBSCRIBE, "1")
    aliveSocket.RCVTIMEO = aliveTime + .1*aliveTime
    for i in range(len(IParray)):
        if i != myID:
            aliveSocket.connect(IParray[i])
    # Second subscriber for subscribing ok msg (topic 2)
    okSocket = context.socket(zmq.SUB)
    okSocket.setsockopt(zmq.SUBSCRIBE, "2")
    okSocket.RCVTIMEO = aliveTime + .1*aliveTime
    for i in range(0,len(IParray)): # Connect with ID's lower than me
        if i != myID:
            okSocket.connect(IParray[i])
    # third subscriber for subscribing elect msg (topic 3)
    electSocket = context.socket(zmq.SUB)
    electSocket.setsockopt(zmq.SUBSCRIBE, "3")
    for i in range(myID+1,len(IParray)): # Connect with ID's grater than me
        if i != myID:
            electSocket.connect(IParray[i])
    return publisherSocket,aliveSocket,okSocket,electSocket


def elect(publisherSocket,aliveSocket,okSocket,electSocket,myID):
    publisherSocket.send_string("3") # Send ok msg to clients that have ID grater than mine
    message = ""
    try:
        message = okSocket.recv_string()
    except zmq.error.Again:
        # If no client with ID grater than me then I'm the leader
        amIleadr = True
        print("I'm now the leader , my ID = %d" %myID)
        return True
    # Else wait until there is a new leader , if waiting doesn't matter then return instead of waiting
    while True:
        try:
            message = aliveSocket.recv_string()
            message = message.split("/")
            print("A new leader with IP: %s is selected" %message[-1])
            return False
        except zmq.error.Again:
            continue


def sendAliveLeader(IParray,myID,publisherSocket):
    global amIleadr
    t = time.time()
    while True:
        if amIleadr == False: # Check if another leader was found
            break
        publish = False
        if time.time()-t >= aliveTime:
            t = time.time()
            publish = True 
        if publish:
            publisherSocket.send_string("1 /"+IParray[myID])
    checkForElection(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID)


# Check if there was a leader sleeping or busy and I took its place
def checkThereIsAnotherLeader(aliveSocket,publisherSocket,okSocket,electSocket,myID):
    global amIleadr
    while True:
        try:
            aliveSocket.recv_string()
            amIleadr = False
            print("I'm not the leader now")
            break
        except zmq.error.Again:
            continue
    checkIsAlive(publisherSocket,aliveSocket,okSocket,electSocket,myID)

    
def checkIsAlive(publisherSocket,aliveSocket,okSocket,electSocket,myID):
    while True:
        try:
            message = aliveSocket.recv_string()
            message = message.split("/")
            print("Leadr with IP: %s is alive" % message[-1])
        except zmq.error.Again:
            print("Leader died we need election")
            if elect(publisherSocket,aliveSocket,okSocket,electSocket,myID): # Then I'm the leader
                break
    checkThereIsAnotherLeader(aliveSocket,publisherSocket,okSocket,electSocket,myID)
            

def checkForElection(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID):
    while True:
        electSocket.recv_string()
        if elect(publisherSocket,aliveSocket,okSocket,electSocket,myID): # Then I'm the leader
            break
    sendAliveLeader(IParray,myID,publisherSocket)



def main(IParray,myID,basePort):
    publisherSocket,aliveSocket,okSocket,electSocket = initializeMySockets(IParray,myID,basePort)
    # Initially there is no leader until all clients elect
    Thread(target=checkIsAlive(publisherSocket,aliveSocket,okSocket,electSocket,myID)).start()
    Thread(target=checkForElection(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID)).start()
            
        







