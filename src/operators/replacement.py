from fitness.evaluation import evaluate_fitness
from algorithm.parameters import params


def replacement(new_pop, old_pop):
    """
    Given a new population and an old population, performs replacement using
    specified replacement operator.
    
    :param new_pop: Newly generated population (after selection, variation &
    evaluation).
    :param old_pop: The previous generation population.
    :return: Replaced population.
    """
    return params['REPLACEMENT'](new_pop, old_pop)


def generational(new_pop, old_pop):
    """
    Replaces the old population with the new population. The ELITE_SIZE best
    individuals from the previous population are appended to new pop regardless
    of whether or not they are better than the worst individuals in new pop.
    
    :param new_pop: The new population (e.g. after selection, variation, &
    evaluation).
    :param old_pop: The previous generation population, from which elites
    are taken.
    :return: The 'POPULATION_SIZE' new population with elites.
    """

    # Sort both populations.
    old_pop.sort(reverse=True)
    new_pop.sort(reverse=True)
    
    # Append the best ELITE_SIZE individuals from the old population to the
    # new population.
    for ind in old_pop[:params['ELITE_SIZE']]:
        new_pop.insert(0, ind)
    
    # Return the top POPULATION_SIZE individuals of the new pop, including
    # elites.
    return new_pop[:params['POPULATION_SIZE']]


def steady_state(individuals):
    """
    Runs a single generation of the evolutionary algorithm process,
    using steady state replacement:
        Selection
        Variation
        Evaluation
        Replacement

    :param individuals: The current generation, upon which a single
    evolutionary generation will be imposed.
    :return: The next generation of the population.
    """

    # Initialise counter for new individuals.
    ind_counter = 0

    while ind_counter < params['POPULATION_SIZE']:
        
        # Select parents from the original population.
        parents = params['SELECTION'](individuals)

        # Create copies of the original parents. This is necessary as the
        # original parents remain in the parent population and changes will
        # affect the originals unless they are cloned.
        ind_0 = parents[0].deep_copy()
        ind_1 = parents[1].deep_copy()

        # Crossover cannot be performed on invalid individuals.
        if not params['INVALID_SELECTION'] and ind_0.invalid or ind_1.invalid:
            s = "operators.crossover.crossover\nError: invalid individuals " \
                "selected for crossover."
            raise Exception(s)

        # Perform crossover on ind_0 and ind_1.
        inds = params['CROSSOVER'](ind_0, ind_1)

        if params['NO_CROSSOVER_INVALIDS'] and \
                any([ind.invalid for ind in inds]):
            # We have an invalid, need to do crossover again.
            pass

        elif params['MAX_TREE_DEPTH'] and \
                any([ind.depth > params['MAX_TREE_DEPTH'] for ind in inds]):
            # Tree is too deep, need to do crossover again.
            pass

        elif params['MAX_TREE_NODES'] and \
                any([ind.nodes > params['MAX_TREE_NODES'] for ind in inds]):
            # Tree has too many nodes, need to do crossover again.
            pass

        elif params['MAX_GENOME_LENGTH'] and \
                any([len(ind.genome) > params['MAX_GENOME_LENGTH'] for ind in
                     inds]):
            # Genome is too long, need to do crossover again.
            pass
    
        # Initialise empty pop for mutation
        new_pop = []
        
        for ind in inds:
            # Mutate each individual.
            new_pop.append(params['MUTATION'](ind))
    
        # Evaluate the fitness of the new population.
        new_pop = evaluate_fitness(new_pop)

        # Sort the original population
        individuals.sort(reverse=True)

        # Combine both populations
        total_pop = individuals[:-len(new_pop)] + new_pop
    
        # Increment the ind counter
        ind_counter += params['GENERATION_SIZE']

    # Return the combined population.
    return total_pop
