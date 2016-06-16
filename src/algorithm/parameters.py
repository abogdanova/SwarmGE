from fitness.fitness_wheel import set_fitness_function, set_fitness_params
from utilities.helper_methods import RETURN_PERCENT
from socket import gethostname
hostname = gethostname().split('.')
machine_name = hostname[0]
from random import seed
import time

"""Algorithm parameters"""
params = {

# Evolutionary Parameters
'POPULATION_SIZE' : 100,
'GENERATIONS' : 10,

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
'VERBOSE' : False,

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
'RANDOM_SEED': 10 # None

}

def set_params(command_line_args):
    from operators.crossover import crossover_wheel
    from operators.mutation import mutation_wheel
    from operators.selection import selection_wheel
    from operators.replacement import replacement_wheel
    from utilities.initialise_run import initialise_run_params
    import getopt

    try:
        #FIXME help option
        print(command_line_args)
        #FIXME Need to decide on these when everything has been fixed
        OPTS, ARGS = getopt.getopt(command_line_args[1:], "",
                                   ["help","population=", "generations=",
                                    "elite_size=", "mutation=", "crossover=",
                                    "bnf_grammar=", "fitness_function=",
                                    "random_seed=", "debug="])
    except getopt.GetoptError as err:
        print("All parameters need a value associated with it \n",
              "Run puthon ponyge.py --help for more info")
        print(str(err))
        exit(2)

    #FIXME Need to update the command line args to reflect parameters dictionary
    for opt, arg in OPTS:
        if opt == "--population":
            params['POPULATION_SIZE'] = int(arg)
            params['GENERATION_SIZE'] = int(arg)
        elif opt == "--generations":
            params.GENERATIONS = int(arg)
        elif opt == "--elite_size":
            params['ELITE_SIZE'] = int(arg)
        elif opt == "--mutation":
            params['MUTATION_PROBABILITY'] = float(arg)
        elif opt == "--crossover":
            params['CROSSOVER_PROBABILITY'] = float(arg)
        elif opt == "--bnf_grammar":
            params['GRAMMAR_FILE'] = arg
        elif opt == "--fitness_function":
            params['FITNESS_FUNCTION'] = arg
        elif opt == "--random_seed":
            params['RANDOM_SEED'] = int(arg)
        elif opt == "--debug":
            params['DEBUG'] = True
        elif opt == "--help":
            print("Help stuff should go here")
            exit()
        else:
            assert False, "Unhandeled Option"

    # Set the size of a generation
    params['GENERATION_SIZE'] = params['POPULATION_SIZE']

    # Elite size is set to either 1 or 1% of the population size, whichever is
    # bigger.
    params['ELITE_SIZE'] = RETURN_PERCENT(1, params['POPULATION_SIZE'])

    # Set random seed
    if params['RANDOM_SEED'] == None:
        #TODO Is this the best way to get a random seed?
        params['RANDOM_SEED'] = int(time.clock()*1000000)
    seed(params['RANDOM_SEED'])


    # Set all parameters as specified in params
    # Set Crossover
    crossover_wheel()

    # Set Mutation
    mutation_wheel()

    # Set Selection
    selection_wheel()

    # Set Replacement
    replacement_wheel()

    # Set GENOME_OPERATIONS automatically
    if params['MUTATION'] == 'int_flip' and \
                    params['CROSSOVER'] == 'onepoint':
        params['GENOME_OPERATIONS'] = True
    else:
        params['GENOME_OPERATIONS'] = False

    # Set problem specifics
    params['GRAMMAR_FILE'], params['ALTERNATE'] = set_fitness_params(params['PROBLEM'], params)
    params['FITNESS_FUNCTION'] = set_fitness_function(params['PROBLEM'],
                                                      params['ALTERNATE'])
    # Initialise run lists and folders
    initialise_run_params()
