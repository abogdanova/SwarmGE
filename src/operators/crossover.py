from representation import individual, tree
from random import randint, random, sample
from algorithm.parameters import params
from copy import deepcopy


def crossover_wheel():
    if params['CROSSOVER'] == "subtree":
        params['CROSSOVER'] = subtree_crossover
    elif params['CROSSOVER'] == "onepoint":
        params['CROSSOVER'] = onepoint_crossover
    else:
        print("Error: Crossover operator not specified correctly")
        exit(2)


def crossover(parents):
    """ Perform crossover on a population """

    cross_pop = []
    while len(cross_pop) < params['GENERATION_SIZE']:
        #TODO check is this correct. We do crossover on a subset of the selected population.
        inds_in = deepcopy(sample(parents, 2))
        inds = params['CROSSOVER'](inds_in[0], inds_in[1])
        if any([ind.invalid for ind in inds]):
            # we have an invalid, need to do crossover again
            pass
        elif any([ind.depth > params['MAX_TREE_DEPTH'] for ind in inds]):
            # Tree is too big, need to do crossover again
            pass
        #TODO we have a global tree depth limit, but no global max used codons length limit. Add in to prevent genome bloat?
        else:
            cross_pop.extend(inds)

    return cross_pop


def onepoint_crossover(p_0, p_1, within_used=True):
    """Given two individuals, create two children using one-point
    crossover and return them."""

    # Get the chromosomes
    c_p_0, c_p_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points. If within_used==True,
    # points will be within the used section.
    if within_used:
        max_p_0, max_p_1 = p_0.used_codons, p_1.used_codons
    else:
        max_p_0, max_p_1 = len(c_p_0), len(c_p_1)
    pt_p_0, pt_p_1 = randint(1, max_p_0), randint(1, max_p_1)

    # Make new chromosomes by crossover: these slices perform copies
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = c_p_0[:pt_p_0] + c_p_1[pt_p_1:]
        c_1 = c_p_1[:pt_p_1] + c_p_0[pt_p_0:]
    else:
        c_0, c_1 = c_p_0[:], c_p_1[:]

    # Put the new chromosomes into new individuals
    ind_0 = individual.individual(c_0, None)
    ind_1 = individual.individual(c_1, None)

    return [ind_0, ind_1]


def subtree_crossover(p_0, p_1):
    """Given two individuals, create two children using subtree
    crossover and return them."""

    if random() > params['CROSSOVER_PROBABILITY']:
        ind0 = p_1
        ind1 = p_0
    else:
        tail_0, tail_1 = p_0.genome[p_0.used_codons:], p_1.genome[p_1.used_codons:]
        tree_0, genome_0, tree_1, genome_1 = tree.subtree_crossover(p_0.tree, p_1.tree)

        ind0 = individual.individual(genome_0, None)
        ind0.genome = genome_0 + tail_0

        ind1 = individual.individual(genome_1, None)
        ind1.genome = genome_1 + tail_1

    return [ind0, ind1]
