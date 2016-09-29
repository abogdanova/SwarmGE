from fitness.fitness import default_fitness
from algorithm.parameters import params
from utilities.trackers import cache
from multiprocessing import Pool
from stats.stats import stats


def evaluation(individuals):
    """
    Wheel for evaluation. Calls the correct evaluation function based on the
    parameters specified in the params dictionary.
    
    :param individuals: A population of individuals to be evaluated.
    :return: The output of the correct evaluation function.
    """
    
    if params['MULTICORE']:
        # Perform multicore evaluation
        
        return evaluate_fitness_multicore(individuals)
    else:
        # Perform single core evaluation
        
        return evaluate_fitness(individuals)


def evaluate_fitness(individuals):
    """
    Evaluate an entire population of individuals sequentially. Invalid
    individuals are given a default bad fitness. If params['CACHE'] is
    specified then individuals have their fitness stored in a dictionary called
    utilities.trackers.cache. Dictionary keys are the string of the phenotype.
    There are currently three options for use with the cache:
        1. If params['LOOKUP_FITNESS'] is specified (default case if
           params['CACHE'] is specified), individuals which have already been
           evaluated have their previous fitness read directly from the cache,
           thus saving fitness evaluations.
        2. If params['LOOKUP_BAD_FITNESS'] is specified, individuals which
           have already been evaluated are given a default bad fitness.
        3. If params['MUTATE_DUPLICATES'] is specified, individuals which
           have already been evaluated are mutated to produce new unique
           individuals which have not been encountered yet by the search
           process.
    
    :param individuals: A population of individuals to be evaluated.
    :return: A population of fully evaluated individuals.
    """

    for ind in individuals:
        # Iterate over all individuals in the population.
        if ind.invalid:
            # Invalid individuals cannot be evaluated and are given a bad
            # default fitness.
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            stats['invalids'] += 1
        
        else:
            # Valid individuals can be evaluated.
            if params['CACHE']:
                # Use the fitness cache in utilities.trackers.cache.
                if ind.phenotype not in cache:
                    # The phenotype string of the individual does not appear
                    # in the cache, it must be evaluated and added to the
                    # cache.
                    ind.evaluate()
                    cache[ind.phenotype] = ind.fitness
                
                else:
                    # The phenotype string of the individual has already
                    # appeared in the cache.
                    if params['LOOKUP_FITNESS']:
                        # Set the fitness as the previous fitness from the
                        # cache.
                        ind.fitness = cache[ind.phenotype]

                    elif params['LOOKUP_BAD_FITNESS']:
                        # Give the individual a bad default fitness.
                        ind.fitness = default_fitness(
                            params['FITNESS_FUNCTION'].maximise)

                    elif params['MUTATE_DUPLICATES']:
                        # Mutate the individual to produce a new phenotype
                        # which has not been encountered yet.
                        while ind.phenotype in cache:
                            ind = params['MUTATION'](ind)
                            stats['regens'] += 1
                        
                        # Evaluate the new individual and add it to the cache.
                        ind.evaluate()
                        cache[ind.phenotype] = ind.fitness
                    
                    else:
                        # Evaluate the individual.
                        ind.evaluate()
            else:
                # Evaluate the individual.
                ind.evaluate()

    return individuals


def evaluate_fitness_multicore(individuals):
    """
    Evaluate an entire population of individuals in parallel. Invalid
    individuals are given a default bad fitness. If params['CACHE'] is
    specified then individuals have their fitness stored in a dictionary called
    utilities.trackers.cache. Dictionary keys are the string of the phenotype.
    There are currently three options for use with the cache:
        1. If params['LOOKUP_FITNESS'] is specified (default case if
           params['CACHE'] is specified), individuals which have already been
           evaluated have their previous fitness read directly from the cache,
           thus saving fitness evaluations.
        2. If params['LOOKUP_BAD_FITNESS'] is specified, individuals which
           have already been evaluated are given a default bad fitness.
        3. If params['MUTATE_DUPLICATES'] is specified, individuals which
           have already been evaluated are mutated to produce new unique
           individuals which have not been encountered yet by the search
           process.
    
    :param individuals: A population of individuals to be evaluated.
    :return: A population of fully evaluated individuals.
    """

    # Initialise a pool of jobs for multicore process workers.
    pool = Pool(processes=params['CORES'])  # , maxtasksperchild=1)
    results = []

    for name, ind in enumerate(individuals):
        # Iterate over all individuals in the population.
        ind.name = name
        if ind.invalid:
            # Invalid individuals cannot be evaluated and are given a bad
            # default fitness.
            ind.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            stats['invalids'] += 1
        
        else:
            # Valid individuals can be evaluated.
            if params['CACHE']:
                # Use the fitness cache in utilities.trackers.cache.
                if ind.phenotype not in cache:
                    # The phenotype string of the individual does not appear
                    # in the cache, it must be added to the pool of jobs.
                    results.append(pool.apply_async(ind.evaluate, ()))
                
                else:
                    # The phenotype string of the individual has already
                    # appeared in the cache.
                    if params['LOOKUP_FITNESS']:
                        # Set the fitness as the previous fitness from the
                        # cache.
                        ind.fitness = cache[ind.phenotype]
                    
                    elif params['LOOKUP_BAD_FITNESS']:
                        # Give the individual a bad default fitness.
                        ind.fitness = default_fitness(
                            params['FITNESS_FUNCTION'].maximise)
                    
                    elif params['MUTATE_DUPLICATES']:
                        # Mutate the individual to produce a new phenotype
                        # which has not been encountered yet.
                        while ind.phenotype in cache:
                            ind = params['MUTATION'](ind)
                            stats['regens'] += 1
                        
                        # Add the new individual to the pool of jobs.
                        results.append(pool.apply_async(ind.evaluate, ()))
                    
                    else:
                        # Add the individual to the pool of jobs.
                        results.append(pool.apply_async(ind.evaluate, ()))
            else:
                # Add the individual to the pool of jobs.
                results.append(pool.apply_async(ind.evaluate, ()))

    for result in results:
        # Execute all jobs in the pool.
        ind = result.get()
        
        # Set the fitness of the evaluated individual by placing the
        # evaluated individual back into the population.
        individuals[ind.name] = ind
        
        # Add the evaluated individual to the cache.
        cache[ind.phenotype] = ind.fitness

    return individuals
