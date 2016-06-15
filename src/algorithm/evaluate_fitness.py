from fitness.fitness import default_fitness
from algorithm.parameters import params


def evaluate_fitness(individuals, phenotypes, invalids):
    """ Perform the mapping for each individual """
    regens = 0
    for ind in individuals:
        if ind.invalid:
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            invalids += 1
        else:
            if params['CACHE']:
                if ind.phenotype not in phenotypes:
                    phenotypes[ind.phenotype] = None
                    ind.evaluate()
                    phenotypes[ind.phenotype] = ind.fitness
                else:
                    if params['MUTATE_DUPLICATES']:
                        while ind.phenotype in phenotypes:
                            ind = params['MUTATION'](ind)
                            regens += 1
                        ind.evaluate()
                        phenotypes[ind.phenotype] = ind.fitness
                    elif params['LOOKUP_FITNESS']:
                        ind.fitness = phenotypes[ind.phenotype]
                    elif params['LOOKUP_BAD_FITNESS']:
                        ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
                    else:
                        ind.evaluate()
            else:
                ind.evaluate()

    return phenotypes, individuals, invalids, regens