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


        
            
class TempResult(object):
    """Temporary result of a solve. Stores necessary rules and weights for reweighting as well as tree information."""

    def __init__(self):
        self.weights = []
        self.depth = None
        self.index = None
        self.error = False
        
        self.true_height = None
                
        self.attr_rules = []
        self.reweight_rules = []
        self.depends_on = []

        self.reweight_depth = None
        self.reweight_results = None
        
        self.roots = [] #list of root spec names as strings
        self.node_depths = {} #dict of all nodes and static depths
        self.io_specs = None
        
    def setup_depths(self, root):
        """Complete breadth first traversal of the tree given by the set of depends_on predicates belonging to self."""

        parents = [root]
        self.node_depths[root] = 0

        true_height = 0
        
        while parents:
            p = parents.pop(0)
            #iterate through all depends_on clauses
            for afun in self.depends_on:
                if afun.args[0] == p and afun.args[1] not in self.node_depths:
                    child = afun.args[1]
                    parents.append(child)
                    new_depth = self.node_depths[p] + 1
                    self.node_depths[child] = new_depth
                    if new_depth > true_height:
                        true_height = new_depth

        self.true_height = true_height

    def new_depth_rules(self, newd):
        """Build new depth/2 rules from the dictuionary node_depths generated during setup. Uses newd as the new max depth. Must be run only after setup."""
                
        rules = []
        for node, depth in self.node_depths.items():
            if depth > newd:
                depth = newd
            rules.append("depth(\"" + node + "\", " + str(depth) +  ").")

        return rules
    
    def setup(self, setup, specs, cost, symbols, depth, ranking, inputspec):
        """Setup the TempResult object after its corresponding initial solve is done. Basically just storing all the information that might be necessary later on for a reweight or a comparison."""
            

        self.weights = cost
        self.depth = depth
        self.attr_rules = asp.extract_functions(symbols, "attr")
        self.index = ranking

        if sum(cost[:4]) > 0:
            self.error = True
            return
        
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
            
        #setup full spec storage
        builder = asp.SpecBuilder(specs, hash_lookup=setup.reusable_and_possible)
        answer = builder.build_specs(self.attr_rules)

        full_specs = spack.cmd.parse_specs(inputspec)
        for spec in full_specs:
            if spec.virtual:
                providers = [spec.name for spec in answer.values() if spec.package.provides(name)]
                name = providers[0]

            concretized = answer[spec.name]
            spec._dup(concretized)


        spec_pairs = list(zip(specs, full_specs))
        self.io_specs = spec_pairs

    def add_to_control(self, control, new_depth):
        """Add all necessary reweighting rules to control object."""
        for p in self.reweight_rules:
            control.add("rule", [], p)

        for d in self.new_depth_rules(new_depth):
            control.add("depth", [], d)

    def print_full_spec(self):
        specs= self.io_specs

        name_fmt = "{name}"
        fmt = "{@version}{%compiler}{compiler_flags}{variants}{arch=architecture}"
        
        tree_kwargs = {
            "cover": "nodes", #args.cover,
            "format": name_fmt + fmt,
            "hashlen": 7, #if args.very_long else 7,
            "show_types": False, #args.types,
            "status_fn": False, #install_status_fn if args.install_status else None,
        }

        for (input, output) in specs:
            # Only show the headers for input specs that are not concrete to avoid
            # repeated output. This happens because parse_specs outputs concrete
            # specs for `/hash` inputs.
            if not input.concrete:
                tree_kwargs["hashes"] = False  # Always False for input spec
                print("Input spec")
                print("--------------------------------")
                print(input.tree(**tree_kwargs))
                print("Concretized")
                print("--------------------------------")

            #tree_kwargs["hashes"] = args.long or args.very_long
            print(output.tree(**tree_kwargs))

                
class Compare(object):
  
    def __init__(self, specs):
        self.specs = spack.cmd.parse_specs(specs)
        self.parent_dir = os.getcwd()

        self.initial_results = []         # list of the top TempResult objects at depth 1
        self.at_depth_results = {}        # dictionary of best TempResult for at every depth in self.depths
        

        self.input_spec_str = specs

        
    def initial_solve(self, depth, count, reuse=True):
        """Run solve setup for the given specs to check for errors. Then solve fully with modified display and max_depth to generate TempResult objects."""
        specs = self.specs


        #setup_only to check for errors
        solver = asp.Solver(reuse=reuse)

        #copied from solver.solve()
        reusable_specs = solver._check_input_and_extract_concrete_specs(specs) 
        reusable_specs.extend(solver._reusable_specs())
        setupobj = asp.SpackSolverSetup() 
        output = asp.OutputConfiguration(timers=False, stats=False, out=None, setup_only=True)

        solver.driver.solve(setupobj, specs, reuse=reusable_specs, output=output, depth=depth)
        
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
                res.setup(setupobj, specs, min_cost, curr_model, depth, idx, self.input_spec_str)

                results.append(res)        
                
        assert len(results) > 0, "No solutions generated for initial solve."
        
        return results

    def reweight_solve(self, result, new_depth, filename=None):
        """Generate weights for the given result evaluated at the given depth."""
        assert result.depth <= new_depth, "Reweight failed - cannot reweight depth" + str(result.depth) + "to depth" + str(new_depth)

        if result.error:
            return
        
        result.reweight_depth = new_depth
        
        solver = asp.Solver()
        driver = solver.driver
        
        driver.control = asp.default_clingo_control()
        driver.assumptions = []
        
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

        result.reweight_results = weights

                    
    def rank_at_depth(self, depth):
        """Rank all initial results at the given depth according to lexicographical order."""
        assert self.initial_results != [], "Must solve for initial results before ranking."

        weights = []
        
        for r in self.initial_results:
            if not r.error:
                assert r.reweight_depth == depth,"Must run reweight to requested depth before ranking."
                new_weights = r.reweight_results
                weights.append((r, new_weights))

        sorted_weights = sorted(weights, key=lambda l : tuple(l[1]))

        ordering = [x[0] for x in sorted_weights]
        return ordering

        
def build_comparison(spec, fresh, depth):
  #setup solver
    dag = Compare(spec)
    dag.initial_results = dag.initial_solve(1,10,not fresh)

    if dag.initial_results[0].error:
        return None

    if depth == None:
        depth = max(1,dag.initial_results[0].true_height) #don't want to allow reweights to depth=0

    at_depth_model = dag.at_depth_results[depth] = dag.initial_solve(depth,1,not fresh)[0]
    for r in dag.initial_results:
        if not r.error:
            dag.reweight_solve(r,depth)


    at_depth_weights = at_depth_model.weights

    
    #extract best reweight result
    bestmodel = dag.rank_at_depth(depth)[0]

    return (bestmodel, at_depth_model)
