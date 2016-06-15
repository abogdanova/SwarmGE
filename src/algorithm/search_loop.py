from operators.initialisers import generate_initial_pop
from utilities.save_plot import search_loop_save_plot
from algorithm import step, evaluate_fitness
from algorithm.parameters import params
from copy import deepcopy
from stats import stats

def search_loop():
    """Loop over max generations"""

    phenotypes = {}
    fitness_plot = []
    invalids = 0
    generation = 0

    # Initialise population
    individuals = generate_initial_pop(params['BNF_GRAMMAR'])

    # Evaluate initial population
    phenotypes, individuals, invalids, regens = evaluate_fitness.evaluate_fitness(individuals, phenotypes, invalids)

    total_inds = params['POPULATION_SIZE']
    best_ever = max(individuals)
    stats.print_stats(0, individuals, best_ever, phenotypes, total_inds, invalids, regens)

    if params['COMPLETE_EVALS']:
        # Runs for a specified number of evaluations
        generation = 1
        while len(phenotypes) < (params['GENERATIONS'] * params['POPULATION_SIZE']):
            # New generation
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                    individuals, best_ever, phenotypes, invalids)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']

            # Print stats
            stats.print_stats(generation, individuals, best_ever, phenotypes,
                              total_inds, invalids, regens)
            if generation == params['GENERATIONS']:
                best_test = deepcopy(best_ever)
                if params['PROBLEM'] == "regression":
                    best_test.evaluate(dist='test')
                if not params['DEBUG']:
                    stats.save_best_midway(generation, best_test)
            if params['SAVE_PLOTS'] and not params['DEBUG']:
                search_loop_save_plot(fitness_plot, best_ever.fitness)
            generation += 1

    else:
        # Traditional GE
        for generation in range(1, (params['GENERATIONS']+1)):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                individuals, best_ever, phenotypes, invalids)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes,
                              total_inds, invalids, regens)
            if params['SAVE_PLOTS'] and not params['DEBUG']:
                search_loop_save_plot(fitness_plot, best_ever.fitness)
    return best_ever, phenotypes, total_inds, invalids, regens, generation
