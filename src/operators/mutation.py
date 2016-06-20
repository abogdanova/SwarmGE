from random import randint, random, choice
from algorithm.parameters import params
from representation import individual
from copy import deepcopy


def mutation_wheel():
    if params['MUTATION'] == "subtree":
        params['MUTATION'] = subtree_mutation
    elif params['MUTATION'] == "int_flip":
        params['MUTATION'] = int_flip_mutation
    else:
        print("Error: Mutation operator not specified correctly")
        exit(2)


def int_flip_mutation(ind):
    """Mutate the individual by randomly choosing a new int with probability
    p_mut. Works per-codon, hence no need for "within_used" option."""

    p_mut = params['MUTATION_EVENTS']
    if type(p_mut) is str:
        p_mut = 1/len(ind.genome)
    elif type(p_mut) is float:
        p_mut = params['MUTATION_EVENTS']
    elif type(p_mut) is int:
        p_mut = p_mut/len(ind.genome)

    for i in range(len(ind.genome)):
        if random() < p_mut:
            ind.genome[i] = randint(0, params['CODON_SIZE'])
    ind = individual.individual(ind.genome, None)
    return ind


def subtree_mutation(ind):
    """Mutate the individual by replacing a randomly selected subtree with a
    new subtree. Guaranteed one event per individual if called."""

    # Allow for multiple subtree mutation events
    p_mut = params['MUTATION_EVENTS']
    if type(p_mut) is not int:
        p_mut = 1

    for i in range(p_mut):
        tail = deepcopy(ind.genome[ind.used_codons+1:])
        ind.phenotype, genome, ind.tree = subtree_mutate(ind.tree)
        ind.used_codons = len(genome)
        ind.depth, ind.nodes = ind.tree.get_tree_info(ind.tree)
        ind.genome = genome + tail[:int(len(genome)/2)]

    return ind


def subtree_mutate(ind_tree):
    """ Creates a list of all nodes and picks one node at random to mutate.
        Because we have a list of all nodes we can (but currently don't)
        choose what kind of nodes to mutate on. Handy. Should hopefully be
        faster and less error-prone to the previous subtree mutation.
    """

    # Find which nodes we can mutate from
    targets = ind_tree.get_target_nodes([], target=params['BNF_GRAMMAR'].non_terminals)

    # Pick a node
    number = choice(targets)

    # Get the subtree
    new_tree = ind_tree.return_node_from_id(number, return_tree=None)

    # Set the depth limits for the new subtree
    new_tree.max_depth = ind_tree.depth_limit - new_tree.get_depth()

    # Mutate a new subtree
    x, y, d, md = new_tree.derivation([], "random", 0, 0, 0, depth_limit=new_tree.max_depth)
    genome = ind_tree.build_genome([])

    return ind_tree.get_output(), genome, ind_tree
