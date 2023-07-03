#!/usr/bin/env spack-python

import spack.solver.compsolve as compsolve

import numpy as np
import matplotlib.pyplot as plt
import time



def run_spec(spec):
    output = ["RUNNING FRESH COMPARISON FOR:" + spec]
    
    t1 = time.time()
    (depth, bestidx, error, wmatch, amatch, deeponly, standonly)= compsolve.print_comparison(spec, True)
    t2 = time.time()

    
    output += ["- comparison at depth " + str(depth) + " of initial model #" + str(bestidx)]
    if error:
        output += ["- error during solve"]
    else:
        output += ["- weights match: " + str(wmatch)]
        output += ["- attrs match: " + str(amatch)]

        if not amatch:
            output += ["\tAttributes in deep solve only: " + str(deeponly)]
            output += ["\tAttributes in stand sol only: " + str(standonly)]

    return (spec, output, t2-t1)
    

def main():

    with open('condvar_specs.txt') as f:
        lines = f.read().splitlines()[:4]
    

if __name__ == "__main__":
    main()




