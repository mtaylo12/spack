#!/usr/bin/env spack-python

import spack.solver.compare as c

encoding = ["Error", "Depth", "Index", "Weights Match", "Attrs Match", "Deep Attr Outliers", "Stand Attr Outliers"]

class EncodedResult(object):

  def __init__(self, spec):
    self.spec = spec
    self.error = False
    
    self.depth = None
    self.bestidx = None
    self.weightmatch = None
    self.attrmatch = None
    self.deepattr_only = None
    self.standattr_only = None

  def encode(self, fresh=True):
    res = c.build_comparison(self.spec, fresh, None)
    
    if not res:
      self.error = True
      return (self.spec, [self.error, self.depth, self.bestidx, self.weightmatch, self.attrmatch, self.deepattr_only, self.standattr_only])

      
    (best, at_depth) = res
    self.depth=best.reweight_depth
    self.bestidx=best.index
        
    if best.reweight_results == at_depth.weights:
      self.weightmatch=True
    else:
      self.weightmatch=False
    
    sorted_at_depth = sorted(at_depth.attr_rules)
    sorted_initial = sorted(best.attr_rules)

    
    if sorted_at_depth == sorted_initial:
      self.attrmatch=True
    else:

      self.attrmatch=False
      s1 = set(sorted_at_depth)
      s2 = set(sorted_initial)
      
      self.deepattr_only = [str(x) for x in s1 if x not in s2]
      self.standattr_only = [str(x) for x in s2 if x not in s1]

      
    #ENCODING
    res = [self.error, self.depth, self.bestidx, self.weightmatch, self.attrmatch, self.deepattr_only, self.standattr_only]
    return (self.spec, res)


  def decode(self):
    print("Spec:", self.spec)

    if self.error:
      print("Error:", self.error)
      return

    print("Depth:", self.depth)
    print("Index:", self.bestidx)
    print("Weights match?", self.weightmatch)
    print("Attrs match?", self.attrmatch)

    if not self.attrmatch:
      print("Deep attr outliers:", self.deepattr_only)
      print("Stand attr outliers:", self.standattr_only)

    
