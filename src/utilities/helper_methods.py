import numpy as np
from representation import tree
from algorithm.parameters import params
from copy import deepcopy
from operators.initialisers import genome_init

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

def RETURN_PERCENT(num, pop_size):
    """Returns either one percent of the population size or a given number,
       whichever is larger."""
    percent = int(round(pop_size/100))
    if percent < num:
        return num
    else:
        return percent


def generate_tree_from_genome(genome):
    """ Returns a tree given an input of a genome. Faster than normal genome
    initialisation as less information is returned. To be used when a tree needs
    to be built quickly from a given genome."""

    new_tree = tree.Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None,
                depth_limit=params['MAX_TREE_DEPTH'])
    _ = new_tree.fast_genome_derivation(genome)
    return new_tree


def verify_tree(ind_tree):
    """ Checks the entire tree for discrepancies """

    check_genome_from_tree(ind_tree)
    invalid = ind_tree.check_expansion()
    if invalid:
        print("Invalid given tree")
        quit()

    def check_nodes(ind_tree, n=0):
        n += 1

        if ind_tree.id != n:
            print("Node ids do not match node numbers")
            print(ind_tree.id, n)
            quit()

        if ind_tree.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in ind_tree.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            if not NT_kids:
                n += 1
            else:
                for child in NT_kids:
                    n = check_nodes(child, n)
        return n

    check_nodes(ind_tree)

    orig_out = deepcopy(ind_tree.get_output())
    orig_gen = deepcopy(ind_tree.build_genome([]))

    output, genome, ind_tree, nodes, invalid, depth, \
    used_codons = genome_init(orig_gen)

    if invalid:
        print("Invalid genome tree")
        print("Original:\t", orig_out)
        print("Genome:  \t", output)
        quit()

    if orig_out != output:
        print("Tree output doesn't match genome tree output")
        print("Original:\t", orig_out)
        print("Genome:  \t", output)
        quit()

    elif orig_gen != genome:
        print("Tree genome doesn't match genome tree genome")
        print("Original:\t", orig_gen)
        print("Genome:  \t", genome)
        quit()


def check_genome_from_tree(ind_tree):
    """ Goes through a tree and checks each codon to ensure production
        choice is correct """

    if ind_tree.codon:
        productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
        selection = ind_tree.codon % len(productions)
        chosen_prod = productions[selection]
        prods = [prod[0] for prod in chosen_prod]
        roots = []
        for kid in ind_tree.children:
            roots.append(kid.root)
        if roots != prods:
            print("\nGenome is incorrect")
            print("Codon productions:\t", prods)
            print("Actual children:  \t", roots)
            quit()
    for kid in ind_tree.children:
        kid.check_genome_from_tree()


def get_Xy_train_test(filename, randomise=True, test_proportion=0.5, skip_header=0):
    """Read in a table of numbers and split it into X (all columns up
    to last) and y (last column), then split it into training and
    testing subsets according to test_proportion. Shuffle if
    required."""
    Xy = np.genfromtxt(filename, skip_header=skip_header)
    if randomise:
        np.random.shuffle(Xy)
    X = Xy[:,:-1] # all columns but last
    y = Xy[:,-1] # last column
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
    train_X = train_Xy[:,:-1].transpose() # all columns but last
    train_y = train_Xy[:,-1].transpose() # last column
    test_X = test_Xy[:,:-1].transpose() # all columns but last
    test_y = test_Xy[:,-1].transpose() # last column

    return train_X, train_y, test_X, test_y


