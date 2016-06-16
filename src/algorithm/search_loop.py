from stats.stats import stats, save_best_midway, get_stats
from operators.initialisers import generate_initial_pop
from algorithm import step, evaluate_fitness
from algorithm.parameters import params
from utilities.trackers import cache

#TODO Setup a search loop wheel for added experimental setting
def search_loop():
    """Loop over max generations"""

    # Initialise population
    individuals = generate_initial_pop(params['BNF_GRAMMAR'])

    # Evaluate initial population
    individuals = evaluate_fitness.evaluate_fitness(individuals)

    # Generate statistics for run so far
    get_stats(individuals)

    if params['COMPLETE_EVALS']:
        # Runs for a specified number of evaluations
        while len(cache) < (params['GENERATIONS'] * params['POPULATION_SIZE']):

            stats['gen'] += 1

            # New generation
            individuals = step.step(individuals)

            # Generate statistics for run so far
            get_stats(individuals)

    else:
        # Traditional GE
        for generation in range(1, (params['GENERATIONS']+1)):
            stats['gen'] = generation

            # New generation
            individuals = step.step(individuals)

            # Generate statistics for run so far
            get_stats(individuals)

    return individuals
