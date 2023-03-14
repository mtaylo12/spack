#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("spec")
parser.add_argument("max_depth")

args = parser.parse_args()

spec = args.spec
depth = int(args.max_depth)


dag = c.DAGCompare(spec)

for d in range(1,depth + 1):
    print("Comparison at DEPTH=",d,"-------------")
    init = dag.at_depth_results[d] = dag.initial_solve(d,1)[0]
    reweights = dag.reweight_solve(init, d)

    if init.weights == reweights:
        print("Generated weights are identical.")

    else:
        print("Initial weights and reweight weights do not match...")
        
        print("Initial weights:")
        print(init.weights)

        print("Reweighted:")
        print(reweights)



