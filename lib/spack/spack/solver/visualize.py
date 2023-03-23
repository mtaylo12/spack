#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse

import matplotlib.pyplot as plt
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("max_depth")
args = parser.parse_args()

specs = ["yajl"]
colors = ["red", "yellow", "lime", "cyan"]

d = int(args.max_depth)


for idx, spec in enumerate(specs):
    dag = c.DAGCompare(spec)

    err = dag.setup_at_depth(d)
    if err == 1:
        break;
    at_depth = dag.at_depth_results[d]    

    print("At depth weights:", at_depth.weights)

    print("Reweight initial result:", dag.reweight_solve(dag.initial_results[0], d))
    
   #  rankings = dag.rank_at_depth(d)
#     first = rankings[0]
#     if first < 4:
#         col = colors[first]
#     else:
#         col = "black"
        
#     best = dag.initial_results[first]
#     print("Closest weights:", dag.reweight_solve(best,d))

#     fdev = dag.first_deviation(first, d)
#     if fdev is not None:
#         (x,y) = fdev
#         plt.plot(x,y,color=col, marker="o")
#         plt.text(x,y,spec)

#     else:
#         print("Spec " + spec + " matches depth result exactly with model #" + str(first))



# plt.show()
# # x = numpy.arange(1, len(at_depth.weights) + 1)
# # # plt.plot(x,at_depth.weights)
# # #
legend = ["depth"]
# legend = []
# for idx, mod in enumerate(rankings[:2]):
#     res = dag.reweights[d][mod]
#     plt.plot(x, numpy.array(res) - numpy.array(at_depth.weights))
#     legend.append("mod" + str(mod) + "-rank" + str(idx))


# plt.legend(legend)
# plt.show()

    
# 

# plt.title("Comparison@Depth=" + str(d))
# plt.plot(x, at_depth.weights)

# for res in initial_results:
#     rw = dag.reweight_solve(res, d)
#     plt.plot(x,rw)

# plt.legend(["depth", "sol1", "sol2", "sol3", "sol4", "sol5", "sol6"])
# plt.show()

