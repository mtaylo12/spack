#!/usr/bin/env spack-python

import json
from pandas import DataFrame as df
import argparse

#parse arguments
parse = argparse.ArgumentParser()
parse.add_argument('dictfile')
parse.add_argument('-f', '--filteron', default=None)

args = parse.parse_args()
inputfn = args.dictfile
filteron = args.filteron

encoding = ["Error", "Depth", "Index", "Weights Match", "Attrs Match", "Deep At\
tr Outliers", "Stand Attr Outliers"]

def create(dictlist, filteron=None):
    data=[]
    finaldict = {}

    with open(dictlist) as f:
        data.extend(f.readlines())

        for d in data:
            finaldict.update(json.loads(d))

    if filteron:
        with open(filteron) as f:
            package_names = f.read().splitlines()
            filtered_dict = {key : finaldict[key] for key in package_names}
            finaldict = filtered_dict
        
    print("Filtered dict of size:", len(finaldict))
    dataframe = df.from_dict(finaldict, orient='index', columns=encoding)
    return dataframe

#Group data by categories listed in clist and show count in each category.
def group_count(clist, data):
    data_grouped = data.groupby(clist).size().reset_index(name="Count")
    total = data_grouped['Count'].sum()
    data_grouped['Percent'] = data_grouped['Count'].div(total)
    return data_grouped

#Clean the Index column to replace nonzero numbers with a single value. Useful for grouping by Index.
def cleanIndex(data):
    data.loc[data.Index == 0, "Index"] = "0"
    data.loc[data.Index != "0", "Index"] = "!=0"
    return data

dataframe = create(inputfn, filteron)
dataframe = cleanIndex(dataframe)
dataframe = group_count(["Index", "Weights Match", "Attrs Match"], dataframe)
print(dataframe)
