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

for d in range(1,depth+1):
    init = dag.at_depth_results[d] = dag.initial_solve(d,1)[0]
    at_depth_weights = init.weights
    reweighted = dag.reweight_solve(init,d)

    if at_depth_weights != reweighted:
        print("TEST FAILED: original weights and reweights don't match at depth", d)
        quit()

print("TESTS PASSED")

