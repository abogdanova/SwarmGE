from random import randint, random, sample, choice
from representation import individual, tree
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
    i = 0
    while len(cross_pop) < params['GENERATION_SIZE']:
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
        i += 1

    return cross_pop


def onepoint_crossover(p_0, p_1, within_used=True):
    """Given two individuals, create two children using one-point crossover and
    return them."""

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
    """Given two individuals, create two children using subtree crossover and
    return them."""

    if random() > params['CROSSOVER_PROBABILITY']:
        ind0 = p_1
        ind1 = p_0
    else:

        tail_0, tail_1 = p_0.genome[p_0.used_codons:], p_1.genome[p_1.used_codons:]
        tree_0, genome_0, tree_1, genome_1 = do_subtree_crossover(p_0.tree, p_1.tree)

        ind0 = individual.individual(genome_0, tree_0)
        ind0.genome = genome_0 + tail_0
        ind0.used_codons = len(genome_0)
        ind0.depth, ind0.nodes = tree_0.get_tree_info(tree_0)

        ind1 = individual.individual(genome_1, tree_1)
        ind1.genome = genome_1 + tail_1
        ind1.used_codons = len(genome_1)
        ind1.depth, ind1.nodes = tree_1.get_tree_info(tree_1)

    return [ind0, ind1]


def do_subtree_crossover(orig_tree1, orig_tree2):

    # Have to do a deepcopy of original trees as identical trees will give the
    # same class instances for their children.
    copy_tree1 = deepcopy(orig_tree1)
    copy_tree2 = deepcopy(orig_tree2)

    def do_crossover(tree1, tree2, intersection):

        crossover_choice = choice(intersection)

        indexes_1 = tree1.get_target_nodes([], target=[crossover_choice])
        indexes_1 = list(set(indexes_1))
        number1 = choice(indexes_1)
        t1 = tree1.return_node_from_id(number1, return_tree=None)

        indexes_2 = tree2.get_target_nodes([], target=[crossover_choice])
        indexes_2 = list(set(indexes_2))
        number2 = choice(indexes_2)
        t2 = tree2.return_node_from_id(number2, return_tree=None)

        d1 = t1.get_depth()
        d2 = t2.get_depth()

        # when the crossover is between the entire tree of both tree1 and tree2
        if d1 == 1 and d2 == 1:
            return t2, t1
        # when only t1 is the entire tree1
        elif d1 == 1:
            p2 = t2.parent
            tree1 = t2
            try:
                p2.children.index(t2)
            except ValueError:
                print("Error: child not in parent.")
                quit()
            i2 = p2.children.index(t2)
            p2.children[i2] = t1
            t1.parent = p2
            t2.parent = None

        # when only t2 is the entire tree2
        elif d2 == 1:
            p1 = t1.parent
            tree2 = t1
            try:
                p1.children.index(t1)
            except ValueError:
                print("Error: child not in parent")
                quit()
            i1 = p1.children.index(t1)
            p1.children[i1] = t2
            t2.parent = p1
            t1.parent = None

        # when the crossover node for both trees is not the entire tree
        else:
            p1 = t1.parent
            p2 = t2.parent

            i1 = p1.children.index(t1)
            i2 = p2.children.index(t2)

            p1.children[i1] = t2
            p2.children[i2] = t1

            t2.parent = p1
            t1.parent = p2

        return tree1, tree2

    def get_labels(t1, t2):
        return t1.getLabels(set()), t2.getLabels(set())

    labels1, labels2 = get_labels(orig_tree1, orig_tree2)

    def intersect(l1, l2):
        intersection = l1.intersection(l2)
        intersection = [i for i in intersection if i in params['BNF_GRAMMAR'].crossover_NTs]
        return sorted(intersection)

    intersection = intersect(labels1, labels2)

    if len(intersection) != 0:
        # Cross over parts of trees
        ret_tree1, ret_tree2 = do_crossover(copy_tree1, copy_tree2,
                                            intersection)
    else:
        # Cross over entire trees
        ret_tree1, ret_tree2 = copy_tree2, copy_tree1

    return ret_tree1, ret_tree1.build_genome([]), ret_tree2, \
           ret_tree2.build_genome([])
