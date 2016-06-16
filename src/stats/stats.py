from utilities.save_plot import save_best_fitness_plot
from algorithm.parameters import params
from os import path, mkdir, getcwd
from datetime import timedelta
from utilities import trackers
from copy import deepcopy
from sys import stdout
import time

"""Algorithm statistics"""
stats = {

"gen" : 0,
"best_ever" : None,
"total_inds" : 0,
"regens" : 0,
"invalids" : 0,
"unique_inds" : len(trackers.cache),
"unused_search" : 0,
"ave_genome_length" : 0,
"max_genome_length" : 0,
"ave_used_codons" : 0,
"max_used_codons" : 0,
"ave_tree_depth" : 0,
"max_tree_depth" : 0,
"ave_tree_nodes" : 0,
"max_tree_nodes" : 0
}


def get_stats(individuals, END=False):
    """Generate the statistics for an evolutionary run"""

    if END or params['VERBOSE'] or not params['DEBUG']:
        t1 = time.clock()
        trackers.time_list.append(t1)
        stats['time_taken'] = timedelta(seconds=trackers.time_list[-1] -
                                                trackers.time_list[-2])
        stats['max_genome_length'] = max([len(i.genome) for i in individuals
                                          if not i.invalid])
        stats['ave_genome_length'] = ave([len(i.genome) for i in individuals
                                          if not i.invalid])
        stats['max_used_codons'] = max([i.used_codons for i in individuals
                                        if not i.invalid])
        stats['ave_used_codons'] = ave([i.used_codons for i in individuals
                                        if not i.invalid])
        stats['max_tree_depth'] = max([i.depth for i in individuals
                                       if not i.invalid])
        stats['ave_tree_depth'] = ave([i.depth for i in individuals
                                       if not i.invalid])
        stats['max_tree_nodes'] = max([i.nodes for i in individuals
                                       if not i.invalid])
        stats['ave_tree_nodes'] = ave([i.nodes for i in individuals
                                       if not i.invalid])
        stats['total_inds'] = params['POPULATION_SIZE'] * (stats['gen'] + 1)
        stats['unique_inds'] = len(trackers.cache)
        stats['unused_search'] = 100 - stats['unique_inds'] / stats['total_inds']*100
        stats['best_ever'] = max(individuals)

    if params['VERBOSE']:
        print_stats()
    else:
        perc = stats['gen'] / (params['GENERATIONS']+1) * 100
        stdout.write("Evolution: %d%% complete\r" % (perc))
        stdout.flush()

    if params['COMPLETE_EVALS'] and not params['DEBUG']:
        if stats['gen'] == params['GENERATIONS']:
            best_test = deepcopy(stats['best_ever'])
            if params['PROBLEM'] == "regression":
                best_test.evaluate(dist='test')
            save_best_midway(best_test)

    if not params['DEBUG']:
        save_stats()
        if params['SAVE_ALL']:
            save_best(stats['gen'])
        else:
            save_best("best")

    if params['SAVE_PLOTS'] and not params['DEBUG']:
        trackers.best_fitness_list.append(stats['best_ever'].fitness)
        save_best_fitness_plot()

    if END:
        total_time = timedelta(seconds=(trackers.time_list[-1] -
                                        trackers.time_list[0]))
        print_final_stats(total_time)
        if not params['DEBUG']:
            save_final_stats(total_time)


def ave(x):
    """
    :param x: a given list
    :return: the average of param x
    """

    return sum(x)/len(x)


def print_stats():
    """Print the statistics for the generation and individuals"""

    print("______\n")
    for stat in stats:
        print(" ", stat, ": \t", stats[stat])
    print("\n")


def save_stats():
    """Write the results to a results file for later analysis"""

    filename = "./results/" + str(params['TIME_STAMP']) + "/stats.csv"
    savefile = open(filename, 'a')

    for stat in stats:
        savefile.write(str(stat) + "\t" + str(stats[stat]) + "\t")
    savefile.write("\n")
    savefile.close()


def print_final_stats(total_time):
    """
    Prints a final review of the overall evolutionary process
    """

    print("Best " + str(stats['best_ever']))
    print("\nTime taken:\t", total_time)
    print("\nTotal evals:  \t", stats['total_inds'])
    print("Unique evals: \t", stats['unique_inds'])
    print("Invalid inds: \t", stats['invalids'])
    print("Unused search:\t", stats['unused_search'], "percent")
    if params['PROBLEM'] == "regression":
        print("\nBest:\n  Training fitness:\t", stats['best_ever'].fitness)
        stats['best_ever'].evaluate(dist='test')
        print("  Test fitness:\t\t", stats['best_ever'].fitness)
    else:
        print("\nBest:\n  Fitness:\t", stats['best_ever'].fitness)
    print("  Phenotype:", stats['best_ever'].phenotype)
    print("  Genome:", stats['best_ever'].genome)


def save_final_stats(total_time):
    """
    Appends the total time taken for a run to the stats file.
    """

    filename = "./results/" + str(params['TIME_STAMP']) + "/stats.csv"
    savefile = open(filename, 'a')
    savefile.write("Total time taken\t" + str(total_time))
    savefile.close()


def save_best(name="best"):
    filename = "./results/" + str(params['TIME_STAMP']) + "/" + str(name) + \
               ".txt"
    savefile = open(filename, 'w')
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(stats['best_ever'].phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(stats['best_ever'].genome) + "\n")
    savefile.write("Tree:\n" + str(stats['best_ever'].tree) + "\n")
    savefile.write("\nfitness:\t" + str(stats['best_ever'].fitness))
    savefile.close()


def save_best_midway(best_ever):
    filename = "./results/" + str(params['TIME_STAMP']) + "/best_" + str(stats['gen']) +\
               ".txt"
    savefile = open(filename, 'w')
    t1 = time.clock()
    trackers.time_list.append(t1)
    time_taken = timedelta(seconds=trackers.time_list[-1] -
                           trackers.time_list[0])
    savefile.write("Generation:\n" + str(stats['gen']) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    savefile.write("\nFitness:\t" + str(best_ever.fitness))
    savefile.write("\nTotal time:\t" + str(time_taken))
    savefile.close()


def generate_folders_and_files():
    """
    Generates necessary folders and files for saving statistics and parameters.
    """

    # Generate save folders
    file_path = getcwd()
    if not path.isdir(str(file_path) + "/results"):
        mkdir(str(file_path) + "/results")
    if not path.isdir(str(file_path) + "/results/" +
                      str(params['TIME_STAMP'])):
        mkdir(str(file_path) + "/Results/" + str(params['TIME_STAMP']))

    # Save evolutionary parameters
    filename = "./results/" + str(params['TIME_STAMP']) + "/parameters.txt"
    savefile = open(filename, 'w')
    for param in params:
        savefile.write("\n" + str(param) + " : \t" + str(params[param]))
    savefile.close()
