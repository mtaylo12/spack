#!/usr/bin/env spack-python

import spack.solver.asp as asp
import networkx as nx
import matplotlib.pyplot as plt
import numpy
import argparse


                 
#----- GLOBAL VARS ----

virtuals = []
providers = []
depths = {}
possible_depths = {}


def generate_depths_many_parents(child, parent, noderules, G, max_depth):
    conditions = [c for c in G[parent][child]]
    rules = []

    if child not in possible_depths:
        possible_depths[child] = []
        
    virtual = ""
    if child in virtuals:
        virtual="virtual_"

    if -2 in conditions:
        #child is provider and parent is virtual
        if parent in depths:
            new_depth = str(min(depths[parent], max_depth))
            rules.append("possible_depth(\"" + child + "\", " + new_depth + ") :- provider(\"" + child + "\", \"" + parent + "\")")
            possible_depths[child].append(new_depth)
        else:
            rules.append("possible_depth(\"" + child + "\", N) :- virtual_depth(\"" + parent + "\", N), provider(\"" + child + "\", \"" + parent + "\")")
        
    elif -1 in conditions:
        if parent in depths:
            new_depth = str(min(depths[parent] + 1, max_depth))
            rules.append(virtual + "possible_depth(\"" + child + "\", " + new_depth + ")")
            possible_depths[child].append(new_depth)
            
        else:
            rules.append(virtual + "possible_depth(\"" + child + "\", N + 1) :- depth(\"" + parent + "\", N)")
    

    #only conditional edges
    else:
        for c in conditions:
            if parent in depths:
                new_depth = str(min(depths[parent] + 1, max_depth))
                rules.append(virtual + "possible_depth(\"" + child + "\", " + new_depth + ") :- condition_holds(" + str(c) + ")")
                possible_depths[child].append(new_depth)
            else:
                rules.append(virtual + "possible_depth(\"" + child + "\", N + 1) :- depth(\"" + parent + "\", N), condition_holds(" + str(c) + ")")

    
    node_depths = possible_depths[child]
    same = True
    depth = None
    
    if len(node_depths) == len(list(G.predecessors(child))):
        for d in node_depths:
            if depth == None:
                depth = d

            elif d != depth:
                same = False
                break
            
        if same:
            noderules[child] = ["depth(\"" + child + "\", " + depth + ") :- attr(_, \"" + child + "\")"]
            depths[child] = int(depth)
            return
    

    noderules[child].extend(rules)


def generate_depths_one_parent(child, parent,noderules, G, max_depth):
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


    noderules[child].extend(rules)



def from_parent_traversal(root, G, max_depth):
    parent_list = [root]

    noderules = {}
    traversed_parents = []
    
    while parent_list:
        curr_parent = parent_list[0]
        
        
        if curr_parent in traversed_parents:
            parent_list.remove(curr_parent)
            continue


        child_list = list(G.neighbors(curr_parent))


        for child in child_list:
            if child not in noderules:
                noderules[child] = []
            
            if child == root:
                continue
                
            parent_list.append(child)
    
            predecessors = list(G.predecessors(child))

            if len(predecessors) == 1:
                generate_depths_one_parent(child, curr_parent, noderules, G, max_depth)
            else:
                generate_depths_many_parents(child, curr_parent, noderules, G, max_depth)
            
        parent_list.remove(curr_parent)
        traversed_parents.append(curr_parent)

    return noderules
        

def create_graph(root, draw):
    #----- SETUP SOLVE -----
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
    
    G = nx.MultiDiGraph()
    

    for fun in asp.extract_functions(model, "depends_on"):
        G.add_edge(fun.args[0], fun.args[1], key=-1, color='b')

    for fun in asp.extract_functions(model, "conditional_depends"):
        x = fun.args[0]
        y = fun.args[1]
        G.add_edge(x,y, key=fun.args[2], color='r')


    for fun in asp.extract_functions(model, "possible_provider"):    
        provider = fun.args[0]
        virtual = fun.args[1]
        virtuals.append(virtual)
        providers.append(provider)
        
        G.add_edge(virtual, provider, key=-2, color='y')

    if draw:
        colors = []
        for (u,v,attrib_dict) in list(G.edges.data()):
            colors.append(attrib_dict['color'])
    
        nx.draw_networkx(G, edge_color=colors)
        plt.savefig("/Users/mayataylor/Desktop/"+root+"_diag.png")                 

    return G

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("max_depth")
    parser.add_argument("root")
    
    args = parser.parse_args()
    root = args.root
    max_depth = int(args.max_depth)

    G = create_graph(root, False)
    
    rules = []
    rules.append("depth(\"" + root + "\", 0) :- attr(\"root\", \"" + root + "\")")

    depths[root] = 0
    
    noderules = from_parent_traversal(root, G, max_depth)
    for child in noderules:
        rules.extend(noderules[child])
    
    [print(a + ".") for a in rules]
     

if __name__ == "__main__":
    main()

