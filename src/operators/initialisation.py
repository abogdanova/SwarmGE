from representation.tree import Tree
from algorithm.parameters import params
from representation import individual
from random import shuffle, randint
from algorithm import mapper
from math import floor


def random_init(size):
    """Randomly create a population of size and return"""
    return [individual.Individual(None, None) for _ in range(size)]


def rhh(size):
    """ Create a population of size using ramped half and half (or sensible
        initialisation) and return. Individuals have a genome created for them
    """

    depths = range(params['BNF_GRAMMAR'].min_ramp + 1,
                   params['MAX_INIT_DEPTH']+1)
    population = []

    if size < 2:
        print("Error: population size too small for RHH initialisation.")
        print("Returning randomly built trees.")
        return [individual.Individual(None, None) for _ in range(size)]
    else:
        if size % 2:
            # Population size is odd
            size += 1
        if size/2 < len(depths):
            depths = depths[:int(size/2)]
        times = int(floor((size/2)/len(depths)))
        remainder = int(size/2 - (times * len(depths)))

        for depth in depths:
            for i in range(times):
                """ Grow """
                method = "random"
                phenotype, genome, ind_tree, nodes, invalid, tree_depth, \
                    used_cod = tree_init(depth, method)
                ind = individual.Individual(genome, ind_tree)
                ind.phenotype, ind.nodes = phenotype, nodes
                ind.depth, ind.used_codons = tree_depth, used_cod
                ind.genome = genome + [randint(0, params['CODON_SIZE']) for
                                       _ in range(int(ind.used_codons/2))]
                population.append(ind)
                """ Full """
                method = "full"
                phenotype, genome, ind_tree, nodes, invalid, tree_depth, \
                    used_cod = tree_init(depth, method)
                ind = individual.Individual(genome, ind_tree)
                ind.phenotype, ind.nodes = phenotype, nodes
                ind.depth, ind.used_codons = tree_depth, used_cod
                ind.genome = genome + [randint(0, params['CODON_SIZE']) for
                                       _ in range(int(ind.used_codons/2))]
                population.append(ind)

        if remainder:
            depths = list(depths)
            shuffle(depths)

        for i in range(remainder):
            depth = depths.pop()
            """ Grow """
            method = "random"
            phenotype, genome, ind_tree, nodes, \
            invalid, tree_depth, used_cod = tree_init(depth, method)
            ind = individual.Individual(genome, ind_tree)
            ind.phenotype, ind.nodes = phenotype, nodes
            ind.depth, ind.used_codons = tree_depth, used_cod
            ind.genome = genome + [randint(0, params['CODON_SIZE']) for
                                   _ in range(int(ind.used_codons/2))]
            population.append(ind)
            """ Full """
            method = "full"
            phenotype, genome, ind_tree, nodes, invalid, \
            tree_depth, used_cod = tree_init(depth, method)
            ind = individual.Individual(genome, ind_tree)
            ind.phenotype, ind.nodes = phenotype, nodes
            ind.depth, ind.used_codons = tree_depth, used_cod
            ind.genome = genome + [randint(0, params['CODON_SIZE']) for
                                   _ in range(int(ind.used_codons/2))]
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
        size += 1
    if size/2 < len(depths):
        depths = depths[:int(size/2)]

    unique_start = int(floor(size/len(depths)))
    ramp = None
    for i in sorted(grammar.permutations.keys()):
        if grammar.permutations[i] > unique_start:
            ramp = i
            break
    return ramp


def pi_random_init(depth):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),),
                None, max_depth=depth, depth_limit=depth)
    genome = tree.pi_random_derivation(0, max_depth=depth)
    if tree.check_expansion():
        print("tree.pi_random_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False


def pi_grow_init(depth):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None,
                max_depth=depth, depth_limit=depth)
    genome = tree.pi_grow(0, max_depth=depth)
    if tree.check_expansion():
        print("tree.pi_grow_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False


def tree_init(depth, method):
    """
    Initialise a tree to a given depth using a specified method for
    initialisation.
    """

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None,
                max_depth=depth-1, depth_limit=depth-1)
    genome, nodes, d, max_depth = mapper.tree_derivation(tree, [], method,
                                                         0, 0, 0, depth-1)

    if tree.check_expansion():
        print("tree.init generated an Invalid")
        quit()

    return tree.get_output(), genome, tree, nodes, \
           False, max_depth, len(genome)
