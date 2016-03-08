from utilities.helper_methods import RETURN_PERCENT
from algorithm.parameters import POPULATION_SIZE,GENERATION_SIZE, TOURNAMENT_SIZE, SELECTION_PROPORTION
from random import sample

def tournament_selection(population):
    """Given an entire population, draw <tournament_size> competitors
    randomly and return the best."""
    tournament_size = RETURN_PERCENT(TOURNAMENT_SIZE,POPULATION_SIZE)
    winners = []
    while len(winners) < GENERATION_SIZE:
        competitors = sample(population, tournament_size)
        competitors.sort(reverse=True)
        winners.append(competitors[0])
    return winners

#Provided but no flag set. Need to append code to use this
def truncation_selection(population):
    """Given an entire population, return the best <proportion> of
    them."""
    population.sort(reverse=True)
    cutoff = int(len(population) * float(SELECTION_PROPORTION))
    return population[0:cutoff]
