import multiprocessing 
import Leader_election
import time

if __name__ == '__main__':
    timePeriod = 5
    numberOfClients = 5 # To test on one machine
    basePort = 7000
    processes = []
    IParray = ["tcp://127.0.0.1:7000","tcp://127.0.0.1:7001","tcp://127.0.0.1:7002","tcp://127.0.0.1:7003","tcp://127.0.0.1:7004"]
    for j in range(len(IParray)):
        t=multiprocessing.Process(target=Leader_election.main,args=(IParray,j,basePort))
        processes.append(t)

    for j in processes:
        j.start()

    t = time.time()    
    count = 0
    while (True):
        if (time.time()-t >= timePeriod and count == 0):
            print("-------------------------------------Process #4 termenated--------------------------------------")
            processes[4].terminate()
            count+=1
        
        if (time.time()-t >= 2*timePeriod and count == 1):
            print("-------------------------------------Process #3 termenated--------------------------------------")
            processes[3].terminate()
            count+=1
        
       
