#!/usr/bin/env python
from tabulate import tabulate

def parse_old(costs, max_depth):
  error_costs = costs[:4]              #4 determined slots at priorities 10,000,000 through 10,000,003
  num_not_concretized = costs[4]       #at priority 1,000,000

  costs = costs[5:]
  leveled1 = costs[:13*(max_depth)]    #at priority in range 100,005 to (100,000 + (max_depth - 1)*100 + 65)
                                       #this setup breaks if the upper range hits 1,000,000, or max depth > 9000
  fixed_bucket = costs[13*(max_depth)] #at priority 100,000

  costs = costs[13*max_depth+1:]
  leveled2 = costs[:13]                #at priority in range 99,905 to 99,965 (because depth D is equal to max depth)

  costs = costs[13:]

  leveled3 = costs[:13*(max_depth+1)]  #at priority in range -95 to ((max_depth-1)*100 + 65)
                                       #breaks if upper range hits 99,905, or max_depth > 999

  costs = costs[13*(max_depth+1):]

  print("----------------------")
  print("PARSING AT DEPTH ", max_depth)

  print("Errors:", error_costs)
  print("Num not concretized:", num_not_concretized)

  print("LEVELED PART 1")
  for i in range(0, max_depth):
    print("Level ", i, ": ", leveled1[i*13: (i+1)*13])

  print("Level ", max_depth, ": ", leveled2)

  print("Fixed bucket:", fixed_bucket)

  print("LEVELED PART 2")
  for i in range(0,max_depth+1):
    print("Level ", i, ": ", leveled3[i*13:(i+1)*13])


  assert costs==[]

def parse(costs, max_depth):
  error_costs = costs[:4]              #4 determined slots at priorities 10,000,000 through 10,000,003
  num_not_concretized = costs[4]       #at priority 1,000,000

  costs = costs[5:]
  leveled1 = costs[:13*(max_depth+1)]    #at priority in range 100,005 to (100,065 + (max_depth)*100)
  fixed_bucket = costs[13*(max_depth+1)] #at priority 100,000

  costs = costs[13*(max_depth+1)+1:]


  leveled3 = costs[:13*(max_depth+1)]  #at priority in range 5 to ((max_depth)*100 + 65)

  costs = costs[13*(max_depth+1):]

  table = {}

  for i in range(0,max_depth+1):
    if i > 0:
      column = [" "] + leveled1[i*13:(i+1)*13] + [" "] + leveled3[i*13:(i+1)*13]
    else:
      column = [num_not_concretized] + leveled1[i*13:(i+1)*13] + [fixed_bucket] + leveled3[i*13:(i+1)*13]

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


  assert costs==[]

