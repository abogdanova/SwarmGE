from algorithm import step, evaluate_fitness
from stats.stats import stats, get_stats
from algorithm.parameters import params
from utilities.trackers import cache


def search_loop_wheel():
    """Allows the user to select different main search functions."""
    if params['COMPLETE_EVALS']:
        return search_loop_complete_evals()
    else:
        return search_loop()


def search_loop():
    """Loop over max generations"""

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness.evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Traditional GE
    for generation in range(1, (params['GENERATIONS']+1)):
        stats['gen'] = generation

        # New generation
        individuals = step.step(individuals)

        # Generate statistics for run so far
        get_stats(individuals)

    return individuals


def search_loop_complete_evals():
    """Loop over total evaluations"""

    # Initialise population
    individuals = params['INITIALISATION'](params['POPULATION_SIZE'])

    # Evaluate initial population
    individuals = evaluate_fitness.evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    # Runs for a specified number of evaluations
    while len(cache) < (params['GENERATIONS'] * params['POPULATION_SIZE']):

        stats['gen'] += 1

        # New generation
        individuals = step.step(individuals)

        # Generate statistics for run so far
        get_stats(individuals)

    return individuals
