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


def main():
    listofResults = MPE(CPTs, Os)
    print(listofResults)

def objectiveFunctions(CPTs, Os, variablesZ3, var_dependencies):
    objectiveFunction = 1
    for cpt in CPTs:
        var = cpt[0]
        indepProbability = 0
        conditionalProbability = 0
        if len(var_dependencies[var]) == 0:
            for triplets in cpt[1]:
                indepProbability  += (triplets[2] * 100 * variablesZ3[var]) if triplets[1][1] == "T" else (triplets[2] * 100 * (1-variablesZ3[var]))                    
            objectiveFunction *= indepProbability
        else:
            for triplets in cpt[1]:
                prob = 1
                for cond in triplets[0]:
                    prob *= variablesZ3[cond[0]] if cond[1] == "T" else (1-variablesZ3[cond[0]])
                prob *= (triplets[2] * 100) * variablesZ3[var] if triplets[1][1] == "T" else (triplets[2] * 100) * (1-variablesZ3[var])
                conditionalProbability += prob
            objectiveFunction *= conditionalProbability
    return objectiveFunction

# function MPE(CPTs, Os) returns a list of pairs of variables and values
def MPE(CPTs, Os):
    variablesZ3 = {}
    var_dependencies = {}
    s = Optimize()

    for cpt in CPTs:
        var_dependencies[cpt[0]] = []
        triplets = cpt[1][0]
        for dependent in triplets[0]:
            var_dependencies[cpt[0]].append(dependent[0])

    for observed_pair in Os:
        variablesZ3[observed_pair[0]] = 1 if observed_pair[1] == "T" else 0
    for var in var_dependencies:
        if var not in variablesZ3.keys():
            variablesZ3[var] = Int(var)
            s.add(And(Int(var) >= 0, Int(var) <= 1))

    objectiveFunction = objectiveFunctions(CPTs, Os, variablesZ3, var_dependencies)
    s.maximize(objectiveFunction)
    if s.check() == sat:
        listofResults = []
        model = s.model()
        for variable in model:
            listofResults.append([variable, "T"]) if model[variable] == 1 else listofResults.append([variable, "F"])
        return listofResults
    else:
        print("False: error to solve the problem!")


if __name__== "__main__":
    main()
