from multiprocessing import cpu_count
from socket import gethostname


hostname = gethostname().split('.')
machine_name = hostname[0]


"""Algorithm parameters"""
params = {
        # Set default step and search loop functions
        'SEARCH_LOOP': 'search_loop',
        'STEP': 'step',

        # Evolutionary Parameters
        'POPULATION_SIZE': 500,
        'GENERATIONS': 50,

        # Set optional experiment name
        'EXPERIMENT_NAME': None,

        # Class of problem
        'FITNESS_FUNCTION': "regression",
        # "regression"
        # "string_match"
        # "classification"

        # Select problem dataset
        'DATASET': "Vladislavleva4",
        # "Dow"
        # "Keijzer6"
        # "Vladislavleva4"
        
        # Set grammar file
        'GRAMMAR_FILE': "Vladislavleva4.bnf",
        # "Vladislavleva4.bnf"
        # "Keijzer6.bnf"
        # "Dow.bnf"
        # "Banknote.bnf"
        # "letter.bnf"
    
        # Select error metric
        'ERROR_METRIC': None,
        # "mse"
        # "mae"
        # "rmse"
        # "hinge"
        # "inverse_f1_score"
    
        # Specify String for StringMatch Problem
        'STRING_MATCH_TARGET': "ponyge_rocks",

        # Set max sizes of individuals
        'MAX_TREE_DEPTH': 17,
        'CODON_SIZE': 100000,
        'GENOME_LENGTH': 500,
        'MAX_WRAPS': 0,

        # INITIALISATION
        'INITIALISATION': "operators.initialisation.rhh",
        # "operators.initialisation.random_init"
        # "operators.initialisation.rhh"
        'MAX_INIT_DEPTH': 10,
        # Set the maximum tree depth for initialisation.
        'GENOME_INIT': False,
        # If True, initialises individuals by generating random genomes (i.e.
        # doesn't use trees to initialise individuals).

        # SELECTION
        'SELECTION': "operators.selection.tournament",
        # "operators.selection.tournament"
        # "operators.selection.truncation",
        'TOURNAMENT_SIZE': 2,
        # For tournament selection
        'SELECTION_PROPORTION': 0.5,
        # For truncation selection
        'INVALID_SELECTION': False,
        # Allow for selection of invalid individuals during selection process.

        # CROSSOVER
        'CROSSOVER': "operators.crossover.onepoint",
        # "operators.crossover.onepoint",
        # "operators.crossover.subtree",
        'CROSSOVER_PROBABILITY': 0.75,

        # MUTATION
        'MUTATION': "operators.mutation.int_flip",
        # "operators.mutation.subtree",
        # "operators.mutation.int_flip",
        'MUTATION_PROBABILITY': None,
        'MUTATION_EVENTS': 1,

        # REPLACEMENT
        'REPLACEMENT': "operators.replacement.generational",
        # "operators.replacement.generational",
        # "operators.replacement.steady_state",
        'ELITE_SIZE': None,

        # DEBUGGING
        # Use this to turn on debugging mode. This mode doesn't write any files
        # and should be used when you want to test new methods.
        'DEBUG': False,

        # PRINTING
        # Use this to print out basic statistics for each generation to the
        # command line.
        'VERBOSE': False,
        # Use this to prevent anything being printed to the command line.
        'SILENT': False,

        # SAVING
        'SAVE_ALL': False,
        # Use this to save the phenotype of the best individual from each
        # generation. Can generate a lot of files. DEBUG must be False.
        'SAVE_PLOTS': True,
        # Saves a plot of the evolution of the best fitness result for each
        # generation.

        # MULTIPROCESSING
        'MULTICORE': False,
        # Multiprocessing of phenotype evaluations.
        'CORES': cpu_count(),

        # CACHING
        'CACHE': False,
        # The cache tracks unique individuals across evolution by saving a
        # string of each phenotype in a big list of all phenotypes. Saves all
        # fitness information on each individual. Gives you an idea of how much
        # repetition is in standard GE/GP.
        'LOOKUP_FITNESS': False,
        # Uses the cache to look up the fitness of duplicate individuals. CACHE
        #  must be set to True if you want to use this.
        'LOOKUP_BAD_FITNESS': False,
        # Uses the cache to give a bad fitness to duplicate individuals. CACHE
        # must be True if you want to use this (obviously)"""
        'MUTATE_DUPLICATES': False,
        # Removes duplicate individuals from the population by replacing them
        # with mutated versions of the original individual. Hopefully this will
        # encourage diversity in the population.

        # Set machine name (useful for doing multiple runs)
        'MACHINE': machine_name,

        # Set Random Seed
        'RANDOM_SEED': None
}


def load_params(file_name):
    """
    Load in a params text file and set the params dictionary directly.
     
    :param file_name: The name/location of a parameters file.
    :return: Nothing.
    """

    try:
        open(file_name, "r")
    except FileNotFoundError:
        print("Error: Parameters file not found. Ensure file\n"
              "       extension is specified, e.g. "
              "'regression.txt'.")
        quit()

    with open(file_name, 'r') as parameters:
        # Read the whole parameters file.
        content = parameters.readlines()

        for line in content:
            components = line.split(":")
            key, value = components[0], components[1].strip()
           
            # Evaluate parameters.
            try:
                value = eval(value)
            except:
                # We can't evaluate, leave value as a string.
                pass
            
            # Set parameter
            params[key] = value


def check_int(param, arg):
    """
    Checks to ensure the given argument is indeed an int. If not, throws an
    error.
    
    :param param: A parameter from the params dictionary.
    :param arg: A given input argument.
    :return: Error if an error occurs, nothing if no error.
    """

    try:
        params[param] = int(arg)
    except:
        print("\nError: Please define", param, "as int. Value given:", arg)
        quit()


def check_float(param, arg):
    """
    Checks to ensure the given argument is indeed a float. If not, throws an
    error. Also checks to ensure the given float is within the range [0:1].
    
    :param param: A parameter from the params dictionary.
    :param arg: A given input argument.
    :return: Error if an error occurs, nothing if no error.
    """

    try:
        params[param] = float(arg)
    except:
        print("\nError: Please define", param, "as float. Value given:", arg)
        quit()
    if not 1 >= params[param] >= 0:
        print("\nError:", param, "outside allowed range [0:1]. Value "
                                 "given:", arg)
        quit()


def set_params(command_line_args):
    """
    This function parses all command line arguments specified by the user.
    If certain parameters are not set then defaults are used (e.g. random
    seeds, elite size). Sets the correct imports given command line
    arguments. Sets correct grammar file and fitness function. Also
    initialises save folders and tracker lists in utilities.trackers.
    
    :param command_line_args: Command line arguments specified by the user.
    :return: Nothing.
    """

    from utilities.algorithm.initialise_run import initialise_run_params
    from utilities.algorithm.initialise_run import set_param_imports
    from utilities.fitness.math_functions import return_percent
    from utilities.help_message import help_message
    from representation import grammar
    import getopt

    try:
        opts, args = getopt.getopt(command_line_args[1:], "",
                                   ["help", "debug", "population=",
                                    "generations=", "initialisation=",
                                    "max_init_depth=", "genome_init",
                                    "max_tree_depth=", "codon_size=",
                                    "selection=", "selection_proportion=",
                                    "tournament_size=", "crossover=",
                                    "crossover_probability=", "replacement=",
                                    "mutation=", "mutation_events=",
                                    "random_seed=", "bnf_grammar=",
                                    "dataset=", "target_string=",
                                    "verbose", "elite_size=", "save_all",
                                    "save_plots", "cache", "lookup_fitness",
                                    "lookup_bad_fitness", "mutate_duplicates",
                                    "genome_length=",
                                    "invalid_selection", "silent",
                                    "dont_lookup_fitness", "experiment_name=",
                                    "multicore", "cores=", "max_wraps=",
                                    "error_metric=", "fitness_function=",
                                    "parameters=", "step=", "search_loop="])
    except getopt.GetoptError as err:
        print("Most parameters need a value associated with them \n",
              "Run python ponyge.py --help for more info")
        print(str(err))
        exit(2)

    for opt, arg in opts:
        if opt == "--help":
            help_message()
            exit()

        # LOAD PARAMETERS FILE
        elif opt == "--parameters":
            load_params("../parameters/" + arg)

        # LOAD STEP AND SEARCH LOOP FUNCTIONS
        elif opt == "--search_loop":
            params['SEARCH_LOOP'] = arg
        elif opt == "--step":
            params['STEP'] = arg

        # POPULATION OPTIONS
        elif opt == "--population":
            check_int('POPULATION_SIZE', arg)
        elif opt == "--generations":
            check_int('GENERATIONS', arg)

        # INDIVIDUAL SIZE
        elif opt == "--max_tree_depth":
            check_int('MAX_TREE_DEPTH', arg)
        elif opt == "--codon_size":
            check_int('CODON_SIZE', arg)
        elif opt == "--genome_length":
            check_int('GENOME_LENGTH', arg)
        elif opt == "--max_wraps":
            check_int('MAX_WRAPS', arg)

        # INITIALISATION
        elif opt == "--initialisation":
            params['INITIALISATION'] = arg
        elif opt == "--max_init_depth":
            check_int('MAX_INIT_DEPTH', arg)
        elif opt == "--genome_init":
            params['GENOME_INIT'] = True
            params['INITIALISATION'] = "operators.initialisation.random_init"

        # SELECTION
        elif opt == "--selection":
            params['SELECTION'] = arg
        elif opt == "--invalid_selection":
            params['INVALID_SELECTION'] = arg
        elif opt == "--tournament_size":
            check_int('TOURNAMENT_SIZE', arg)
        elif opt == "--selection_proportion":
            check_float('SELECTION_PROPORTION', arg)

        # EVALUATION
        elif opt == "--multicore":
            params['MULTIPCORE'] = True
        elif opt == "--cores":
            check_int('CORES', arg)

        # CROSSOVER
        elif opt == "--crossover":
            params['CROSSOVER'] = arg
        elif opt == "--crossover_probability":
            check_float('CROSSOVER_PROBABILITY', arg)

        # MUTATION
        elif opt == "--mutation":
            params['MUTATION'] = arg
        elif opt == "--mutation_events":
            check_int('MUTATION_EVENTS', arg)
        elif opt == "--mutation_probability":
            check_float('MUTATION_PROBABILITY', arg)

        # REPLACEMENT
        elif opt == "--replacement":
            params['REPLACEMENT'] = arg
        elif opt == "--elite_size":
            check_int('ELITE_SIZE', arg)

        # PROBLEM SPECIFICS
        elif opt == "--bnf_grammar":
            params['GRAMMAR_FILE'] = arg
        elif opt == "--fitness_function":
            params['FITNESS_FUNCTION'] = arg
        elif opt == "--dataset":
            params['DATASET'] = arg
        elif opt == "--target_string":
            params['STRING_MATCH_TARGET'] = arg
        elif opt == "--experiment_name":
            params['EXPERIMENT_NAME'] = arg
        elif opt == "--error_metric":
            params['ERROR_METRIC'] = arg

        # OPTIONS
        elif opt == "--random_seed":
            check_int('RANDOM_SEED', arg)
        elif opt == "--debug":
            params['DEBUG'] = True
        elif opt == "--verbose":
            params['VERBOSE'] = True
        elif opt == "--silent":
            params['SILENT'] = True
        elif opt == "--save_all":
            params['SAVE_ALL'] = True
        elif opt == "--save_plots":
            params['SAVE_PLOTS'] = True

        # CACHING
        elif opt == "--cache":
            params['CACHE'] = True
            params['LOOKUP_FITNESS'] = True
        elif opt == "--dont_lookup_fitness":
            params['LOOKUP_FITNESS'] = False
        elif opt == "--lookup_bad_fitness":
            params['LOOKUP_FITNESS'] = False
            params['LOOKUP_BAD_FITNESS'] = True
        elif opt == "--mutate_duplicates":
            params['LOOKUP_FITNESS'] = False
            params['MUTATE_DUPLICATES'] = True
        else:
            assert False, "Unhandled Option, use --help for available params"

    # Elite size is set to either 1 or 1% of the population size, whichever is
    # bigger if no elite size is previously set.
    if params['ELITE_SIZE'] is None:
        params['ELITE_SIZE'] = return_percent(1, params['POPULATION_SIZE'])

    # Set the size of a generation
    params['GENERATION_SIZE'] = params['POPULATION_SIZE'] - params[
        'ELITE_SIZE']

    # Set GENOME_OPERATIONS automatically for faster linear operations.
    if (params['MUTATION'] == 'operators.mutation.int_flip' or
                params['MUTATION'] == 'int_flip') and \
            (params['CROSSOVER'] == 'operators.crossover.onepoint' or
                     params['CROSSOVER'] == 'onepoint'):
        params['GENOME_OPERATIONS'] = True
    else:
        params['GENOME_OPERATIONS'] = False

    # Set correct param imports for specified function options, including
    # error metrics and fitness functions.
    set_param_imports()
    
    # Initialise run lists and folders
    initialise_run_params()

    # Parse grammar file and set grammar class.
    params['BNF_GRAMMAR'] = grammar.Grammar("../grammars/" +
                                            params['GRAMMAR_FILE'])
