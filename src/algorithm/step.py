from algorithm.parameters import params
from algorithm import evaluate_fitness
from operators import crossover
from copy import deepcopy

def step(individuals, best_ever, phenotypes, invalids):
    """Return individuals and best ever individual from a step of
    the EA iteration"""
    #Select parents
    parents = params['SELECTION'](individuals)
    #Crossover parents and add to the new population
    cross_pop = crossover.crossover(parents)
    #Mutate the new population
    new_pop = list(map(params['MUTATION'], deepcopy(cross_pop)))
    #Evaluate the fitness of the new population
    phenotypes, new_pop, invalids, \
    regens = evaluate_fitness.evaluate_fitness(new_pop, phenotypes, invalids)
    #Replace the sorted individuals with the new populations
    individuals = params['REPLACEMENT'](new_pop, individuals)
    best_ever = max(best_ever, max(individuals))
    print ("______")
    return individuals, best_ever, phenotypes, invalids, regens