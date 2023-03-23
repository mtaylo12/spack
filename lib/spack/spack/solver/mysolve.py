#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse
import spack.solver.parse_costs as pcosts

parser = argparse.ArgumentParser()
parser.add_argument("spec")
parser.add_argument("max_depth")

args = parser.parse_args()

spec = args.spec
d = int(args.max_depth)

dag = c.DAGCompare(spec)

#setup depth result at d, max 10 initial results at d = 1 and the reweight for each at d
dag.setup_at_depth(d)

at_depth_weights = dag.at_depth_results[d].weights
initial_result = dag.initial_results[0]
reweights0 = dag.reweights[d][0]
reweights1 = dag.reweights[d][1]

pcosts.parse(at_depth_weights, d)
pcosts.parse(reweights0,d)
pcosts.parse(reweights1,d)



