#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("spec")

args = parser.parse_args()

spec = args.spec

dag = c.DAGCompare(spec)

init = dag.at_depth_results[1] = dag.initial_solve(1,1)[0]
init.spec_trees[spec].print_tree()




