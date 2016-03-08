from utilities.helper_methods import RETURN_PERCENT
from fitness.fitness_wheel import set_fitness_function

"""algorithm Parameters"""

CODON_SIZE = 100000
POPULATION_SIZE = 500
GENERATION_SIZE = POPULATION_SIZE
ELITE_SIZE = RETURN_PERCENT(1,POPULATION_SIZE)
GENERATIONS = 50
MAX_TREE_DEPTH = 10
MUTATION_PROBABILITY = "1 over the length of the genome"
CROSSOVER_PROBABILITY = 0.5

#For tournament selection
TOURNAMENT_SIZE = 3
#For truncation selection
SELECTION_PROPORTION = 0.5

#Select Regression PRoblem Suite
SUITE = "Keijzer6"
# "Dow"
# "Keijzer6"
# "Vladislavleva4"

#Specify String for StringMatch Problem
STRING_MATCH_TARGET = "ponyge_rocks"

PROBLEM, ALTERNATE, GRAMMAR_FILE = "regression", SUITE, "grammars/" + SUITE + ".bnf"
#PROBLEM, ALTERNATE, GRAMMAR_FILE = "string_match", STRING_MATCH_TARGET, "grammars/letter.bnf"

#by default this is set to string match
FITNESS_FUNCTION = set_fitness_function(PROBLEM,ALTERNATE)

#Set the initialisation to be used
INITIALISATION = "rhh"
# "random"
# "rhh"


"""With random initialisation you have the choice of either the initialisation
of a random genome and subsequent derivation of a tree/individual (which may
or may not be valid), or the initialisation of a random tree (which is
guaranteed to always be valid). Default is the creation of a random valid tree.
"""
GENOME_INIT = False

"""Switch between tree and genome variation operators. Essentially switch
between GE and GGP."""
GENOME_OPERATIONS = False

"""Use this to turn on debugging mode. This mode doesn't write any
files and should be used when you want to test new methods or grammars, etc."""
DEBUG = True

"""Use this to save the phenotype of the best individual from each generation.
This is useful for maiking gifs of the evolution of the best indivs, but can
generate a lot of files."""
SAVE_ALL = not DEBUG

"""Saves a CDF graph of the first individual and the final evolved individual.
Also saves a graph of the evolution of the best fitness result for each
generation."""
SAVE_PLOTS = not DEBUG

"""Tracks unique individuals across evolution by saving a string of each
phenotype in a big list of all phenotypes. Saves all fitness information on
each individual. Gives you an idea of how much repitition is in standard GE/GP.
Must be True if you're using REMOVE_DUPLICATES."""
CACHE = True

"""Uses the cache to look up the fitness of duplicate individuals. CACHE must
be True if you want to use this (obviously)"""
LOOKUP_FITNESS = False

"""Uses the cache to give a bad fitness to duplicate individuals. CACHE must
be True if you want to use this (obviously)"""
LOOKUP_BAD_FITNESS = True

"""Removes duplicate individuals from the population by replacing them with
mutated versions of the original individual. Hopefully this will encourage
diversity in the population."""
MUTATE_DUPLICATES = False

""" Using the cache doesn't execute the full number of fitness evaluations. Use
this to continue the run in order to execute the full number of fitness
evaluations."""
COMPLETE_EVALS = False
