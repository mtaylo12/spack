#!/usr/bin/env spack-python

import spack.solver.asp as asp

import os
import argparse

#import clingo -- imported by driver?
import numpy
import spack.cmd
import matplotlib.pyplot as plt


reweight_predicates = ["literal_not_solved",
                       "build",
                       "optimize_for_reuse",
                       "requirement_weight",
                       "build_priority",
                       "version_weight",
                       "variant_not_default",
                       "provider_weight",
                       "variant_default_not_used",
                       "compiler_mismatch",
                       "compiler_mismatch_required",
                       "node_os_mismatch",
                       "compiler_weight",
                       "node_os_weight",
                       "node_target_mismatch",
                       "node_target_weight",
                       ]


class SpecNode(object):
    """Node object for spec tree, useful basically only for debugging (the print_tree output should match the spec from spack solve."""
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []

        if parent==None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
            parent.add_child(self)

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, max_depth=10, level=0):
        print("\t" * level, self.name)
        for child in self.children:
            child.print_tree(max_depth, level + 1)
        
            
class TempResult(object):
    """Temporary result of a solve. Stores necessary rules and weights for reweighting as well as tree information."""

    def __init__(self):
        self.weights = []
        self.depth = None
                
        self.attr_rules = []
        self.reweight_rules = []
        self.depends_on = []
        
        self.roots = [] #list of root spec names as strings
        self.node_depths = {} #dict of all nodes and static depths

    def setup_tree(self, root):
        """Setup spec tree of SpecNode objects. Useful for debugging only."""
        r = SpecNode(root)
        
        parents = [r]
        traversed = [root]
        while parents != []:
            p = parents.pop(0)
            
            for afun in self.depends_on:        
                if afun.args[0] == p.name and afun.args[1] not in traversed:
                    child = SpecNode(afun.args[1], p)
                    traversed.append(child.name)
                    parents.append(child)
        return r
        
    def setup_depths(self, root):
        """Complete breadth first traversal of the tree given by the set of depends_on predicates belonging to self."""

        parents = [root]
        self.node_depths[root] = 0
 
        while parents:
            p = parents.pop(0)
            #iterate through all depends_on clauses
            for afun in self.depends_on:
                if afun.args[0] == p and afun.args[1] not in self.node_depths:
                    child = afun.args[1]
                    parents.append(child)
                    self.node_depths[child] = self.node_depths[p] + 1


    def new_depth_rules(self, newd):
        """Build new depth/2 rules from the dictuionary node_depths generated during setup. Uses newd as the new max depth. Must be run only after setup."""
                
        rules = []
        for node, depth in self.node_depths.items():
            if depth > newd:
                depth = newd
            rules.append("depth(\"" + node + "\", " + str(depth) +  ").")

        return rules
    
    def setup(self,specs, cost, symbols, depth, ranking):
        """Setup the TempResult object after its corresponding initial solve is done. Basically just storing all the information that might be necessary later on for a reweight or a comparison."""
        self.weights = cost
        self.depth = depth

        self.attr_rules = asp.extract_functions(symbols, "attr")

        for a in self.attr_rules:
            if a.args[0] == "root":
                self.roots.append(a.args[1])

        
        #rules for reweighting are in global list but must also include attr
        self.reweight_rules = [str(e) + "." for e in self.attr_rules]
        for p in reweight_predicates:
            for e in asp.extract_functions(symbols, p):
                self.reweight_rules.append(str(e) + ".")

        #used to regenerate depths statically
        self.depends_on = asp.extract_functions(symbols, "depends_on")

        #setup spec tree for printing and for depth regeneration
        for root in self.roots:
            self.setup_depths(str(root))

                               
    def add_to_control(self, control, new_depth):
        """Add all necessary reweighting rules to control object."""
        for p in self.reweight_rules:
            control.add("rule", [], p)

        for d in self.new_depth_rules(new_depth):
            control.add("depth", [], d)


        
class Compare(object):
  
    def __init__(self, specs):
        self.specs = spack.cmd.parse_specs(specs)
        self.parent_dir = os.getcwd()

        self.initial_results = []         # list of the top TempResult objects at depth 1
        self.at_depth_results = {}        # dictionary of best TempResult for at every depth in self.depths
        self.reweights = {}               # dictionary of depth, list of weights for each initial result


    def initial_solve(self, depth, count, reuse=True):
        """Run solve setup for the given specs to check for errors. Then solve fully with modified display and max_depth to generate TempResult objects."""
        specs = self.specs
        
        #setup_only to check for errors
        solver = asp.Solver(reuse=reuse)
        solver.solve(specs, setup_only=True)
        
        #solve with specific max_depth and detailed display
        driver = solver.driver
        driver.control.load(os.path.join(self.parent_dir, "concretize.lp"))
        driver.control.load(os.path.join(self.parent_dir, "os_compatibility.lp"))
        driver.control.load(os.path.join(self.parent_dir, "display-recreate.lp"))
        
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
                #only retrieve up to count solutions
                if idx >= count: break

                #create TempResult object 
                res = TempResult()
                res.setup(specs, min_cost, curr_model, depth, idx)
                
                results.append(res)        
                
        assert len(results) > 0, "No solutions generated for initial solve."

        return results

    def reweight_solve(self, result, new_depth, filename=None):
        """Generate weights for the given result evaluated at the given depth."""
        assert result.depth <= new_depth, "Reweight failed - cannot reweight to smaller depth."

        solver = asp.Solver()
        driver = solver.driver
        
        driver.control = asp.default_clingo_control()
        
        driver.control.load(os.path.join(self.parent_dir, "minimize.lp"))
        #driver.control.load(os.path.join(self.parent_dir, "display-recreate.lp"))
        
        #add result predicates to control object
        result.add_to_control(driver.control, new_depth)

        driver.control.add("depth", [], "#const max_depth = " + str(new_depth) + ".")        
        driver.control.ground([("base", []), ("depth",[]), ("attr", []), ("rule",[])])
        
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
           
        assert solve_res.satisfiable, "Reweight failed - no solutions found."
        assert len(models) == 1, "Reweight failed - more than one solution found."
        
        model = min(sorted(models))
        (weights, symbols) = model

        l1 = len(weights)
        l2 = 6 + (1+new_depth)*26

        assert l1==l2, "Reweight failed - wrong length weight vector."

        return weights

            
    def setup_at_depth(self, d, reuse=True):
        """Solve at the given depth and at depth 1. Compute reweights to compare."""
        
        self.initial_results = (self.initial_solve(1, 10, reuse))
        self.at_depth_results[d] = self.initial_solve(d,1,reuse)[0]
        self.reweights[d] = [self.reweight_solve(r,d) for r in self.initial_results]

        
    def rank_at_depth(self, depth):
        """Rank all initial results at the given depth according to lexicographical order."""
        assert depth in self.reweights, "invalid depth request"

        weights = []
        
        for idx, r in enumerate(self.initial_results):
            new_weights = self.reweights[depth][idx]
            weights.append((idx, new_weights))

        sorted_weights = sorted(weights, key=lambda l : tuple(l[1]))

        ordering = [x[0] for x in sorted_weights]
        return ordering

        
