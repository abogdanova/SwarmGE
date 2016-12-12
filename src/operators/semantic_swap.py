from random import choice

from algorithm.parameters import params
from representation import individual
from utilities.stats import trackers


def semantic_swap(parents):
    """
    Perform semantic swap on a population of individuals. The size of the
    swap population is defined as params['GENERATION_SIZE'] rather than params[
    'POPULATION_SIZE']. This saves on wasted evaluations and prevents search
    from evaluating too many individuals.

    :param parents: A population of parent individuals on which semantic swap
    is to be performed.
    :return: A population of fully semantically swapped individuals.
    """
    
    # Initialise an empty population.
    swap_pop = []
    
    # Iterate over entire parent population
    for ind in parents:
        
        # Make a copy of the individaul so we don't over-write the original
        # parent population.
        ind = ind.deep_copy()
        
        # Semantic swap cannot be performed on invalid individuals.
        if ind.invalid:
            print("Error, invalid ind selected for crossover")
            quit()
        
        # Perform semantic swap on ind.
        ind = semantic_subtree_swap(ind)
        
        if ind.invalid:
            # We have an invalid, need to do swap again.
            pass
        
        elif params['MAX_TREE_DEPTH'] and ind.depth > params['MAX_TREE_DEPTH']:
            # Tree is too deep, need to do swap again.
            pass
        
        elif params['MAX_TREE_NODES'] and ind.nodes > params['MAX_TREE_NODES']:
            # Tree has too many nodes, need to do swap again.
            pass
        
        elif params['MAX_GENOME_LENGTH'] and len(ind.genome) > \
                params['MAX_GENOME_LENGTH']:
            # Genome is too long, need to do swap again.
            pass
        
        else:
            # Swap was successful, extend the new population.
            swap_pop.append(ind)
    
    return swap_pop


def semantic_subtree_swap(ind):
    """
    Given one individual, search the derivation tree to see if any nodes can be
    swapped with existing better nodes from the snippets repository.

    :param ind: Parent 0.
    :return: The new individual.
    """

    # Get the set of labels of non terminals for the tree.
    nodes = ind.tree.get_node_labels_with_output([])

    # Initialise list of possible nodes to swap with existing snippets.
    swap_list = []
    
    for node in nodes:
        # Generate keys to check for snippets.
        RL_key = " ".join([str(node[2].pheno_index_rl), 'RL', node[0]])
        LR_key = " ".join([str(node[2].pheno_index_lr), 'LR', node[0]])
            
        if RL_key in trackers.snippets and not node[2].semantic_lock:
            # We have an existing snippet that we can swap in to improve the
            # current individual.
            swap_list.append([node, trackers.snippets[RL_key], RL_key])

        elif LR_key in trackers.snippets and not node[2].semantic_lock:
            # We have an existing snippet that we can swap in to improve the
            # current individual.
            swap_list.append([node, trackers.snippets[LR_key], LR_key])
    
    if swap_list:
        # There are improvements to be made
        # Pick a random item from the swap list.
        node = choice(swap_list)

        # Make new copy of existing snippet
        new_node = node[1].__copy__()
        
        # Get parent of original node
        parent = node[0][2].parent

        if parent:
            # Get the index of the original node in the children of its parent.
            idx = parent.children.index(node[0][2])

            # Set new child
            parent.children[idx] = new_node
        
        # Set parent of new node
        new_node.parent = parent
        
        # Re-map individual with new tree.
        ind = individual.Individual(None, ind.tree)
    
    return ind
