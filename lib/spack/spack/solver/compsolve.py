#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse
import spack.solver.parse_costs as pcosts


def main():
    #setup arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-D', "--max-depth", type=int, help="maximum depth for optimization", default=10)
    parser.add_argument('-f', '--fresh', action='store_true', help="fresh solve")
    parser.add_argument('-t', '--tree', action='store_true', help="print deep solve tree")

    parser.add_argument('spec', type=str, nargs='+', help="spec to solve")
    
    args = parser.parse_args()

    spec = args.spec
    fresh = args.fresh
    tree = args.tree
    d = args.max_depth

    #setup solver
    dag = c.Compare(spec)
    dag.setup_at_depth(d, not fresh) #setup depth 1 and depth d results, do reweighting

    at_depth_model = dag.at_depth_results[d]
    at_depth_weights = at_depth_model.weights

    #extract best reweight result
    bestidx = dag.rank_at_depth(d)[0]
    reweights = dag.reweights[d][bestidx]

    #print results
    print("***************** Model evaluated at depth *******************")
    pcosts.parse(at_depth_weights, d)

    print("********************* Reweighted model (index:"+ str(bestidx)+ ") **********************")
    if reweights == at_depth_weights:
        print("Identical to weights computed at depth.")
    else:
        pcosts.parse(reweights,d)    

    if tree:
        print("********************* Depth evaluated spec tree **********************")
        for r in at_depth_model.root_nodes:
            r.print_tree()

    
if __name__ == "__main__":
    main()

