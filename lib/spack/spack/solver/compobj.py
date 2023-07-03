#!/usr/bin/env spack-python

import spack.solver.compare as c

class CompObj(object):

  def __init__(self, spec):
    self.spec = spec
    self.depth = None
    self.bestidx = None
    self.error = False
    self.weightmatch = False
    self.attrmatch = False
    self.deepattr_only = []
    self.standattr_only = []

  def run_comparison(self, fresh):
    dag = c.Compare(self.spec)

    dag.initial_results = (dag.initial_solve(1,10,not fresh))

    if dag.initial_results[0].error == True:
      self.error=True
      return
    
    depth = dag.initial_results[0].true_height

    at_depth_model = dag.at_depth_results[depth] = dag.initial_solve(depth,1,not fresh)[0]
    dag.reweights[depth] = [dag.reweight_solve(r,depth) for r in dag.initial_results]

    at_depth_weights = at_depth_model.weights
    at_depth_attrs = at_depth_model.attr_rules

    self.bestidx = dag.rank_at_depth(depth)[0]
    best_initial_model = dag.initial_results[bestidx]
    best_initial_attrs = best_initial_model.attr_rules

    reweights = dag.reweights[depth][bestidx]

    if sum(at_depth_weights[:4]) > 0 or sum(best_initial_model.weights[:4]) > 0:
      self.error=True
      return


    if reweights == at_depth_weights:
      self.weightmatch = True

      sorted_at_depth = sorted(at_depth_attrs)
      sorted_initial = sorted(best_initial_attrs)

      if sorted_at_depth == sorted_initial:
        self.attrmatch = True
      else:
        s1 = set(sorted_at_depth)
        s2 = set(sorted_initial)
        self.deepattr_only = [x for x in s1 if x not in s2]
        self.standattr_only = [x for x in s2 if x not in s1]


                               


