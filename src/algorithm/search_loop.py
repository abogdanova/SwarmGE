from algorithm import step, evaluate_fitness
from algorithm.parameters import params
from stats import stats
from copy import deepcopy
from os import path, mkdir, getcwd
import matplotlib.pyplot as plt

def search_loop(max_generations, individuals, grammar, replacement, selection, crossover, mutation, fitness_function, time_list, TIME_STAMP):
    """Loop over max generations"""

    phenotypes = {}
    fitness_plot = []
    invalids = 0
    #Evaluate initial population
    phenotypes, individuals, invalids, regens = evaluate_fitness.evaluate_fitness(individuals, grammar, fitness_function, phenotypes, invalids, mutation)
    total_inds = params['POPULATION_SIZE']
    best_ever = max(individuals)
    stats.print_stats(0, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
    if params['COMPLETE_EVALS']:
        generation = 1
        while len(phenotypes) < (max_generations * params['POPULATION_SIZE']):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                    individuals, grammar, replacement, selection, crossover,
                    mutation, fitness_function, best_ever, phenotypes,
                    invalids, generation, TIME_STAMP)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
            if generation == max_generations:
                best_test = deepcopy(best_ever)
                best_test.evaluate(fitness_function, dist='test')
                if not params['DEBUG']:
                    #What is this!!!!!!!
                    save_best_midway(generation, best_test, TIME_STAMP, time_list)
            if params['SAVE_PLOTS']:
                file_path = getcwd()
                if not path.isdir(str(file_path) + "/Results"):
                    mkdir(str(file_path) + "/Results")
                if not path.isdir(str(file_path) + "/Results/" + str(TIME_STAMP)):
                    mkdir(str(file_path) + "/Results/" + str(TIME_STAMP))
                fitness_plot.append(best_ever.fitness)
                fig = plt.figure()#figsize=[20,15])
                ax1 = fig.add_subplot(1,1,1)
                ax1.plot(fitness_plot)
                ax1.set_ylabel('fitness', fontsize=14)
                ax1.set_xlabel('Generation', fontsize=14)
                plt.savefig(getcwd()+'/Results/'+str(TIME_STAMP)+'/fitness.pdf')
                plt.close()
            generation += 1
    else:
        for generation in range(1, (max_generations+1)):
            individuals, best_ever, phenotypes, invalids, step_regens = step.step(
                individuals, grammar, replacement, selection, crossover,
                mutation, fitness_function, best_ever, phenotypes,
                invalids, generation, TIME_STAMP)
            regens += step_regens
            total_inds += params['POPULATION_SIZE']
            stats.print_stats(generation, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP)
            if params['SAVE_PLOTS']:
                file_path = getcwd()
                if not path.isdir(str(file_path) + "/Results"):
                    mkdir(str(file_path) + "/Results")
                if not path.isdir(str(file_path) + "/Results/" + str(TIME_STAMP)):
                    mkdir(str(file_path) + "/Results/" + str(TIME_STAMP))
                fitness_plot.append(best_ever.fitness)
                fig = plt.figure()#figsize=[20,15])
                ax1 = fig.add_subplot(1,1,1)
                ax1.plot(fitness_plot)
                ax1.set_ylabel('fitness', fontsize=14)
                ax1.set_xlabel('Generation', fontsize=14)
                plt.savefig(getcwd()+'/Results/'+str(TIME_STAMP)+'/fitness.pdf')
                plt.close()
    return best_ever, phenotypes, total_inds, invalids, regens, generation