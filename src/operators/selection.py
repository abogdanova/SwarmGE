from utilities.helper_methods import RETURN_PERCENT
from algorithm.parameters import params
from random import sample

def tournament_selection(population):
    """Given an entire population, draw <tournament_size> competitors
    randomly and return the best."""
    tournament_size = RETURN_PERCENT(params['TOURNAMENT_SIZE'],params['POPULATION_SIZE'])
    winners = []
    while len(winners) < params['GENERATION_SIZE']:
        competitors = sample(population, tournament_size)
        competitors.sort(reverse=True)
        winners.append(competitors[0])
    return winners

#Provided but no flag set. Need to append code to use this
def truncation_selection(population):
    """Given an entire population, return the best <proportion> of
    them."""
    population.sort(reverse=True)
    cutoff = int(len(population) * float(params['SELECTION_PROPORTION']))
    return population[0:cutoff]
