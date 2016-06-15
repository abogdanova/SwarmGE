#! /usr/bin/env python

# PonyGE
# Copyright (c) 2009 Erik Hemberg, James McDermott, Michael Fenton and David Fagan
# Hereby licensed under the GNU GPL v3.
""" Python GE implementation """

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')
from random import seed
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

    params['TIME_LIST'] = [time.clock()]
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    params['TIME_STAMP'] = (str(time1.year)[2:] + "_" + str(time1.month) +
                            "_" + str(time1.day) + "_" + hms +
                            "_" + str(time1.microsecond))
    print ("\nStart:\t", time1, "\n")
    if params['DEBUG']:
        print ("Seed:\t", ran_seed, "\n")
    else:
        stats.generate_folders_and_files(ran_seed)

    #Set Fitness Funtion
    params['FITNESS_FUNCTION'] = set_fitness_function(params['PROBLEM'],
                                                      params['ALTERNATE'])
    #Set Grammar File
    bnf_grammar = grammar.grammar(params['GRAMMAR_FILE'])

    #Calculate the minimum ramping level for the grammar
    bnf_grammar.min_ramp = initialisers.get_min_ramp_depth(bnf_grammar)
    params['BNF_GRAMMAR'] = bnf_grammar

    # Loop
    best_ever, phenotypes, total_inds, invalids, regens, final_gen = search_loop.search_loop(
                    params['GENERATIONS'], generate_initial_pop(bnf_grammar))

    #END LOOP
    params['TIME_LIST'].append(time.clock())
    total_time = timedelta(seconds = (params['TIME_LIST'][-1] - params['TIME_LIST'][0]))

    # Print final review
    stats.print_final_stats(best_ever, total_time, total_inds, len(phenotypes),
                            invalids)

    if not params['DEBUG']:
        stats.save_best("best", final_gen, best_ever)
        stats.save_results(final_gen, best_ever.fitness, total_time,
                   len(phenotypes), total_inds, invalids, regens, None, None,
                   None, None, total_time=total_time, END=True)
    return params['TIME_STAMP'], best_ever.fitness

if __name__ == "__main__":
    set_params(sys.argv)
    mane()
