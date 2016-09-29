from random import randint, random, choice

from algorithm.parameters import params
from representation import individual
from representation.tree import generate_tree


def mutation(pop):
    """
    Perform mutation on a population of individuals. Calls mutation operator as
    specified in params dictionary.
    
    :param pop: A population of individuals to be mutated.
    :return: A fully mutated population.
    """

    return list(map(params['MUTATION'], pop))


def int_flip(ind):
    """
    Mutate the genome of an individual by randomly choosing a new int with
    probability p_mut. Works per-codon.
    
    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    # Set mutation probability. Default is 1 over the length of the genome.
    if params['MUTATION_PROBABILITY']:
        p_mut = params['MUTATION_PROBABILITY']
    else:
        # Default mutation events per individual is 1. Raising this number
        # will influence the mutation probability for each codon.
        p_mut = params['MUTATION_EVENTS']/len(ind.genome)

    # Mutation probability works per-codon over the entire genome (not just
    # the used length).
    for i in range(len(ind.genome)):
        if random() < p_mut:
            ind.genome[i] = randint(0, params['CODON_SIZE'])

    # Re-build a new individaul with the newly mutated genetic information.
    new_ind = individual.Individual(ind.genome, None)

    return new_ind


def subtree(ind):
    """
    Mutate the individual by replacing a randomly selected subtree with a
    new subtree. Guaranteed one event per individual if called.
    
    :param ind: An individual to be mutated.
    :return: A mutated individual.
    """

    # Save the tail of the genome.
    tail = ind.genome[ind.used_codons:]
    
    # Allows for multiple mutation events should that be desired.
    for i in range(params['MUTATION_EVENTS']):
        genome, ind.tree = subtree_mutate(ind.tree)
    
    # Re-build a new individaul with the newly mutated genetic information.
    ind = individual.Individual(genome, ind.tree)
    
    # Add in the previous tail.
    ind.genome = genome + tail

    return ind


def subtree_mutate(ind_tree):
    """
    Creates a list of all nodes and picks one node at random to mutate.
    Because we have a list of all nodes, we can (but currently don't) choose
    what kind of nodes to mutate on. Handy.
    
    :param ind_tree: The full tree of an individual.
    :return: The full mutated tree and the associated genome.
    """

    # Find which nodes we can mutate from
    targets = \
        ind_tree.get_target_nodes([],
                                  target=params['BNF_GRAMMAR'].non_terminals)

    # Pick a node
    number = choice(targets)

    # Get the subtree
    new_tree = ind_tree.return_node_from_id(number, return_tree=None)

    # Set the depth limits for the new subtree
    new_tree.max_depth = params['MAX_TREE_DEPTH'] - \
                         new_tree.get_current_depth()

    # Mutate a new subtree
    generate_tree(new_tree, [], "random", 0, 0, 0, new_tree.max_depth)

    return ind_tree.build_genome([]), ind_tree
