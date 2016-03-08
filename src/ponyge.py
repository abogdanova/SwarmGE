#! /usr/bin/env python

# PonyGE
# Copyright (c) 2009 Erik Hemberg, James McDermott, Michael Fenton and David Fagan
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

from __future__ import division

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')
from random import seed
from os import path, mkdir, getcwd
from datetime import datetime, timedelta
import sys
from representation import grammar
from algorithm import parameters, search_loop
from operators import initialisers,mutation,crossover,selection,replacement
from fitness.fitness_wheel import set_fitness_function
from stats import stats
import time

def mane(SEED):
    """ Run program """
    # Read grammar
    time1 = datetime.now()
    ran_seed = SEED

    seed(ran_seed)

    if parameters.GENOME_OPERATIONS:
        version = "GE"
    else:
        version = "GGP"

    time_list = [time.clock()]
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    TIME_STAMP = (str(time1.year)[2:] + "_" + str(time1.month) + "_" + str(time1.day) + "_" + hms + "_" + str(time1.microsecond))
    print "\nStart:\t", time1, "\n"
    if parameters.DEBUG:
        print "Seed:\t", ran_seed, "\n"
    else:
        from socket import gethostname
        hostname = gethostname().split('.')
        name = hostname[0]
        file_path = getcwd()
        if not path.isdir(str(file_path) + "/Results"):
            mkdir(str(file_path) + "/Results")
        if not path.isdir(str(file_path) + "/Results/" + str(TIME_STAMP)):
            mkdir(str(file_path) + "/Results/" + str(TIME_STAMP))
        filename = "./Results/" + str(TIME_STAMP) + "/" + str(TIME_STAMP)+ ".txt"
        savefile = open(filename, 'w')
        savefile.write("# Machine: " + str(name) + "\tSeed: " + str(ran_seed) + "\n# Version: " + str(version) + "\n# Suite: " + str(parameters.GRAMMAR_FILE.split("/")[1].split(".")[0]) + "\n#\n")
        savefile.close()

    #Set Fitness Funtion
    parameters.FITNESS_FUNCTION = set_fitness_function(parameters.PROBLEM, parameters.ALTERNATE)
    #Set Grammar File
    bnf_grammar = grammar.grammar(parameters.GRAMMAR_FILE)

    #Calculate the minimum ramping level for the grammar
    bnf_grammar.min_ramp = initialisers.get_min_ramp_depth(parameters.POPULATION_SIZE, bnf_grammar, parameters.MAX_TREE_DEPTH)

    # Create Individuals
    if parameters.INITIALISATION == "random":
        individuals = initialisers.random_initialisation(parameters.POPULATION_SIZE, bnf_grammar, parameters.GENOME_INIT)
    elif parameters.INITIALISATION == "rhh":
        individuals = initialisers.rhh_initialisation(parameters.POPULATION_SIZE, bnf_grammar, parameters.MAX_TREE_DEPTH)
    else:
        print "Error: initialisation method not recognised"
        quit()

    # Loop
    # We can probably remove the likes of crossover and mutation from this and set them directly in step
    # We should probably parameterise things more.
    if parameters.GENOME_OPERATIONS:
        best_ever, phenotypes, total_inds, invalids, regens, final_gen = search_loop.search_loop(
                            parameters.GENERATIONS, individuals, bnf_grammar,
                            replacement.generational_replacement, selection.tournament_selection,
                            crossover.onepoint_crossover, mutation.int_flip_mutation,
                            parameters.FITNESS_FUNCTION, time_list, TIME_STAMP)
    else:
        best_ever, phenotypes, total_inds, invalids, regens, final_gen = search_loop.search_loop(
                            parameters.GENERATIONS, individuals, bnf_grammar,
                            replacement.generational_replacement, selection.tournament_selection,
                            crossover.subtree_crossover, mutation.subtree_mutation,
                            parameters.FITNESS_FUNCTION, time_list, TIME_STAMP)
    #END LOOP

    #Print Some stats - MOVE ME TO STATS MAYBE
    print("Best " + str(best_ever))
    time_list.append(time.clock())
    total_time = timedelta(seconds = (time_list[-1] - time_list[0]))
    print "\nTime taken:\t", total_time
    print "\nTotal evals:  \t", total_inds
    print "Unique evals: \t", len(phenotypes)
    print "Invalid inds: \t", invalids
    print "Unused search:\t", 100 - (len(phenotypes)/float(total_inds))*100,"percent"
    print "\nBest:\n  Training fitness:\t", best_ever.fitness
    best_ever.evaluate(parameters.FITNESS_FUNCTION, dist='test')
    print "  Test fitness:\t\t", best_ever.fitness
    print "  Phenotype:", best_ever.phenotype
    print "  Genome:", best_ever.genome
    if not parameters.DEBUG:
        stats.save_best("best", final_gen, best_ever, TIME_STAMP)
        stats.save_results(final_gen, best_ever.fitness, total_time, len(phenotypes), total_inds, invalids, regens, None, None, None, None, TIME_STAMP, total_time=total_time, END=True)
    return TIME_STAMP, best_ever.fitness

if __name__ == "__main__":
    import getopt
    try:
        #FIXME help option
        print(sys.argv)
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "p:g:e:m:x:b:f:",
                                   ["population", "generations",
                                    "elite_size", "mutation", "crossover",
                                    "bnf_grammar", "fitness_function"])
    except getopt.GetoptError as err:
        print(str(err))
        #FIXME usage
        sys.exit(2)
    for opt, arg in OPTS:
        if opt in ("-p", "--population"):
            parameters.POPULATION_SIZE = int(arg)
            parameters.GENERATION_SIZE = int(arg)
        elif opt in ("-g", "--generations"):
            parameters.GENERATIONS = int(arg)
        elif opt in ("-e", "--elite_size"):
            parameters.ELITE_SIZE = int(arg)
        elif opt in ("-m", "--mutation"):
            parameters.MUTATION_PROBABILITY = float(arg)
        elif opt in ("-x", "--crossover"):
            parameters.CROSSOVER_PROBABILITY = float(arg)
        elif opt in ("-b", "--bnf_grammar"):
            parameters.GRAMMAR_FILE = arg
        elif opt in ("-f", "--fitness_function"):
            parameters.FITNESS_FUNCTION = arg
        else:
            assert False, "unhandeled option"
    mane(datetime.now().microsecond)
