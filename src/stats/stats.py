from algorithm.parameters import params
from os import path, mkdir, getcwd
from datetime import timedelta
import time


def ave(x):
    """
    :param x: a given list
    :return: the average of param x
    """

    return sum(x)/len(x)


def print_stats(generation, individuals, best_ever, phenotypes, total_inds,
                invalids, regens):
    """Print the statistics for the generation and individuals"""
    t1 = time.clock()
    params['TIME_LIST'].append(t1)
    time_taken = timedelta(seconds=params['TIME_LIST'][-1] -
                                   params['TIME_LIST'][-2])

    print("\nGen:\t", generation)
    print("  Best fitness:\t", best_ever.fitness)
    print("  Total inds: \t", total_inds)
    if params['CACHE']:
        print("  Re-generated:\t", regens)
        print("  Unique evals:\t", len(phenotypes))
    print("  Invalid inds:\t", invalids)
    if params['CACHE']:
        print("  Unused search:",100 -
               len(phenotypes)/float(total_inds)*100, "percent")

    if params['GENOME_OPERATIONS']:
        max_depth = max([len(i.genome) for i in individuals
                         if not i.invalid])
        ave_depth = ave([len(i.genome) for i in individuals
                         if not i.invalid])
        max_nodes = max([i.used_codons for i in individuals
                         if not i.invalid])
        ave_nodes = ave([i.used_codons for i in individuals
                         if not i.invalid])
        print("  Ave genome length:", ave_depth)
        print("  Max genome length:", max_depth)
        print("  Ave used codons  :", ave_nodes)
        print("  Max used codons  :", max_nodes)

    else:
        max_depth = max([i.depth for i in individuals
                         if not i.invalid])
        ave_depth = ave([i.depth for i in individuals
                         if not i.invalid])
        max_nodes = max([i.nodes for i in individuals
                         if not i.invalid])
        ave_nodes = ave([i.nodes for i in individuals
                         if not i.invalid])
        print("  Ave tree depth:", ave_depth)
        print("  Max tree depth:", max_depth)
        print("  Ave tree nodes:", ave_nodes)
        print("  Max tree nodes:", max_nodes)

    print("  Time Taken: \t", time_taken, "\n")
    if not params['DEBUG']:
        save_results(generation, best_ever.fitness, time_taken, len(phenotypes),
                     total_inds, invalids, regens, ave_depth, max_depth,
                     ave_nodes, max_nodes)
        if params['SAVE_ALL']:
            save_best(generation, generation, best_ever)
        else:
            save_best("best", generation, best_ever)


def print_final_stats(best_ever, total_time, total_inds, phenotypes, invalids):
    """
    Prints a final review of the overall evolutionary process
    """

    print("Best " + str(best_ever))
    print("\nTime taken:\t", total_time)
    print("\nTotal evals:  \t", total_inds)
    print("Unique evals: \t", phenotypes)
    print("Invalid inds: \t", invalids)
    print("Unused search:\t", 100 -
          (phenotypes/float(total_inds))*100, "percent")
    if params['PROBLEM'] == "regression":
        print("\nBest:\n  Training fitness:\t", best_ever.fitness)
        best_ever.evaluate(dist='test')
        print("  Test fitness:\t\t", best_ever.fitness)
    else:
        print("\nBest:\n  Fitness:\t", best_ever.fitness)
    print("  Phenotype:", best_ever.phenotype)
    print("  Genome:", best_ever.genome)


def save_results(generation, fitness, time_taken, phenotypes, total_inds,
                 invalids, regens, ave_depth, max_depth, ave_nodes, max_nodes,
                 total_time=None, END=False):
    """Write the results to a results file for later analysis"""

    filename = "./Results/" + str(params['TIME_STAMP']) + "/" + str(params['TIME_STAMP'])+ ".txt"
    savefile = open(filename, 'a')
    if not END:
        savefile.write("Gen:\t" + str(generation))
        savefile.write("\tfitness:\t" + str(fitness))
        savefile.write("\tTotal inds:\t" + str(total_inds))
        savefile.write("\tRe-generated:\t" + str(regens))
        savefile.write("\tUnique evals:\t" + str(phenotypes))
        savefile.write("\tInvalid inds:\t" + str(invalids))
        savefile.write("\tUnused search:\t" + str(100 - (phenotypes/float(total_inds))*100) + " percent")
        if params['GENOME_OPERATIONS']:
            savefile.write("\tAve genome length:\t" + str(ave_depth))
            savefile.write("\tMax genome length:\t" + str(max_depth))
            savefile.write("\tAve used codons:\t" + str(ave_nodes))
            savefile.write("\tMax used codons:\t" + str(max_nodes))
        else:
            savefile.write("\tAve tree depth:\t" + str(ave_depth))
            savefile.write("\tMax tree depth:\t" + str(max_depth))
            savefile.write("\tAve tree nodes:\t" + str(ave_nodes))
            savefile.write("\tMax tree nodes:\t" + str(max_nodes))
        savefile.write("\tTime Taken:\t" + str(time_taken) + "\n")
    elif END:
        savefile.write("\n\nGrammar =      \t" +
                       str(params['GRAMMAR_FILE'].split("/")[1].split(".")[0]) +
                       "\nBest fitness = \t" + str(fitness) +
                       "\nPopulation Size = " + str(params['POPULATION_SIZE']) +
                       "\nGenerations =  \t" + str(params['GENERATIONS']) +
                       "\nMutation =     \t" + str(params['MUTATION_PROBABILITY']) +
                       "\nCrossover =    \t" + str(params['CROSSOVER_PROBABILITY']) +
                       "\nCodon Size =   \t" + str(params['CODON_SIZE']) +
                       "\nTotal inds =   \t" + str(total_inds) +
                       "\nRe-generated = \t" + str(regens) +
                       "\nUnique evals = \t" + str(phenotypes) +
                       "\nInvalid inds = \t" + str(invalids) +
                       "\nUnused search =\t" + str(100 - (phenotypes/float(total_inds))*100) + " percent"
                       "\nTotal time:\t" + str(total_time))
    savefile.close()


def save_best(name, gen, best_ever):
    filename = "./Results/" + str(params['TIME_STAMP']) + "/" + str(name) + \
               ".txt"
    savefile = open(filename, 'w')
    savefile.write("Generation:\n" + str(gen) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    savefile.write("\nfitness:\t" + str(best_ever.fitness))
    savefile.close()


def save_best_midway(gen, best_ever):
    filename = "./Results/" + str(params['TIME_STAMP']) + "/best_" + str(gen) +\
               ".txt"
    savefile = open(filename, 'w')
    t1 = time.clock()
    params['TIME_LIST'].append(t1)
    time_taken = timedelta(seconds=params['TIME_LIST'][-1] -
                           params['TIME_LIST'][0])
    savefile.write("Generation:\n" + str(gen) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    savefile.write("\nFitness:\t" + str(best_ever.fitness))
    savefile.write("\nTotal time:\t" + str(time_taken))
    savefile.close()


def generate_folders_and_files(ran_seed):
    from socket import gethostname
    hostname = gethostname().split('.')
    name = hostname[0]
    file_path = getcwd()
    if not path.isdir(str(file_path) + "/Results"):
        mkdir(str(file_path) + "/Results")
    if not path.isdir(str(file_path) + "/Results/" +
                      str(params['TIME_STAMP'])):
        mkdir(str(file_path) + "/Results/" + str(params['TIME_STAMP']))
    filename = "./Results/" + str(params['TIME_STAMP']) + "/" + \
               str(params['TIME_STAMP'])+ ".txt"
    savefile = open(filename, 'w')
    savefile.write("# Machine: " + str(name) + "\tSeed: " + str(ran_seed) +
                   "\n# Suite: " +
                   str(params['GRAMMAR_FILE'].split("/")[1].split(".")[0]) +
                   "\n#\n")
    savefile.close()
