from algorithm.parameters import params
from copy import copy


def replacement(new_pop, individuals):
    """
    Given a new population and an old population, performs replacement using
    specified replacement operator
    :param new_pop: Newly generated population (after selection, variation &
    evaluation).
    :param individuals: Previous generation population
    :return: Replaced population
    """
    return params['REPLACEMENT'](new_pop, individuals)


def generational(new_pop, individuals):
    """
    Replaces the old population with the new population. The ELITE_SIZE best
    individuals from the previous population are appended to new pop regardless
    of whether or not they are better than the worst individuals in new pop.
    :param new_pop: The new population (e.g. after selection, variation, &
    evaluation).
    :param individuals: The previous generation population, from which elites
    are taken.
    :return: The 'POPULATION_SIZE' new population with elites.
    """

    individuals.sort(reverse=True)
    new_pop.sort(reverse=True)
    for ind in individuals[:params['ELITE_SIZE']]:
        new_pop.insert(0,copy(ind))
    return new_pop[:params['POPULATION_SIZE']]


# Provided but no flag set. Need to append code to use this
def steady_state(new_pop, individuals):
    """Return individuals. If the best of new pop is better than the
    worst of individuals it is inserted into individuals"""
    individuals.sort(reverse=True)
    individuals[-1] = max(new_pop + individuals[-1:])
    return individuals
