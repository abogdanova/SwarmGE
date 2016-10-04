from algorithm.parameters import params
from representation.tree import Tree
import numpy as np


def python_filter(txt):
    """ Create correct python syntax.

    We use {: and :} as special open and close brackets, because
    it's not possible to specify indentation correctly in a BNF
    grammar without this type of scheme."""

    indent_level = 0
    tmp = txt[:]
    i = 0
    while i < len(tmp):
        tok = tmp[i:i+2]
        if tok == "{:":
            indent_level += 1
        elif tok == ":}":
            indent_level -= 1
        tabstr = "\n" + "  " * indent_level
        if tok == "{:" or tok == ":}":
            tmp = tmp.replace(tok, tabstr, 1)
        i += 1
    # Strip superfluous blank lines.
    txt = "\n".join([line for line in tmp.split("\n")
                     if line.strip() != ""])
    return txt


def return_percent(num, pop_size):
    """Returns either one percent of the population size or a given number,
       whichever is larger."""
    percent = int(round(pop_size/100))
    if percent < num:
        return num
    else:
        return percent


def generate_tree_from_genome(genome):
    """ Returns a tree given an input of a genome. Faster than normal genome
    initialisation as less information is returned. To be used when a tree
    needs to be built quickly from a given genome."""

    new_tree = Tree(str(params['BNF_GRAMMAR'].start_rule[0]), None,
                    depth_limit=params['MAX_TREE_DEPTH'])
    new_tree.fast_genome_derivation(genome)
    return new_tree


def get_Xy_train_test(filename, randomise=True, test_proportion=0.5,
                      skip_header=0):
    """Read in a table of numbers and split it into X (all columns up
    to last) and y (last column), then split it into training and
    testing subsets according to test_proportion. Shuffle if
    required."""
    Xy = np.genfromtxt(filename, skip_header=skip_header)
    if randomise:
        np.random.shuffle(Xy)
    X = Xy[:, :-1]  # all columns but last
    y = Xy[:, -1]  # last column
    idx = int((1.0 - test_proportion) * len(y))
    train_X = X[:idx]
    train_y = y[:idx]
    test_X = X[idx:]
    test_y = y[idx:]
    return train_X, train_y, test_X, test_y


def get_Xy_train_test_separate(train_filename, test_filename, skip_header=0):
    """Read in training and testing data files, and split each into X
    (all columns up to last) and y (last column)."""
    train_Xy = np.genfromtxt(train_filename, skip_header=skip_header)
    test_Xy = np.genfromtxt(test_filename, skip_header=skip_header)
    train_X = train_Xy[:, :-1].transpose()  # all columns but last
    train_y = train_Xy[:, -1].transpose()  # last column
    test_X = test_Xy[:, :-1].transpose()  # all columns but last
    test_y = test_Xy[:, -1].transpose()  # last column

    return train_X, train_y, test_X, test_y


def check_expansion(tree, nt_keys):
    """ Check if a given tree is completely expanded or not. Return boolean
        True if the tree IS NOT completely expanded.
    """
    
    check = False
    if tree.root in nt_keys:
        # Current node is a NT and should have children
        if tree.children:
            # Everything is as expected
            for child in tree.children:
                check = child.check_expansion(nt_keys)
                if check:
                    break
        else:
            # Current node is not completely expanded
            check = True
    
    return check


def build_genome(tree, genome):
    """
    Goes through a tree and builds a genome from all codons in the subtree.

    :param genome: The list of all codons in a subtree.
    :return: The fully built genome of a subtree.
    """
    
    if tree.codon:
        # If the current node has a codon, append it to the genome.
        genome.append(tree.codon)
    
    for child in tree.children:
        # Recurse on all children.
        genome = child.build_genome(genome)
    
    return genome


def get_tree_info(tree, current, number=0, max_depth=0):
    """ Get the number of nodes and the max depth of the tree.
    """
    
    number += 1
    # if current.root in params['BNF_GRAMMAR'].non_terminals:
    
    if current.parent:
        current.depth = current.parent.depth + 1
    else:
        current.depth = 1
    if current.depth > max_depth:
        max_depth = current.depth
    NT_kids = [kid for kid in
               tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]
    if not NT_kids:
        number += 1
    else:
        for child in NT_kids:
            max_depth, number = child.get_tree_info(child, number,
                                                    max_depth)
    
    return max_depth, number


def get_max_tree_depth(tree, max_d=1):
    """ Returns the maximum depth of the tree from the current node. """
    
    curr_depth = tree.get_current_depth()
    if curr_depth > max_d:
        max_d = curr_depth
    for child in tree.children:
        max_d = child.get_max_tree_depth(child, max_d)
    return max_d