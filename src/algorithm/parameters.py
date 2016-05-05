from utilities.helper_methods import RETURN_PERCENT
from fitness.fitness_wheel import set_fitness_function
import time

"""algorithm Parameters"""
params = {
'RANDOM_SEED': None,
'CODON_SIZE' : 100000,
'POPULATION_SIZE' : 500,
'GENERATION_SIZE' : None,
'ELITE_SIZE' : None,
'GENERATIONS' : 50,
'MAX_TREE_DEPTH' : 10,
'MUTATION_PROBABILITY' : "1 over the length of the genome",
'CROSSOVER_PROBABILITY' : 0.5,

#For tournament selection
'TOURNAMENT_SIZE' : 3,
#For truncation selection
'SELECTION_PROPORTION' : 0.5,
#With random initialisation you have the choice of either the initialisation
#of a random genome and subsequent derivation of a tree/individual (which may
#or may not be valid), or the initialisation of a random tree (which is
#guaranteed to always be valid). Default is the creation of a random valid tree.
'GENOME_INIT' : False,
#Switch between tree and genome variation operators. Essentially switch
#between GE and GGP."""
'GENOME_OPERATIONS' : False,
#"""Use this to turn on debugging mode. This mode doesn't write any
#files and should be used when you want to test new methods or grammars, etc."""
'DEBUG' : True,
#"""Use this to save the phenotype of the best individual from each generation.
#This is useful for maiking gifs of the evolution of the best indivs, but can
#generate a lot of files.
#Changed the next to from not DEBUG, DEBUG should be used correctly"""
'SAVE_ALL' : False,
#"""Saves a CDF graph of the first individual and the final evolved individual.
#Also saves a graph of the evolution of the best fitness result for each
#generation."""
'SAVE_PLOTS' : False,
#"""Tracks unique individuals across evolution by saving a string of each
#phenotype in a big list of all phenotypes. Saves all fitness information on
#each individual. Gives you an idea of how much repitition is in standard GE/GP.
#Must be True if you're using REMOVE_DUPLICATES."""
'CACHE' : True,
#"""Uses the cache to look up the fitness of duplicate individuals. CACHE must
#be True if you want to use this (obviously)"""
'LOOKUP_FITNESS' : False,
#"""Uses the cache to give a bad fitness to duplicate individuals. CACHE must
#be True if you want to use this (obviously)"""
'LOOKUP_BAD_FITNESS' : True,
#"""Removes duplicate individuals from the population by replacing them with
#mutated versions of the original individual. Hopefully this will encourage
#diversity in the population."""
'MUTATE_DUPLICATES' : False,
#""" Using the cache doesn't execute the full number of fitness evaluations. Use
#this to continue the run in order to execute the full number of fitness
#evaluations."""
'COMPLETE_EVALS' : False,
#Select Regression PRoblem Suite
'SUITE' : "Keijzer6",
# "Dow"
# "Keijzer6"
# "Vladislavleva4"
#Specify String for StringMatch Problem
'STRING_MATCH_TARGET' : "ponyge_rocks",
#Specifies the problem
'PROBLEM' : None,
#Specifies the modifier for the problem depending on the problem
'ALTERNATE' : None,
#The grammar file to be used
'GRAMMAR_FILE' : None,
#The Fitness Function to be used
'FITNESS_FUNCTION' : None,
#Set the initialisation to be used
'INITIALISATION' : "rhh"
# "random"
# "rhh"
}

def set_params(command_line_args):
    import getopt
    try:
        #FIXME help option
        print(command_line_args)
        #FIXME Need to decide on these when everything has been fixed
        OPTS, ARGS = getopt.getopt(command_line_args[1:], "p:g:e:m:x:b:f:r:",
                                   ["population", "generations",
                                    "elite_size", "mutation", "crossover",
                                    "bnf_grammar", "fitness_function", "random_seed"])
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
        else:
            assert False, "unhandeled option"

    #Set the size of a generation :-/ seems redundant but need to examine of Population size changes
    params['GENERATION_SIZE'] = params['POPULATION_SIZE']
    #This needs to be defined better, porobabl make 1 into variable
    params['ELITE_SIZE'] = RETURN_PERCENT(1,params['POPULATION_SIZE'])

    if params['RANDOM_SEED'] == None:
        params['RANDOM_SEED'] = int(time.clock()*1000000)

    #FIXME Need to move these to before the command line args are set.
    #To run Regression
    params['PROBLEM'],params['ALTERNATE'],params['GRAMMAR_FILE'] = "regression", params['SUITE'], "grammars/" + params['SUITE'] + ".bnf",
    #To run String Match
    #params['PROBLEM'],params['ALTERNATE'],params['GRAMMAR_FILE'] = "string_match", params['STRING_MATCH_TARGET'], "grammars/letter.bnf"
    params['FITNESS_FUNCTION'] = set_fitness_function(params['PROBLEM'],params['ALTERNATE'])

