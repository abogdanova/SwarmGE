from fitness.fitness import default_fitness
from algorithm.parameters import params
from utilities.trackers import cache
from multiprocessing import Pool
from stats.stats import stats


def evaluation(individuals):
    if params['MULTICORE']:
        return evaluate_fitness_multicore(individuals)
    else:
        return evaluate_fitness(individuals)


def evaluate_fitness(individuals):
    """ Perform the mapping for each individual """

    for ind in individuals:
        if ind.invalid:
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            stats['invalids'] += 1
        else:
            if params['CACHE']:
                if ind.phenotype not in cache:
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


def evaluate_fitness_multicore(individuals):
    """ Perform the mapping for each individual """

    pool = Pool(processes=params['CORES'])  # , maxtasksperchild=1)
    results = []

    for name, ind in enumerate(individuals):
        ind.name = name
        if ind.invalid:
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            stats['invalids'] += 1
        else:
            if params['CACHE']:
                if ind.phenotype not in cache:
                    results.append(pool.apply_async(ind.evaluate, ()))
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
                        results.append(pool.apply_async(ind.evaluate, ()))
                    else:
                        results.append(pool.apply_async(ind.evaluate, ()))
            else:
                results.append(pool.apply_async(ind.evaluate, ()))

    for result in results:
        ind = result.get()
        individuals[ind.name] = ind
        cache[ind.phenotype] = ind.fitness

    return individuals
