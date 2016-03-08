from algorithm import parameters
from sys import maxint


def evaluate_fitness(individuals, grammar, fitness_function, phenotypes, invalids, mutation):
    """ Perform the mapping for each individual """
    regens = 0
    for ind in individuals:
        if ind.genome and (ind.phenotype == None) and (ind.tree == None):
            ind.phenotype, ind.used_codons = grammar.generate(ind.genome)
        elif ind.tree and (ind.phenotype == None):
            ind.phenotype = ind.tree.get_output()
        if ind.phenotype == None:
            ind.fitness = maxint
            invalids += 1
        if parameters.CACHE:
            if parameters.MUTATE_DUPLICATES:
                while ind.phenotype in phenotypes:
                    ind = mutation(ind)
                    regens += 1
            if ind.phenotype and (ind.phenotype not in phenotypes):
                phenotypes[ind.phenotype] = None
                ind.evaluate(fitness_function)
                phenotypes[ind.phenotype] = ind.fitness
            else:
                if ind.phenotype and (ind.phenotype in phenotypes):
                    if parameters.LOOKUP_FITNESS:
                        ind.fitness = phenotypes[ind.phenotype]
                    elif parameters.LOOKUP_BAD_FITNESS:
                        ind.fitness = maxint
                    else:
                        ind.evaluate(fitness_function)
        else:
            if ind.phenotype:
                ind.evaluate(fitness_function)
    return phenotypes, individuals, invalids, regens