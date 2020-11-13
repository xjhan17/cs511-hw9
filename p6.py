from z3 import *
import sys
import numpy as np
import ast
import json

CPTs = [
    ["V1", [[[], ["V1", "T"], 0.8], [[], ["V1", "F"], 0.2]]],
    ["V2", [[[], ["V2", "T"], 0.7], [[], ["V2", "F"], 0.3]]],
    ["V3", [[[["V1", "F"], ["V2", "F"]], ["V3", "F"], 0.9],
           [[["V1", "F"], ["V2", "F"]], ["V3", "T"], 0.1],
           [[["V1", "F"], ["V2", "T"]], ["V3", "F"], 0.2],
           [[["V1", "F"], ["V2", "T"]], ["V3", "T"], 0.8],
           [[["V1", "T"], ["V2", "F"]], ["V3", "F"], 0.3],
           [[["V1", "T"], ["V2", "F"]], ["V3", "T"], 0.7],
           [[["V1", "T"], ["V2", "T"]], ["V3", "F"], 0.4],
           [[["V1", "T"], ["V2", "T"]], ["V3", "T"], 0.6]]],
    ["V4", [[[], ["V4", "T"], 0.1], [[], ["V4", "F"], 0.9]]],
    ["V5", [[[["V3", "F"], ["V4", "F"]], ["V5", "F"], 0.1],
           [[["V3", "F"], ["V4", "F"]], ["V5", "T"], 0.9],
           [[["V3", "F"], ["V4", "T"]], ["V5", "F"], 0.2],
           [[["V3", "F"], ["V4", "T"]], ["V5", "T"], 0.8],
           [[["V3", "T"], ["V4", "F"]], ["V5", "F"], 0.7],
           [[["V3", "T"], ["V4", "F"]], ["V5", "T"], 0.3],
           [[["V3", "T"], ["V4", "T"]], ["V5", "F"], 0.4],
           [[["V3", "T"], ["V4", "T"]], ["V5", "T"], 0.6]]]
]
Os = [["V1", "T"]]
Vs = ["V5"]

dependencies = {}
variablesZ3Py = {}


def main():
    listofResults = MAP(CPTs, Os, Vs)
    print(listofResults)

# function MAP(CPTs, Os, Vs) returns a list of pairs of variables and values
def MAP(CPTs, Os, Vs):
    s = Optimize()
    for cpt in CPTs:
        dependencies[cpt[0]] = cpt[1]

    observed_vars = []
    for pairs in Os:
        observed_vars.append(pairs[0])
        variablesZ3Py[pairs[0]] = 1 if pairs[1] == "T" else 0

    objectiveFunction = objectiveFunctions(CPTs, Os, Vs)

    for variables in Vs:
        s.add(And(Int(variables) >= 0, Int(variables) <= 1))

    s.maximize(objectiveFunction)
    if s.check() == sat:
        listofResults = []
        model = s.model()
        for variable in model:
            listofResults.append([variable, "T"]) if model[variable] == 1 else listofResults.append([variable, "F"])
        return listofResults
    else:
        print("False: error to solve the problem!")

def objectiveFunctions(CPTs, Os, Vs):
    objectiveFunction = 1
    for variables in Vs:
        variablesZ3Py[variables] = Int(variables)
        [true, false] = recursiveFunction(variables)
        objectiveFunction *= (Int(variables)*true+(1-Int(variables))*false)
    return objectiveFunction
    
def recursiveFunction(variables):
    triplets = dependencies[variables]
    trueProbability = 0
    falseProbabilty = 0
    for triplet in triplets:
        if len(triplet[0]) == 0:
            if triplet[1][1] == "T":
                trueProbability = triplet[2]*100
            else:
                falseProbabilty = triplet[2]* 00
        else:
            variableProbability = triplet[2]*100
            for condition in triplet[0]:
                [trueDep, falseDep] = recursiveFunction(condition[0])
                if condition[0] not in variablesZ3Py.keys():
                    variableProbability *= trueDep if condition[1] == "T" else falseDep
                else:
                    variableProbability *= variablesZ3Py[condition[0]] if condition[1] == "T" else (1-variablesZ3Py[condition[0]])  
            if triplet[1][1] == "T":
                trueProbability += variableProbability
            else:
                falseProbabilty += variableProbability
    return [trueProbability, falseProbabilty]


if __name__== "__main__":
    main()
