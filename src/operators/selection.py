from algorithm.parameters import params
from random import sample


def selection(population):
    """
    Perform selection on a population
    :param population: input population
    :return: selected population
    """
    return params['SELECTION'](population)


def tournament(population):
    """Given an entire population, draw <tournament_size> competitors
    randomly and return the best."""

    tournament_size = params['TOURNAMENT_SIZE']
    winners = []
    if params['INVALID_SELECTION']:
        available = population
    else:
        available = [i for i in population if not i.invalid]
    while len(winners) < params['GENERATION_SIZE']:
        competitors = sample(available, tournament_size)
        competitors.sort(reverse=True)
        winners.append(competitors[0])
    return winners


# Provided but no flag set. Need to append code to use this
def truncation(population):
    """Given an entire population, return the best <proportion> of
    them."""
    population.sort(reverse=True)
    cutoff = int(len(population) * float(params['SELECTION_PROPORTION']))
    return population[0:cutoff]
