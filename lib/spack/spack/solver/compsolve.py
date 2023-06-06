#!/usr/bin/env spack-python

import spack.solver.compare as c
import argparse
from tabulate import tabulate

def parse(costs, max_depth):
  """Parse under the assumption that costs are ordered as follows: errors, number of specs not concretized, all build costs, number of specs to build vs reuse, all reuse costs."""

  error_costs = costs[:4]              #4 determined slots at priorities 10,000,000 through 10,000,003
  num_not_concretized = costs[4]       #at priority 1,000,000
  build_costs = costs[5:13*(max_depth+1)+5]    #at priority in range 100,005 to (100,065 + (max_depth)*100)
  num_to_build = costs[13*(max_depth+1)+5] #at priority 100,000
  reuse_costs = costs[13*(max_depth+1) + 6:]  #at priority in range 5 to ((max_depth)*100 + 65)
  table = {}

  for i in range(0,max_depth+1):
    if i > 0:
      column = [" "] + build_costs[i*13:(i+1)*13] + [" "] + reuse_costs[i*13:(i+1)*13]
    else:
      column = [num_not_concretized] + build_costs[i*13:(i+1)*13] + [num_to_build] + reuse_costs[i*13:(i+1)*13]
      
    table[str(i)] = column
    

  criterion = ["fixed: number of input specs not concretized",
               "build: requirement weight",
               "build: deprecated versions used",
               "build: version badness",
               "build: number of non-default variants",
               "build: preferred providers",
               "build: default values of variants not being used",
               "build: compiler mismatches (not from CLI)",
               "build: compiler mismatches (from CLI)",
               "build: OS mismatches",
               "build: non-preferred compilers",
               "build: non-preferred OS's",
               "build: target mismatches",
               "build: non-preferred targets",
               "fixed: number of packages to build (vs. reuse)",
               "reuse: requirement weight",
               "reuse: deprecated versions used",
               "reuse: version badness",
               "reuse: number of non-default variants",
               "reuse: preferred providers",
               "reuse: default values of variants not being used",
               "reuse: compiler mismatches (not from CLI)",
               "reuse: compiler mismatches (from CLI)",
               "reuse: OS mismatches",
               "reuse: non-preferred compilers",
               "reuse: non-preferred OS's",
               "reuse: target mismatches",
               "reuse: non-preferred targets"
               ]

  table["Criterion"] = criterion
  print(tabulate(table, headers="keys"))
  
def compare_with_metric(spec, fresh, depth):
  print("Comparing", spec, "at depth", depth)
  dag = c.Compare(spec)
  dag.setup_at_depth(depth, not fresh)

  at_depth_model = dag.at_depth_results[depth]
  at_depth_weights = at_depth_model.weights
  at_depth_attrs = at_depth_model.attr_rules
  
  bestidx = dag.rank_at_depth(depth)[0]
  best_initial_model = dag.initial_results[bestidx]
  best_initial_attrs = best_initial_model.attr_rules
  
  reweights = dag.reweights[depth][bestidx]

  if reweights == at_depth_weights:
    print("deep model and standard model", bestidx, "have identical weights")
    sorted_at_depth = sorted(at_depth_attrs)
    sorted_initial = sorted(best_initial_attrs)

    if sorted_at_depth == sorted_initial:
      print("attrs are identical")
    
  else:
    print("deep and standard models differ")

    
def compare_and_print(spec, fresh, depth, spectree):
  #setup solver
  dag = c.Compare(spec)
  dag.setup_at_depth(depth, not fresh) #setup depth 1 and depth d results, do reweighting
  
  at_depth_model = dag.at_depth_results[depth]
  at_depth_weights = at_depth_model.weights
  
  #extract best reweight result                                                                                                                                                                                                                           
  bestidx = dag.rank_at_depth(depth)[0]
  reweights = dag.reweights[depth][bestidx]
  
        
  #print results

  if spectree:
    at_depth_model.print_full_spec()

    
  print("***************** Model evaluated at depth *******************")
  parse(at_depth_weights, depth)
  
  print("********************* Reweighted model (index:"+ str(bestidx)+ ") **********************")
  if reweights == at_depth_weights:
    print("Identical to weights computed at depth.")
  else:
    parse(reweights,depth)    

    
def main():
    #setup arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-D', "--max-depth", type=int, help="maximum depth for optimization", default=10)
    parser.add_argument('-f', '--fresh', action='store_true', help="fresh solve")
    parser.add_argument('-s', '--spectree', action='store_true', help="print spec tree for deep solve")

    parser.add_argument('spec', type=str, nargs='+', help="spec to solve")
    
    args = parser.parse_args()

    spec = args.spec
    fresh = args.fresh
    d = args.max_depth
    spectree = args.spectree
    
    compare_and_print(spec, fresh, d, spectree)
    
if __name__ == "__main__":
    main()

