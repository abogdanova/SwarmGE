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
from algorithm import search_loop
from algorithm.parameters import params,set_params
from operators import initialisers,mutation,crossover,selection,replacement
from operators.initialisers import generate_initial_pop
from fitness.fitness_wheel import set_fitness_function
from stats import stats
import time

def mane():
    """ Run program """
    time1 = datetime.now()
    ran_seed = params['RANDOM_SEED']
    seed(ran_seed)

    if params['GENOME_OPERATIONS']:
        version = "GE"
    else:
        version = "GGP"

    time_list = [time.clock()]
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    TIME_STAMP = (str(time1.year)[2:] + "_" + str(time1.month) + "_" + str(time1.day) + "_" + hms + "_" + str(time1.microsecond))
    print ("\nStart:\t", time1, "\n")
    if params['DEBUG']:
        print ("Seed:\t", ran_seed, "\n")
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
        savefile.write("# Machine: " + str(name) + "\tSeed: " + str(ran_seed) + "\n# Version: " + str(version) + "\n# Suite: " + str(params['GRAMMAR_FILE'].split("/")[1].split(".")[0]) + "\n#\n")
        savefile.close()

    #Set Fitness Funtion
    params['FITNESS_FUNCTION'] = set_fitness_function(params['PROBLEM'], params['ALTERNATE'])
    #Set Grammar File
    bnf_grammar = grammar.grammar(params['GRAMMAR_FILE'])

    #Calculate the minimum ramping level for the grammar
    bnf_grammar.min_ramp = initialisers.get_min_ramp_depth(params['POPULATION_SIZE'], bnf_grammar, params['MAX_TREE_DEPTH'])

    # Loop
    # We can probably remove the likes of crossover and mutation from this and set them directly in step
    # We should probably parameterise things more.
    if params['GENOME_OPERATIONS']:
        best_ever, phenotypes, total_inds, invalids, regens, final_gen = search_loop.search_loop(
                            params['GENERATIONS'], generate_initial_pop(bnf_grammar), bnf_grammar,
                            replacement.generational_replacement, selection.tournament_selection,
                            crossover.onepoint_crossover, mutation.int_flip_mutation,
                            params['FITNESS_FUNCTION'], time_list, TIME_STAMP)
    else:
        best_ever, phenotypes, total_inds, invalids, regens, final_gen = search_loop.search_loop(
                            params['GENERATIONS'], generate_initial_pop(bnf_grammar), bnf_grammar,
                            replacement.generational_replacement, selection.tournament_selection,
                            crossover.subtree_crossover, mutation.subtree_mutation,
                            params['FITNESS_FUNCTION'], time_list, TIME_STAMP)
    #END LOOP

    #Print Some stats - MOVE ME TO STATS MAYBE
    print("Best " + str(best_ever))
    time_list.append(time.clock())
    total_time = timedelta(seconds = (time_list[-1] - time_list[0]))
    print ("\nTime taken:\t", total_time)
    print ("\nTotal evals:  \t", total_inds)
    print ("Unique evals: \t", len(phenotypes))
    print ("Invalid inds: \t", invalids)
    print ("Unused search:\t", 100 - (len(phenotypes)/float(total_inds))*100,"percent")
    print ("\nBest:\n  Training fitness:\t", best_ever.fitness)
    #FIXME This is hacky
    best_ever.evaluate(params['FITNESS_FUNCTION'], dist='test')
    print ("  Test fitness:\t\t", best_ever.fitness)
    print ("  Phenotype:", best_ever.phenotype)
    print ("  Genome:", best_ever.genome)
    if not params['DEBUG']:
        stats.save_best("best", final_gen, best_ever, TIME_STAMP)
        stats.save_results(final_gen, best_ever.fitness, total_time, len(phenotypes), total_inds, invalids, regens, None, None, None, None, TIME_STAMP, total_time=total_time, END=True)
    return TIME_STAMP, best_ever.fitness

if __name__ == "__main__":
    set_params(sys.argv)
    mane()
