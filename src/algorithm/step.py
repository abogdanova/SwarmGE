from algorithm import parameters,evaluate_fitness
from copy import deepcopy
from random import sample

def step(individuals, grammar, replacement, selection, crossover, mutation, fitness_function, best_ever, phenotypes, invalids, gen, TIME_STAMP):
    """Return individuals and best ever individual from a step of
    the EA iteration"""
    #Select parents
    parents = selection(individuals)
    #Crossover parents and add to the new population
    cross_pop = []
    while len(cross_pop) < parameters.GENERATION_SIZE:
        cross_pop.extend(crossover(*sample(parents, 2)))
    #Mutate the new population
    new_pop = list(map(mutation, deepcopy(cross_pop)))
    #Evaluate the fitness of the new population
    phenotypes, new_pop, invalids, regens = evaluate_fitness.evaluate_fitness(new_pop, grammar, fitness_function, phenotypes, invalids, mutation)
    #Replace the sorted individuals with the new populations
    individuals = replacement(new_pop, individuals)
    best_ever = max(best_ever, max(individuals))
    print "______"
    return individuals, best_ever, phenotypes, invalids, regens