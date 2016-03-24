from algorithm.parameters import params
from random import shuffle, randint
from representation import tree,individual
from math import floor

def generate_initial_pop(grammar):
    if  params['INITIALISATION'] == "random":
        return random_initialisation(params['POPULATION_SIZE'], grammar, params['GENOME_INIT'])
    elif params['INITIALISATION'] == "rhh":
        return rhh_initialisation(params['POPULATION_SIZE'], grammar, params['MAX_TREE_DEPTH'])
    else:
        print ("Error: initialisation method not recognised")
        quit()


def random_initialisation(size, grammar, genome_init):
    """Randomly create a population of size and return"""
    return [individual.individual(None, None, grammar, chromosome=genome_init) for _ in range(size)]

def rhh_initialisation(size, grammar, max_tree_depth):
    """ Create a population of size using ramped half and half (or sensible
        initialisation) and return. Individuals have a genome created for them
    """

    depths = range(grammar.min_path, max_tree_depth+1)
    population = []

    if size < 2:
        print ("Error: population size too small for RHH initialisation. Returning randomly built trees.")
        return [individual.individual(None, None, grammar) for _ in range(size)]
    else:
        if size % 2:
            # Population size is odd
            size = size + 1
        if size/2 < depths:
            depths = depths[:int(size/2)]
        times = int(floor((size/2)/len(depths)))
        remainder = int(size/2 - (times * len(depths)))

        for depth in depths:
            for i in range(times):
                """ Grow """
                phenotype_1, genome_1, tree_1, nodes_1, invalid_1 = tree.random_init(grammar, depth)
                ind_1 = individual.individual(None, tree_1, grammar)
                ind_1.phenotype, ind_1.used_codons, ind_1.invalid = phenotype_1, len(genome_1), invalid_1
                ind_1.genome = genome_1 + [randint(0, grammar.codon_size) for i in range(int(ind_1.used_codons/2))]
                ind_1.nodes = nodes_1
                ind_1.depth = ind_1.tree.get_max_children(ind_1.tree, 0)
                population.append(ind_1)
                """ Full """
                phenotype_2, genome_2, tree_2, nodes_2, invalid_2 = tree.full_init(grammar, depth)
                ind_2 = individual.individual(None, tree_2, grammar)
                ind_2.phenotype, ind_2.used_codons, ind_2.invalid = phenotype_2, len(genome_2), invalid_2
                ind_2.genome = genome_2 + [randint(0, grammar.codon_size) for i in range(int(ind_2.used_codons/2))]
                ind_2.nodes = nodes_2
                ind_2.depth = ind_2.tree.get_max_children(ind_2.tree, 0)
                population.append(ind_2)
        if remainder:
            shuffle(depths)
        for i in range(remainder):
            depth = depths.pop()
            """ Grow """
            phenotype_1, genome_1, tree_1, nodes_1, invalid_1 = tree.random_init(grammar, depth)
            ind_1 = individual.individual(None, tree_1, grammar)
            ind_1.phenotype, ind_1.used_codons, ind_1.invalid = phenotype_1, len(genome_1), invalid_1
            ind_1.genome = genome_1 + [randint(0, grammar.codon_size) for i in range(int(ind_1.used_codons/2))]
            ind_1.nodes = nodes_1
            ind_1.depth = ind_1.tree.get_max_children(ind_1.tree, 0)
            population.append(ind_1)
            """ Full """
            phenotype_2, genome_2, tree_2, nodes_2, invalid_2 = tree.full_init(grammar, depth)
            ind_2 = individual.individual(None, tree_2, grammar)
            ind_2.phenotype, ind_2.used_codons, ind_2.invalid = phenotype_2, len(genome_2), invalid_2
            ind_2.genome = genome_2 + [randint(0, grammar.codon_size) for i in range(int(ind_2.used_codons/2))]
            ind_2.nodes = nodes_2
            ind_2.depth = ind_2.tree.get_max_children(ind_2.tree, 0)
            population.append(ind_2)
        return population

def get_min_ramp_depth(size, grammar, max_tree_deth):
    """ Find the minimum depth at which ramping can start where we can have
        unique solutions (no duplicates)."""

    depths = range(grammar.min_path, max_tree_deth+1)

    if size % 2:
        # Population size is odd
        size = size + 1
    if size/2 < depths:
        depths = depths[:int(size/2)]

    unique_start = int(floor((size)/len(depths)))
    ramp = None
    for i in sorted(grammar.permutations.keys()):
        if grammar.permutations[i] > unique_start:
            ramp = i
            break
    return ramp