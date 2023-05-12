#!/usr/bin/env spack-python

import spack.solver.asp as asp
import networkx as nx
import matplotlib.pyplot as plt
import numpy
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("root")
parser.add_argument("max_depth")

args = parser.parse_args()
root = args.root
max_depth = int(args.max_depth)


#----- SETUP SOLVE -----
#print("---EXTRACTING NECESSARY PREDICATES---")
asp.bootstrap_clingo()

ctl = asp.default_clingo_control()
ctl.load(root + ".lp")

ctl.load("extract.lp")
ctl.ground([("base", [])])

models = []
def on_model(model):
    models.append(model.symbols(shown=True, terms=True))

ctl.solve(on_model=on_model)

#should only be one model
model = models[0]

#----- CREATE GRAPH ----
#print("---BUILDING GRAPH---")
G = nx.MultiDiGraph()


for fun in asp.extract_functions(model, "depends_on"):
    G.add_edge(fun.args[0], fun.args[1], key=-1, color='b')

for fun in asp.extract_functions(model, "conditional_depends"):
    x = fun.args[0]
    y = fun.args[1]
    G.add_edge(x,y, key=fun.args[2], color='r')

virtuals = []
providers = []

for fun in asp.extract_functions(model, "possible_provider"):    
    provider = fun.args[0]
    virtual = fun.args[1]

    virtuals.append(virtual)
        
    providers.append(provider)
        
    G.add_edge(virtual, provider, key=-2, color='y')
        
colors = []
for (u,v,attrib_dict) in list(G.edges.data()):
    colors.append(attrib_dict['color'])
    
#nx.draw_networkx(G, edge_color=colors)
#plt.savefig("/Users/mayataylor/Desktop/"+root+"_diag.png")                 
                 
#----- GENERATE RULES ----

traversed = [root]
rules = []

rules.append("depth(\"" + root + "\", 0) :- attr(\"root\", \"" + root + "\")")

depths = {}
depths[root] = 0
gnodes = []

def generate_depths_many_parents(child, parent):
    conditions = [c for c in G[parent][child]]
    rules = []

    if -2 in conditions:
        #child is provider and parent is virtual
        if parent in depths:
            new_depth = str(min(depths[parent], max_depth))
            rules.append("possible_depth(\"" + child + "\", " + new_depth + ") :- provider(\"" + child + "\", \"" + parent + "\")")
        else:
            rules.append("possible_depth(\"" + child + "\", N) :- virtual_depth(\"" + parent + "\", N), provider(\"" + child + "\", \"" + parent + "\")")
        
    elif -1 in conditions:
        virtual = ""
        if child in virtuals:
            virtual="virtual_"
            
        if parent in depths:
            new_depth = str(min(depths[parent] + 1, max_depth))
            rules.append(virtual + "possible_depth(\"" + child + "\", " + new_depth + ")")
            
            #parent depth unknown:
        else:
            rules.append(virtual + "possible_depth(\"" + child + "\", N + 1) :- depth(\"" + parent + "\", N)")
    

    #only conditional edges
    else:
        virtual = ""
        if child in virtuals:
            virtual="virtual_"
            
        for c in conditions:
            if parent in depths:
                new_depth = str(min(depths[parent] + 1, max_depth))
                rules.append(virtual + "possible_depth(\"" + child + "\", " + new_depth + ") :- condition_holds(" + str(c) + ")")

            else:
                rules.append(virtual + "possible_depth(\"" + child + "\", N + 1) :- depth(\"" + parent + "\", N), condition_holds(" + str(c) + ")")

    return rules


def generate_depths_one_parent(child, parent):
    conditions = [c for c in G[parent][child]]
    rules = []

    if child in virtuals:
        if parent in depths:
            new_depth = str(min(depths[parent] + 1, max_depth))
            rules.append("virtual_depth(\"" + child + "\", " + new_depth + ")")
            depths[child] = depths[parent] + 1
        else:
            rules.append("virtual_depth(\"" + child + "\", N + 1) :- N = #min{D : depth(\"" + parent + "\", D); max_depth-1}")
            
    elif (-2 in conditions):
        #child is provider and parent is virtual
        if parent in depths:
            new_depth = str(min(depths[parent], max_depth))
            rules.append("depth(\"" + child + "\", " + new_depth + ") :- attr(_, \"" + child + "\")")
            depths[child] = depths[parent]

        else:
            rules.append("depth(\"" + child + "\", N) :- virtual_depth(\"" + parent + "\", N), attr(_, \"" + child + "\")")

    
    else:
        if parent in depths:
            new_depth = str(min(depths[parent] + 1, max_depth))
            rules.append("depth(\"" + child + "\", " + new_depth + ") :- attr(_, \"" + child + "\")")
            depths[child] = depths[parent] + 1
        else:
            rules.append("depth(\"" + child + "\", N + 1) :- N = #min{D : depth(\"" + parent + "\", D); max_depth-1}, attr(_, \"" + child + "\")")


    return rules
        

    
def traverse_subtree(root):

    child_list = list(G.neighbors(root))    
    rules = []

    gnodes.append(root)
    
    while child_list:

        for child in child_list:
            #only traverse every node once (necessary because there could be cycles)
            if child in traversed:
                child_list.remove(child)
                continue

            pred = list(G.predecessors(child))

            #Case 1: only one parent
            if len(pred) == 1:
                p = pred[0]
                rules.extend(generate_depths_one_parent(child, p))

            #Case 2: more than one parent
            else:
                if all(p in depths for p in pred):
                    minp = min(depths, key=depths.get)
                    rules.extend(generate_depths_one_parent(child, minp))
                                 
                else:
                    for p in pred:
                        rules.extend(generate_depths_many_parents(child, p))
                        
        
            child_list.remove(child)
            traversed.append(child)

            for new_child in list(G.neighbors(child)):
                if new_child not in traversed:
                    child_list.append(new_child)
                    
    return rules

def from_parent_traversal(root):
    parent_list = [root]

    rules = []
    traversed_parents = []
    
    while parent_list:
        curr_parent = parent_list[0]
        
        
        if curr_parent in traversed_parents:
            parent_list.remove(curr_parent)
            continue


        child_list = list(G.neighbors(curr_parent))


        for child in child_list:

            if child == root:
                continue
                
            parent_list.append(child)
    
            predecessors = list(G.predecessors(child))
            if len(predecessors) == 1:
                rules.extend(generate_depths_one_parent(child, curr_parent))
            else:                
                rules.extend(generate_depths_many_parents(child, curr_parent))        
            
        parent_list.remove(curr_parent)
        traversed_parents.append(curr_parent)

    return rules
        
#print("---TRAVERSING---")
#rules.extend(traverse_subtree(root))
#[print(rule + ".") for rule in rules]


depths = {}
depths[root] = 0

#print("---ALT TRAVERSAL---")
alt_rules = ["depth(\"" + root + "\", 0) :- attr(\"root\", \"" + root + "\")"]
alt_rules.extend(from_parent_traversal(root))
[print(a + ".") for a in alt_rules]
     
