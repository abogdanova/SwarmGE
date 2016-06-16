from fitness.fitness_wheel import set_fitness_function
from utilities.helper_methods import RETURN_PERCENT
from socket import gethostname
hostname = gethostname().split('.')
machine_name = hostname[0]
from utilities import trackers
from datetime import datetime
from random import seed
import time

"""Algorithm parameters"""
params = {

# Evolutionary Parameters
'POPULATION_SIZE' : 500,
'GENERATIONS' : 50,

# Class of problem
'PROBLEM' : "regression",
    # "regression"
    # "string_match"

# Select Regression Problem Suite
'SUITE' : "Vladislavleva4",
    # "Dow"
    # "Keijzer6"
    # "Vladislavleva4"

# Specify String for StringMatch Problem
'STRING_MATCH_TARGET' : "ponyge_rocks",

# Set max sizes of individuals
'MAX_TREE_DEPTH' : 17,
'CODON_SIZE' : 100000,

# Initialisation
'INITIALISATION' : "rhh",
    # "random"
    # "rhh"
'MAX_INIT_DEPTH' : 10,
    # Set the maximum tree depth for initialisation.
'GENOME_INIT' : False,
    # If True, initialises individuals by generating random genomes (i.e.
    # doesn't use trees to initialise individuals).

# Selection
'SELECTION' : "tournament",
    # "tournament",
    # "truncation",
'TOURNAMENT_SIZE' : 3,
    # For tournament selection
'SELECTION_PROPORTION' : 0.5,
    # For truncation selection

# Crossover
'CROSSOVER' : "subtree",
    # "onepoint",
    # "subtree",
'CROSSOVER_PROBABILITY' : 0.75,

# Mutation
'MUTATION' : "subtree",
    # "subtree",
    # "int_flip",
    # "split",
'MUTATION_PROBABILITY' : "1 over the length of the genome",
    # Subtree mutation is guaranteed to mutate one subtree per individual

# Replacement
'REPLACEMENT' : "generational",
    # "generational",
    # "steady_state",

# Debugging
    # Use this to turn on debugging mode. This mode doesn't write any files and
    # should be used when you want to test new methods or grammars, etc.
'DEBUG' : False,

# Printing
    # Use this to print out basic statistics for each generation to the command
    # line.
'VERBOSE' : True,

# Saving
'SAVE_ALL' : False,
    # Use this to save the phenotype of the best individual from each
    # generation. Can generate a lot of files. DEBUG must be False.
'SAVE_PLOTS' : True,
    # Saves a plot of the evolution of the best fitness result for each
    # generation.

# Caching
'CACHE' : True,
    # The cache tracks unique individuals across evolution by saving a string of
    # each phenotype in a big list of all phenotypes. Saves all fitness
    # information on each individual. Gives you an idea of how much repetition
    # is in standard GE/GP.
'LOOKUP_FITNESS' : False,
    # Uses the cache to look up the fitness of duplicate individuals. CACHE must
    # be set to True if you want to use this.
'LOOKUP_BAD_FITNESS' : True,
    # Uses the cache to give a bad fitness to duplicate individuals. CACHE must
    # be True if you want to use this (obviously)"""
'MUTATE_DUPLICATES' : False,
    # Removes duplicate individuals from the population by replacing them with
    # mutated versions of the original individual. Hopefully this will encourage
    # diversity in the population.
'COMPLETE_EVALS' : False,
    # Using the cache doesn't execute the full number of fitness evaluations.
    # Use this to continue the run in order to execute the full number of
    # fitness evaluations.

# Set machine name (useful for doing multiple runs)
'MACHINE' : machine_name,

# Set Random Seed
'RANDOM_SEED': None

}

def set_params(command_line_args):
    import getopt
    try:
        #FIXME help option
        print(command_line_args)
        #FIXME Need to decide on these when everything has been fixed
        OPTS, ARGS = getopt.getopt(command_line_args[1:], "p:g:e:m:x:b:f:r:d",
                                   ["population", "generations",
                                    "elite_size", "mutation", "crossover",
                                    "bnf_grammar", "fitness_function",
                                    "random_seed", "debug"])
    except getopt.GetoptError as err:
        print(str(err))
        #FIXME usage
        exit(2)

    #FIXME Need to update the command line args to reflect parameters dictionary
    for opt, arg in OPTS:
        if opt in ("-p", "--population"):
            params['POPULATION_SIZE'] = int(arg)
            params['GENERATION_SIZE'] = int(arg)
        elif opt in ("-g", "--generations"):
            params.GENERATIONS = int(arg)
        elif opt in ("-e", "--elite_size"):
            params['ELITE_SIZE'] = int(arg)
        elif opt in ("-m", "--mutation"):
            params['MUTATION_PROBABILITY'] = float(arg)
        elif opt in ("-x", "--crossover"):
            params['CROSSOVER_PROBABILITY'] = float(arg)
        elif opt in ("-b", "--bnf_grammar"):
            params['GRAMMAR_FILE'] = arg
        elif opt in ("-f", "--fitness_function"):
            params['FITNESS_FUNCTION'] = arg
        elif opt in ("-r", "--random_seed"):
            params['RANDOM_SEED'] = int(arg)
        elif opt in ("-d", "--debug"):
            params['DEBUG'] = True
        else:
            assert False, "unhandeled option"

    # Set the size of a generation
    params['GENERATION_SIZE'] = params['POPULATION_SIZE']

    # Elite size is set to either 1 or 1% of the population size, whichever is
    # bigger.
    params['ELITE_SIZE'] = RETURN_PERCENT(1,params['POPULATION_SIZE'])

    if params['RANDOM_SEED'] == None:
        params['RANDOM_SEED'] = int(time.clock()*1000000)

    # Set all parameters as specified in params
    from operators import crossover, mutation, selection, replacement

    # Crossover
    # TODO Crossover Param Wheel to tidy this up
    if params['CROSSOVER'] == "subtree":
        params['CROSSOVER'] = crossover.subtree_crossover
    elif params['CROSSOVER'] == "onepoint":
        params['CROSSOVER'] = crossover.onepoint_crossover

    # Mutation
    #TODO Mutation Param Wheel to tidy this up
    if params['MUTATION'] == "subtree":
        params['MUTATION'] = mutation.subtree_mutation
    elif params['MUTATION'] == "int_flip":
        params['MUTATION'] = mutation.int_flip_mutation
    elif params['MUTATION'] == "split":
        params['MUTATION'] = mutation.split_mutation

    # Set GENOME_OPERATIONS automatically
    if params['MUTATION'] == mutation.int_flip_mutation and \
                    params['CROSSOVER'] == crossover.onepoint_crossover:
        params['GENOME_OPERATIONS'] = True
    else:
        params['GENOME_OPERATIONS'] = False

    # Selection
    #TODO Selection Param Wheel
    if params['SELECTION'] == "tournament":
        params['SELECTION'] = selection.tournament_selection
    elif params['SELECTION'] == "truncation":
        params['SELECTION'] = selection.truncation_selection

    # Replacement
    #TODO Replacement Param Wheel
    if params['REPLACEMENT'] == "generational":
        params['REPLACEMENT'] = replacement.generational_replacement
    elif params['REPLACEMENT'] == "steady_state":
        params['REPLACEMENT'] = replacement.steady_state_replacement

    # Set problem specifics
    #TODO Fitness Param Wheel
    if params['PROBLEM'] == "regression":
        params['GRAMMAR_FILE'] = "grammars/" + params['SUITE'] + ".bnf"
        params['ALTERNATE'] = params['SUITE']
    elif params['PROBLEM'] == "string_match":
        params['GRAMMAR_FILE'] = "grammars/letter.bnf"
        params['ALTERNATE'] = params['STRING_MATCH_TARGET']

    params['FITNESS_FUNCTION'] = set_fitness_function(params['PROBLEM'],
                                                      params['ALTERNATE'])

    # Set random seed
    seed(params['RANDOM_SEED'])

    # Initialise time lists and trackers
    time1 = datetime.now()
    trackers.time_list.append(time.clock())
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    params['TIME_STAMP'] = (str(time1.year)[2:] + "_" + str(time1.month) +
                            "_" + str(time1.day) + "_" + hms +
                            "_" + str(time1.microsecond))
    print("\nStart:\t", time1, "\n")

    # Generate save folders and files
    if params['DEBUG']:
        print("Seed:\t", params['RANDOM_SEED'], "\n")
    else:
        from stats.stats import generate_folders_and_files
        generate_folders_and_files()

