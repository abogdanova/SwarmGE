from random import randint, random, shuffle
from algorithm.parameters import params
from representation import individual
from copy import deepcopy


def mutation_wheel():
    if params['MUTATION'] == "subtree":
        params['MUTATION'] = subtree_mutation
    elif params['MUTATION'] == "int_flip":
        params['MUTATION'] = int_flip_mutation
    elif params['MUTATION'] == "split":
        params['MUTATION'] = split_mutation
    else:
        print("Error: Mutation operator not specified correctly")
        exit(2)


def int_flip_mutation(ind):
    """Mutate the individual by randomly choosing a new int with probability
    p_mut. Works per-codon, hence no need for "within_used" option."""

    p_mut = params['MUTATION_EVENTS']
    if type(p_mut) is str:
        p_mut == 1/len(ind.genome)
    elif type(p_mut) is float:
        p_mut = params['MUTATION_EVENTS']
    elif type(p_mut) is int:
        p_mut == p_mut/len(ind.genome)

    for i in range(len(ind.genome)):
        if random() < p_mut:
            ind.genome[i] = randint(0, params['CODON_SIZE'])
    ind = individual.individual(ind.genome, None)
    return ind


def split_mutation(pop, gen):
    """Takes a population of individuals and performs subtree mutation on some
    and leaf mutation on others. Proportions of each varies as generations
    progress"""

    min_perc = 30
    var_perc = min_perc + (gen / float(params['GENERATIONS'])) * \
                          (100 - (2 * min_perc))
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
    """Mutate the individual by replacing a randomly selected subtree with a
    new subtree. Guaranteed one event per individual if called."""

    # Allow for multiple subtree mutation events
    p_mut = params['MUTATION_EVENTS']
    if type(p_mut) is not int:
        p_mut = 1

    for i in range(p_mut):
        tail = deepcopy(ind.genome[ind.used_codons+1:])
        ind.phenotype, genome, ind.tree = ind.tree.subtree_mutate()
        ind = individual.individual(genome, None)
        ind.genome = genome + tail[:int(len(genome)/2)]

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
