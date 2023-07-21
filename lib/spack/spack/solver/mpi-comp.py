#!/usr/bin/env spack-python

from mpi4py import MPI

import time
import spack.solver.encode as e
import random
import json
import argparse

#parse arguments
parse = argparse.ArgumentParser()
parse.add_argument('inputfile')
parse.add_argument('outputfile')
parse.add_argument('-b', '--bufsize', dest='bufsize', type=int, default=100)

args = parse.parse_args()
inputfn = args.inputfile
outputfn = args.outputfile
bufsize = int(args.bufsize)

#setup MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

assert size > 1, "Must use at least two threads."

# select test packages
with open(inputfn) as f:
    lines = f.read().splitlines()

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
    results = {}
    
    while finished_threads < size-1:
        s = comm.recv()

        if s == 0:
            finished_threads += 1
            print("Finished thread " + str(finished_threads) +"/" + str(size-1), flush=True)
            continue

        res_count += 1
        print("Received result " + str(res_count) + "/" + str(totalwork), flush=True)

        (spec, encoding) = s
        results[spec] = encoding
        
        if (res_count%bufsize) == 0:
            with open(outputfn, "a") as f:
                f.write(json.dumps(results))
                f.write("\n")
                results = {}

    if results != {}:
        with open(outputfn, "a") as f:
            f.write(json.dumps(results))

    t2 = time.time()
    
else:
    specobjs = []
    for job in myjobs:
        print("Starting job: " + job + " on thread", rank, flush=True)
        spec_obj = e.EncodedResult(job)
        spec_encoding = spec_obj.encode()
        
        comm.send(spec_encoding,dest=0)
    comm.send(0, dest=0)
                
