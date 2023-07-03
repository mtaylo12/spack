#!/usr/bin/env spack-python

from mpi4py import MPI

import time
import spack.solver.compobj as compobj


comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

with open("condvar_specs.txt") as f:
    lines = f.read().splitlines()

lines = lines[:5]



totalwork = len(lines)
assert totalwork >= size, "More processors than tasks"

worksize = totalwork // size

if totalwork % size > 0:
    worksize += 1

starti = rank*worksize
endi = (rank + 1)*worksize


t1 = time.time()
myjobs = lines[starti:endi]

# if rank == 0:
#     for i in range(1, size):
#         data = comm.recv(source = i)

#     t2 = time.time()
#     print("Completed for list of size", totalwork, " in time:", t2-t1)
# else:
for job in myjobs:
    specobj = compobj.CompObj(job)
    
    print("Beginning job for spec", job, "on processor", rank)
    specobj.run_comparison(True)

    if specobj.error == False:
        print("Completed result for spec", job)
    else:
        print("Error solving for spec", job)
        
#comm.send(data, dest=0)
