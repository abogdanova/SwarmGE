from random import randint, random, sample, choice
from algorithm.parameters import params
from representation import individual


def crossover(parents):
    """
    Perform crossover on a population of individuals. The size of the crossover
    population is defined as params['GENERATION_SIZE'] rather than params[
    'POPULATION_SIZE']. This saves on wasted evaluations and prevents search
    from evaluating too many individuals.
    
    :param parents: A population of parent individuals on which crossover is to
    be performed.
    :return: A population of fully crossed over individuals.
    """

    # Initialise an empty population.
    cross_pop = []
    while len(cross_pop) < params['GENERATION_SIZE']:
        
        # Randomly choose two parents from the parent population.
        inds_in = sample(parents, 2)

        # Create copies of the original parents. This is necessary as the
        # original parents remain in the parent population and changes will
        # affect the originals unless they are cloned.
        ind_0 = inds_in[0].deep_copy()
        ind_1 = inds_in[1].deep_copy()

        # Crossover cannot be performed on invalid individuals.
        if ind_0.invalid or ind_1.invalid:
            print("Error, invalid inds selected for crossover")
            exit(2)

        # Perform crossover on ind_0 and ind_1.
        inds = params['CROSSOVER'](ind_0, ind_1)
        
        if any([ind.invalid for ind in inds]):
            # We have an invalid, need to do crossover again.
            pass
        
        elif any([ind.depth > params['MAX_TREE_DEPTH'] for ind in inds]):
            # Tree is too big, need to do crossover again.
            pass
        
        else:
            # Crossover was successful, extend the new population.
            cross_pop.extend(inds)

    return cross_pop


def onepoint(p_0, p_1, within_used=True):
    """
    Given two individuals, create two children using one-point crossover and
    return them. A different point is selected on each genome for crossover
    to occur. Crossover points are selected within the used portion of the
    genome by default (i.e. crossover does not occur in the tail of the
    individual).
    
    Onepoint crossover in Grammatical Evolution is explained further in:
        O'Neill, M., Ryan, C., Keijzer, M. and Cattolico, M., 2003.
        Crossover in grammatical evolution.
        Genetic programming and evolvable machines, 4(1), pp.67-93.
        DOI: 10.1023/A:1021877127167
    
    :param p_0: Parent 0
    :param p_1: Parent 1
    :param within_used: Boolean flag for selecting whether or not crossover
    is performed within the used portion of the genome. Default set to True.
    :return: A list of crossed-over individuals.
    """

    # Get the chromosomes.
    c_p_0, c_p_1 = p_0.genome, p_1.genome

    # Uniformly generate crossover points. If within_used==True,
    # points will be within the used section.
    if within_used:
        max_p_0, max_p_1 = p_0.used_codons, p_1.used_codons
    else:
        max_p_0, max_p_1 = len(c_p_0), len(c_p_1)
        
    # Select unique points on each genome for crossover to occur.
    pt_p_0, pt_p_1 = randint(1, max_p_0), randint(1, max_p_1)

    # Make new chromosomes by crossover: these slices perform copies.
    if random() < params['CROSSOVER_PROBABILITY']:
        c_0 = c_p_0[:pt_p_0] + c_p_1[pt_p_1:]
        c_1 = c_p_1[:pt_p_1] + c_p_0[pt_p_0:]
    else:
        c_0, c_1 = c_p_0[:], c_p_1[:]

    # Put the new chromosomes into new individuals.
    ind_0 = individual.Individual(c_0, None)
    ind_1 = individual.Individual(c_1, None)

    return [ind_0, ind_1]


def subtree(p_0, p_1):
    """
    Given two individuals, create two children using subtree crossover and
    return them. Candidate subtrees are selected based on matching
    non-terminal nodes rather than matching terminal nodes.
    
    :param p_0: Parent 0.
    :param p_1: Parent 1.
    :return: A list of crossed-over individuals.
    """

    def do_crossover(tree0, tree1, shared_nodes):
        """
        Given two instances of the representation.tree.Tree class (
        derivation trees of individuals) and a list of intersecting
        non-terminal nodes across both trees, performs subtree crossover on
        these trees.
        
        :param tree0: The derivation tree of individual 0.
        :param tree1: The derivation tree of individual 1.
        :param shared_nodes: The sorted list of all non-terminal nodes that are
        in both derivation trees.
        :return: The new derivation trees after subtree crossover has been
        performed.
        """
    
        # Randomly choose a non-terminal from the set of permissible
        # intersecting non-terminals.
        crossover_choice = choice(shared_nodes)
    
        # Find the indexes of all nodes in tree0 that match the chosen
        # crossover node.
        indexes_0 = tree0.get_target_nodes([], target=[crossover_choice])
        indexes_0 = list(set(indexes_0))
        
        # Randomly pick an index and return the corresponding subtree at
        # that index.
        number_0 = choice(indexes_0)
        t0 = tree0.return_node_from_id(number_0, return_tree=None)

        # Find the indexes of all nodes in tree1 that match the chosen
        # crossover node.
        indexes_1 = tree1.get_target_nodes([], target=[crossover_choice])
        indexes_1 = list(set(indexes_1))

        # Randomly pick an index and return the corresponding subtree at
        # that index.
        number_1 = choice(indexes_1)
        t1 = tree1.return_node_from_id(number_1, return_tree=None)
    
        # Get the depths of both chosen subtrees.
        d0 = t0.get_current_depth()
        d1 = t1.get_current_depth()
    
        if d0 == 1 and d1 == 1:
            # Crossover is between the entire tree of both tree0 and tree1.
            
            return t1, t0
        
        elif d0 == 1:
            # Only t0 is the entire of tree0.
            # Get the original parent of subtree t1.
            p1 = t1.parent
            tree0 = t1

            # Swap over the subtrees between parents.
            i1 = p1.children.index(t1)
            p1.children[i1] = t0

            # Set the parents of the crossed-over subtrees as their new
            # parents. Since the entire tree of t1 is now a whole
            # individual, it has no parent.
            t0.parent = p1
            t1.parent = None
    
        elif d1 == 1:
            # Only t1 is the entire of tree1.
            # Get the original parent of subtree t0.
            p0 = t0.parent
            tree1 = t0

            # Swap over the subtrees between parents.
            i0 = p0.children.index(t0)
            p0.children[i0] = t1

            # Set the parents of the crossed-over subtrees as their new
            # parents. Since the entire tree of t0 is now a whole
            # individual, it has no parent.
            t1.parent = p0
            t0.parent = None
    
        else:
            # The crossover node for both trees is not the entire tree.
            # Get the original parents of both chosen subtrees.
            p0 = t0.parent
            p1 = t1.parent
        
            # For the parent nodes of the original subtrees, get the indexes
            # of the original subtrees.
            i0 = p0.children.index(t0)
            i1 = p1.children.index(t1)
        
            # Swap over the subtrees between parents.
            p0.children[i0] = t1
            p1.children[i1] = t0
        
            # Set the parents of the crossed-over subtrees as their new
            # parents.
            t1.parent = p0
            t0.parent = p1
    
        return tree0, tree1

    def intersect(l0, l1):
        """
        Returns the intersection of two sets of labels of nodes of
        derivation trees. Only returns matching non-terminal nodes across
        both derivation trees.
        
        :param l0: The labels of all nodes of tree 0.
        :param l1: The labels of all nodes of tree 1.
        :return: The sorted list of all non-terminal nodes that are in both
        derivation trees.
        """
        
        # Find all intersecting elements of both sets l0 and l1.
        shared_nodes = l0.intersection(l1)
        
        # Find only the non-terminals present in the intersecting set of
        # labels.
        shared_nodes = [i for i in shared_nodes if i in params['BNF_GRAMMAR'].crossover_NTs]
        
        return sorted(shared_nodes)

    if random() > params['CROSSOVER_PROBABILITY']:
        # Crossover is not to be performed, return entire individuals.
        ind0 = p_1
        ind1 = p_0
    
    else:
        # Crossover is to be performed. Save tail of each genome.
        tail_0, tail_1 = p_0.genome[p_0.used_codons:], \
                         p_1.genome[p_1.used_codons:]
        
        # Get the set of labels of non terminals for each tree.
        labels1 = p_0.tree.get_labels(set())
        labels2 = p_1.tree.get_labels(set())

        # Find overlapping non-terminals across both trees.
        shared_nodes = intersect(labels1, labels2)

        if len(shared_nodes) != 0:
            # There are overlapping NTs, cross over parts of trees.
            ret_tree0, ret_tree1 = do_crossover(p_0.tree, p_1.tree,
                                                shared_nodes)
        else:
            # There are no overlapping NTs, cross over entire trees.
            ret_tree0, ret_tree1 = p_1.tree, p_0.tree

        # Build new genomes
        genome_0 = ret_tree0.build_genome([]) + tail_0
        genome_1 = ret_tree1.build_genome([]) + tail_1

        # Initialise new individuals.
        ind0 = individual.Individual(genome_0, ret_tree0)
        ind1 = individual.Individual(genome_1, ret_tree1)

    return [ind0, ind1]
