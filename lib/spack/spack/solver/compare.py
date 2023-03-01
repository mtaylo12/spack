#!/usr/bin/env spack-python

import spack.solver.asp as asp

import os
import argparse
#import clingo imported by driver?
import numpy
import spack.cmd

# setup the parser
parser = argparse.ArgumentParser()
parser.add_argument("specs", nargs=argparse.REMAINDER, help="specs of packages")

args = parser.parse_args()
specs = spack.cmd.parse_specs(args.specs) 

# setup general objects
parse_files = None
parent_dir = "/Users/mayataylor/spack/lib/spack/spack/solver"

class TempResult(object):
    """Temporary result of a solve."""
    def __init__(self):
        self.weights = []
        self.depth = None

        self.attr = []
        self.rules = []

    def setup(self, cost, symbols, depth, ranking):

        self.weights = cost
        self.attr = [str(e) + "." for e in asp.extract_functions(symbols, "attr")]
        self.depth = depth
        

        predicates = ["build_priority",
                      "depends_on",
                      "build",
                      "version_declared",
                      "error",
                      "internal_error",
                      "opt_criterion"
                      "requirement_has_weight",
                      "requirement_weight",
                      "version_weight",
                      "provider_weight",
                      "compiler_weight",
                      "node_os_weight",
                      "node_target_weight",
                      "compiler_mismatch",
                      "compiler_mismatch_required",
                      "node_os_mismatch",
                      "node_target_mismatch",
                      "variant_not_default",
                      "variant_default_not_used",
                      "literal_not_solved",
                      "optimize_for_reuse"]
        
        for p in predicates:
            for e in asp.extract_functions(symbols, p):
                self.rules.append(str(e) + ".")

    def add_to_control(self, control):
        for a in self.attr:
            control.add("attr", [], a)

        for p in self.rules:
            control.add("rule", [], p)

    def print_program(self):
        filename = "model"  + "-depth" + str(self.depth) + ".lp"
        f = open(filename, 'w')

        for a in self.attr:
            f.write(a + "\n")
        for p in self.rules:
            f.write(p + "\n")

        f.close()



def initial_solve(specs, depth, count):
    #do a setup only solve to check errors

    solver = asp.Solver()
    solver.solve(specs, setup_only=True)

    driver = solver.driver
    

    driver.control.load(os.path.join(parent_dir, "concretize.lp"))
    driver.control.load(os.path.join(parent_dir, "os_compatibility.lp"))
    driver.control.load(os.path.join(parent_dir, "display-recreate.lp"))

    driver.control.add("depth", [], "#const max_depth = " + str(depth) + ".")
    driver.control.ground([("base", [])])

    models = []
    cores = []

    def on_model(model):
        #shown variable determines if results from display.lp are included in the model representation
        models.append((model.cost, model.symbols(shown=True, terms=True)))

    solve_kwargs = {
        "assumptions": driver.assumptions,
        "on_model": on_model,
        "on_core": cores.append
    }
    
    solve_res = driver.control.solve(**solve_kwargs)

    results = []
    
    if solve_res.satisfiable:
        for idx, (min_cost, curr_model) in enumerate(sorted(models)):
             if idx >= count: break
             res = TempResult()
             res.setup(min_cost, curr_model, depth, idx)
             results.append(res)

    print("solving for",count,"models with depth", depth)
    assert len(results) > 0, "No solutions generated for initial solve."
    return results


def reweight_solve(result, new_depth):

    #for debugging purposes
    result.print_program()
    
    control = asp.default_clingo_control()

    control.load(os.path.join(parent_dir, "minimize.lp"))
    result.add_to_control(control)

    control.add("depth", [], "#const max_depth = " + str(new_depth) + ".")

    control.ground([("base", []), ("depth",[]), ("attr", []), ("rule",[])])

    models = []

    def on_model(model):
        #shown variable determines if results from display.lp are included in the model representation
        models.append((model.cost, model.symbols(shown=True, terms=True)))

    solve_res = control.solve(on_model=on_model)

    assert solve_res.satisfiable, "Reweight failed - no solutions found."
    assert len(models) == 1, "Reweight failed - more than one solution found."

    (weights, model) = models[0]
    return weights
        
    

results_depth1 = (initial_solve(specs, 1, 10))
deep_results = []

for i in range(2,3):
    res = initial_solve(specs, i, 1)
    deep_results.append(res[0])

print("depth 1 initial weights:")
print(results_depth1[0].weights)

#print(reweight_solve(deep_results[0], 2))
#print(deep_results[0].weights)


# def priorities(depth, filename):
#     control = asp.default_clingo_control()
#     parent_dir = os.path.dirname(__file__)

#     control.load(os.path.join(parent_dir, "minimize.lp"))
#     control.load(filename)
#     control.add("#const max_depth=" + str(depth) + ".")

#     control.ground()
    
#     models = []

#     def on_model(model):
#         models.append(model.cost)

#     control.solve(on_model=on_model)

#     assert(len(models) == 1)

#     return models[0]


