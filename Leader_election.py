import zmq
import socket
import time
from threading import Thread,RLock

# To know if I'm the leader or not
amIleadr = False
# I'm alive time
aliveTime = .5
synlock = RLock()

# IParray: holding IP's for all machines in the system, myID: containing my ID (index), basePort: 
def initializeMySockets(IParray,myID,basePort):
    # Publisher for publishing I'm alive: topic "1" (if master) else if ok msg: topic "2" (to reply for clients which ask for election),
    #  else elect msg topic "3" (to ask clients that have ID grater than mine)
    context = zmq.Context()
    publisherSocket = context.socket(zmq.PUB)
    port = basePort + myID
    publisherSocket.bind("tcp://127.0.0.1:%s" % str(port))
    # First subscriber for subscribing I'm alive msg (topic 1)
    aliveSocket = context.socket(zmq.SUB)
    aliveSocket.setsockopt_string(zmq.SUBSCRIBE, "1")
    aliveSocket.RCVTIMEO = int(aliveTime*2000)
    for i in range(len(IParray)):
        if i != myID:
            aliveSocket.connect(IParray[i])
    # Second subscriber for subscribing ok msg (topic 2)
    okSocket = context.socket(zmq.SUB)
    okSocket.setsockopt_string(zmq.SUBSCRIBE, "2")
    okSocket.RCVTIMEO = int(aliveTime*2000)
    for i in range(myID+1,len(IParray)): # Connect with ID's lower than me
        okSocket.connect(IParray[i])
    # third subscriber for subscribing elect msg (topic 3)
    electSocket = context.socket(zmq.SUB)
    electSocket.setsockopt_string(zmq.SUBSCRIBE, "3")
    for i in range(0,myID): # Connect with ID's grater than me
        electSocket.connect(IParray[i])
    print("Initialization finished myID: %d" %myID)
    return publisherSocket,aliveSocket,okSocket,electSocket


def elect(publisherSocket,aliveSocket,okSocket,electSocket,myID):
    global amIleadr
    publisherSocket.send_string("3 %d"%myID) # Send elect msg to clients that have ID grater than mine
    message = ""
    try:
        message = okSocket.recv_string()
        print("Received ok msg from ID:%s" %message.split()[-1])
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
    return False


def sendAliveLeader(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID):
    global amIleadr
    print("D5lt send alive ID=%d" % myID)
    t = time.time()
    while True:
        if amIleadr == False: # Check if another leader was found
            break
        publish = False
        if time.time()-t >= aliveTime:
            t = time.time()
            publish = True 
        if publish and amIleadr:
            print("Send alive msg myID: %d" %myID)
            publisherSocket.send_string("1 /"+IParray[myID])
    checkIsAlive(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID)


# Check if there was a leader sleeping or busy and I took its place
def checkThereIsAnotherLeader(IParray,aliveSocket,publisherSocket,okSocket,electSocket,myID):
    global amIleadr
    while True:
        if amIleadr == False:
            break
        try:
            msg = aliveSocket.recv_string()
            if int(msg.split(":")[-1]) > int(IParray[myID].split(":")[-1]): # If there is a leader with ID grater than me then make it the leader
                amIleadr = False
                print("I'm not the leader now my ID:%d"%myID)
                break
        except zmq.error.Again:
            continue
    checkForElection(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID)
    
def checkIsAlive(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID):
    global amIleadr
    while True:
        try:
            message = aliveSocket.recv_string()
            message = message.split("/")
            print("My ID:%d Leader with IP: %s is alive" % (myID,message[-1]))
        except zmq.error.Again:
            print("There is no leader we need election")
            if elect(publisherSocket,aliveSocket,okSocket,electSocket,myID) or amIleadr: # Then I'm the leader
                break
    sendAliveLeader(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID)
            

def checkForElection(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID):
    global amIleadr
    while True:
        msg = electSocket.recv_string()
        print("Received elect msg from:%s ,,,,,, myID:%d"%(msg.split()[-1],myID))
        publisherSocket.send_string("2 %d" %myID)
        print("Ok sent ID:%d" %myID)
        if elect(publisherSocket,aliveSocket,okSocket,electSocket,myID) or amIleadr: # Then I'm the leader
            break
    checkThereIsAnotherLeader(IParray,aliveSocket,publisherSocket,okSocket,electSocket,myID)



def main(IParray,myID,basePort):
    publisherSocket,aliveSocket,okSocket,electSocket = initializeMySockets(IParray,myID,basePort)
    # Initially there is no leader until all clients elect
    t1 = Thread(target=checkIsAlive,args=(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID))
    t2 = Thread(target=checkForElection,args=(IParray,publisherSocket,aliveSocket,okSocket,electSocket,myID))
    t1.start()
    t2.start()
   
    # Write the logic of the program here