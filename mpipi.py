
"""
Simple program that estimates pi using the Leibniz approximation
1 - (1/3) + (1/5) - (1/7) + ... = pi/4
to demonstrate simple usage of MPI4PY.

The following code by jcchurch was used as a basic reference.
https://gist.github.com/jcchurch/930276
"""

from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

termToComputeTo = 100000
numWorkers = size - 1
sliceSize = termToComputeTo/numWorkers

#master
if rank == 0:

    start = time.time()

    pi_estimate = 0

    #send jobs
    for i in range(0, numWorkers):
        print "Sending start", i * sliceSize, "to process", (i + 1)
        comm.send(i * sliceSize, dest=i+1, tag=1)
        comm.send(i * sliceSize + sliceSize, dest=i+1, tag=2)

    #recieve jobs
    recieved = 0
    while recieved < numWorkers:
        pi_estimate += comm.recv(source=MPI.ANY_SOURCE, tag=1)
        process = comm.recv(source=MPI.ANY_SOURCE, tag=2)
        print "Recieved data from process", process
        recieved += 1

    print "Estimate is", 4.0 * pi_estimate
    print "Runtime is", (time.time() - start), "seconds"

#worker
else:
    value = 0.0

    #recieve job
    start = comm.recv(source=0, tag=1)
    end = comm.recv(source=0, tag=2)

    #do computation
    for i in range(start, end):
        if i % 2 == 0:
            value += 1.0/(2*i + 1)
        else:
            value -= 1.0/(2*i + 1)

    #send information back
    comm.send(value, dest=0, tag=1)
    comm.send(rank, dest=0, tag=2)
