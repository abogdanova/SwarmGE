from fitness.fitness import default_fitness
from algorithm.parameters import params
from utilities.trackers import cache
from stats.stats import stats


def evaluate_fitness(individuals):
    """ Perform the mapping for each individual """

    for ind in individuals:
        if ind.invalid:
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            stats['invalids'] += 1
        else:
            if params['CACHE']:
                if ind.phenotype not in cache:
                    cache[ind.phenotype] = None
                    ind.evaluate()
                    cache[ind.phenotype] = ind.fitness
                else:
                    if params['LOOKUP_FITNESS']:
                        ind.fitness = cache[ind.phenotype]
                    elif params['LOOKUP_BAD_FITNESS']:
                        ind.fitness = default_fitness(
                            params['FITNESS_FUNCTION'].maximise)
                    elif params['MUTATE_DUPLICATES']:
                        while ind.phenotype in cache:
                            ind = params['MUTATION'](ind)
                            stats['regens'] += 1
                        ind.evaluate()
                        cache[ind.phenotype] = ind.fitness
                    else:
                        ind.evaluate()
            else:
                ind.evaluate()

    return individuals
