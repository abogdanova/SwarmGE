from copy import deepcopy
from random import randint, random, shuffle
from algorithm import parameters

def int_flip_mutation(ind):
    """Mutate the individual by randomly chosing a new int with
    probability p_mut. Works per-codon, hence no need for
    "within_used" option."""
    for i in range(len(ind.genome)):
        if random() < (1/len(ind.genome)):
            ind.genome[i] = randint(0, parameters.CODON_SIZE)
    ind.phenotype, ind.used_codons, ind.tree = None, None, None
   # ind.phenotype, ind.used_codons, ind.tree, ind.invalid = tree.genome_init(ind.tree.grammar, ind.genome)
   # if type(ind.used_codons) is list:
   #     ind.genome, ind.used_codons = ind.used_codons[0], ind.used_codons[1]
    return ind

def split_mutation(pop, gen):
    """Takes a population of individuals and performs subtree mutation on some
    and leaf mutation on others. Proportions of each varies as generations
    progress"""

    min_perc = 30
    var_perc = min_perc + (gen / float(parameters.GENERATIONS)) * (100 - (2 * min_perc))
    shuffle(pop)

    pop = deepcopy(pop)

    br_point = int((var_perc/100)*len(pop))
    pop_1 = pop[:br_point]
    pop_2 = pop[br_point:]
    pop_1 = list(map(leaf_mutation, pop_1))
    pop_2 = list(map(subtree_mutation, pop_2))
    pop = pop_1 + pop_2
    return pop

def subtree_mutation(ind):
    """Mutate the individual by randomly chosing a new int with
    probability p_mut. Works per-codon, hence no need for
    "within_used" option."""

    tail = ind.genome[ind.used_codons:]
    ind.phenotype, genome, ind.tree = ind.tree.subtree_mutate()
    ind.used_codons = len(genome)
    ind.genome = genome + tail
    ind.nodes = ind.tree.get_nodes()
    ind.depth = ind.tree.get_max_children(ind.tree, 0)
    return ind

def leaf_mutation(ind):
    """Mutate the individual by randomly chosing a new int with
    probability p_mut. Works per-codon, hence no need for
    "within_used" option."""

    tail = ind.genome[ind.used_codons:]
    ind.phenotype, genome, ind.tree = ind.tree.leaf_mutate()
    ind.used_codons = len(genome)
    ind.genome = genome + tail
    return ind
