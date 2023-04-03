#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse
import spack.solver.parse_costs as pcosts

parser = argparse.ArgumentParser()

parser.add_argument("max_depth")
parser.add_argument('-f', '--fresh',
                    action='store_true')

parser.add_argument('specs', type=str, nargs='+')

args = parser.parse_args()

spec = args.specs
d = int(args.max_depth)
fresh = args.fresh

dag = c.Compare(spec)

#setup depth result at d, max 10 initial results at d = 1 and the reweight for each at d
dag.setup_at_depth(d, not fresh)

at_depth_model = dag.at_depth_results[d]
at_depth_weights = at_depth_model.weights

bestidx = dag.rank_at_depth(d)[0]
reweights = dag.reweights[d][bestidx]

print("***************** Model evaluated at depth *******************")
pcosts.parse(at_depth_weights, d)

print("********************* Reweighted model (index:"+ str(bestidx)+ ") **********************")
if reweights == at_depth_weights:
    print("Identical to weights computed at depth.")
else:
    pcosts.parse(reweights,d)    

print("********************* Depth evaluated spec tree **********************")
for r in at_depth_model.root_nodes:
    r.print_tree()


# print("********************* Reweighted spec tree **********************")
# for r in dag.initial_results[bestidx].root_nodes:
#     r.print_tree()


