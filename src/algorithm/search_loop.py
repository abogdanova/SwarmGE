from copy import deepcopy
from algorithm import step, evaluate_fitness
from algorithm.parameters import params
from stats import stats
from utilities.save_plot import search_loop_save_plot

def search_loop(max_generations, individuals):
    """Loop over max generations"""

    phenotypes = {}
    fitness_plot = []
    invalids = 0
    #Evaluate initial population
    phenotypes, individuals, invalids, regens = evaluate_fitness.evaluate_fitness(individuals, phenotypes, invalids)
    total_inds = params['POPULATION_SIZE']
    best_ever = max(individuals)
    stats.print_stats(0, individuals, best_ever, phenotypes, total_inds, invalids, regens)
    #This runs for a certain number of evals
    if params['COMPLETE_EVALS']:
        generation = 1
        while len(phenotypes) < (max_generations * params['POPULATION_SIZE']):
            # New generation
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                    individuals, best_ever, phenotypes, invalids)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']

            # Print stats
            stats.print_stats(generation, individuals, best_ever, phenotypes,
                              total_inds, invalids, regens)
            if generation == max_generations:
                best_test = deepcopy(best_ever)
                if params['PROBLEM'] == "regression":
                    best_test.evaluate(dist='test')
                if not params['DEBUG']:
                    stats.save_best_midway(generation, best_test)
            if params['SAVE_PLOTS']:
                search_loop_save_plot(fitness_plot, best_ever.fitness)
            generation += 1
    #This is traditional GE
    else:
        for generation in range(1, (max_generations+1)):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                individuals, best_ever, phenotypes, invalids)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes,
                              total_inds, invalids, regens)
            if params['SAVE_PLOTS']:
                search_loop_save_plot(fitness_plot, best_ever.fitness)
    return best_ever, phenotypes, total_inds, invalids, regens, generation