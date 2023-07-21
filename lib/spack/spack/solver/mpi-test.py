#!/usr/bin/env spack-python

from mpi4py import MPI

import time
import spack.solver.compare as c
import random
import argparse

#parse arguments                                                                                                                                                                                    
parse = argparse.ArgumentParser()
parse.add_argument('inputfile')

args = parse.parse_args()
inputfn = args.inputfile

tpass = "PASSED"
tfail = "FAILED"
terror = "ERROR"

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()
t1 = time.time()
 
# select test packages
with open(inputfn) as f:
    all_packages = f.read().splitlines()  
    
lines = random.sample(all_packages, 100)

# outline work split
totalwork = len(lines)
worksize = totalwork // (size - 1)

if totalwork % (size - 1) > 0:
    worksize += 1

starti = (rank-1)*worksize
endi = rank*worksize
myjobs = lines[starti:endi]


if rank == 0:
    finished_threads = 0
    res_count = 0
    results = {
        "PASSED" : 0,
        "FAILED" : 0,
        "ERROR" : 0,
    }
    
    while finished_threads < size-1:
        s = comm.recv()

        if s == -100:
            finished_threads += 1
            continue

        res_count += 1

        (spec, result) = s
        results[result] += 1
       
        print("Test" + str(res_count) + "/" + str(totalwork))
        print("Spec name:", spec)
        print("Status: " + result)
        print("***********")

    print("OVERALL STATS:")
    print(results)
    
else:
    specobjs = []
    for job in myjobs:
        res = c.build_comparison(job, True, 1)

        test = 0
        if res:
            (best, at_depth) = res
            if best.reweight_results == at_depth.weights:
                test = tpass
        else:
            test = terror    

        message = (job, test)
        comm.send(message,dest=0)

    comm.send(-100, dest=0)
                
