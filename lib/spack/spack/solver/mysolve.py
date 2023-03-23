#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse
import spack.solver.parse_costs as pcosts

parser = argparse.ArgumentParser()
parser.add_argument("spec")
parser.add_argument("max_depth")
parser.add_argument('-r', '--reuse',
                    action='store_true')

args = parser.parse_args()

spec = args.spec
d = int(args.max_depth)
reuse = args.reuse

dag = c.DAGCompare(spec)

#setup depth result at d, max 10 initial results at d = 1 and the reweight for each at d
dag.setup_at_depth(d, reuse)

at_depth_weights = dag.at_depth_results[d].weights
initial_result = dag.initial_results[0]

bestidx = dag.rank_at_depth(d)[0]
reweights = dag.reweights[d][bestidx]

print("***************** Model evaluated at depth *******************")
pcosts.parse(at_depth_weights, d)

print("\n")

print("********************* Reweighted model (index:", bestidx, ") **********************")
pcosts.parse(reweights,d)



