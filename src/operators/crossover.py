from representation import individual,tree
from algorithm.parameters import params
from random import randint, random

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
    ind_0 = individual.individual(c_0, None, None)
   # ind_0.phenotype, ind_0.used_codons = grammar.generate(c_0)
    #ind_0.phenotype, ind_0.used_codons, ind_0.tree, ind_0.invalid = tree.genome_init(grammar, c_0)
   # if type(ind_0.used_codons) is list:
   #     ind_0.genome, ind_0.used_codons = ind_0.used_codons[0], ind_0.used_codons[1]
    ind_1 = individual.individual(c_1, None, None)
   # ind_1.phenotype, ind_1.used_codons = grammar.generate(c_1)
    #ind_1.phenotype, ind_1.used_codons, ind_1.tree, ind_1.invalid = tree.genome_init(grammar, c_1)
   # if type(ind_1.used_codons) is list:
   #     ind_1.genome, ind_1.used_codons = ind_1.used_codons[0], ind_1.used_codons[1]
    return [ind_0, ind_1]

def subtree_crossover(p_0, p_1, within_used=True):
    """Given two individuals, create two children using subtree
    crossover and return them."""
    # Get the chromosomes#

    if random() > params['CROSSOVER_PROBABILITY']:
        ind0 = p_1
        ind1 = p_0
    else:
        c_p_0, c_p_1 = p_0.tree, p_1.tree
        g_t_0, g_t_1 = p_0.genome[p_0.used_codons:], p_1.genome[p_1.used_codons:]
        tree_0, genome_0, tree_1, genome_1 = tree.subtree_crossover(c_p_0, c_p_1)
        ind0 = individual.individual(genome_0, tree_0, None)
        ind0.used_codons = len(genome_0)
        ind0.genome = ind0.genome + g_t_0
        ind0.phenotype = tree_0.get_output()
        ind1 = individual.individual(genome_1, tree_1, None)
        ind1.used_codons = len(genome_1)
        ind1.genome = ind1.genome + g_t_1
        ind1.phenotype = tree_1.get_output()

    return [ind0, ind1]