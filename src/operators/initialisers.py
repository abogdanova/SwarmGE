from algorithm.parameters import params
from random import shuffle, randint
from representation import tree,individual
from math import floor


def generate_initial_pop(grammar):
    if params['INITIALISATION'] == "random" or params['GENOME_INIT']:
        return random_initialisation(params['POPULATION_SIZE'], grammar, params['GENOME_INIT'])
    elif params['INITIALISATION'] == "rhh":
        return rhh_initialisation(params['POPULATION_SIZE'], grammar)
    else:
        print("Error: initialisation method not recognised")
        quit()


def random_initialisation(size, grammar, genome_init):
    """Randomly create a population of size and return"""
    return [individual.individual(None, None, grammar, chromosome=genome_init) for _ in range(size)]


def rhh_initialisation(size, grammar):
    """ Create a population of size using ramped half and half (or sensible
        initialisation) and return. Individuals have a genome created for them
    """

    depths = range(grammar.min_ramp + 1, params['MAX_INIT_DEPTH']+1)
    population = []

    if size < 2:
        print("Error: population size too small for RHH initialisation. Returning randomly built trees.")
        return [individual.individual(None, None) for _ in range(size)]
    else:
        if size % 2:
            # Population size is odd
            size = size + 1
        if size/2 < len(depths):
            depths = depths[:int(size/2)]
        times = int(floor((size/2)/len(depths)))
        remainder = int(size/2 - (times * len(depths)))

        for depth in depths:
            for i in range(times):
                """ Grow """
                method = "random"
                phenotype, genome, ind_tree, nodes, invalid, tree_depth, used_cod = tree.init(depth, method)
                ind = individual.individual(genome, None)
                ind.genome = genome + [randint(0, grammar.codon_size) for i in range(int(ind.used_codons/2))]
                population.append(ind)
                """ Full """
                method = "full"
                phenotype, genome, ind_tree, nodes, invalid, tree_depth, used_cod = tree.init(depth, method)
                ind = individual.individual(genome, None)
                ind.genome = genome + [randint(0, grammar.codon_size) for i in range(int(ind.used_codons/2))]
                population.append(ind)

        if remainder:
            depths = list(depths)
            shuffle(depths)

        for i in range(remainder):
            depth = depths.pop()
            """ Grow """
            method = "random"
            phenotype, genome, ind_tree, nodes, invalid, tree_depth, used_cod = tree.init(depth, method)
            ind = individual.individual(genome, None)
            ind.genome = genome + [randint(0, grammar.codon_size) for i in range(int(ind.used_codons/2))]
            population.append(ind)
            """ Full """
            method = "full"
            phenotype, genome, ind_tree, nodes, invalid, tree_depth, used_cod = tree.init(depth, method)
            ind = individual.individual(genome, None)
            ind.genome = genome + [randint(0, grammar.codon_size) for i in range(int(ind.used_codons/2))]
            population.append(ind)
        return population


def get_min_ramp_depth(grammar):
    """ Find the minimum depth at which ramping can start where we can have
        unique solutions (no duplicates)."""

    max_tree_deth = params['MAX_TREE_DEPTH']
    depths = range(grammar.min_path, max_tree_deth+1)
    size = params['POPULATION_SIZE']

    if size % 2:
        # Population size is odd
        size = size + 1
    if size/2 < len(depths):
        depths = depths[:int(size/2)]

    unique_start = int(floor((size)/len(depths)))
    ramp = None
    for i in sorted(grammar.permutations.keys()):
        if grammar.permutations[i] > unique_start:
            ramp = i
            break
    return ramp
